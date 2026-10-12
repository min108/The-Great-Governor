import { useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { api, hrefFor } from "./api";
import { KIND, Loading, statusPill, useLoad, type Row } from "./kit";

const SAMPLE = `中信集团演示〔2026〕40号  关于节假日公务活动的补充要求。

各所属企业应当在业务招待发生之前完成审批，审批单写明对象、事由和人均标准。

不得把法定节假日的内部值班餐列入业务招待费。

请各单位于下周五前在办公会上口头传达。

对重大事项，相关负责人应当严格把关。`;

const TAG: Record<string, string> = {
  requirement: "要求",
  experience: "经验",
  deployment: "部署",
  fact: "事实",
  ambiguous: "待判断",
  untouched: "尚未处理",
  waived: "不单列",
};

export function Tasks() {
  const { data, error, reload } = useLoad<Row[]>("/api/tasks");
  const [title, setTitle] = useState("节假日公务活动补充要求");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  async function createTask() {
    setBusy(true);
    setMessage("");
    try {
      const form = new FormData();
      form.append("title", title.trim() || "新的梳理");
      form.append("theme", "监督要求");
      form.append("org_scope", "集团总部及所属企业");
      const created = await api<{ id: string }>("/api/tasks", { method: "POST", body: form });
      window.location.href = `/tasks/${created.id}`;
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : "没有发起");
    } finally {
      setBusy(false);
    }
  }
  if (!data) return <Loading error={error} />;
  return (
    <>
      <div className="page-head">
        <div>
          <div className="kicker">正在办理</div>
          <h1>把一份材料拆成多项</h1>
          <p className="muted">工作要求和巡视报告先按段落拆开。模型归纳的内容要人确认。一项里两件事要拆开。段落没有着落，整单不能发布。</p>
        </div>
        <button className="btn secondary" onClick={reload}>刷新</button>
      </div>
      <div className="card" style={{ marginBottom: 12 }}>
        <h2>新开一份梳理</h2>
        <div className="row">
          <input style={{ flex: 1 }} value={title} onChange={(event) => setTitle(event.target.value)} />
          <button className="btn" disabled={busy} onClick={createTask}>发起</button>
        </div>
        {message ? <p className="issue">{message}</p> : null}
      </div>
      <div className="stack">
        {data.map((task) => (
          <Link key={task.id} to={`/tasks/${task.id}`} className="card">
            <div className="row">{statusPill(task.status)}<span className="pill plain">{task.theme}</span></div>
            <h3>{task.title}</h3>
            <p className="muted">{task.summary}</p>
            {task.updated_note ? <p className="mini">{task.updated_note}</p> : null}
          </Link>
        ))}
      </div>
    </>
  );
}

