"""Build the branded PyQA Suite dashboard + analytics page from Allure data.

Reads the widget and data JSON files produced by `allure generate` and
writes standalone pages styled to match nkululeko-portfolio.vercel.app:

  index.html   - headline dashboard (stats, pipeline, coverage, environment)
  graphs.html  - analytics: status donut, severity, slowest tests, waterfall

Usage: python scripts/build_dashboard.py <allure_report_dir> <output_dir>
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_json(path):
    p = Path(path)
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return None


def load_widget(report_dir, name):
    return load_json(Path(report_dir) / "widgets" / name)


def fmt_duration(ms):
    if ms is None:
        return "-"
    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.0f}s"
    return f"{int(seconds // 60)}m {int(seconds % 60)}s"


def collect_tests(report_dir):
    """Flatten data/suites.json into a list of test dicts with severity."""
    suites = load_json(Path(report_dir) / "data" / "suites.json") or {}
    tests = []

    def walk(node, parents):
        children = node.get("children")
        if children is not None:
            for child in children:
                walk(child, parents + [node.get("name", "")])
        else:
            time = node.get("time", {}) or {}
            tests.append({
                "uid": node.get("uid", ""),
                "name": node.get("name", "?"),
                "suite": next((p for p in parents if p and p != "suites"), ""),
                "status": node.get("status", "unknown"),
                "start": time.get("start"),
                "stop": time.get("stop"),
                "duration": time.get("duration", 0) or 0,
            })

    walk(suites, [])

    for t in tests:
        tc = load_json(Path(report_dir) / "data" / "test-cases" / f"{t['uid']}.json") or {}
        sev = tc.get("severity")
        if not sev:
            labels = tc.get("labels", []) or []
            sev = next((l.get("value") for l in labels if l.get("name") == "severity"), None)
        t["severity"] = (sev or "normal").lower()
        t["feature"] = next(
            (l.get("value") for l in (tc.get("labels", []) or []) if l.get("name") == "feature"),
            t["suite"],
        )
    return tests


FEATURE_ICONS = {
    "REST API": "&#9741;",
    "Checkout": "&#128179;",
    "Authentication": "&#128273;",
    "Product Catalogue": "&#128722;",
    "Shopping Cart": "&#128717;",
    "Site Health": "&#127973;",
}

SHARED_CSS = """
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #020617; --surface: #0a0f1e; --card: #0f172a; --card-hover: #131d35;
    --border: rgba(30,41,59,0.7); --border-h: rgba(6,182,212,0.45);
    --accent: #06b6d4; --accent-l: #22d3ee; --accent-g: rgba(6,182,212,0.10);
    --violet: #8b5cf6; --text: #f1f5f9; --muted: #94a3b8; --faint: #334155;
    --radius: 12px; --radius-lg: 20px;
    --mono: 'Space Mono', monospace; --sans: 'Inter', sans-serif;
    --pass: #34d399; --fail: #f87171; --warn: #fbbf24; --skip: #64748b;
  }
  html { scroll-behavior: smooth; }
  body {
    background: linear-gradient(145deg, #020617 0%, #0a0f1e 40%, #0f172a 100%);
    background-attachment: fixed;
    color: var(--text); font-family: var(--sans); line-height: 1.6; min-height: 100vh;
  }
  .glow {
    position: fixed; top: -220px; left: 50%; transform: translateX(-50%);
    width: 900px; height: 480px; border-radius: 50%; pointer-events: none;
    background: radial-gradient(ellipse, rgba(6,182,212,0.13) 0%, transparent 65%);
  }
  .wrap { max-width: 1320px; margin: 0 auto; padding: 0 32px 80px; position: relative; }
  nav { display: flex; align-items: center; justify-content: space-between; padding: 26px 0 0; }
  .brand { font-family: var(--mono); font-weight: 700; font-size: 16px; color: var(--text); text-decoration: none; }
  .brand span { color: var(--accent-l); }
  .nav-links { display: flex; gap: 24px; align-items: center; flex-wrap: wrap; }
  .nav-links a { color: var(--muted); text-decoration: none; font-size: 14px; transition: color 0.2s; }
  .nav-links a:hover { color: var(--accent-l); }
  .nav-links a.active { color: var(--accent-l); }
  .kicker {
    font-family: var(--mono); font-size: 12.5px; letter-spacing: 0.28em;
    color: var(--accent-l); text-transform: uppercase; margin-bottom: 16px;
    display: flex; align-items: center; gap: 12px;
  }
  .kicker::before { content: ''; width: 34px; height: 1px; background: var(--accent); }
  .section { margin-top: 56px; }
  .section h2 {
    font-family: var(--mono); font-size: 12.5px; letter-spacing: 0.28em;
    color: var(--accent-l); text-transform: uppercase; margin-bottom: 20px;
    display: flex; align-items: center; gap: 12px;
  }
  .section h2::before { content: ''; width: 34px; height: 1px; background: var(--accent); }
  .panel { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 30px; }
  footer {
    margin-top: 80px; padding-top: 26px; border-top: 1px solid var(--border);
    display: flex; flex-wrap: wrap; gap: 10px; justify-content: space-between;
    color: var(--faint); font-family: var(--mono); font-size: 12px; letter-spacing: 0.06em;
  }
  footer a { color: var(--muted); text-decoration: none; }
  footer a:hover { color: var(--accent-l); }
"""


def build_index(report_dir, output_dir):
    summary = load_widget(report_dir, "summary.json") or {}
    stats = summary.get("statistic", {})
    time_info = summary.get("time", {})

    total = stats.get("total", 0)
    skipped = stats.get("skipped", 0)
    executed = total - skipped
    passed = stats.get("passed", 0)
    failed = stats.get("failed", 0) + stats.get("broken", 0)
    pass_pct = round(passed / executed * 100) if executed else 0
    duration = fmt_duration(time_info.get("duration"))

    behaviors = load_widget(report_dir, "behaviors.json") or {}
    features = []
    for item in behaviors.get("items", []):
        f_stats = item.get("statistic", {})
        f_total = f_stats.get("total", 0)
        f_passed = f_stats.get("passed", 0)
        f_skipped = f_stats.get("skipped", 0)
        f_run = f_total - f_skipped
        if f_run == 0:
            continue
        features.append({
            "name": item.get("name", "?"),
            "total": f_run,
            "passed": f_passed,
            "pct": round(f_passed / f_run * 100) if f_run else 0,
        })
    features.sort(key=lambda f: -f["total"])

    env_items = load_widget(report_dir, "environment.json") or []
    environment = [(i.get("name", "?").replace(".", " "), ", ".join(i.get("values", []))) for i in env_items]

    executors = load_widget(report_dir, "executors.json") or []
    run_number = executors[0].get("buildOrder") if executors else None
    build_url = executors[0].get("buildUrl", "https://github.com/Nkuempoofu/pyqa-suite/actions") if executors \
        else "https://github.com/Nkuempoofu/pyqa-suite/actions"

    generated = datetime.now(timezone.utc).strftime("%d %b %Y &middot; %H:%M UTC")
    run_chip = f"Run #{run_number}" if run_number else "Latest run"

    feature_rows = "\n".join(
        f'''        <div class="feat-row">
          <div class="feat-icon">{FEATURE_ICONS.get(f["name"], "&#9679;")}</div>
          <div class="feat-name">{f["name"]}</div>
          <div class="feat-bar"><div class="feat-fill{' full' if f['pct'] == 100 else ''}" style="width:{f["pct"]}%"></div></div>
          <div class="feat-count">{f["passed"]}/{f["total"]}</div>
        </div>'''
        for f in features
    )
    env_rows = "\n".join(
        f'''          <div class="env-row"><span class="env-key">{k}</span><span class="env-val">{v}</span></div>'''
        for k, v in environment
    )

    ring_deg = round(pass_pct * 3.6)
    all_green = failed == 0 and executed > 0
    status_word = f"ALL {executed} TESTS PASSING" if all_green else f"{failed} OF {executed} TESTS FAILING"
    status_class = "ok" if all_green else "bad"
    skip_note = f'<span class="chip">+{skipped} on-demand health checks</span>' if skipped else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PyQA Suite | Live Test Automation Dashboard | Nkululeko Mpofu</title>
<meta name="description" content="Live CI test results for PyQA Suite - a Python + Selenium WebDriver automation framework by Nkululeko Mpofu, QA Engineer. Updated automatically on every push.">
<meta property="og:title" content="PyQA Suite | Live Test Automation Dashboard">
<meta property="og:description" content="{executed} automated tests, {pass_pct}% passing. Python, Selenium WebDriver, pytest, Allure, GitHub Actions.">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>&#129514;</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
{SHARED_CSS}
  header {{ padding: 72px 0 0; }}
  h1 {{ font-size: clamp(38px, 5.5vw, 62px); font-weight: 800; letter-spacing: -0.025em; line-height: 1.06; }}
  h1 .grad {{
    background: linear-gradient(90deg, var(--accent), var(--accent-l), var(--violet));
    -webkit-background-clip: text; background-clip: text; color: transparent;
  }}
  .sub {{ color: var(--muted); margin-top: 18px; max-width: 680px; font-size: 17px; }}
  .sub a {{ color: var(--accent-l); text-decoration: none; border-bottom: 1px solid rgba(34,211,238,0.3); }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 22px; }}
  .chip {{
    font-family: var(--mono); font-size: 12px; color: var(--muted);
    border: 1px solid var(--border); border-radius: 999px; padding: 5px 14px;
    background: rgba(15,23,42,0.6);
  }}
  .status-row {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 26px; align-items: center; }}
  .status {{
    display: inline-flex; align-items: center; gap: 9px;
    font-family: var(--mono); font-size: 12px; letter-spacing: 0.14em; font-weight: 700;
    padding: 8px 18px; border-radius: 999px; border: 1px solid;
  }}
  .status.ok {{ color: var(--pass); border-color: rgba(52,211,153,0.4); background: rgba(52,211,153,0.08); }}
  .status.bad {{ color: var(--fail); border-color: rgba(248,113,113,0.4); background: rgba(248,113,113,0.08); }}
  .dot {{ width: 8px; height: 8px; border-radius: 50%; background: currentColor; animation: pulse 2s infinite; }}
  @keyframes pulse {{ 50% {{ opacity: 0.35; }} }}
  .run-chip {{
    font-family: var(--mono); font-size: 12px; color: var(--muted); text-decoration: none;
    border: 1px solid var(--border); border-radius: 999px; padding: 8px 16px; transition: border-color 0.2s, color 0.2s;
  }}
  .run-chip:hover {{ border-color: var(--border-h); color: var(--accent-l); }}
  .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; margin-top: 52px; }}
  .card {{
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-lg);
    padding: 30px; transition: border-color 0.25s, transform 0.25s;
    display: flex; flex-direction: column; justify-content: space-between; min-height: 190px;
  }}
  .card:hover {{ border-color: var(--border-h); transform: translateY(-3px); }}
  .card .label {{ font-family: var(--mono); font-size: 11px; letter-spacing: 0.22em; color: var(--muted); text-transform: uppercase; }}
  .card .value {{ font-size: 52px; font-weight: 800; letter-spacing: -0.02em; line-height: 1; }}
  .card .hint {{ color: var(--faint); font-size: 13px; }}
  .value.pass {{ color: var(--pass); }}
  .value.fail {{ color: {'var(--fail)' if failed else 'var(--text)'}; }}
  .ring-card {{ align-items: flex-start; gap: 16px; }}
  .ring {{
    width: 118px; height: 118px; border-radius: 50%;
    background: conic-gradient(var(--pass) {ring_deg}deg, var(--faint) {ring_deg}deg);
    display: flex; align-items: center; justify-content: center;
  }}
  .ring-inner {{
    width: 90px; height: 90px; border-radius: 50%; background: var(--card);
    display: flex; align-items: center; justify-content: center;
    font-size: 25px; font-weight: 800;
  }}
  .pipe-track {{
    display: flex; align-items: stretch; overflow-x: auto;
    border: 1px solid var(--border); border-radius: var(--radius-lg);
    background: var(--card); padding: 26px 12px;
  }}
  .pipe-step {{ flex: 1; min-width: 140px; text-align: center; position: relative; padding: 0 12px; }}
  .pipe-step:not(:last-child)::after {{
    content: '\\2192'; position: absolute; right: -8px; top: 8px;
    color: var(--faint); font-size: 16px;
  }}
  .pipe-num {{
    width: 36px; height: 36px; margin: 0 auto; border-radius: 50%;
    border: 1px solid var(--border-h); color: var(--accent-l);
    font-family: var(--mono); font-size: 13px; font-weight: 700;
    display: flex; align-items: center; justify-content: center; background: var(--accent-g);
  }}
  .pipe-title {{ font-weight: 600; font-size: 14.5px; margin-top: 10px; }}
  .pipe-desc {{ color: var(--muted); font-size: 12.5px; margin-top: 3px; }}
  .feat-row {{ display: grid; grid-template-columns: 44px 210px 1fr 70px; gap: 16px; align-items: center; padding: 13px 0; }}
  .feat-row + .feat-row {{ border-top: 1px solid var(--border); }}
  .feat-icon {{ font-size: 19px; text-align: center; }}
  .feat-name {{ font-weight: 600; font-size: 15.5px; }}
  .feat-bar {{ height: 9px; border-radius: 999px; background: rgba(51,65,85,0.5); overflow: hidden; }}
  .feat-fill {{ height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--accent), var(--accent-l)); }}
  .feat-fill.full {{ background: linear-gradient(90deg, var(--accent), var(--pass)); }}
  .feat-count {{ font-family: var(--mono); font-size: 13px; color: var(--muted); text-align: right; }}
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
  .env-row {{ display: flex; justify-content: space-between; gap: 14px; padding: 11px 0; border-bottom: 1px solid var(--border); font-size: 14px; }}
  .env-row:last-child {{ border-bottom: none; }}
  .env-key {{ color: var(--muted); font-family: var(--mono); font-size: 12.5px; letter-spacing: 0.04em; }}
  .env-val {{ text-align: right; font-weight: 500; }}
  .about-list {{ list-style: none; }}
  .about-list li {{ padding: 9px 0 9px 26px; position: relative; color: var(--muted); font-size: 14.5px; }}
  .about-list li::before {{ content: '\\2713'; position: absolute; left: 0; color: var(--pass); font-weight: 700; }}
  .about-list strong {{ color: var(--text); font-weight: 600; }}
  .cta-row {{ display: flex; flex-wrap: wrap; gap: 14px; margin-top: 52px; }}
  .btn {{
    display: inline-flex; align-items: center; gap: 10px;
    padding: 15px 28px; border-radius: var(--radius); font-weight: 700; font-size: 15px;
    text-decoration: none; transition: transform 0.2s, box-shadow 0.2s;
  }}
  .btn:hover {{ transform: translateY(-2px); }}
  .btn-primary {{ background: linear-gradient(90deg, var(--accent), var(--accent-l)); color: #04121a; box-shadow: 0 8px 28px rgba(6,182,212,0.25); }}
  .btn-ghost {{ border: 1px solid var(--border); color: var(--text); background: var(--accent-g); }}
  .btn-ghost:hover {{ border-color: var(--border-h); }}
  @media (max-width: 980px) {{ .grid {{ grid-template-columns: 1fr 1fr; }} .two-col {{ grid-template-columns: 1fr; }} }}
  @media (max-width: 560px) {{
    .grid {{ grid-template-columns: 1fr; }}
    .feat-row {{ grid-template-columns: 34px 1fr 64px; }}
    .feat-bar {{ grid-column: 1 / -1; }}
    header {{ padding-top: 48px; }}
  }}
</style>
</head>
<body>
<div class="glow"></div>
<div class="wrap">

  <nav>
    <a class="brand" href="./">&lt;/&gt; PyQA<span>Suite</span></a>
    <div class="nav-links">
      <a href="./" class="active">Dashboard</a>
      <a href="./graphs.html">Analytics</a>
      <a href="./report/" target="_blank" rel="noopener">Full report &#8599;</a>
      <a href="https://github.com/Nkuempoofu/pyqa-suite" target="_blank" rel="noopener">GitHub</a>
      <a href="https://nkululeko-portfolio.vercel.app" target="_blank" rel="noopener">Portfolio</a>
    </div>
  </nav>

  <header>
    <div class="kicker">Live CI &middot; Automated Test Report</div>
    <h1>Quality, proven<br>on <span class="grad">every push.</span></h1>
    <p class="sub">PyQA Suite is a Python + Selenium WebDriver automation framework built by
      <a href="https://nkululeko-portfolio.vercel.app" target="_blank" rel="noopener">Nkululeko Mpofu</a>. Every commit triggers
      the full suite on GitHub Actions - the numbers below are the latest live run, not a mock-up.</p>
    <div class="chips">
      <span class="chip">Python</span><span class="chip">Selenium WebDriver</span>
      <span class="chip">pytest</span><span class="chip">Page Object Model</span>
      <span class="chip">REST API Testing</span><span class="chip">Allure</span>
      <span class="chip">GitHub Actions</span>{skip_note}
    </div>
    <div class="status-row">
      <span class="status {status_class}"><span class="dot"></span>{status_word}</span>
      <a class="run-chip" href="{build_url}" target="_blank" rel="noopener">{run_chip} &middot; view build &#8599;</a>
      <span class="run-chip" style="pointer-events:none;">Duration &middot; {duration}</span>
    </div>
  </header>

  <div class="grid">
    <div class="card ring-card">
      <div class="label">Pass rate</div>
      <div class="ring"><div class="ring-inner">{pass_pct}%</div></div>
    </div>
    <div class="card"><div class="label">Test cases</div><div class="value">{executed}</div><div class="hint">UI + API, executed this run</div></div>
    <div class="card"><div class="label">Passed</div><div class="value pass">{passed}</div><div class="hint">verified this run</div></div>
    <div class="card"><div class="label">Failures</div><div class="value fail">{failed}</div><div class="hint">including broken</div></div>
  </div>

  <div class="section">
    <h2>The pipeline</h2>
    <div class="pipe-track">
      <div class="pipe-step"><div class="pipe-num">1</div><div class="pipe-title">Push</div><div class="pipe-desc">commit lands on main</div></div>
      <div class="pipe-step"><div class="pipe-num">2</div><div class="pipe-title">Build</div><div class="pipe-desc">Python + deps install</div></div>
      <div class="pipe-step"><div class="pipe-num">3</div><div class="pipe-title">Test</div><div class="pipe-desc">headless Chrome + API</div></div>
      <div class="pipe-step"><div class="pipe-num">4</div><div class="pipe-title">Report</div><div class="pipe-desc">Allure + screenshots</div></div>
      <div class="pipe-step"><div class="pipe-num">5</div><div class="pipe-title">Publish</div><div class="pipe-desc">this page updates</div></div>
    </div>
  </div>

  <div class="section">
    <h2>Coverage by feature</h2>
    <div class="panel">
{feature_rows}
    </div>
  </div>

  <div class="section">
    <h2>Run details</h2>
    <div class="two-col">
      <div class="panel">
{env_rows}
      </div>
      <div class="panel">
        <ul class="about-list">
          <li><strong>Page Object Model</strong> architecture - locators live in one place</li>
          <li><strong>Self-healing actions</strong> - every click and keystroke verifies its outcome</li>
          <li><strong>Screenshots on failure</strong> - attached automatically to the report</li>
          <li><strong>Smoke &amp; regression markers</strong> - fast checks or full depth on demand</li>
          <li><strong>API layer</strong> - GET/POST/PUT/DELETE with schema validation</li>
          <li><strong>Site health mode</strong> - point the suite at any URL from the Actions tab</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="cta-row">
    <a class="btn btn-primary" href="./graphs.html">Explore analytics &rarr;</a>
    <a class="btn btn-ghost" href="./report/" target="_blank" rel="noopener">Full Allure report &#8599;</a>
    <a class="btn btn-ghost" href="https://github.com/Nkuempoofu/pyqa-suite" target="_blank" rel="noopener">Source on GitHub</a>
  </div>

  <footer>
    <span>&copy; 2026 Nkululeko Mpofu &middot; QA Engineer</span>
    <span>Generated {generated} &middot; <a href="https://nkululeko-portfolio.vercel.app">nkululeko-portfolio.vercel.app</a></span>
  </footer>
</div>
</body>
</html>
"""
    out = Path(output_dir) / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"index.html written ({executed} executed, {pass_pct}% pass)")


