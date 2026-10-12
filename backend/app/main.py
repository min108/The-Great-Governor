import json
import os
import re
import uuid
from pathlib import Path

import anyio
import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .db import dumps, load_env, loads
from .quality import coverage_issues, gate_candidate
from .seed import build

load_env()
app = FastAPI(title="监督智源")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
DB_LOCK = anyio.Lock()


@app.middleware("http")
async def serialize_sqlite(request, call_next):
    async with DB_LOCK:
        return await call_next(request)

CONN = None


@app.on_event("startup")
def startup():
    global CONN
    rebuild = os.environ.get("ZHIYUAN_REBUILD") == "1"
    CONN = build(rebuild=rebuild)


def q(sql, params=()):
    return CONN.execute(sql, params).fetchall()


def one(sql, params=()):
    row = CONN.execute(sql, params).fetchone()
    if row is None:
        raise HTTPException(404, "没有找到")
    return row


def asset_dict(row):
    data = dict(row)
    data["body"] = loads(data.pop("body_json"), {})
    return data


def relations_for(kind, item_id, limit=28):
    rows = [
        dict(row)
        for row in q(
            """SELECT * FROM relations
            WHERE (from_kind=? AND from_id=?) OR (to_kind=? AND to_id=?)
            ORDER BY confirm_status, rel_type""",
            (kind, item_id, kind, item_id),
        )
    ]
    preferred = [row for row in rows if row["rel_type"] != "引用数据"]
    bulk = [row for row in rows if row["rel_type"] == "引用数据"]
    chosen = (preferred + bulk)[:limit]
    result = []
    for item in chosen:
        if item["from_kind"] == kind and item["from_id"] == item_id:
            item["other_kind"] = item["to_kind"]
            item["other_id"] = item["to_id"]
            item["way"] = "指出"
        else:
            item["other_kind"] = item["from_kind"]
            item["other_id"] = item["from_id"]
            item["way"] = "被引"
        item["other_name"] = label_of(item["other_kind"], item["other_id"])
        result.append(item)
    return result, len(rows)


def label_of(kind, item_id):
    if kind == "standard":
        row = CONN.execute("SELECT name FROM data_standards WHERE code=?", (item_id,)).fetchone()
        return row["name"] if row else item_id
    if kind == "algorithm":
        row = CONN.execute("SELECT name FROM algorithms WHERE code=?", (item_id,)).fetchone()
        return row["name"] if row else item_id
    if kind == "object":
        row = CONN.execute("SELECT name FROM objects WHERE id=?", (item_id,)).fetchone()
        return row["name"] if row else item_id
    if kind in ("rule", "knowledge", "mapping"):
        row = CONN.execute("SELECT name FROM assets WHERE id=?", (item_id,)).fetchone()
        return row["name"] if row else item_id
    return item_id


@app.get("/api/health")
def health():
    return {"ok": True, "name": "监督智源"}


@app.get("/api/overview")
def overview():
    standards = CONN.execute("SELECT COUNT(*) c FROM data_standards").fetchone()["c"]
    algorithms = CONN.execute("SELECT COUNT(*) c FROM algorithms").fetchone()["c"]
    rules = CONN.execute("SELECT COUNT(*) c FROM assets WHERE kind='rule'").fetchone()["c"]
    knowledge = CONN.execute("SELECT COUNT(*) c FROM assets WHERE kind='knowledge'").fetchone()["c"]
    mappings = CONN.execute("SELECT COUNT(*) c FROM assets WHERE kind='mapping'").fetchone()["c"]
    pending_rules = CONN.execute(
        "SELECT COUNT(*) c FROM algorithms WHERE related_rules IS NOT NULL AND related_rules != ''"
    ).fetchone()["c"]
    plates = [dict(r) for r in q("SELECT plate, COUNT(*) n FROM assets WHERE kind='rule' GROUP BY plate ORDER BY n DESC")]
    threads = [
        {"id": "obj-matter-split", "name": "化整为零规避招标", "hint": "限额、拆分、口径和不能认定围标"},
        {"id": "obj-matter-sz", "name": "先实施后补程序", "hint": "付款日期早于党委会"},
        {"id": "obj-matter-ent", "name": "节假日业务招待", "hint": "先分对象，再看审批先后"},
        {"id": "obj-matter-rect", "name": "整改回头看", "hint": "措施没有打在成因上"},
    ]
    tasks = [dict(r) for r in q("SELECT id,title,status,theme,summary FROM tasks ORDER BY id")]
    return {
        "standards": standards,
        "algorithms": algorithms,
        "rules": rules,
        "knowledge": knowledge,
        "mappings": mappings,
        "pending_rule_cites": pending_rules,
        "plates": plates,
        "threads": threads,
        "tasks": tasks,
        "orgs": CONN.execute("SELECT COUNT(*) c FROM organizations").fetchone()["c"],
    }


