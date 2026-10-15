import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import { api, auth, currency, roleLabel, type User } from "./api";

type Page = "overview" | "insight" | "accounts" | "governance";
type NavigationContext = { prompt?: string; customerId?: string };
type Navigate = (page: Page, context?: NavigationContext) => void;
type DemoUser = User & { password: string };
type Customer = { id: string; name: string; industry: string; location: string; segment: string; account_owner: string; health_score: number; outstanding_balance: number; open_cases: number };
type Citation = { source_type: string; source_id: string; label: string };
type AskResult = { answer: string; mode: string; tools_used: string[]; citations: Citation[]; limitations: string[]; latency_ms: number };
type DailyAiQuota = { user_limit: number; user_used: number; user_remaining: number; global_limit: number; global_used: number; global_remaining: number; available: boolean; reset_at: string };

const navItems: { id: Page; label: string; eyebrow: string; icon: string }[] = [
  { id: "overview", label: "Overview", eyebrow: "Business pulse", icon: "grid" },
  { id: "insight", label: "Insight AI", eyebrow: "Decision workspace", icon: "spark" },
  { id: "accounts", label: "Accounts", eyebrow: "Customer briefings", icon: "users" },
  { id: "governance", label: "Governance", eyebrow: "Evidence and audit", icon: "shield" }
];

function Icon({ name, size = 20 }: { name: string; size?: number }) {
  const paths: Record<string, ReactNode> = {
    grid: <><rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/></>,
    spark: <><path d="m12 3 1.4 4.6L18 9l-4.6 1.4L12 15l-1.4-4.6L6 9l4.6-1.4L12 3Z"/><path d="m5 15 .8 2.2L8 18l-2.2.8L5 21l-.8-2.2L2 18l2.2-.8L5 15Z"/></>,
    users: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></>,
    shield: <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/>,
    arrow: <><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></>,
    logout: <><path d="M10 17l5-5-5-5"/><path d="M15 12H3"/><path d="M21 19V5a2 2 0 0 0-2-2h-6"/></>,
    chevron: <path d="m9 18 6-6-6-6"/>,
    check: <path d="m5 12 4 4L19 6"/>,
    alert: <><path d="M10.3 2.9 1.8 17a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 2.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/></>,
    database: <><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/></>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
    refresh: <><path d="M20 12a8 8 0 1 1-2.3-5.7L20 8"/><path d="M20 3v5h-5"/></>
  };
  return <svg aria-hidden="true" viewBox="0 0 24 24" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">{paths[name] || paths.grid}</svg>;
}

function Logo({ dark = false }: { dark?: boolean }) {
  return <div className={`brand ${dark ? "brand-dark" : ""}`}>
    <span className="logo-mark"><span/><span/><span/></span>
    <span><strong>Northstar</strong><small>Industrial Supply</small></span>
  </div>;
}

