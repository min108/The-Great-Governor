import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { asLines, statusPill, type Row } from "./kit";

function Block({ title, children }: { title: string; children: ReactNode }) {
  if (!children) return null;
  return (
    <div className="block">
      <h3>{title}</h3>
      {children}
    </div>
  );
}

function Maybe({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <Block title={title}>
      <Lines items={items} />
    </Block>
  );
}

function Lines({ items }: { items: string[] }) {
  if (!items.length) return null;
  return (
    <div className="stack">
      {items.map((item) => (
        <div key={item}>{item}</div>
      ))}
    </div>
  );
}

export function ShapeBody({ asset }: { asset: Row }) {
  const body = (asset.body || {}) as Row;
  const shape = String(asset.shape || "");
  if (shape === "threshold") return <Threshold body={body} />;
  if (shape === "procedure") return <Procedure body={body} />;
  if (shape === "matrix") return <Matrix body={body} />;
  if (shape === "bundle") return <Bundle asset={asset} body={body} />;
  if (shape === "mapping") return <Mapping body={body} status={asset.status} />;
  if (shape === "distinction") return <Distinction body={body} />;
  if (shape === "checkpath") return <CheckPath body={body} />;
  if (shape === "timeline") return <Timeline body={body} />;
  if (shape === "mechanism") return <Mechanism body={body} />;
  if (shape === "rectification") return <Rectification body={body} />;
  return <Clause body={body} />;
}

function Threshold({ body }: { body: Row }) {
  const rows = Array.isArray(body.rows) ? body.rows : [];
  return (
    <>
      <Block title="衡量口径"><p>{body.gauge}</p>{body.caliber ? <p className="muted">{body.caliber}</p> : null}</Block>
      <Block title="界限">
        <table>
          <thead><tr><th>事项</th><th>界限</th><th>怎么掌握</th></tr></thead>
          <tbody>
            {rows.map((row: Row) => (
              <tr key={row.item}><td>{row.item}</td><td>{row.line}</td><td>{row.method}</td></tr>
            ))}
          </tbody>
        </table>
      </Block>
      {body.below ? <Block title="限额以下"><p>{body.below}</p></Block> : null}
      <Maybe title="例外" items={asLines(body.exceptions)} />
      <Maybe title="核查时看什么" items={asLines(body.verify)} />
    </>
  );
}

function Clause({ body }: { body: Row }) {
  return (
    <>
      <div className="block">
        <div className="kv">
          <i>文号</i><span>{body.doc_no || "—"} {body.article || ""}</span>
          <i>表述</i><span>{body.modality || "—"}</span>
          <i>适用主体</i><span>{body.actor || "—"}</span>
          <i>行为</i><span>{body.action || "—"}</span>
          <i>对象</i><span>{body.target || "—"}</span>
        </div>
      </div>
      <Maybe title="同时满足" items={asLines(body.conditions)} />
      <Maybe title="例外" items={asLines(body.exceptions)} />
      <Maybe title="核查时看什么" items={asLines(body.verify)} />
      {body.note ? <Block title="说明"><p>{body.note}</p></Block> : null}
      {body.forbid ? <Block title="不予认可"><p>{body.forbid}</p></Block> : null}
    </>
  );
}

function Procedure({ body }: { body: Row }) {
  const steps = Array.isArray(body.steps) ? body.steps : [];
  return (
    <>
      <Block title="办理顺序">
        <div className="steps">
          {steps.map((step: Row) => (
            <div className="step" key={step.order}>
              <div className="num">{step.order}</div>
              <div>
                <b>{step.name}</b>
                <p className="muted">{step.who} · {step.limit}</p>
                {step.stop_if_missing ? <p className="issue">缺了就不能往下走：{step.stop_if_missing}</p> : null}
              </div>
            </div>
          ))}
        </div>
      </Block>
      {body.forbid ? <Block title="不予认可"><p>{body.forbid}</p></Block> : null}
      <Maybe title="核查时看什么" items={asLines(body.verify)} />
    </>
  );
}

function Matrix({ body }: { body: Row }) {
  const columns = Array.isArray(body.columns) ? body.columns : [];
  const rows = Array.isArray(body.rows) ? body.rows : [];
  return (
    <>
      <div className="block">
        <table>
          <thead><tr>{columns.map((col: string) => <th key={col}>{col}</th>)}</tr></thead>
          <tbody>
            {rows.map((row: string[], index: number) => (
              <tr key={index}>{row.map((cell, cellIndex) => <td key={cellIndex}>{cell}</td>)}</tr>
            ))}
          </tbody>
        </table>
      </div>
      <Maybe title="职责要分开" items={asLines(body.separation)} />
    </>
  );
}