@app.get("/api/orgs")
def orgs(org_type: str = ""):
    if org_type:
        rows = q("SELECT * FROM organizations WHERE org_type=? ORDER BY sort_order", (org_type,))
    else:
        rows = q("SELECT * FROM organizations ORDER BY sort_order")
    return [dict(r) for r in rows]


@app.get("/api/orgs/{org_id}")
def org_detail(org_id: str):
    row = dict(one("SELECT * FROM organizations WHERE id=?", (org_id,)))
    owned = [asset_dict(r) for r in q("SELECT * FROM assets WHERE owner_org=? ORDER BY kind,name", (row["name"],))]
    applicable = []
    if row["org_type"] in ("subsidiary", "demo", "headquarters"):
        applicable = [
            asset_dict(r)
            for r in q(
                "SELECT * FROM assets WHERE kind='rule' AND applicable LIKE '%所属企业%' ORDER BY plate,name LIMIT 40"
            )
        ]
    objects = [dict(r) for r in q("SELECT id,obj_type,name,summary FROM objects WHERE org_id=?", (org_id,))]
    return {"org": row, "owned": owned, "applicable": applicable, "objects": objects, "pending": len(owned) == 0}


@app.get("/api/domains")
def domains():
    data = [dict(r) for r in q(
        "SELECT domain_code code, domain_name name, COUNT(*) n FROM data_standards GROUP BY domain_code, domain_name ORDER BY domain_code"
    )]
    algos = [dict(r) for r in q(
        "SELECT domain name, COUNT(*) n FROM algorithms GROUP BY domain ORDER BY domain"
    )]
    return {"data": data, "algorithms": algos}


@app.get("/api/standards")
def standards(qtext: str = "", domain: str = "", page: int = 1, size: int = 20):
    where = ["1=1"]
    params = []
    if domain:
        where.append("domain_code=?")
        params.append(domain)
    if qtext:
        where.append("(name LIKE ? OR code LIKE ? OR meaning LIKE ? OR category2 LIKE ?)")
        like = f"%{qtext}%"
        params.extend([like, like, like, like])
    sql_where = " AND ".join(where)
    total = CONN.execute(f"SELECT COUNT(*) c FROM data_standards WHERE {sql_where}", params).fetchone()["c"]
    offset = (page - 1) * size
    rows = q(
        f"SELECT code,domain_code,domain_name,category2,category3,name,form,sensitivity FROM data_standards WHERE {sql_where} ORDER BY code LIMIT ? OFFSET ?",
        (*params, size, offset),
    )
    return {"total": total, "page": page, "items": [dict(r) for r in rows]}


@app.get("/api/standards/{code}")
def standard_detail(code: str):
    row = dict(one("SELECT * FROM data_standards WHERE code=?", (code,)))
    row["relations"], row["relation_total"] = relations_for("standard", code)
    cited = []
    if row.get("related_rules"):
        cited = [c.strip() for c in re.split(r"[；;]", row["related_rules"]) if c.strip()]
    row["pending_rules"] = cited[:12]
    return row


@app.get("/api/algorithms")
def algorithms(qtext: str = "", domain: str = "", algo_type: str = "", page: int = 1, size: int = 20):
    where = ["1=1"]
    params = []
    if domain:
        where.append("domain=?")
        params.append(domain)
    if algo_type:
        where.append("algo_type=?")
        params.append(algo_type)
    if qtext:
        where.append("(name LIKE ? OR code LIKE ? OR scenario LIKE ?)")
        like = f"%{qtext}%"
        params.extend([like, like, like])
    sql_where = " AND ".join(where)
    total = CONN.execute(f"SELECT COUNT(*) c FROM algorithms WHERE {sql_where}", params).fetchone()["c"]
    offset = (page - 1) * size
    rows = q(
        f"SELECT code,domain,subcategory,algo_type,name FROM algorithms WHERE {sql_where} ORDER BY code LIMIT ? OFFSET ?",
        (*params, size, offset),
    )
    return {"total": total, "page": page, "items": [dict(r) for r in rows]}


