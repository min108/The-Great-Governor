import json

from .corpus_bulk import bulk_knowledge, bulk_rules
from .corpus_extra import extra_knowledge
from .corpus_common import OBJECTS, organizations
from .corpus_deep import DEEP_KNOWLEDGE, DEEP_RELATIONS, DEEP_RULES, MORE_DEEP_RULES
from .corpus_tasks import INSPECT_PARAS, MAPPINGS, PURCHASE_PARAS, TRIALS, candidates, task_rows
from .db import dumps, init_db
from .importer import import_algorithms, import_standards, link_algorithm_data


def _expand_more(item):
    rid, code, name, plate, shape, owner, modality, actor, action, target, conditions, exceptions, verify, doc, article = item
    return {
        "id": rid, "kind": "rule", "code": code, "name": name, "plate": plate, "shape": shape,
        "status": "已发布", "maturity": "可指导", "summary": f"{actor}{modality}{action}。",
        "owner_org": owner, "maintainer": "党风廉政办", "applicable": "集团总部及所属企业",
        "period": "2024年1月1日起", "version": "演示2026-1", "source_doc": doc, "source_locator": article,
        "body": {
            "modality": modality, "actor": actor, "action": action, "target": target,
            "conditions": conditions, "exceptions": exceptions, "verify": verify,
            "article": article, "doc_no": doc,
        },
    }


def all_assets():
    rules = list(DEEP_RULES) + [_expand_more(x) for x in MORE_DEEP_RULES] + bulk_rules()
    knowledge = list(DEEP_KNOWLEDGE) + bulk_knowledge() + extra_knowledge()
    return rules + knowledge + MAPPINGS


def build(rebuild=False):
    conn = init_db()
    if rebuild:
        for table in (
            "organizations", "assets", "objects", "relations", "materials", "spans",
            "tasks", "candidates", "algo_trials", "versions", "data_standards", "algorithms",
        ):
            conn.execute(f"DELETE FROM {table}")
        conn.commit()
    if conn.execute("SELECT COUNT(*) c FROM data_standards").fetchone()["c"] == 0:
        n1 = import_standards(conn)
        n2 = import_algorithms(conn)
        n3 = link_algorithm_data(conn)
        conn.commit()
        print(f"imported standards={n1} algorithms={n2} data-links={n3}")
    if conn.execute("SELECT COUNT(*) c FROM assets").fetchone()["c"] > 0:
        return conn
    for row in organizations():
        conn.execute(
            "INSERT INTO organizations (id,name,short_name,org_type,role_note,plate,sort_order) VALUES (?,?,?,?,?,?,?)",
            row,
        )
    for oid, otype, name, summary, org_id, body in OBJECTS:
        conn.execute(
            "INSERT INTO objects (id,obj_type,name,summary,org_id,body_json) VALUES (?,?,?,?,?,?)",
            (oid, otype, name, summary, org_id, dumps(body)),
        )
    for asset in all_assets():
        conn.execute(
            """INSERT INTO assets
            (id,kind,code,name,plate,shape,status,maturity,summary,owner_org,maintainer,applicable,period,version,source_doc,source_locator,body_json)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                asset["id"], asset["kind"], asset.get("code"), asset["name"], asset.get("plate"),
                asset.get("shape"), asset.get("status"), asset.get("maturity"), asset.get("summary"),
                asset.get("owner_org"), asset.get("maintainer"), asset.get("applicable"),
                asset.get("period"), asset.get("version"), asset.get("source_doc"),
                asset.get("source_locator"), dumps(asset.get("body") or {}),
            ),
        )
    for rel in DEEP_RELATIONS:
        conn.execute(
            """INSERT INTO relations
            (id,from_kind,from_id,to_kind,to_id,rel_type,period,condition,confirm_status,evidence)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            rel,
        )
    conn.execute(
        "INSERT INTO versions (id,asset_id,version,note,snapshot_json) VALUES (?,?,?,?,?)",
        (
            "ver-limit-0", "rule-cg-limit", "演示2025-1",
            "上一版限额未写明含税。2026年文本改为按含税估算价。历史事项仍可查看这一版。",
            dumps({"goods": "400万元未注明税口径"}),
        ),
    )
    for trial in TRIALS:
        conn.execute(
            "INSERT INTO algo_trials (algo_code,title,summary,rows_json,missing,other_explanations) VALUES (?,?,?,?,?,?)",
            (trial["algo_code"], trial["title"], trial["summary"], dumps(trial["rows"]), trial["missing"], trial["other_explanations"]),
        )
    for row in task_rows():
        conn.execute(
            "INSERT INTO tasks (id,title,theme,status,expected,org_scope,summary,updated_note) VALUES (?,?,?,?,?,?,?,?)",
            row,
        )
    conn.execute(
        "INSERT INTO materials (id,task_id,title,doc_type,doc_no,body) VALUES (?,?,?,?,?,?)",
        ("mat-purchase", "task-purchase", "关于进一步规范采购组织的工作要求", "工作要求", "中信集团演示〔2026〕12号", "\n".join(p[2] for p in PURCHASE_PARAS)),
    )
    conn.execute(
        "INSERT INTO materials (id,task_id,title,doc_type,doc_no,body) VALUES (?,?,?,?,?,?)",
        ("mat-inspect", "task-inspect", "示例单位党委巡视情况报告（演示）", "巡视报告", "演示报告", "\n".join(p[2] for p in INSPECT_PARAS)),
    )
    for idx, (sid, tag, text) in enumerate(PURCHASE_PARAS):
        conn.execute(
            "INSERT INTO spans (id,material_id,para_index,text,tag) VALUES (?,?,?,?,?)",
            (sid, "mat-purchase", idx, text, tag),
        )
    for idx, (sid, tag, text) in enumerate(INSPECT_PARAS):
        conn.execute(
            "INSERT INTO spans (id,material_id,para_index,text,tag) VALUES (?,?,?,?,?)",
            (sid, "mat-inspect", idx, text, tag),
        )
    for cid, task_id, material_id, kind, title, status, origin, confidence, span_ids, summary, body, abandon in candidates():
        conn.execute(
            """INSERT INTO candidates
            (id,task_id,material_id,kind,title,status,origin,confidence,span_ids,summary,body_json,abandon_reason,questions_json,asset_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (cid, task_id, material_id, kind, title, status, origin, confidence, span_ids, summary, dumps(body), abandon, "[]", ""),
        )
    conn.commit()
    print("seed assets", conn.execute("SELECT COUNT(*) c FROM assets").fetchone()["c"])
    print("seed rules", conn.execute("SELECT COUNT(*) c FROM assets WHERE kind='rule'").fetchone()["c"])
    print("seed knowledge", conn.execute("SELECT COUNT(*) c FROM assets WHERE kind='knowledge'").fetchone()["c"])
    return conn


if __name__ == "__main__":
    build(rebuild=True)