function Bundle({ asset, body }: { asset: Row; body: Row }) {
  const items = Array.isArray(asset.bundle_items) ? asset.bundle_items : [];
  return (
    <>
      <Block title="办理这件事时一起看"><p>{body.how_to_read}</p></Block>
      <div className="stack">
        {items.map((item: Row, index: number) => (
          <Link key={item.id} to={`/assets/${item.id}`} className="thread">
            <b>{index + 1}. {item.name}</b>
            <span className="muted">{item.summary}</span>
          </Link>
        ))}
      </div>
    </>
  );
}

function Mapping({ body, status }: { body: Row; status?: string }) {
  const pending = body.verified === false || status === "待核";
  return (
    <div className="block">
      <div className="row" style={{ marginBottom: 10 }}>
        {pending ? statusPill("待核") : statusPill("已发布")}
        <span className="mini">{body.unit} · {body.system}</span>
      </div>
      <div className="kv">
        <i>源字段</i><span>{body.source_field}</span>
        <i>源口径</i><span>{body.source_caliber}</span>
        <i>标准项</i><span><Link className="jump" to={`/standards/${body.standard_code}`}>{body.standard_code}</Link> {body.standard_expect}</span>
        <i>怎么换算</i><span>{body.conversion}</span>
        <i>是不是同一对象</i><span>{body.same_object}</span>
        <i>去哪里调</i><span>{body.path}</span>
        <i>谁核对过</i><span>{body.checked_by ? `${body.checked_by} · ${body.checked_on}` : "尚未核对"}</span>
      </div>
    </div>
  );
}

function Distinction({ body }: { body: Row }) {
  const explanations = Array.isArray(body.explanations) ? body.explanations : [];
  return (
    <>
      <Block title="遇到的情形"><p>{body.situation}</p></Block>
      {explanations.map((item: Row) => (
        <div className="block" key={item.name}>
          <h3>{item.name}</h3>
          <p>支持这种解释：{item.support}</p>
          <p className="muted">削弱这种解释：{item.weaken}</p>
        </div>
      ))}
      <Block title="不能就此认定"><p>{body.cannot_conclude}</p></Block>
      {body.check_first ? <Block title="先看什么"><p>{body.check_first}</p></Block> : null}
      {body.boundary ? <Block title="不适用的情形"><p>{body.boundary}</p></Block> : null}
    </>
  );
}

function CheckPath({ body }: { body: Row }) {
  const steps = Array.isArray(body.steps) ? body.steps : [];
  return (
    <>
      <Block title="要判断的事"><p>{body.goal}</p></Block>
      <div className="steps">
        {steps.map((step: Row) => (
          <div className="step" key={step.order}>
            <div className="num">{step.order}</div>
            <div>
              <b>{step.do}</b>
              <p className="muted">{step.who} · 材料：{step.material}</p>
              <p className="issue">{step.if_missing}</p>
            </div>
          </div>
        ))}
      </div>
      {body.detour ? <Block title="走过的弯路"><p>{body.detour}</p></Block> : null}
      {body.boundary ? <Block title="不适用的情形"><p>{body.boundary}</p></Block> : null}
    </>
  );
}

function Timeline({ body }: { body: Row }) {
  const events = Array.isArray(body.events) ? body.events : [];
  return (
    <>
      <Block title="事项主体"><p>{body.subject}</p></Block>
      <div className="stack">
        {events.map((event: Row) => (
          <div className="block" key={`${event.date}-${event.text}`}>
            <div className="row">
              <b>{event.date}</b>
              {event.turn ? <span className="pill bad">判断在这里转弯</span> : null}
            </div>
            <p>{event.text}</p>
          </div>
        ))}
      </div>
      {body.lesson ? <Block title="改变判断的一点"><p>{body.lesson}</p></Block> : null}
      {body.boundary ? <Block title="使用边界"><p>{body.boundary}</p></Block> : null}
    </>
  );
}

function Mechanism({ body }: { body: Row }) {
  return (
    <>
      <Block title="通常怎样发生"><p>{body.how_it_works}</p></Block>
      <Block title="为什么要这样管"><p>{body.why_control_exists}</p></Block>
      <Maybe title="可以看见的迹象" items={asLines(body.signals)} />
      {body.boundary ? <Block title="不适用的情形"><p>{body.boundary}</p></Block> : null}
    </>
  );
}

function Rectification({ body }: { body: Row }) {
  return (
    <>
      <Block title="问题表现"><p>{body.problem}</p></Block>
      <Block title="成因"><p>{body.cause}</p></Block>
      <Block title="当时的措施"><p>{body.measure}</p></Block>
      <Block title="怎样验证"><p>{body.verify}</p></Block>
      <Block title="再次发生"><p>{body.again}</p></Block>
      {body.boundary ? <Block title="不能扩大解释"><p>{body.boundary}</p></Block> : null}
    </>
  );
}
