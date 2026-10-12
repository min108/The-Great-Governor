import { createContext, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, hrefFor, type Relation } from "./api";

export type Row = Record<string, any>;

export const ViewContext = createContext({ role: "党风廉政办", unit: "集团总部" });

export const VIEWS = [
  { role: "党风廉政办", unit: "集团总部" },
  { role: "党委巡视办", unit: "集团总部" },
  { role: "驻集团纪检监察组", unit: "集团总部" },
  { role: "财务管理部", unit: "集团总部" },
  { role: "示例制造企业", unit: "示例制造企业" },
  { role: "示例金融子公司", unit: "示例金融子公司" },
];

export const KIND: Record<string, string> = {
  rule: "监督要求",
  knowledge: "经验",
  mapping: "口径对照",
  standard: "数据标准",
  algorithm: "分析思路",
  object: "业务对象",
  fact: "事实经过",
  abandon: "不收录",
};

export const SHAPE: Record<string, string> = {
  clause: "条款",
  matrix: "权限表",
  procedure: "办理程序",
  threshold: "数额与界限",
  bundle: "一并遵循",
  mapping: "口径对照",
  distinction: "辨析",
  checkpath: "核查顺序",
  timeline: "经过",
  mechanism: "成因",
  rectification: "整改验证",
};

export function statusPill(status?: string) {
  if (!status) return null;
  const bad = ["已退回", "待判断"];
  const warn = ["待核", "待审核", "待补充", "待人员确认", "试行"];
  const ok = ["已发布", "已确认"];
  const plain = ["草稿", "已放弃"];
  const cls = bad.includes(status) ? "bad" : warn.includes(status) ? "warn" : ok.includes(status) ? "ok" : plain.includes(status) ? "plain" : "";
  return <span className={`pill ${cls}`}>{status}</span>;
}

export function useLoad<T>(path: string | null) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  const [tick, setTick] = useState(0);
  useEffect(() => {
    if (!path) return;
    let live = true;
    setData(null);
    setError("");
    api<T>(path)
      .then((item) => {
        if (live) setData(item);
      })
      .catch((reason: Error) => {
        if (live) setError(reason.message || "没有读到");
      });
    return () => {
      live = false;
    };
  }, [path, tick]);
  return { data, error, setData, reload: () => setTick((value) => value + 1) };
}

export function Loading({ error }: { error?: string }) {
  if (error) return <div className="error">{error}</div>;
  return <p className="muted">正在读取。</p>;
}

export function Relations({ items, total }: { items?: Relation[]; total?: number }) {
  if (!items?.length) return <p className="muted">还没有写明的关联。</p>;
  return (
    <div>
      {items.map((rel) => (
        <Link key={rel.id} to={hrefFor(rel.other_kind, rel.other_id)} className="rel">
          <div className="row">
            <span className="pill plain">{rel.rel_type}</span>
            <span className="pill">{rel.way === "指出" ? "本项指向" : "对方指向本项"}</span>
            {statusPill(rel.confirm_status)}
          </div>
          <b>{KIND[rel.other_kind] ? `${KIND[rel.other_kind]} · ` : ""}{rel.other_name}</b>
          <p>{[rel.period, rel.condition, rel.evidence].filter(Boolean).join(" · ")}</p>
        </Link>
      ))}
      {total && total > items.length ? (
        <p className="mini">共 {total} 条关联。大量数据引用不在这里铺开，避免把清单看成一张网。</p>
      ) : null}
    </div>
  );
}

export function linkify(text?: string) {
  if (!text) return null;
  const parts = text.split(/(D\.\d{2}\.\d{2}\.\d{3}|A\.\d{2}\.\d{2}\.\d{3})/g);
  return parts.map((part, index) => {
    if (/^D\./.test(part)) return <Link key={index} className="jump" to={`/standards/${part}`}>{part}</Link>;
    if (/^A\./.test(part)) return <Link key={index} className="jump" to={`/algorithms/${part}`}>{part}</Link>;
    return <span key={index}>{part}</span>;
  });
}

export function asLines(value: unknown): string[] {
  if (!value) return [];
  if (typeof value === "string") return [value];
  if (!Array.isArray(value)) return [];
  return value
    .map((item) => {
      if (typeof item === "string") return item;
      if (item && typeof item === "object") {
        const row = item as Row;
        if (row.title && row.when) return `${row.title}：${row.when}`;
        return [row.name, row.do, row.text].filter(Boolean).join("；");
      }
      return "";
    })
    .filter(Boolean);
}