GRAPHS_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Analytics | PyQA Suite | Nkululeko Mpofu</title>
<meta name="description" content="Test analytics for PyQA Suite - status, severity, durations, and execution waterfall.">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>&#129514;</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
%%SHARED_CSS%%
  header { padding: 56px 0 0; }
  h1 { font-size: clamp(30px, 4vw, 44px); font-weight: 800; letter-spacing: -0.02em; }
  .sub { color: var(--muted); margin-top: 12px; max-width: 640px; font-size: 16px; }
  .charts { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 44px; }
  .chart-panel {
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-lg);
    padding: 26px; transition: border-color 0.25s;
  }
  .chart-panel:hover { border-color: var(--border-h); }
  .chart-title { font-family: var(--mono); font-size: 11.5px; letter-spacing: 0.22em; color: var(--muted); text-transform: uppercase; margin-bottom: 4px; }
  .chart-sub { color: var(--faint); font-size: 13px; margin-bottom: 18px; }
  .chart-box { position: relative; height: 300px; }
  .chart-box.tall { height: 560px; }
  .full { grid-column: 1 / -1; }
  .legend { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 14px; }
  .legend span { display: inline-flex; align-items: center; gap: 7px; font-size: 12.5px; color: var(--muted); font-family: var(--mono); }
  .swatch { width: 11px; height: 11px; border-radius: 3px; }
  @media (max-width: 900px) { .charts { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<div class="glow"></div>
<div class="wrap">

  <nav>
    <a class="brand" href="./">&lt;/&gt; PyQA<span>Suite</span></a>
    <div class="nav-links">
      <a href="./">Dashboard</a>
      <a href="./graphs.html" class="active">Analytics</a>
      <a href="./report/" target="_blank" rel="noopener">Full report &#8599;</a>
      <a href="https://github.com/Nkuempoofu/pyqa-suite" target="_blank" rel="noopener">GitHub</a>
      <a href="https://nkululeko-portfolio.vercel.app" target="_blank" rel="noopener">Portfolio</a>
    </div>
  </nav>

  <header>
    <div class="kicker">Analytics &middot; Latest Run</div>
    <h1>The run, <span style="color: var(--accent-l);">visualised.</span></h1>
    <p class="sub">Status, severity, speed, and the execution waterfall of the latest CI run - generated from the raw Allure data.</p>
  </header>

  <div class="charts">
    <div class="chart-panel">
      <div class="chart-title">Result breakdown</div>
      <div class="chart-sub">Every test in the latest run by outcome</div>
      <div class="chart-box"><canvas id="statusChart"></canvas></div>
    </div>

    <div class="chart-panel">
      <div class="chart-title">Severity coverage</div>
      <div class="chart-sub">How critical the covered scenarios are</div>
      <div class="chart-box"><canvas id="severityChart"></canvas></div>
    </div>

    <div class="chart-panel full">
      <div class="chart-title">Slowest tests</div>
      <div class="chart-sub">Top 10 by execution time - automation candidates for optimisation</div>
      <div class="chart-box"><canvas id="slowChart"></canvas></div>
    </div>

    <div class="chart-panel full">
      <div class="chart-title">Execution waterfall</div>
      <div class="chart-sub">When each test started and finished, relative to the start of the run</div>
      <div class="legend">
        <span><span class="swatch" style="background:#34d399"></span>passed</span>
        <span><span class="swatch" style="background:#f87171"></span>failed / broken</span>
        <span><span class="swatch" style="background:#64748b"></span>skipped</span>
      </div>
      <div class="chart-box tall"><canvas id="waterfallChart"></canvas></div>
    </div>
  </div>

  <footer>
    <span>&copy; 2026 Nkululeko Mpofu &middot; QA Engineer</span>
    <span>Generated %%GENERATED%% &middot; <a href="https://nkululeko-portfolio.vercel.app">nkululeko-portfolio.vercel.app</a></span>
  </footer>
</div>

<script>
const DATA = %%DATA%%;

const css = getComputedStyle(document.documentElement);
const C = {
  text: '#f1f5f9', muted: '#94a3b8', faint: 'rgba(51,65,85,0.45)',
  cyan: '#06b6d4', cyanL: '#22d3ee', violet: '#8b5cf6',
  pass: '#34d399', fail: '#f87171', warn: '#fbbf24', skip: '#64748b',
};

Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 12.5;
Chart.defaults.color = C.muted;
Chart.defaults.borderColor = C.faint;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyle = 'rectRounded';
Chart.defaults.plugins.legend.labels.padding = 18;
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(2,6,23,0.92)';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(6,182,212,0.4)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.titleFont = { family: "'Space Mono', monospace", size: 12 };

// ── Result breakdown doughnut ──
const s = DATA.stats;
new Chart(document.getElementById('statusChart'), {
  type: 'doughnut',
  data: {
    labels: ['Passed', 'Failed', 'Broken', 'Skipped'],
    datasets: [{
      data: [s.passed, s.failed, s.broken, s.skipped],
      backgroundColor: [C.pass, C.fail, C.warn, C.skip],
      borderColor: '#0f172a', borderWidth: 4, hoverOffset: 10,
    }]
  },
  options: {
    maintainAspectRatio: false, cutout: '68%',
    plugins: { legend: { position: 'right' } }
  },
  plugins: [{
    id: 'centerText',
    afterDraw(chart) {
      const executed = s.passed + s.failed + s.broken;
      const pct = executed ? Math.round(s.passed / executed * 100) : 0;
      const { ctx, chartArea } = chart;
      const x = (chartArea.left + chartArea.right) / 2;
      const y = (chartArea.top + chartArea.bottom) / 2;
      ctx.save();
      ctx.textAlign = 'center';
      ctx.fillStyle = C.text;
      ctx.font = "800 30px 'Inter', sans-serif";
      ctx.fillText(pct + '%', x, y - 2);
      ctx.fillStyle = C.muted;
      ctx.font = "12px 'Space Mono', monospace";
      ctx.fillText('pass rate', x, y + 20);
      ctx.restore();
    }
  }]
});

// ── Severity polar chart ──
const sevOrder = ['blocker', 'critical', 'normal', 'minor', 'trivial'];
const sevColors = { blocker: C.fail, critical: C.warn, normal: C.cyan, minor: C.violet, trivial: C.skip };
const sevData = sevOrder.filter(k => DATA.severities[k]).map(k => ({ k, v: DATA.severities[k] }));
new Chart(document.getElementById('severityChart'), {
  type: 'polarArea',
  data: {
    labels: sevData.map(d => d.k),
    datasets: [{
      data: sevData.map(d => d.v),
      backgroundColor: sevData.map(d => sevColors[d.k] + 'CC'),
      borderColor: '#0f172a', borderWidth: 3,
    }]
  },
  options: {
    maintainAspectRatio: false,
    scales: { r: { grid: { color: C.faint }, ticks: { display: false } } },
    plugins: { legend: { position: 'right' } }
  }
});

// ── Slowest tests ──
const slow = [...DATA.tests].sort((a, b) => b.duration - a.duration).slice(0, 10).reverse();
new Chart(document.getElementById('slowChart'), {
  type: 'bar',
  data: {
    labels: slow.map(t => t.name.replace(/^test_/, '').replaceAll('_', ' ')),
    datasets: [{
      data: slow.map(t => +(t.duration / 1000).toFixed(1)),
      backgroundColor: slow.map((t, i) => i === slow.length - 1 ? C.cyanL : C.cyan + 'B3'),
      borderRadius: 6, barThickness: 18,
    }]
  },
  options: {
    indexAxis: 'y', maintainAspectRatio: false,
    scales: {
      x: { title: { display: true, text: 'seconds', color: C.muted }, grid: { color: C.faint } },
      y: { grid: { display: false } }
    },
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.x}s` } }
    }
  }
});

// ── Execution waterfall ──
const runnable = DATA.tests.filter(t => t.start && t.stop).sort((a, b) => a.start - b.start);
const t0 = runnable.length ? runnable[0].start : 0;
const statusColor = t => t.status === 'passed' ? C.pass : (t.status === 'skipped' ? C.skip : C.fail);
new Chart(document.getElementById('waterfallChart'), {
  type: 'bar',
  data: {
    labels: runnable.map(t => t.name.replace(/^test_/, '').replaceAll('_', ' ')),
    datasets: [{
      data: runnable.map(t => [(t.start - t0) / 1000, Math.max((t.stop - t0) / 1000, (t.start - t0) / 1000 + 0.3)]),
      backgroundColor: runnable.map(t => statusColor(t) + 'D9'),
      borderColor: runnable.map(statusColor),
      borderWidth: 1, borderRadius: 4, barThickness: 12, borderSkipped: false,
    }]
  },
  options: {
    indexAxis: 'y', maintainAspectRatio: false,
    scales: {
      x: { position: 'top', title: { display: true, text: 'seconds since run start', color: C.muted }, grid: { color: C.faint } },
      y: { grid: { display: false }, ticks: { autoSkip: false, font: { size: 11.5 } } }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => {
            const t = runnable[ctx.dataIndex];
            return ` ${t.status} · ${((t.stop - t.start) / 1000).toFixed(1)}s (${((t.start - t0) / 1000).toFixed(1)}s → ${((t.stop - t0) / 1000).toFixed(1)}s)`;
          }
        }
      }
    }
  }
});
</script>
</body>
</html>
"""


def build_graphs(report_dir, output_dir):
    summary = load_widget(report_dir, "summary.json") or {}
    stats = summary.get("statistic", {})
    tests = collect_tests(report_dir)

    severities = {}
    for t in tests:
        if t["status"] != "skipped":
            severities[t["severity"]] = severities.get(t["severity"], 0) + 1

    data = {
        "stats": {
            "passed": stats.get("passed", 0),
            "failed": stats.get("failed", 0),
            "broken": stats.get("broken", 0),
            "skipped": stats.get("skipped", 0),
        },
        "severities": severities,
        "tests": [
            {k: t[k] for k in ("name", "status", "start", "stop", "duration")}
            for t in tests if t["status"] != "skipped"
        ],
    }

    generated = datetime.now(timezone.utc).strftime("%d %b %Y &middot; %H:%M UTC")
    html = (
        GRAPHS_TEMPLATE
        .replace("%%SHARED_CSS%%", SHARED_CSS)
        .replace("%%DATA%%", json.dumps(data))
        .replace("%%GENERATED%%", generated)
    )
    out = Path(output_dir) / "graphs.html"
    out.write_text(html, encoding="utf-8")
    print(f"graphs.html written ({len(data['tests'])} tests charted)")


def main():
    report_dir = sys.argv[1] if len(sys.argv) > 1 else "allure-report/report"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "allure-report"
    build_index(report_dir, output_dir)
    build_graphs(report_dir, output_dir)


if __name__ == "__main__":
    main()