@app.get("/api/algorithms/{code}")
def algorithm_detail(code: str):
    row = dict(one("SELECT * FROM algorithms WHERE code=?", (code,)))
    row["relations"], row["relation_total"] = relations_for("algorithm", code)
    trial = CONN.execute("SELECT * FROM algo_trials WHERE algo_code=?", (code,)).fetchone()
    if trial:
        item = dict(trial)
        item["rows"] = loads(item.pop("rows_json"), [])
        row["trial"] = item
    else:
        row["trial"] = None
    codes = [c.strip() for c in re.split(r"[；;]", row.get("related_rules") or "") if c.strip()]
    row["pending_rules"] = codes[:16]
    return row


@app.get("/api/assets")
def assets(kind: str = "", plate: str = "", qtext: str = "", shape: str = ""):
    where = ["1=1"]
    params = []
    if kind:
        where.append("kind=?")
        params.append(kind)
    if plate:
        where.append("plate=?")
        params.append(plate)
    if shape:
        where.append("shape=?")
        params.append(shape)
    if qtext:
        where.append("(name LIKE ? OR summary LIKE ? OR code LIKE ?)")
        like = f"%{qtext}%"
        params.extend([like, like, like])
    rows = q(
        f"SELECT id,kind,code,name,plate,shape,status,maturity,summary,owner_org,applicable,period,version FROM assets WHERE {' AND '.join(where)} ORDER BY plate,name",
        params,
    )
    return [dict(r) for r in rows]


@app.get("/api/assets/{asset_id}")
def asset_detail(asset_id: str):
    data = asset_dict(one("SELECT * FROM assets WHERE id=?", (asset_id,)))
    data["relations"], data["relation_total"] = relations_for(data["kind"], asset_id)
    versions = [dict(r) for r in q("SELECT id,version,note FROM versions WHERE asset_id=?", (asset_id,))]
    data["versions"] = versions
    if data["shape"] == "bundle":
        order = data["body"].get("order") or []
        linked = []
        for rid in order:
            row = CONN.execute("SELECT id,name,shape,summary,source_locator FROM assets WHERE id=?", (rid,)).fetchone()
            if row:
                linked.append(dict(row))
        data["bundle_items"] = linked
    return data


@app.get("/api/objects/{obj_id}")
def object_detail(obj_id: str):
    row = dict(one("SELECT * FROM objects WHERE id=?", (obj_id,)))
    row["body"] = loads(row.pop("body_json"), {})
    row["relations"], row["relation_total"] = relations_for("object", obj_id)
    return row


@app.get("/api/graph")
def graph(focus: str):
    seen = {focus}
    edges = []
    frontier = [focus]
    for _ in range(2):
        nxt = []
        for node in frontier:
            rows = q(
                "SELECT * FROM relations WHERE from_id=? OR to_id=?",
                (node, node),
            )
            for row in rows:
                if row["confirm_status"] == "材料写明" or row["confirm_status"] == "人员确认" or row["id"].startswith("rel-"):
                    pass
                edge = dict(row)
                if edge["id"] in {e["id"] for e in edges}:
                    continue
                if edge["from_kind"] == "algorithm" and edge["rel_type"] == "引用数据" and focus not in (edge["from_id"], edge["to_id"]):
                    continue
                edges.append(edge)
                if edge["rel_type"] == "引用数据":
                    continue
                for nid in (edge["from_id"], edge["to_id"]):
                    if nid not in seen:
                        seen.add(nid)
                        nxt.append(nid)
        frontier = nxt
    data_edges = [e for e in edges if e["rel_type"] == "引用数据"]
    other = [e for e in edges if e["rel_type"] != "引用数据"]
    if focus.startswith("A.") or focus.startswith("D."):
        kept_data = data_edges[:8]
        truncated = max(0, len(data_edges) - len(kept_data))
        edges = other + kept_data
    else:
        truncated = len(data_edges)
        edges = other
    seen = {focus}
    for edge in edges:
        seen.add(edge["from_id"])
        seen.add(edge["to_id"])
    nodes = []
    for nid in seen:
        kind = "object"
        for edge in edges:
            if edge["from_id"] == nid:
                kind = edge["from_kind"]
            elif edge["to_id"] == nid:
                kind = edge["to_kind"]
        if nid.startswith("D."):
            kind = "standard"
        elif nid.startswith("A."):
            kind = "algorithm"
        elif nid.startswith("rule"):
            kind = "rule"
        elif nid.startswith("know"):
            kind = "knowledge"
        elif nid.startswith("map"):
            kind = "mapping"
        nodes.append({"id": nid, "kind": kind, "name": label_of(kind, nid)})
    return {"focus": focus, "truncated": truncated, "nodes": nodes, "edges": [
        {
            "id": e["id"], "from": e["from_id"], "to": e["to_id"], "rel_type": e["rel_type"],
            "condition": e["condition"], "period": e["period"], "confirm_status": e["confirm_status"],
            "evidence": e["evidence"],
        } for e in edges
    ]}