export function TaskPage() {
  const { id = "" } = useParams();
  const { data, error, setData, reload } = useLoad<Row>(id ? `/api/tasks/${id}` : null);
  const [picked, setPicked] = useState("");
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [draft, setDraft] = useState(SAMPLE);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function act(cid: string, action: string, extra: Record<string, string> = {}) {
    setBusy(true);
    setMessage("");
    try {
      const next = await api<Row>(`/api/tasks/${id}/candidates/${cid}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, ...extra }),
      });
      setData(next);
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : "操作没有完成");
    } finally {
      setBusy(false);
    }
  }

  async function publish() {
    setBusy(true);
    setMessage("");
    try {
      await api(`/api/tasks/${id}/publish`, { method: "POST" });
      reload();
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : "还不能发布");
    } finally {
      setBusy(false);
    }
  }

  async function ingest() {
    if (!draft.trim()) return;
    setBusy(true);
    setMessage("");
    try {
      const form = new FormData();
      form.append("file", new Blob([draft], { type: "text/plain" }), "梳理材料.txt");
      await api(`/api/tasks/${id}/materials`, { method: "POST", body: form });
      const next = await api<Row>(`/api/tasks/${id}/extract`, { method: "POST" });
      setData(next);
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : "没有拆开");
    } finally {
      setBusy(false);
    }
  }

  if (!data) return <Loading error={error} />;
  const task = data.task;
  const materials = data.materials || [];
  const candidates = data.candidates || [];
  const spans = materials.flatMap((material: Row) => material.spans || []);
  const uncovered = new Set<string>(data.uncovered || []);
  const anchor = candidates[0]?.id || "";

  return (
    <>
      <div className="page-head">
        <div>
          <div className="kicker">梳理 · {task.theme} · {task.org_scope}</div>
          <div className="row"><h1>{task.title}</h1>{statusPill(task.status)}</div>
          <p className="muted">{task.summary}</p>
          {task.updated_note ? <p className="mini">{task.updated_note}</p> : null}
        </div>
        <button className="btn" disabled={busy || task.status === "已发布"} onClick={publish}>提交发布</button>
      </div>
      {message ? <div className="error" style={{ marginBottom: 12 }}>{message}</div> : null}
      {!materials.length ? (
        <div className="card" style={{ marginBottom: 12 }}>
          <h2>放入材料</h2>
          <p className="muted">一段里如果有两件可以分开的事，先拆开再确认。部署性的话不入库。看不清主体的句子先追问。</p>
          <textarea rows={8} value={draft} onChange={(event) => setDraft(event.target.value)} />
          <div className="row" style={{ marginTop: 8 }}>
            <button className="btn secondary" onClick={() => setDraft(SAMPLE)}>放入一份补充要求</button>
            <button className="btn" disabled={busy} onClick={ingest}>读入并拆解</button>
          </div>
        </div>
      ) : null}
      <div className="split">
        <div className="card">
          <h2>原文</h2>
          <div className="legend">
            {Object.entries(TAG).map(([key, label]) => <span key={key} className={`pill plain`}>{label}</span>)}
          </div>
          {materials.map((material: Row) => (
            <div key={material.id}>
              <p className="mini">{material.title} {material.doc_no}</p>
              {(material.spans || []).map((span: Row) => {
                const on = picked && candidates.some((item: Row) => item.id === picked && String(item.span_ids || "").split(",").includes(span.id));
                return (
                  <div key={span.id} className={`para ${span.tag} ${on ? "on" : ""}`} onClick={() => {
                    const hit = candidates.find((item: Row) => String(item.span_ids || "").split(",").includes(span.id));
                    if (hit) setPicked(hit.id);
                  }}>
                    <div className="row"><span className="pill plain">{TAG[span.tag] || span.tag}</span>{uncovered.has(span.id) ? <span className="pill warn">尚未收录</span> : null}</div>
                    {span.text}
                  </div>
                );
              })}
            </div>
          ))}
          {data.uncovered?.length ? (
            <div className="block">
              <h3>这些段落还没有着落</h3>
              {spans.filter((span: Row) => uncovered.has(span.id)).map((span: Row) => (
                <div key={span.id} className="row" style={{ marginBottom: 8 }}>
                  <span className="mini" style={{ flex: 1 }}>{span.text}</span>
                  <button className="btn secondary" disabled={busy || !anchor} onClick={() => act(anchor, "waive", { reason: span.id })}>确认不单列</button>
                </div>
              ))}
            </div>
          ) : materials.length ? <p className="mini">需要处理的段落都有着落。</p> : null}
        </div>
        <div className="stack">
          {candidates.map((candidate: Row) => {
            const body = candidate.body || {};
            const canSplit = candidate.kind === "rule" && (String(body.action || "").includes("并且") || (String(body.action || "").includes("归档") && String(body.action || "").includes("结算")));
            const needsAnswer = candidate.kind === "rule" && !body.actor;
            return (
              <div key={candidate.id} id={`cand-${candidate.id}`} className="cand" style={{ outline: picked === candidate.id ? "2px solid var(--red)" : undefined }} onClick={() => setPicked(candidate.id)}>
                <div className="row">
                  {statusPill(candidate.status)}
                  <span className="pill plain">{KIND[candidate.kind] || candidate.kind}</span>
                  <span className={`pill ${candidate.origin === "模型归纳" ? "warn" : "plain"}`}>{candidate.origin}</span>
                </div>
                <h3>{candidate.title}</h3>
                <p>{candidate.summary}</p>
                {candidate.abandon_reason ? <p className="mini">不收录的原因：{candidate.abandon_reason}</p> : null}
                {(candidate.issues || []).map((issue: string) => <p key={issue} className="issue">{issue}</p>)}
                {candidate.kind !== "abandon" && candidate.kind !== "fact" && candidate.status !== "已确认" ? (
                  <div className="stack">
                    {needsAnswer ? (
                      <div className="row">
                        <input
                          placeholder="补上谁来办，以及重大指什么"
                          value={notes[candidate.id] ?? (candidate.id === "c-p9" ? "重大采购指达到公开招标限额的项目，由采购归口部门负责人把关" : "")}
                          onChange={(event) => setNotes({ ...notes, [candidate.id]: event.target.value })}
                        />
                        <button className="btn" disabled={busy} onClick={() => act(candidate.id, "answer", { reason: notes[candidate.id] ?? (candidate.id === "c-p9" ? "重大采购指达到公开招标限额的项目，由采购归口部门负责人把关" : "") })}>按补充口径确认</button>
                      </div>
                    ) : null}
                    <div className="row">
                      {!needsAnswer ? <button className="btn" disabled={busy} onClick={() => act(candidate.id, "confirm")}>确认</button> : null}
                      {canSplit ? <button className="btn secondary" disabled={busy} onClick={() => act(candidate.id, "split")}>拆开</button> : null}
                      {candidate.kind === "rule" ? <button className="btn ghost" disabled={busy} onClick={() => act(candidate.id, "retype", { kind: "knowledge" })}>改作经验</button> : null}
                      {candidate.kind === "knowledge" ? <button className="btn ghost" disabled={busy} onClick={() => act(candidate.id, "retype", { kind: "rule" })}>改作要求</button> : null}
                    </div>
                    <div className="row">
                      <input placeholder="不收录的原因" value={notes[`ab-${candidate.id}`] || ""} onChange={(event) => setNotes({ ...notes, [`ab-${candidate.id}`]: event.target.value })} />
                      <button className="btn secondary" disabled={busy} onClick={() => act(candidate.id, "abandon", { reason: notes[`ab-${candidate.id}`] || "" })}>放弃</button>
                    </div>
                  </div>
                ) : null}
                {candidate.asset_id ? <p><Link className="jump" to={`/assets/${candidate.asset_id}`}>已发布为资产</Link></p> : null}
              </div>
            );
          })}
          {!candidates.length && materials.length ? <div className="card"><button className="btn" disabled={busy} onClick={async () => { const next = await api<Row>(`/api/tasks/${id}/extract`, { method: "POST" }); setData(next); }}>按段落拆解</button></div> : null}
        </div>
      </div>
    </>
  );
}

export function Apply() {
  const [unit, setUnit] = useState("示例制造企业");
  const [date, setDate] = useState("2026-03-18");
  const [matter, setMatter] = useState("化整为零");
  const [result, setResult] = useState<Row | null>(null);
  const [error, setError] = useState("");
  async function run() {
    setError("");
    try {
      setResult(await api("/api/apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ unit, date, matter }),
      }));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "没有试算");
    }
  }
  return (
    <>
      <div className="page-head">
        <div>
          <div className="kicker">适用试算</div>
          <h1>这件事可能要对照哪些要求</h1>
          <p className="muted">按单位、日期和事项，列出已发布要求。缺日期或缺例外材料时单独标出。这不是监督结论。</p>
        </div>
      </div>
      <div className="card" style={{ marginBottom: 12 }}>
        <div className="filters">
          <select value={unit} onChange={(event) => setUnit(event.target.value)}>
            {["示例制造企业", "示例金融子公司", "示例工程企业", "示例综合单位", "集团总部"].map((item) => <option key={item}>{item}</option>)}
          </select>
          <input type="date" value={date} onChange={(event) => setDate(event.target.value)} />
          <input value={matter} onChange={(event) => setMatter(event.target.value)} placeholder="事项，例如拆分、招待、补程序" />
          <button className="btn" onClick={run}>试算</button>
        </div>
      </div>
      {error ? <div className="error">{error}</div> : null}
      {result ? (
        <div className="grid-2">
          <div className="card">
            <h2>可能适用</h2>
            {(result.items || []).map((item: Row) => (
              <Link key={item.id} to={`/assets/${item.id}`} className="rel">
                <b>{item.name}</b>
                <p>{item.summary}</p>
                <p>{item.applicable} · {item.period} · {item.source}</p>
              </Link>
            ))}
            {!result.items?.length ? <p className="muted">没有直接对上的已发布要求。</p> : null}
          </div>
          <div className="card">
            <h2>还不能闭合的地方</h2>
            {(result.missing || []).map((item: string) => <p key={item} className="issue">{item}</p>)}
            <p className="mini">列出的是可能适用的要求，不是对{result.unit}具体事项的结论。</p>
          </div>
        </div>
      ) : null}
    </>
  );
}

export function Ask() {
  const [question, setQuestion] = useState("节假日有餐饮发票，能不能直接认定违规招待？");
  const [result, setResult] = useState<Row | null>(null);
  const [error, setError] = useState("");
  async function run() {
    setError("");
    try {
      setResult(await api("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      }));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "没有答上");
    }
  }
  return (
    <>
      <div className="page-head">
        <div>
          <div className="kicker">问一问</div>
          <h1>只根据已发布成果回答</h1>
          <p className="muted">答不上来就说没有对上。分析思路的命中不是已经查实的结论。待核依据不能当成现行要求。</p>
        </div>
      </div>
      <div className="card" style={{ marginBottom: 12 }}>
        <textarea rows={4} value={question} onChange={(event) => setQuestion(event.target.value)} />
        <div className="row" style={{ marginTop: 8 }}>
          <button className="btn" onClick={run}>提问</button>
          {["化整为零怎么核查", "先划款后补党委会怎么看", "整改销号后又出现怎么办"].map((item) => (
            <button key={item} className="btn secondary" onClick={() => setQuestion(item)}>{item}</button>
          ))}
        </div>
      </div>
      {error ? <div className="error">{error}</div> : null}
      {result ? (
        <div className="grid-2">
          <div className="card"><h2>回答</h2><div className="answer">{result.answer}</div></div>
          <div className="card">
            <h2>依据</h2>
            {(result.hits || []).map((hit: Row) => (
              <Link key={hit.id} to={hrefFor(hit.kind, hit.id)} className="rel">
                <b>{hit.name}</b>
                <p>{hit.summary}</p>
                <p>{hit.source}</p>
              </Link>
            ))}
          </div>
        </div>
      ) : null}
    </>
  );
}

export function SearchPage() {
  const [params] = useSearchParams();
  const qtext = params.get("q") || "";
  const { data, error } = useLoad<Row>(qtext ? `/api/search?qtext=${encodeURIComponent(qtext)}` : null);
  return (
    <>
      <div className="page-head"><div><div className="kicker">检索</div><h1>{qtext || "请输入"}</h1></div></div>
      {!qtext ? <p className="muted">从页眉检索要求、经验、标准或思路。</p> : !data ? <Loading error={error} /> : (
        <div className="grid-2">
          <div className="card">
            <h2>要求、经验与对照</h2>
            {(data.assets || []).map((item: Row) => (
              <Link key={item.id} to={`/assets/${item.id}`} className="rel"><b>{KIND[item.kind]} · {item.name}</b><p>{item.summary}</p></Link>
            ))}
          </div>
          <div className="stack">
            <div className="card">
              <h2>数据标准</h2>
              {(data.standards || []).map((item: Row) => <Link key={item.code} to={`/standards/${item.code}`} className="rel"><b>{item.code} {item.name}</b><p>{item.domain_name}</p></Link>)}
            </div>
            <div className="card">
              <h2>分析思路</h2>
              {(data.algorithms || []).map((item: Row) => <Link key={item.code} to={`/algorithms/${item.code}`} className="rel"><b>{item.code} {item.name}</b><p>{item.domain}</p></Link>)}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export function GraphPage() {
  const { focus = "" } = useParams();
  const { data, error } = useLoad<Row>(focus ? `/api/graph?focus=${encodeURIComponent(focus)}` : null);
  if (!data) return <Loading error={error} />;
  const names = new Map<string, string>((data.nodes || []).map((node: Row) => [node.id, node.name]));
  const groups = ["rule", "knowledge", "algorithm", "mapping", "standard", "object"];
  return (
    <>
      <div className="page-head">
        <div>
          <div className="kicker">关联</div>
          <h1>{names.get(focus) || focus}</h1>
          <p className="muted">只展开和这件事直接有关的要求、经验和对照。方向、期间、条件和确认状态写在每一条上。</p>
        </div>
      </div>
      {data.truncated ? <p className="mini">另有 {data.truncated} 条数据引用没有展开。</p> : null}
      <div className="grid-2">
        <div className="card">
          <h2>相关内容</h2>
          {groups.map((kind) => {
            const nodes = (data.nodes || []).filter((node: Row) => node.kind === kind && node.id !== focus);
            if (!nodes.length) return null;
            return (
              <div key={kind}>
                <h3>{KIND[kind]}</h3>
                {nodes.map((node: Row) => (
                  <Link key={node.id} to={hrefFor(node.kind, node.id)} className="graph-node" style={{ display: "block", marginBottom: 8 }}>{node.name}</Link>
                ))}
              </div>
            );
          })}
        </div>
        <div className="card">
          <h2>关系怎样成立</h2>
          {(data.edges || []).map((edge: Row) => (
            <div key={edge.id} className="edge">
              <b>{names.get(edge.from) || edge.from}</b>
              <span> — {edge.rel_type} → </span>
              <b>{names.get(edge.to) || edge.to}</b>
              <div>{[edge.period, edge.condition, edge.confirm_status, edge.evidence].filter(Boolean).join(" · ")}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
