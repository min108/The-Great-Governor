import { useMemo, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { KIND, Loading, Relations, SHAPE, linkify, statusPill, useLoad, type Row } from "./kit";
import { ShapeBody } from "./shapes";

export function AssetList({ kind, title, lead }: { kind: string; title: string; lead: string }) {
  const [params] = useSearchParams();
  const initialPlate = params.get("plate") || "";
  const [plate, setPlate] = useState(initialPlate);
  const [qtext, setQtext] = useState("");
  const [shape, setShape] = useState("");
  const { data, error } = useLoad<Row[]>(`/api/assets?kind=${kind}`);
  const plates = useMemo(() => Array.from(new Set((data || []).map((item) => item.plate).filter(Boolean))), [data]);
  const shapes = useMemo(() => Array.from(new Set((data || []).map((item) => item.shape).filter(Boolean))), [data]);
  if (!data) return <Loading error={error} />;
  const items = data.filter((item) => {
    if (plate && item.plate !== plate) return false;
    if (shape && item.shape !== shape) return false;
    if (qtext && !`${item.name}${item.summary}${item.code}`.includes(qtext.trim())) return false;
    return true;
  });
  return (
    <>
      <div className="page-head">
        <div>
          <div className="kicker">{KIND[kind]}</div>
          <h1>{title}</h1>
          <p className="muted">{lead}</p>
        </div>
        <b>{items.length} 项</b>
      </div>
      <div className="filters">
        <input value={qtext} placeholder="按名称或要点" onChange={(event) => setQtext(event.target.value)} />
        <select value={plate} onChange={(event) => setPlate(event.target.value)}>
          <option value="">全部板块</option>
          {plates.map((item) => <option key={item}>{item}</option>)}
        </select>
        <select value={shape} onChange={(event) => setShape(event.target.value)}>
          <option value="">全部体例</option>
          {shapes.map((item) => <option key={item} value={item}>{SHAPE[item] || item}</option>)}
        </select>
      </div>
      <div className="card">
        <table>
          <thead>
            <tr><th>名称</th><th>板块</th><th>体例</th><th>状态</th><th>适用</th></tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td><Link className="jump" to={`/assets/${item.id}`}>{item.name}</Link><div className="mini">{item.summary}</div></td>
                <td>{item.plate}</td>
                <td>{SHAPE[item.shape] || item.shape}</td>
                <td>{statusPill(item.status)} <span className="mini">{item.maturity}</span></td>
                <td>{item.applicable}<div className="mini">{item.period}</div></td>
              </tr>
            ))}
          </tbody>
        </table>
        {!items.length ? <p className="muted">没有对上的条目。</p> : null}
      </div>
    </>
  );
}

export function AssetPage() {
  const { id = "" } = useParams();
  const { data, error } = useLoad<Row>(id ? `/api/assets/${id}` : null);
  if (!data) return <Loading error={error} />;
  return (
    <article className="card" style={{ padding: 0 }}>
      <header className="dossier-head">
        <div className="kicker">{KIND[data.kind]} · {SHAPE[data.shape] || data.shape} · {data.code}</div>
        <div className="row">
          <h1>{data.name}</h1>
          {statusPill(data.status)}
          <span className="pill plain">{data.maturity}</span>
        </div>
        <p className="muted">{data.summary}</p>
      </header>
      <div className="dossier-body">
        <div>
          <ShapeBody asset={data} />
          {Array.isArray(data.versions) && data.versions.length ? (
            <div className="block">
              <h3>以往版本</h3>
              {data.versions.map((version: Row) => <p key={version.id}>{version.version}：{version.note}</p>)}
            </div>
          ) : null}
        </div>
        <aside className="stack">
          <div className="block">
            <h3>归属与适用</h3>
            <div className="kv">
              <i>板块</i><span>{data.plate}</span>
              <i>归口</i><span>{data.owner_org}</span>
              <i>维护</i><span>{data.maintainer}</span>
              <i>适用</i><span>{data.applicable}</span>
              <i>期间</i><span>{data.period}</span>
              <i>版本</i><span>{data.version}</span>
              <i>依据</i><span>{data.source_doc} {data.source_locator}</span>
            </div>
          </div>
          <div className="block">
            <div className="row" style={{ justifyContent: "space-between" }}>
              <h3>关联</h3>
              <Link className="jump" to={`/graph/${data.id}`}>展开周围</Link>
            </div>
            <Relations items={data.relations} total={data.relation_total} />
          </div>
        </aside>
      </div>
    </article>
  );
}

