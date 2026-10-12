import { Link } from "react-router-dom";
import { useContext } from "react";
import { Loading, ViewContext, statusPill, useLoad, type Row } from "./kit";

export function Home() {
  const view = useContext(ViewContext);
  const { data, error } = useLoad<Row>("/api/overview");
  if (!data) return <Loading error={error} />;
  return (
    <>
      <div className="hero">
        <div className="card">
          <div className="kicker">党风廉政办 · 党委巡视办</div>
          <h1>把制度、清单和报告，收成办得了的监督资产</h1>
          <p className="muted">
            当前按{view.role}浏览，范围记为{view.unit}。切换身份只改变抬头，不锁内容，便于一次把主线看完。
            数据落在标准项上，要求、思路和经验分开写，业务细节仍回源系统调阅。
          </p>
          <div className="metrics">
            <div className="metric"><b>{data.standards}</b><span>数据标准</span></div>
            <div className="metric"><b>{data.rules}</b><span>监督要求</span></div>
            <div className="metric"><b>{data.algorithms}</b><span>分析思路</span></div>
            <div className="metric"><b>{data.knowledge}</b><span>经验</span></div>
          </div>
        </div>
        <div className="card">
          <div className="kicker">先看这四条</div>
          <h2>顺着一条事项看穿</h2>
          <div className="stack">
            {data.threads.map((thread: Row) => (
              <Link key={thread.id} to={`/objects/${thread.id}`} className="thread">
                <b>{thread.name}</b>
                <span className="muted">{thread.hint}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="house" style={{ marginBottom: 16 }}>
        <div className="sidepost">归属与适用</div>
        <div className="floors">
          <div className="floor roof">成果运用<small>梳理、审核、发布，再回到下一次办理</small></div>
          <Link className="floor" to="/knowledge"><b>经验</b><small>问题表现、核查顺序、整改是否打中成因</small></Link>
          <Link className="floor" to="/rules"><b>监督要求</b><small>{data.rules} 项，按总部板块归口</small></Link>
          <Link className="floor" to="/algorithms"><b>分析思路</b><small>{data.algorithms} 条已整理思路，命中不是结论</small></Link>
          <Link className="floor" to="/standards"><b>数据标准</b><small>{data.standards} 项，业务系统按对照去调</small></Link>
        </div>
        <div className="sidepost">可见与责任</div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h2>正在办理</h2>
          <p className="mini">一份材料先拆开，人确认之后才能发布。质量关没过的，整单停住。</p>
          <div className="stack" style={{ marginTop: 10 }}>
            {data.tasks.map((task: Row) => (
              <Link key={task.id} to={`/tasks/${task.id}`} className="thread">
                <div className="row"><b>{task.title}</b>{statusPill(task.status)}</div>
                <span className="muted">{task.summary}</span>
              </Link>
            ))}
          </div>
        </div>
        <div className="stack">
          <div className="card">
            <h2>要求归在哪些板块</h2>
            {data.plates.map((plate: Row) => (
              <Link key={plate.plate} to={`/rules?plate=${encodeURIComponent(plate.plate)}`} className="rel">
                <b>{plate.plate}</b>
                <p>{plate.n} 项</p>
              </Link>
            ))}
          </div>
          <div className="card">
            <h3>名录与对照</h3>
            <p className="muted">组织 {data.orgs} 家，含总部机构、派驻机构和一级子公司名录。子公司只用于归属和适用，不据此推断股权，也不附会具体问题。</p>
            <p className="muted">示例单位的口径对照 {data.mappings} 条。清单里写下、正文尚未入库的规则编号，一律作待核依据。</p>
            <div className="row">
              <Link className="btn secondary" to="/orgs">组织名录</Link>
              <Link className="btn secondary" to="/mappings">口径对照</Link>
              <Link className="btn secondary" to="/apply">适用试算</Link>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