@app.get("/api/tasks")
def tasks():
    return [dict(r) for r in q("SELECT * FROM tasks")]


@app.get("/api/tasks/{task_id}")
def task_detail(task_id: str):
    task = dict(one("SELECT * FROM tasks WHERE id=?", (task_id,)))
    materials = []
    for material in q("SELECT * FROM materials WHERE task_id=?", (task_id,)):
        item = dict(material)
        item["spans"] = [dict(s) for s in q("SELECT * FROM spans WHERE material_id=? ORDER BY para_index", (item["id"],))]
        materials.append(item)
    cands = []
    for candidate in q("SELECT * FROM candidates WHERE task_id=? ORDER BY id", (task_id,)):
        item = dict(candidate)
        item["body"] = loads(item.pop("body_json"), {})
        item["questions"] = loads(item.pop("questions_json"), [])
        item["issues"] = gate_candidate(candidate, [])
        cands.append(item)
    span_rows = []
    for material in materials:
        span_rows.extend(material["spans"])
    cand_rows = q("SELECT * FROM candidates WHERE task_id=?", (task_id,))
    left = coverage_issues(span_rows, cand_rows)
    return {"task": task, "materials": materials, "candidates": cands, "uncovered": left}


class CandidateAction(BaseModel):
    action: str
    reason: str = ""
    kind: str = ""
    title: str = ""


