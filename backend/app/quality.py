from .db import loads


def gate_candidate(candidate, spans):
    issues = []
    body = loads(candidate["body_json"], {}) or {}
    kind = candidate["kind"]
    if kind in ("abandon", "fact"):
        if kind == "abandon" and not (candidate["abandon_reason"] or "").strip():
            issues.append("放弃需要写明原因")
        return issues
    if candidate["status"] in ("待判断", "待人员确认", "待补充"):
        issues.append(f"当前是{candidate['status']}，还不能发布")
    if candidate["origin"] == "模型归纳" and candidate["status"] != "已确认":
        issues.append("模型归纳的内容要经人员确认")
    span_ids = [s for s in (candidate["span_ids"] or "").split(",") if s]
    if candidate["origin"] != "人员补充" and not span_ids:
        issues.append("没有对应到原文")
    if kind == "rule":
        if not body.get("actor") or not body.get("modality"):
            issues.append("要求缺少适用主体，或没有写明应当、不得、可以")
        action = body.get("action") or ""
        if "并且" in action or "并" in (candidate["title"] or "") and "归档" in action and "结算" in action:
            issues.append("一项里有两件可以分开的事，请先拆开")
    if kind == "knowledge":
        boundary = body.get("boundary") or body.get("cannot_conclude") or body.get("situation")
        if not boundary and candidate["status"] == "已确认":
            issues.append("经验缺少适用情境或不能沿用的情形")
        if "建议拆" in (candidate["summary"] or "") and candidate["status"] != "已确认":
            issues.append("模型建议拆开，尚未确认")
    return issues


def coverage_issues(spans, candidates):
    covered = set()
    for candidate in candidates:
        for sid in (candidate["span_ids"] or "").split(","):
            if sid:
                covered.add(sid)
    left = []
    for span in spans:
        if span["tag"] in ("requirement", "experience", "ambiguous", "untouched") and span["id"] not in covered:
            left.append(span["id"])
    return left