function Login({ onLogin }: { onLogin: (user: User) => void }) {
  const [users, setUsers] = useState<DemoUser[]>([]);
  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");

  useEffect(() => { api<DemoUser[]>("/api/auth/demo-users").then(setUsers).catch((err) => setError(err.message)); }, []);

  const signIn = async (user: DemoUser) => {
    setLoading(user.email); setError("");
    try {
      const result = await api<{ token: string; user: User }>("/api/auth/login", { method: "POST", body: JSON.stringify({ email: user.email, password: user.password }) });
      auth.save(result.token); onLogin(result.user);
    } catch (err) { setError(err instanceof Error ? err.message : "Could not sign in"); }
    finally { setLoading(""); }
  };

  return <main className="login-page">
    <section className="login-story">
      <Logo />
      <div className="story-content">
        <span className="kicker light">Governed enterprise intelligence</span>
        <h1>Turn fragmented operations into confident decisions.</h1>
        <p>Northstar Insight connects customer, finance, delivery, inventory, service, and policy evidence—without giving AI uncontrolled access to business systems.</p>
        <div className="story-proof">
          <span><Icon name="shield"/><b>Permission aware</b><small>Backend authorization on every tool</small></span>
          <span><Icon name="database"/><b>Evidence grounded</b><small>Records, calculations, and citations</small></span>
          <span><Icon name="spark"/><b>Decision focused</b><small>Useful answers, visible limitations</small></span>
        </div>
      </div>
      <div className="story-foot">Fictional company · Synthetic data · Phase 1 read-only · Daily AI quota</div>
    </section>
    <section className="login-panel">
      <div className="login-box">
        <span className="kicker">Interactive portfolio environment</span>
        <h2>Choose a demo role</h2>
        <p>Each persona sees a different authorized slice of the same company.</p>
        {error && <div className="inline-error"><Icon name="alert"/> {error}</div>}
        <div className="persona-list">
          {users.map((user) => <button key={user.email} className="persona" onClick={() => signIn(user)} disabled={!!loading}>
            <span className={`avatar role-${user.role}`}>{user.name.split(" ").map((part) => part[0]).join("")}</span>
            <span><b>{user.name}</b><small>{user.title}</small></span>
            <span className="persona-role">{roleLabel(user.role)}</span>
            <Icon name={loading === user.email ? "refresh" : "arrow"}/>
          </button>)}
        </div>
        <div className="login-note"><Icon name="shield"/><span><b>Safe by design</b><small>No real customer, employee, or financial data is used.</small></span></div>
      </div>
    </section>
  </main>;
}

function Shell({ user, onLogout }: { user: User; onLogout: () => void }) {
  const [page, setPage] = useState<Page>("overview");
  const [navigation, setNavigation] = useState<NavigationContext & { id: number }>({ id: 0 });
  const active = navItems.find((item) => item.id === page)!;
  const navigate: Navigate = (nextPage, context = {}) => { setNavigation({ ...context, id: Date.now() }); setPage(nextPage); };
  return <div className="app-shell">
    <aside className="sidebar">
      <Logo />
      <nav aria-label="Primary navigation">
        {navItems.map((item) => <button key={item.id} aria-label={item.label} title={item.label} className={page === item.id ? "active" : ""} onClick={() => navigate(item.id)}>
          <Icon name={item.icon}/><span><b>{item.label}</b><small>{item.eyebrow}</small></span>
        </button>)}
      </nav>
      <div className="phase-card"><span className="phase-dot"/><b>Phase 1 environment</b><small>Read-only decision support</small></div>
      <button className="user-card" onClick={onLogout} aria-label={`Sign out ${user.name}`} title="Sign out">
        <span className={`avatar role-${user.role}`}>{user.name.split(" ").map((part) => part[0]).join("")}</span>
        <span><b>{user.name}</b><small>{roleLabel(user.role)}</small></span><Icon name="logout" size={18}/>
      </button>
    </aside>
    <main className="main-content">
      <header className="topbar">
        <div><span className="kicker">{active.eyebrow}</span><h1>{active.label}</h1></div>
        <div className="topbar-status"><span className="live-dot"/> Live synthetic environment</div>
      </header>
      <AICommandCenter page={page} user={user} navigate={navigate}/>
      {page === "overview" && <Overview user={user} navigate={navigate}/>} 
      {page === "insight" && <InsightWorkspace key={navigation.id} initialQuestion={navigation.prompt} initialCustomerId={navigation.customerId}/>}
      {page === "accounts" && <Accounts initialCustomerId={navigation.customerId}/>}
      {page === "governance" && <Governance user={user}/>} 
    </main>
  </div>;
}