@app.post("/api/tasks/{task_id}/candidates/{cid}")
def candidate_action(task_id: str, cid: str, payload: CandidateAction):
    row = one("SELECT * FROM candidates WHERE id=? AND task_id=?", (cid, task_id))
    action = payload.action
    if action == "confirm":
        CONN.execute("UPDATE candidates SET status='已确认', origin=CASE WHEN origin='模型归纳' THEN '人员确认' ELSE origin END WHERE id=?", (cid,))
    elif action == "abandon":
        if not payload.reason.strip():
            raise HTTPException(400, "放弃需要写明原因")
        CONN.execute("UPDATE candidates SET kind='abandon', status='已放弃', abandon_reason=? WHERE id=?", (payload.reason.strip(), cid))
    elif action == "retype":
        if payload.kind not in ("rule", "knowledge", "fact"):
            raise HTTPException(400, "类型不正确")
        CONN.execute("UPDATE candidates SET kind=?, status='待人员确认' WHERE id=?", (payload.kind, cid))
    elif action == "split":
        body = loads(row["body_json"], {}) or {}
        new_id = "c-" + uuid.uuid4().hex[:8]
        new_body = dict(body)
        new_body["action"] = "缺关键文件时不得结算"
        new_body["modality"] = "不得"
        body["action"] = "将采购全过程材料一并归档"
        CONN.execute("UPDATE candidates SET body_json=?, summary=?, status='待人员确认' WHERE id=?", (dumps(body), "已按归档义务收窄，请确认。", cid))
        CONN.execute(
            """INSERT INTO candidates
            (id,task_id,material_id,kind,title,status,origin,confidence,span_ids,summary,body_json,abandon_reason,questions_json,asset_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (new_id, task_id, row["material_id"], row["kind"], "缺件不得结算", "待人员确认", "人员补充", "高", row["span_ids"], "从原项拆出的结算限制。", dumps(new_body), "", "[]", ""),
        )
    elif action == "waive":
        span_id = payload.reason.strip() or (row["span_ids"] or "")
        if not span_id:
            raise HTTPException(400, "没有指定段落")
        CONN.execute("UPDATE spans SET tag='waived' WHERE id=?", (span_id,))
    elif action == "answer":
        body = loads(row["body_json"], {}) or {}
        if not payload.reason.strip():
            raise HTTPException(400, "请写下补充")
        body["actor"] = body.get("actor") or "采购归口部门负责人"
        body["conditions"] = ["重大采购指达到公开招标限额的项目"]
        body["note"] = payload.reason.strip()
        CONN.execute(
            "UPDATE candidates SET body_json=?, status='已确认', origin='人员补充', summary=? WHERE id=?",
            (dumps(body), "人员补充了主体和重大采购的口径。", cid),
        )
    else:
        raise HTTPException(400, "不支持的操作")
    CONN.commit()
    return task_detail(task_id)


@app.post("/api/tasks/{task_id}/publish")
def publish(task_id: str):
    detail = task_detail(task_id)
    problems = []
    if detail["uncovered"]:
        problems.append("还有段落没有收录或放弃：" + "、".join(detail["uncovered"]))
    for candidate in detail["candidates"]:
        if candidate["kind"] in ("abandon", "fact"):
            if candidate["kind"] == "abandon" and not candidate.get("abandon_reason"):
                problems.append(candidate["title"] + "：放弃需要原因")
            continue
        for issue in candidate["issues"]:
            problems.append(f"{candidate['title']}：{issue}")
    if problems:
        raise HTTPException(400, "；".join(problems))
    published = []
    for candidate in detail["candidates"]:
        if candidate["kind"] in ("abandon", "fact"):
            continue
        if candidate.get("asset_id"):
            published.append(candidate["asset_id"])
            continue
        asset_id = "pub-" + candidate["id"]
        body = candidate["body"] or {}
        kind = candidate["kind"]
        CONN.execute(
            """INSERT OR REPLACE INTO assets
            (id,kind,code,name,plate,shape,status,maturity,summary,owner_org,maintainer,applicable,period,version,source_doc,source_locator,body_json)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                asset_id, kind, asset_id, candidate["title"], "本次梳理",
                "clause" if kind == "rule" else "distinction",
                "已发布", "可参考", candidate["summary"], "党委巡视办（党风廉政办）", "党风廉政办",
                detail["task"]["org_scope"], "自发布起", "梳理稿1",
                detail["materials"][0]["title"] if detail["materials"] else "",
                candidate["span_ids"], dumps(body),
            ),
        )
        CONN.execute("UPDATE candidates SET asset_id=?, status='已确认' WHERE id=?", (asset_id, candidate["id"]))
        published.append(asset_id)
    CONN.execute("UPDATE tasks SET status='已发布', updated_note='已通过质量关并发布' WHERE id=?", (task_id,))
    CONN.commit()
    return {"published": published}


class ApplyBody(BaseModel):
    unit: str
    date: str = ""
    matter: str


@app.post("/api/apply")
def apply_rules(payload: ApplyBody):
    like = f"%{payload.matter}%"
    rows = q(
        """SELECT id,name,plate,summary,applicable,period,source_locator,source_doc,body_json
        FROM assets WHERE kind='rule' AND (name LIKE ? OR summary LIKE ? OR plate LIKE ?) LIMIT 12""",
        (like, like, like),
    )
    items = []
    missing = []
    if not payload.date:
        missing.append("没有填写事项日期，无法确定适用版本")
    if not payload.unit:
        missing.append("没有填写单位")
    for row in rows:
        body = loads(row["body_json"], {})
        items.append({
            "id": row["id"], "name": row["name"], "plate": row["plate"], "summary": row["summary"],
            "applicable": row["applicable"], "period": row["period"],
            "source": f"{row['source_doc']} {row['source_locator']}",
            "exceptions": body.get("exceptions") or body.get("forbid") or [],
        })
    if payload.matter and "紧急" not in payload.matter:
        missing.append("如主张紧急处置，需要24小时内补报记录，当前没有提供")
    return {"unit": payload.unit, "items": items, "missing": missing}


class AskBody(BaseModel):
    question: str


