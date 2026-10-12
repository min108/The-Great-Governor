import { useState } from "react";
import { NavLink, Route, Routes, useNavigate } from "react-router-dom";
import { VIEWS, ViewContext } from "./kit";
import { Home } from "./Home";
import { AlgorithmPage, Algorithms, AssetList, AssetPage, ObjectPage, OrgPage, Orgs, StandardPage, Standards } from "./Browse";
import { Apply, Ask, GraphPage, SearchPage, TaskPage, Tasks } from "./Work";

const NAV = [
  ["/", "全貌"],
  ["/rules", "监督要求"],
  ["/knowledge", "经验"],
  ["/standards", "数据标准"],
  ["/algorithms", "分析思路"],
  ["/orgs", "组织名录"],
  ["/tasks", "正在办理"],
  ["/apply", "适用试算"],
  ["/ask", "问一问"],
];

export default function App() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [view, setView] = useState(() => {
    try {
      const saved = JSON.parse(localStorage.getItem("zhiyuan-view") || "");
      if (saved?.role && saved?.unit) return saved;
    } catch {
      /* 使用默认视角 */
    }
    return VIEWS[0];
  });

  function changeView(role: string) {
    const next = VIEWS.find((item) => item.role === role) || VIEWS[0];
    localStorage.setItem("zhiyuan-view", JSON.stringify(next));
    setView(next);
  }

  return (
    <ViewContext.Provider value={view}>
      <div className="shell">
        <aside className="rail">
          <div className="brand">
            <b>监督智源</b>
            <span>集团大监督业务资产</span>
          </div>
          {NAV.map(([path, label]) => (
            <NavLink key={path} to={path} end={path === "/"} className={({ isActive }) => (isActive ? "active" : "")}>
              {label}
            </NavLink>
          ))}
          <div className="foot">党风廉政办牵头维护。正式文本以内部印发为准。</div>
        </aside>
        <div className="main">
          <header className="top">
            <form className="search" onSubmit={(event) => { event.preventDefault(); if (query.trim()) navigate(`/search?q=${encodeURIComponent(query.trim())}`); }}>
              <input value={query} placeholder="查要求、经验、标准或思路" onChange={(event) => setQuery(event.target.value)} />
              <button className="btn" type="submit">检索</button>
            </form>
            <select value={view.role} onChange={(event) => changeView(event.target.value)} aria-label="当前身份">
              {VIEWS.map((item) => <option key={item.role}>{item.role}</option>)}
            </select>
          </header>
          <div className="content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/rules" element={<AssetList kind="rule" title="监督要求" lead="按条款、程序、权限表、界限和组合来读。适用主体、期间和例外写在每一项上。" />} />
              <Route path="/knowledge" element={<AssetList kind="knowledge" title="经验" lead="问题表现、核查顺序、被排除的解释、走过的弯路，以及整改有没有打在成因上。" />} />
              <Route path="/mappings" element={<AssetList kind="mapping" title="口径对照" lead="示例单位台账和标准项怎么对上。没有核对完的，停在待核。" />} />
              <Route path="/assets/:id" element={<AssetPage />} />
              <Route path="/standards" element={<Standards />} />
              <Route path="/standards/:code" element={<StandardPage />} />
              <Route path="/algorithms" element={<Algorithms />} />
              <Route path="/algorithms/:code" element={<AlgorithmPage />} />
              <Route path="/orgs" element={<Orgs />} />
              <Route path="/orgs/:id" element={<OrgPage />} />
              <Route path="/objects/:id" element={<ObjectPage />} />
              <Route path="/graph/:focus" element={<GraphPage />} />
              <Route path="/tasks" element={<Tasks />} />
              <Route path="/tasks/:id" element={<TaskPage />} />
              <Route path="/apply" element={<Apply />} />
              <Route path="/ask" element={<Ask />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="*" element={<p className="muted">没有这一页。</p>} />
            </Routes>
            <p className="footer-note">演示环境中，规则正文、案例和办理过程为按公开制度精神与集团组织框架拟制的展示内容；数据标准和监督思路来自已整理清单；正式文本以内部印发为准。</p>
          </div>
        </div>
      </div>
    </ViewContext.Provider>
  );
}