const aiPageCopy: Record<Page, { eyebrow: string; title: string; placeholder: string }> = {
  overview: { eyebrow: "AI decision layer", title: "Ask your role-aware business copilot", placeholder: "Ask AI to explain today's priorities…" },
  insight: { eyebrow: "Governed AI workspace", title: "Investigate with evidence, tools, and citations", placeholder: "Ask a question across authorized business data…" },
  accounts: { eyebrow: "AI account intelligence", title: "Turn account records into meeting-ready insight", placeholder: "Ask AI to prepare or compare an account…" },
  governance: { eyebrow: "AI trust and controls", title: "Understand how every answer is governed", placeholder: "Ask AI about evidence, access, or controls…" },
};

const rolePrompts: Record<string, string> = {
  account_manager: "Prepare a briefing for my highest-priority customer account.",
  finance_analyst: "Summarize overdue exposure and the collections actions that matter most.",
  operations_manager: "Show the delivery and inventory risks that need action today.",
  executive: "Create an executive brief of the most material cross-functional risks.",
  ai_administrator: "Explain the current AI control status and configuration limitations.",
};

function AICommandCenter({ page, user, navigate }: { page: Page; user: User; navigate: Navigate }) {
  const copy = aiPageCopy[page];
  const [prompt, setPrompt] = useState("");
  const [status, setStatus] = useState<any>(null);
  useEffect(() => {
    const refresh = () => { api("/api/system/status").then(setStatus).catch(() => undefined); };
    refresh();
    window.addEventListener("northstar:quota-used", refresh);
    return () => window.removeEventListener("northstar:quota-used", refresh);
  }, []);
  const rolePrompt = rolePrompts[user.role] || "Summarize the most important business risks in my authorized scope.";
  const ask = (event: FormEvent) => { event.preventDefault(); const question = prompt.trim() || rolePrompt; navigate("insight", { prompt: question }); };
  const mode = status?.ai_mode === "model-assisted" ? "Model assisted" : "Deterministic AI";
  const quota = status?.daily_ai_quota as DailyAiQuota | undefined;
  return <section className="ai-command-center" aria-label="Northstar Insight AI command center">
    <div className="ai-orb" aria-hidden="true"><span><Icon name="spark" size={23}/></span><i/><i/><i/></div>
    <div className="ai-command-copy"><span className="ai-eyebrow"><b>Northstar Insight AI</b><em><span/>{mode}</em></span><h2>{copy.title}</h2><p>{copy.eyebrow} · Permission-aware answers grounded in live synthetic records.</p></div>
    <form className="ai-command-form" onSubmit={ask}>
      <div><Icon name="spark" size={18}/><input value={prompt} onChange={(event) => setPrompt(event.target.value)} aria-label="Ask Northstar AI" placeholder={copy.placeholder}/></div>
      <button type="submit">Ask AI <Icon name="arrow" size={17}/></button>
    </form>
    <div className="ai-command-foot">
      <button onClick={() => navigate("insight", { prompt: rolePrompt })}><Icon name="spark" size={13}/>Suggested for {roleLabel(user.role)}</button>
      <span className={quota && !quota.available ? "quota-empty" : "quota-live"}><Icon name="clock" size={13}/>{quota ? `${quota.user_remaining}/${quota.user_limit} AI requests left today` : "Daily quota protected"}</span>
      <span><Icon name="shield" size={13}/>Role scoped</span><span><Icon name="database" size={13}/>Evidence grounded</span><span><Icon name="check" size={13}/>Citations on</span>
    </div>
    <div className="ai-grid-glow" aria-hidden="true"/>
  </section>;
}