@app.post("/api/ask")
def ask(payload: AskBody):
    question = payload.question.strip()
    if not question:
        raise HTTPException(400, "请写下问题")
    like = f"%{question[:12]}%"
    hits = []
    for row in q(
        "SELECT id,name,summary,source_doc,source_locator,kind FROM assets WHERE name LIKE ? OR summary LIKE ? LIMIT 6",
        (like, like),
    ):
        hits.append({"kind": row["kind"], "id": row["id"], "name": row["name"], "summary": row["summary"], "source": f"{row['source_doc']} {row['source_locator']}"})
    # keyword fallbacks for the four threads
    keys = [
        ("拆", "化整为零"), ("招标", "限额"), ("围标", "联系方式"), ("电话", "联系方式"),
        ("补程序", "先实施"), ("付款", "先实施"), ("招待", "节假日"), ("整改", "回头看"), ("销号", "整改"),
    ]
    for word, probe in keys:
        if word in question:
            for row in q(
                "SELECT id,name,summary,source_doc,source_locator,kind FROM assets WHERE name LIKE ? OR summary LIKE ? LIMIT 4",
                (f"%{probe}%", f"%{probe}%"),
            ):
                item = {"kind": row["kind"], "id": row["id"], "name": row["name"], "summary": row["summary"], "source": f"{row['source_doc']} {row['source_locator']}"}
                if item not in hits:
                    hits.append(item)
    if not hits:
        return {"answer": "已发布成果里没有直接对上的条目。可以换一个事项名称，或从四条主线进入。", "hits": [], "grounded": True}
    lines = [f"{h['name']}：{h['summary']}（{h['source']}）" for h in hits[:5]]
    answer = "根据已发布成果，可以这样看：\n" + "\n".join(lines)
    answer += "\n分析思路的命中不是已经查实的结论。待核依据不能当作现行要求。"
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if key:
        try:
            composed = compose_with_model(question, lines, key)
            if composed:
                answer = composed
        except Exception:
            pass
    return {"answer": answer, "hits": hits[:6], "grounded": True}


def compose_with_model(question, lines, key):
    base = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-flash")
    prompt = (
        "你是集团党风廉政办的资产使用助手。只根据给出的已发布成果回答，不要补充材料里没有的事实。"
        "明确这不是监督结论。用办里的话，分短段。\n问题：" + question + "\n成果：\n" + "\n".join(lines)
    )
    response = httpx.post(
        base.rstrip("/") + "/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


@app.post("/api/tasks")
def create_task(title: str = Form(...), theme: str = Form("监督要求"), org_scope: str = Form("集团总部")):
    task_id = "task-" + uuid.uuid4().hex[:8]
    CONN.execute(
        "INSERT INTO tasks (id,title,theme,status,expected,org_scope,summary,updated_note) VALUES (?,?,?,?,?,?,?,?)",
        (task_id, title, theme, "办理中", "从新材料中拆出资产", org_scope, "新发起的梳理。", ""),
    )
    CONN.commit()
    return {"id": task_id}


@app.post("/api/tasks/{task_id}/materials")
async def upload_material(task_id: str, file: UploadFile = File(...)):
    one("SELECT id FROM tasks WHERE id=?", (task_id,))
    raw = await file.read()
    text = raw.decode("utf-8", errors="ignore")
    if file.filename and file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        text = read_image(raw, file.content_type or "image/png")
    material_id = "mat-" + uuid.uuid4().hex[:8]
    CONN.execute(
        "INSERT INTO materials (id,task_id,title,doc_type,doc_no,body) VALUES (?,?,?,?,?,?)",
        (material_id, task_id, file.filename or "上传材料", "上传材料", "", text),
    )
    paras = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    for idx, para in enumerate(paras):
        tag = classify_para(para)
        CONN.execute(
            "INSERT INTO spans (id,material_id,para_index,text,tag) VALUES (?,?,?,?,?)",
            (f"{material_id}-{idx}", material_id, idx, para, tag),
        )
    CONN.commit()
    return task_detail(task_id)


def classify_para(para: str):
    if any(w in para for w in ("下周五", "办公会", "口头强调", "传达")):
        return "deployment"
    if any(w in para for w in ("应当", "不得", "可以", "严禁", "报批")):
        return "requirement"
    if any(w in para for w in ("核查", "不能", "误判", "弯路", "整改", "判断")):
        return "experience"
    if any(w in para for w in ("经过", "万元", "签署")):
        return "fact"
    return "untouched"


def read_image(raw, content_type):
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        return "（图片已接收。未配置识读密钥，请把图中文字另行贴入，或在本机配置密钥后重试。）"
    import base64
    b64 = base64.b64encode(raw).decode()
    base = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-flash")
    response = httpx.post(
        base.rstrip("/") + "/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "逐段抄写图中的中文，保留应当、不得等原词。读不清的地方标出。"},
                    {"type": "image_url", "image_url": {"url": f"data:{content_type};base64,{b64}"}},
                ],
            }],
        },
        timeout=90,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