export function Standards() {
  const [domain, setDomain] = useState("");
  const [draft, setDraft] = useState("");
  const [qtext, setQtext] = useState("");
  const [page, setPage] = useState(1);
  const domains = useLoad<Row>("/api/domains");
  const list = useLoad<Row>(`/api/standards?domain=${encodeURIComponent(domain)}&qtext=${encodeURIComponent(qtext)}&page=${page}&size=15`);
  return (
    <>
      <div className="page-head">
        <div>
          <div className="kicker">数据标准</div>
          <h1>业务里要调到的数据项</h1>
          <p className="muted">标准项来自已整理清单。各单位台账的字段名和口径，要先做对照，再拿来和限额、日期比较。</p>
        </div>
        <Link className="btn secondary" to="/mappings">看口径对照</Link>
      </div>
      <div className="filters">
        <input value={draft} placeholder="名称、编码或含义" onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") { setQtext(draft); setPage(1); } }} />
        <select value={domain} onChange={(event) => { setDomain(event.target.value); setPage(1); }}>
          <option value="">全部领域</option>
          {(domains.data?.data || []).map((item: Row) => <option key={item.code} value={item.code}>{item.code} {item.name}（{item.n}）</option>)}
        </select>
        <button className="btn" onClick={() => { setQtext(draft); setPage(1); }}>检索</button>
      </div>
      {!list.data ? <Loading error={list.error} /> : (
        <div className="card">
          <table>
            <thead><tr><th>编码</th><th>名称</th><th>分类</th><th>形态</th><th>敏感</th></tr></thead>
            <tbody>
              {list.data.items.map((item: Row) => (
                <tr key={item.code}>
                  <td><Link className="jump" to={`/standards/${item.code}`}>{item.code}</Link></td>
                  <td>{item.name}<div className="mini">{item.domain_name}</div></td>
                  <td>{item.category2}<div className="mini">{item.category3}</div></td>
                  <td>{item.form}</td>
                  <td>{item.sensitivity}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <Pager page={list.data.page} total={list.data.total} size={15} onPage={setPage} />
        </div>
      )}
    </>
  );
}

export function StandardPage() {
  const { code = "" } = useParams();
  const { data, error } = useLoad<Row>(code ? `/api/standards/${encodeURIComponent(code)}` : null);
  if (!data) return <Loading error={error} />;
  const pending = String(data.related_rules || "").split(/[；;]/).map((item) => item.trim()).filter(Boolean);
  return (
    <article className="card" style={{ padding: 0 }}>
      <header className="dossier-head">
        <div className="kicker">数据标准 · {data.domain_code} {data.domain_name}</div>
        <h1>{data.name}</h1>
        <p className="muted">{data.code} · {data.category2} / {data.category3}</p>
      </header>
      <div className="dossier-body">
        <div>
          <div className="block">
            <div className="kv">
              <i>业务含义</i><span>{data.meaning || "—"}</span>
              <i>数据形态</i><span>{data.form || "—"}</span>
              <i>资产归属</i><span>{data.asset_class || "—"}</span>
              <i>参考形式</i><span>{data.reference_form || "—"}</span>
              <i>值域约束</i><span>{data.constraints || "—"}</span>
              <i>标准依据</i><span>{data.basis || "—"}</span>
              <i>正例</i><span>{data.positive_example || "—"}</span>
              <i>反例</i><span>{data.negative_example || "—"}</span>
              <i>敏感级别</i><span>{data.sensitivity || "—"}</span>
            </div>
          </div>
          {pending.length ? (
            <div className="block">
              <h3>清单中的规则编号</h3>
              <p className="mini">这些编号还没有对应的正文，只作待核依据，不能当作现行要求。</p>
              <div className="row">{pending.slice(0, 12).map((item) => <span key={item} className="pill warn">{item}</span>)}</div>
            </div>
          ) : null}
        </div>
        <aside className="block">
          <div className="row" style={{ justifyContent: "space-between" }}>
            <h3>谁在用这项</h3>
            <Link className="jump" to={`/graph/${data.code}`}>展开周围</Link>
          </div>
          <Relations items={data.relations} total={data.relation_total} />
        </aside>
      </div>
    </article>
  );
}

export function Algorithms() {
  const [domain, setDomain] = useState("");
  const [algoType, setAlgoType] = useState("");
  const [draft, setDraft] = useState("");
  const [qtext, setQtext] = useState("");
  const [page, setPage] = useState(1);
  const domains = useLoad<Row>("/api/domains");
  const list = useLoad<Row>(`/api/algorithms?domain=${encodeURIComponent(domain)}&algo_type=${encodeURIComponent(algoType)}&qtext=${encodeURIComponent(qtext)}&page=${page}&size=15`);
  return (
    <>
      <div className="page-head">
        <div>
          <div className="kicker">分析思路</div>
          <h1>怎样从数据里看出疑点</h1>
          <p className="muted">思路来自已整理清单。命中只说明要去核对，不是已经查实的结论。两条样本做了试运行，其余不连真实库。</p>
        </div>
      </div>
      <div className="filters">
        <input value={draft} placeholder="名称或编码" onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") { setQtext(draft); setPage(1); } }} />
        <select value={domain} onChange={(event) => { setDomain(event.target.value); setPage(1); }}>
          <option value="">全部领域</option>
          {(domains.data?.algorithms || []).map((item: Row) => <option key={item.name}>{item.name}</option>)}
        </select>
        <select value={algoType} onChange={(event) => { setAlgoType(event.target.value); setPage(1); }}>
          <option value="">全部类型</option>
          <option>穿透识别</option>
          <option>预警拦截</option>
          <option>画像研判</option>
        </select>
        <button className="btn" onClick={() => { setQtext(draft); setPage(1); }}>检索</button>
      </div>
      {!list.data ? <Loading error={list.error} /> : (
        <div className="card">
          <div className="row" style={{ marginBottom: 8 }}>
            <Link className="pill" to="/algorithms/A.04.01.001">样本：化整为零</Link>
            <Link className="pill" to="/algorithms/A.06.01.004">样本：节假日餐饮</Link>
          </div>
          <table>
            <thead><tr><th>编码</th><th>名称</th><th>领域</th><th>类型</th></tr></thead>
            <tbody>
              {list.data.items.map((item: Row) => (
                <tr key={item.code}>
                  <td><Link className="jump" to={`/algorithms/${item.code}`}>{item.code}</Link></td>
                  <td>{item.name}</td>
                  <td>{item.domain}<div className="mini">{item.subcategory}</div></td>
                  <td>{item.algo_type}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <Pager page={list.data.page} total={list.data.total} size={15} onPage={setPage} />
        </div>
      )}
    </>
  );
}

export function AlgorithmPage() {
  const { code = "" } = useParams();
  const { data, error } = useLoad<Row>(code ? `/api/algorithms/${encodeURIComponent(code)}` : null);
  if (!data) return <Loading error={error} />;
  const pending = String(data.related_rules || "").split(/[；;]/).map((item) => item.trim()).filter(Boolean);
  return (
    <article className="card" style={{ padding: 0 }}>
      <header className="dossier-head">
        <div className="kicker">分析思路 · {data.code} · {data.algo_type}</div>
        <h1>{data.name}</h1>
        <p className="muted">{data.domain} · {data.subcategory}</p>
      </header>
      <div className="dossier-body">
        <div>
          <div className="block"><h3>用在什么情形</h3><p>{data.scenario || "—"}</p></div>
          <div className="block"><h3>需要哪些数据</h3><p>{linkify(data.data_needs)}</p></div>
          <div className="block"><h3>怎么分析</h3><p>{data.method || "—"}</p></div>
          <div className="block"><h3>怎样才算命中</h3><p>{data.judgment || "—"}</p></div>
          <div className="block"><h3>输出给办理人员看什么</h3><p>{data.output_template || "—"}</p></div>
          {data.trial ? (
            <div className="block">
              <h3>样本试运行 · {data.trial.title}</h3>
              <p>{data.trial.summary}</p>
              <table>
                <thead><tr><th>样本</th><th>金额或情况</th><th>归口</th><th>掌握</th></tr></thead>
                <tbody>
                  {(data.trial.rows || []).map((row: Row) => (
                    <tr key={row.item}><td>{row.item}</td><td>{row.amount}</td><td>{row.dept}</td><td>{row.level}</td></tr>
                  ))}
                </tbody>
              </table>
              <p className="muted">还缺的材料：{data.trial.missing}</p>
              <p>其他解释：{data.trial.other_explanations}</p>
              <p className="mini">这是示例单位的样本，不是对真实子公司的查实结论。</p>
            </div>
          ) : <div className="block"><h3>试运行</h3><p className="muted">这条思路尚未用样本试跑，不能当成已经核对过的结果。</p></div>}
          {pending.length ? (
            <div className="block">
              <h3>清单引用的规则编号</h3>
              <p className="mini">正文未入库，标为待核依据。</p>
              <div className="row">{pending.slice(0, 16).map((item) => <span key={item} className="pill warn">{item}</span>)}</div>
            </div>
          ) : null}
        </div>
        <aside className="block">
          <div className="row" style={{ justifyContent: "space-between" }}>
            <h3>关联</h3>
            <Link className="jump" to={`/graph/${data.code}`}>展开周围</Link>
          </div>
          <Relations items={data.relations} total={data.relation_total} />
        </aside>
      </div>
    </article>
  );
}

export function Orgs() {
  const { data, error } = useLoad<Row[]>("/api/orgs");
  if (!data) return <Loading error={error} />;
  const groups = [
    { title: "派驻与总部", types: ["dispatched", "headquarters"] },
    { title: "演示单位", types: ["demo"] },
    { title: "一级子公司名录", types: ["subsidiary"] },
  ];
  return (
    <>
      <div className="page-head">
        <div>
          <div className="kicker">组织与适用</div>
          <h1>谁归口，谁适用</h1>
          <p className="muted">名录用于建设范围、资产归属和适用范围。不据此推断股权，也不把真实企业写成案例主体。案例只用四家示例单位和化名。</p>
        </div>
      </div>
      {groups.map((group) => (
        <div className="card" key={group.title} style={{ marginBottom: 12 }}>
          <h2>{group.title}</h2>
          <div className="grid-3">
            {data.filter((org) => group.types.includes(org.org_type)).map((org) => (
              <Link key={org.id} to={`/orgs/${org.id}`} className="thread">
                <b>{org.short_name || org.name}</b>
                <span className="muted">{org.role_note}</span>
              </Link>
            ))}
          </div>
        </div>
      ))}
    </>
  );
}

export function OrgPage() {
  const { id = "" } = useParams();
  const { data, error } = useLoad<Row>(id ? `/api/orgs/${id}` : null);
  if (!data) return <Loading error={error} />;
  const org = data.org;
  return (
    <>
      <div className="page-head">
        <div>
          <div className="kicker">{org.org_type === "demo" ? "演示单位" : org.org_type === "subsidiary" ? "一级子公司" : "总部机构"}</div>
          <h1>{org.name}</h1>
          <p className="muted">{org.role_note} {org.plate ? `· ${org.plate}` : ""}</p>
        </div>
      </div>
      {data.pending ? <div className="error">归口到本单位名下的已发布资产还没有单列，适用关系待核。这里不补写虚构的问题或案件。</div> : null}
      <div className="grid-2">
        <div className="card">
          <h2>归口资产</h2>
          <AssetLinks items={data.owned} empty="尚未单列归口资产。" />
        </div>
        <div className="card">
          <h2>本单位业务对象</h2>
          {(data.objects || []).length ? data.objects.map((item: Row) => (
            <Link key={item.id} to={`/objects/${item.id}`} className="rel"><b>{item.name}</b><p>{item.summary}</p></Link>
          )) : <p className="muted">没有挂在本单位下的演示对象。</p>}
          {data.applicable?.length ? (
            <>
              <h3 style={{ marginTop: 16 }}>写明适用于所属企业的要求（节选）</h3>
              <AssetLinks items={data.applicable} empty="" />
            </>
          ) : null}
        </div>
      </div>
    </>
  );
}

function AssetLinks({ items, empty }: { items: Row[]; empty: string }) {
  if (!items?.length) return <p className="muted">{empty}</p>;
  return (
    <div>
      {items.slice(0, 24).map((item) => (
        <Link key={item.id} to={`/assets/${item.id}`} className="rel">
          <div className="row">{statusPill(item.status)}<b>{item.name}</b></div>
          <p>{item.summary}</p>
        </Link>
      ))}
    </div>
  );
}

const OBJECT_LABEL: Record<string, string> = {
  duty: "职责",
  separation: "分开承担",
  credit_code: "演示代码",
  contact: "联系电话",
  note: "说明",
  year: "年度",
  lots: "分项",
  total: "合计（元）",
  amount_incl_tax: "含税金额（元）",
  amount_excl_tax: "不含税金额（元）",
  signed: "签署日期",
  decision_date: "会议日期",
  pay_date: "划款日期",
  dates: "涉及日期",
  round: "轮次",
  role: "身份",
};

const OBJECT_TYPE: Record<string, string> = {
  matter: "事项", post: "岗位", supplier: "相对方", project: "项目", contract: "合同", person: "人员",
};

export function ObjectPage() {
  const { id = "" } = useParams();
  const { data, error } = useLoad<Row>(id ? `/api/objects/${id}` : null);
  if (!data) return <Loading error={error} />;
  const body = data.body || {};
  const chain = Array.isArray(body.chain) ? body.chain : [];
  return (
    <article className="card" style={{ padding: 0 }}>
      <header className="dossier-head">
        <div className="kicker">{OBJECT_TYPE[data.obj_type] || "业务对象"}</div>
        <h1>{data.name}</h1>
        <p className="muted">{data.summary}</p>
        {chain.length ? (
          <div className="chain">
            {chain.map((item: string, index: number) => (
              <span key={item} className="row"><span className="pill">{item}</span>{index < chain.length - 1 ? <i>→</i> : null}</span>
            ))}
          </div>
        ) : null}
      </header>
      <div className="dossier-body">
        <div className="block">
          <h3>材料里写明的情况</h3>
          <div className="kv">
            {Object.entries(body).filter(([key]) => key !== "chain" && key !== "thread").map(([key, value]) => (
              <span key={key} style={{ display: "contents" }}>
                <i>{OBJECT_LABEL[key] || key}</i>
                <span>{Array.isArray(value) ? value.join("、") : String(value)}</span>
              </span>
            ))}
          </div>
          {data.obj_type === "person" ? <p className="mini">化名只出现在演示材料里，不对应真实人员。</p> : null}
        </div>
        <aside className="block">
          <div className="row" style={{ justifyContent: "space-between" }}>
            <h3>顺着看</h3>
            <Link className="jump" to={`/graph/${data.id}`}>展开周围</Link>
          </div>
          <Relations items={data.relations} total={data.relation_total} />
        </aside>
      </div>
    </article>
  );
}

function Pager({ page, total, size, onPage }: { page: number; total: number; size: number; onPage: (page: number) => void }) {
  const pages = Math.max(1, Math.ceil(total / size));
  return (
    <div className="row" style={{ marginTop: 12 }}>
      <button className="btn secondary" disabled={page <= 1} onClick={() => onPage(page - 1)}>上一页</button>
      <span className="mini">第 {page} / {pages} 页，共 {total} 条</span>
      <button className="btn secondary" disabled={page >= pages} onClick={() => onPage(page + 1)}>下一页</button>
    </div>
  );
}