function Overview({ user, navigate }: { user: User; navigate: Navigate }) {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");
  useEffect(() => { api("/api/dashboard").then(setData).catch((err) => setError(err.message)); }, []);
  if (error) return <ErrorState message={error}/>;
  if (!data) return <LoadingState label="Assembling your authorized business view"/>;
  const maxRevenue = Math.max(...data.revenue_trend.map((point: any) => point.value), 1);
  const attention = data.attention || { eyebrow: "Requires attention", title: "Priority exceptions", summary: "Authorized items that may need action.", count_label: "actions", empty_title: "No priority exceptions detected" };
  const attentionLabel = data.exceptions.length === 1 ? attention.count_label.replace(/actions$/, "action") : attention.count_label;
  return <div className="page-grid">
    <section className="welcome-banner">
      <div><span className="kicker light">Role-based decision brief</span><h2>Good morning, {user.name.split(" ")[0]}.</h2><p>{attention.summary} <b>{data.exceptions.length} {data.exceptions.length === 1 ? "item" : "items"}</b> currently {data.exceptions.length === 1 ? "requires" : "require"} review.</p></div>
      <button className="primary-button light-button" onClick={() => navigate("insight")}>Ask Insight <Icon name="arrow"/></button>
      <div className="orbit orbit-one"/><div className="orbit orbit-two"/>
    </section>
    <section className="kpi-grid">
      <Metric label="Recognized revenue" value={currency(data.kpis.recognized_revenue)} note="Delivered demo orders" trend="+8.4%"/>
      <Metric label="Outstanding balance" value={currency(data.kpis.outstanding_balance)} note="Open and overdue" tone="amber"/>
      <Metric label="On-time delivery" value={`${data.kpis.on_time_delivery}%`} note="Recorded shipments" tone={data.kpis.on_time_delivery < 85 ? "amber" : "green"}/>
      <Metric label="Open service cases" value={String(data.kpis.open_service_cases)} note={data.scope_note} tone="blue"/>
    </section>
    <section className="panel chart-panel">
      <PanelHeader kicker="Commercial activity" title="Order value trend" action="Synthetic CAD"/>
      <div className="bar-chart" aria-label="Monthly order value chart">
        {data.revenue_trend.map((point: any) => <div className="bar-column" key={point.month}><span className="bar-value">{currency(point.value)}</span><div className="bar-track"><div className="bar" style={{height: `${Math.max(12, (point.value / maxRevenue) * 100)}%`}}/></div><small>{point.month}</small></div>)}
      </div>
    </section>
    <section className="panel exceptions-panel">
      <PanelHeader kicker={attention.eyebrow} title={attention.title} action={`${data.exceptions.length} ${attentionLabel}`}/>
      <div className="exception-list">
        {data.exceptions.slice(0, 5).map((item: any, index: number) => <button key={`${item.title}-${index}`} aria-label={`${item.title}. ${item.next_action}`} onClick={() => navigate((item.target_page || "insight") as Page, { prompt: item.suggested_question, customerId: item.customer_id || undefined })}>
          <span className={`severity severity-${item.severity}`}><Icon name="alert" size={17}/></span>
          <span className="exception-copy"><b>{item.title}</b><small>{item.detail}</small><em><span>{item.context}</span>{item.next_action}</em></span>
          <span className="record-id">{item.record_id || item.customer_id}</span><Icon name="chevron" size={17}/>
        </button>)}
        {!data.exceptions.length && <div className="exception-empty"><span className="severity severity-low"><Icon name="check" size={17}/></span><span><b>{attention.empty_title}</b><small>The role-specific monitoring rules found nothing requiring action.</small></span></div>}
      </div>
    </section>
    <section className="panel portfolio-panel">
      <PanelHeader kicker="Customer portfolio" title="Account health" action={`${data.portfolio.length} accounts`}/>
      <div className="health-list">
        {data.portfolio.map((item: any) => <div key={item.id}><span><b>{item.name}</b><small>{item.segment}</small></span><div className="health-track"><span style={{width: `${item.score}%`}} className={item.score < 70 ? "risk" : item.score < 85 ? "watch" : "healthy"}/></div><strong>{item.score}</strong></div>)}
      </div>
    </section>
    <section className="panel value-panel">
      <span className="kicker">What this proves</span><h3>Business evidence, not a chatbot demo.</h3><p>Every number is calculated by application code. Every AI claim can be traced to permitted records or current documents. Every request leaves a reviewable audit event.</p>
      <div className="value-tags"><span><Icon name="check"/> Deterministic KPIs</span><span><Icon name="check"/> Bounded AI tools</span><span><Icon name="check"/> Role-based access</span></div>
    </section>
  </div>;
}