@app.post("/api/tasks/{task_id}/extract")
def extract(task_id: str):
    materials = q("SELECT * FROM materials WHERE task_id=?", (task_id,))
    if not materials:
        raise HTTPException(400, "还没有材料")
    material = materials[-1]
    spans = q("SELECT * FROM spans WHERE material_id=? ORDER BY para_index", (material["id"],))
    existing = {row["span_ids"] for row in q("SELECT span_ids FROM candidates WHERE task_id=?", (task_id,))}
    made = 0
    for span in spans:
        if span["id"] in existing or span["tag"] in ("waived",):
            continue
        if span["tag"] == "deployment":
            CONN.execute(
                """INSERT INTO candidates
                (id,task_id,material_id,kind,title,status,origin,confidence,span_ids,summary,body_json,abandon_reason,questions_json,asset_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (f"c-{span['id']}", task_id, material["id"], "abandon", "部署性语句", "已放弃", "材料写明", "中", span["id"], span["text"][:80], "{}", "这是一次性部署，不是长期要求或可引用经验", "[]", ""),
            )
            made += 1
        elif span["tag"] == "requirement":
            vague = "相关负责人" in span["text"] or "严格把关" in span["text"]
            CONN.execute(
                """INSERT INTO candidates
                (id,task_id,material_id,kind,title,status,origin,confidence,span_ids,summary,body_json,abandon_reason,questions_json,asset_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    f"c-{span['id']}", task_id, material["id"], "rule", span["text"][:18],
                    "待判断" if vague else "待人员确认",
                    "模型归纳" if vague else "材料写明",
                    "低" if vague else "中",
                    span["id"], span["text"][:120],
                    dumps({"modality": "应当" if "应当" in span["text"] else "不得" if "不得" in span["text"] else "可以", "actor": "" if vague else "见原文", "action": span["text"][:40], "target": "", "conditions": [], "exceptions": [], "verify": []}),
                    "", "[]", "",
                ),
            )
            made += 1
        elif span["tag"] == "experience":
            CONN.execute(
                """INSERT INTO candidates
                (id,task_id,material_id,kind,title,status,origin,confidence,span_ids,summary,body_json,abandon_reason,questions_json,asset_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    f"c-{span['id']}", task_id, material["id"], "knowledge", span["text"][:18], "待人员确认", "材料写明", "中",
                    span["id"], span["text"][:140],
                    dumps({"situation": span["text"][:80], "cannot_conclude": "需人员确认边界", "boundary": ""}),
                    "", "[]", "",
                ),
            )
            made += 1
        elif span["tag"] == "fact":
            CONN.execute(
                """INSERT INTO candidates
                (id,task_id,material_id,kind,title,status,origin,confidence,span_ids,summary,body_json,abandon_reason,questions_json,asset_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (f"c-{span['id']}", task_id, material["id"], "fact", "事实经过", "已确认", "材料写明", "高", span["id"], "只作载体，不单独发布。", "{}", "", "[]", ""),
            )
            made += 1
    CONN.commit()
    return {"made": made, **task_detail(task_id)}


@app.get("/api/search")
def search(qtext: str):
    like = f"%{qtext}%"
    assets = [dict(r) for r in q("SELECT id,kind,name,summary,plate FROM assets WHERE name LIKE ? OR summary LIKE ? LIMIT 8", (like, like))]
    standards = [dict(r) for r in q("SELECT code,name,domain_name FROM data_standards WHERE name LIKE ? OR code LIKE ? LIMIT 5", (like, like))]
    algorithms = [dict(r) for r in q("SELECT code,name,domain FROM algorithms WHERE name LIKE ? OR code LIKE ? LIMIT 5", (like, like))]
    return {"assets": assets, "standards": standards, "algorithms": algorithms}