function Metric({ label, value, note, trend, tone = "navy" }: { label: string; value: string; note: string; trend?: string; tone?: string }) {
  return <article className={`metric metric-${tone}`}><div><span>{label}</span>{trend && <em>{trend}</em>}</div><strong>{value}</strong><small>{note}</small></article>;
}

function PanelHeader({ kicker, title, action }: { kicker: string; title: string; action: string }) {
  return <header className="panel-header"><div><span className="kicker">{kicker}</span><h3>{title}</h3></div><span className="panel-action">{action}</span></header>;
}

const suggestedQuestions = [
  "Prepare a briefing for Horizon Construction.",
  "Which delayed orders require attention today?",
  "Which authorized customers have overdue invoices?",
  "What approval is required for a purchase above $25,000?"
];

function InsightWorkspace({ initialQuestion, initialCustomerId }: { initialQuestion?: string; initialCustomerId?: string }) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customerId, setCustomerId] = useState(initialCustomerId || "");
  const [question, setQuestion] = useState(initialQuestion || suggestedQuestions[0]);
  const [result, setResult] = useState<AskResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => { api<Customer[]>("/api/customers").then(setCustomers).catch(() => undefined); }, []);

  const ask = async (event?: FormEvent) => {
    event?.preventDefault(); if (!question.trim()) return;
    setLoading(true); setError("");
    try { setResult(await api<AskResult>("/api/ask", { method: "POST", body: JSON.stringify({ question, customer_id: customerId || null }) })); window.dispatchEvent(new Event("northstar:quota-used")); }
    catch (err) { setError(err instanceof Error ? err.message : "Insight could not answer"); }
    finally { setLoading(false); }
  };

  return <div className="insight-layout">
    <section className="workspace panel">
      <div className="workspace-head"><div className="insight-symbol"><Icon name="spark" size={24}/></div><div><span className="kicker">Governed assistant</span><h2>Ask Northstar Insight</h2><p>Grounded in your authorized operational records and current internal documents.</p></div><span className="read-only-badge"><Icon name="shield" size={15}/> Read only</span></div>
      <form className="ask-box" onSubmit={ask}>
        <textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask a business question…" aria-label="Business question"/>
        <div className="ask-controls">
          <label><span>Account context</span><select value={customerId} onChange={(event) => setCustomerId(event.target.value)}><option value="">Auto-detect</option>{customers.map((customer) => <option key={customer.id} value={customer.id}>{customer.name}</option>)}</select></label>
          <button className="primary-button" disabled={loading || !question.trim()}>{loading ? <><span className="spinner"/> Analyzing</> : <>Ask Insight <Icon name="arrow"/></>}</button>
        </div>
      </form>
      {error && <div className="inline-error"><Icon name="alert"/> {error}</div>}
      {!result && !loading && <div className="suggested"><span className="kicker">Try a governed workflow</span>{suggestedQuestions.map((item) => <button key={item} onClick={() => { setQuestion(item); }}>{item}<Icon name="arrow" size={16}/></button>)}</div>}
      {loading && <div className="thinking"><div className="thinking-orbit"><span/><span/><span/></div><h3>Building an evidence-backed answer</h3><p>Checking permissions, selecting business tools, and reconciling sources.</p></div>}
      {result && !loading && <div className="answer">
        <div className="answer-meta"><span className={`mode-badge mode-${result.mode}`}><span/>{result.mode.replace("-", " ")}</span><span><Icon name="clock" size={15}/>{result.latency_ms} ms</span><span><Icon name="database" size={15}/>{result.citations.length} sources</span></div>
        <FormattedAnswer text={result.answer}/>
        {!!result.limitations.length && <div className="limitations"><Icon name="alert"/><div><b>Limitations</b>{result.limitations.map((item) => <p key={item}>{item}</p>)}</div></div>}
        {!!result.citations.length && <div className="sources"><span className="kicker">Evidence used</span><div>{result.citations.map((item) => <span key={`${item.source_type}-${item.source_id}`}><Icon name="database" size={15}/><b>{item.label}</b><small>{item.source_type} · {item.source_id}</small></span>)}</div></div>}
      </div>}
    </section>
    <aside className="context-rail">
      <section className="panel"><span className="kicker">Control boundary</span><h3>What Insight can do</h3><ul className="control-list"><li><Icon name="check"/>Retrieve approved records</li><li><Icon name="check"/>Calculate verified metrics</li><li><Icon name="check"/>Search current documents</li><li><Icon name="check"/>Explain and recommend</li></ul><hr/><h3>What it cannot do</h3><ul className="control-list blocked"><li>Change orders or invoices</li><li>Execute payments</li><li>Bypass role permissions</li><li>Browse arbitrary systems</li></ul></section>
      <section className="panel architecture-mini"><span className="kicker">Request path</span><div><span>User question</span><i/><span>Authorization</span><i/><span>Business tools</span><i/><span>Evidence-backed answer</span></div></section>
    </aside>
  </div>;
}

function renderInline(text: string): ReactNode[] {
  return text.split(/(\*\*.*?\*\*)/g).filter(Boolean).map((part, index) => part.startsWith("**") ? <strong key={index}>{part.slice(2, -2)}</strong> : <span key={index}>{part}</span>);
}

function FormattedAnswer({ text }: { text: string }) {
  const lines = text.split("\n");
  return <div className="formatted-answer">{lines.map((line, index) => {
    if (line.startsWith("### ")) return <h3 key={index}>{line.slice(4)}</h3>;
    if (line.startsWith("## ")) return <h2 key={index}>{line.slice(3)}</h2>;
    if (line.startsWith("- ")) return <div className="answer-bullet" key={index}><span/> <p>{renderInline(line.slice(2))}</p></div>;
    if (!line.trim()) return <div className="answer-space" key={index}/>;
    return <p key={index}>{renderInline(line)}</p>;
  })}</div>;
}

function Accounts({ initialCustomerId }: { initialCustomerId?: string }) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selected, setSelected] = useState(initialCustomerId || "");
  const [briefing, setBriefing] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  useEffect(() => { api<Customer[]>("/api/customers").then((items) => { setCustomers(items); if (items[0]) setSelected((current) => current && items.some((item) => item.id === current) ? current : items[0].id); }); }, []);
  useEffect(() => { if (!selected) return; setLoading(true); api(`/api/customers/${selected}/briefing`).then(setBriefing).finally(() => setLoading(false)); }, [selected]);
  const filtered = customers.filter((customer) => `${customer.name} ${customer.id} ${customer.industry}`.toLowerCase().includes(search.toLowerCase()));
  return <div className="accounts-layout">
    <section className="account-list panel">
      <div className="account-search"><Icon name="search"/><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Find an authorized account"/></div>
      <div className="account-count">{filtered.length} accounts in your scope</div>
      {filtered.map((customer) => <button key={customer.id} className={selected === customer.id ? "selected" : ""} onClick={() => setSelected(customer.id)}><span className="company-avatar">{customer.name.split(" ").map((part) => part[0]).join("").slice(0, 2)}</span><span><b>{customer.name}</b><small>{customer.industry} · {customer.location}</small><em>{customer.segment}</em></span><strong className={customer.health_score < 70 ? "risk" : customer.health_score < 85 ? "watch" : "healthy"}>{customer.health_score}</strong></button>)}
    </section>
    <section className="account-detail">
      {loading || !briefing ? <LoadingState label="Reconciling account evidence"/> : <>
        <header className="account-hero"><div><span className="kicker">{briefing.customer.id} · {briefing.customer.segment}</span><h2>{briefing.customer.name}</h2><p>{briefing.customer.industry} · {briefing.customer.location} · Customer since {briefing.customer.since}</p></div><div className="score-ring"><strong>{briefing.customer.health_score}</strong><small>health</small></div></header>
        <div className="account-metrics"><Metric label="Outstanding" value={currency(briefing.metrics.outstanding_balance)} note={`${currency(briefing.metrics.overdue_balance)} overdue`} tone={briefing.metrics.overdue_balance ? "amber" : "green"}/><Metric label="On-time delivery" value={`${briefing.metrics.on_time_delivery}%`} note="Recorded shipments" tone="blue"/><Metric label="Open cases" value={String(briefing.metrics.open_cases)} note="Service attention"/></div>
        <div className="briefing-grid">
          <section className="panel"><PanelHeader kicker="Meeting preparation" title="Priority risks" action="Evidence backed"/><ul className="brief-list risks">{briefing.risks.map((item: string) => <li key={item}><Icon name="alert"/>{item}</li>)}</ul></section>
          <section className="panel"><PanelHeader kicker="Account development" title="Opportunities" action="Human review"/><ul className="brief-list opportunities">{briefing.opportunities.map((item: string) => <li key={item}><Icon name="spark"/>{item}</li>)}</ul></section>
          <section className="panel orders-table"><PanelHeader kicker="Recent activity" title="Orders" action={`${briefing.orders.length} shown`}/><div className="data-table"><div className="table-head"><span>Order</span><span>Status</span><span>Promised</span><span>Value</span></div>{briefing.orders.map((order: any) => <div key={order.id}><b>{order.id}<small>{order.summary}</small></b><span className={`status status-${order.status.toLowerCase().replace(" ", "-")}`}>{order.status}</span><span>{order.promised_date}</span><span>{currency(order.total)}</span></div>)}</div></section>
          <section className="panel evidence-table"><PanelHeader kicker="Traceability" title="Source evidence" action={`${briefing.citations.length} records`}/><div className="evidence-list">{briefing.citations.map((item: Citation) => <div key={`${item.source_type}-${item.source_id}`}><Icon name="database"/><span><b>{item.label}</b><small>{item.source_type} · {item.source_id}</small></span><Icon name="check"/></div>)}</div></section>
        </div>
      </>}
    </section>
  </div>;
}

function Governance({ user }: { user: User }) {
  const [status, setStatus] = useState<any>(null);
  const [events, setEvents] = useState<any[]>([]);
  const [cases, setCases] = useState<any[]>([]);
  const [indexing, setIndexing] = useState("");
  const refresh = () => Promise.all([api("/api/system/status").then(setStatus), api<any[]>("/api/audit").then(setEvents), api<any[]>("/api/evaluation/cases").then(setCases)]);
  useEffect(() => { refresh(); }, []);
  const reindex = async () => { setIndexing("Indexing…"); try { const result = await api<any>("/api/admin/reindex", {method: "POST"}); setIndexing(result.message); refresh(); } catch (err) { setIndexing(err instanceof Error ? err.message : "Index failed"); } };
  if (!status) return <LoadingState label="Loading governance evidence"/>;
  return <div className="governance-grid">
    <section className="system-banner"><div className="system-icon"><Icon name="shield" size={28}/></div><div><span className="kicker light">Control status</span><h2>Governed by design</h2><p>Authorization, evidence, safe failure, and auditability are application controls—not instructions we hope the model follows.</p></div><span className="control-state"><Icon name="check"/> Operational</span></section>
    <section className="panel system-panel"><PanelHeader kicker="Runtime configuration" title="System status" action={status.phase}/><div className="system-grid"><StatusItem label="Database" value={status.database} state="Connected"/><StatusItem label="AI answer mode" value={status.ai_mode.replace("-", " ")} state={status.chat_model_configured ? "Configured" : "Safe fallback"}/><StatusItem label="Semantic retrieval" value={`${status.document_count} governed documents`} state={status.embedding_model_configured ? "Configured" : "Keyword mode"}/><StatusItem label="Daily demo quota" value={`${status.daily_ai_quota.user_remaining} of ${status.daily_ai_quota.user_limit} AI requests left`} state={status.daily_ai_quota.available ? "Cost protected" : "Fallback active"}/><StatusItem label="Active role" value={roleLabel(status.user_role)} state="Authorized"/></div>{user.role === "ai_administrator" && <div className="admin-action"><div><b>Semantic document index</b><small>Add your key and embedding model, then build the pgvector index.</small></div><button className="secondary-button" onClick={reindex}><Icon name="refresh"/>{indexing || "Build index"}</button></div>}</section>
    <section className="panel eval-panel"><PanelHeader kicker="Quality framework" title="Evaluation cases" action={`${cases.length} scenarios`}/><div className="eval-list">{cases.map((item) => <div key={item.category}><span>{item.category}</span><b>{item.question}</b><p>{item.expected}</p></div>)}</div></section>
    <section className="panel audit-panel"><PanelHeader kicker="Operational evidence" title="Audit timeline" action={user.role === "ai_administrator" ? "All users" : "Your activity"}/><div className="audit-list">{events.length ? events.map((event) => <div key={event.id}><span className="audit-node"><Icon name={event.event_type === "login" ? "users" : "spark"}/></span><span><b>{event.event_type.replaceAll("_", " ")}</b><p>{event.request_summary}</p><small>{new Date(event.created_at).toLocaleString()} · {event.user_email} · {event.latency_ms} ms</small></span><div><em className={`mode-badge mode-${event.mode}`}><span/>{event.mode}</em>{event.tools_used.slice(0, 2).map((tool: string) => <small key={tool}>{tool}</small>)}</div></div>) : <div className="empty-audit">Use Insight or generate a briefing to create reviewable events.</div>}</div></section>
    <section className="panel risk-panel"><span className="kicker">Responsible AI boundary</span><h3>Human accountability stays visible.</h3><div className="risk-controls"><span><b>Facts</b><small>Come from authorized records</small></span><span><b>Metrics</b><small>Calculated by deterministic code</small></span><span><b>Interpretation</b><small>May be model generated</small></span><span><b>Action</b><small>Requires human judgment</small></span></div></section>
  </div>;
}

function StatusItem({ label, value, state }: { label: string; value: string; state: string }) { return <div><span className="status-check"><Icon name="check"/></span><span><small>{label}</small><b>{value}</b></span><em>{state}</em></div>; }
function LoadingState({ label }: { label: string }) { return <div className="loading-state"><div className="thinking-orbit"><span/><span/><span/></div><h3>{label}</h3><p>Northstar is checking the current synthetic environment.</p></div>; }
function ErrorState({ message }: { message: string }) { return <div className="error-state"><Icon name="alert" size={28}/><h3>Something needs attention</h3><p>{message}</p></div>; }

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [checking, setChecking] = useState(!!auth.token());
  useEffect(() => {
    const unauthorized = () => { setUser(null); setChecking(false); };
    window.addEventListener("northstar:unauthorized", unauthorized);
    if (auth.token()) api<User>("/api/auth/me").then(setUser).catch(() => auth.clear()).finally(() => setChecking(false));
    return () => window.removeEventListener("northstar:unauthorized", unauthorized);
  }, []);
  const logout = () => { auth.clear(); setUser(null); };
  if (checking) return <LoadingState label="Opening your authorized workspace"/>;
  return user ? <Shell user={user} onLogout={logout}/> : <Login onLogin={setUser}/>;
}
