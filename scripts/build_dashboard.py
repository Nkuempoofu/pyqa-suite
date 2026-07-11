"""Build the branded PyQA Suite dashboard from Allure report data.

Reads the widget JSON files produced by `allure generate` and writes a
standalone index.html styled to match nkululeko-portfolio.vercel.app.

Usage: python scripts/build_dashboard.py <allure_report_dir> <output_dir>
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_widget(report_dir, name):
    path = Path(report_dir) / "widgets" / name
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def fmt_duration(ms):
    if ms is None:
        return "-"
    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.0f}s"
    return f"{int(seconds // 60)}m {int(seconds % 60)}s"


FEATURE_ICONS = {
    "REST API": "&#9741;",
    "Checkout": "&#128179;",
    "Authentication": "&#128273;",
    "Product Catalogue": "&#128722;",
    "Shopping Cart": "&#128717;",
}


def main():
    report_dir = sys.argv[1] if len(sys.argv) > 1 else "allure-report/report"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "allure-report"

    summary = load_widget(report_dir, "summary.json") or {}
    stats = summary.get("statistic", {})
    time_info = summary.get("time", {})

    total = stats.get("total", 0)
    passed = stats.get("passed", 0)
    failed = stats.get("failed", 0) + stats.get("broken", 0)
    pass_pct = round(passed / total * 100) if total else 0
    duration = fmt_duration(time_info.get("duration"))

    behaviors = load_widget(report_dir, "behaviors.json") or {}
    features = []
    for item in behaviors.get("items", []):
        f_stats = item.get("statistic", {})
        f_total = f_stats.get("total", 0)
        f_passed = f_stats.get("passed", 0)
        features.append({
            "name": item.get("name", "?"),
            "total": f_total,
            "passed": f_passed,
            "pct": round(f_passed / f_total * 100) if f_total else 0,
        })
    features.sort(key=lambda f: -f["total"])

    env_items = load_widget(report_dir, "environment.json") or []
    environment = []
    for item in env_items:
        values = item.get("values", [])
        key = item.get("name", "?").replace(".", " ")
        environment.append((key, ", ".join(values)))

    executors = load_widget(report_dir, "executors.json") or []
    run_number = None
    build_url = "https://github.com/Nkuempoofu/pyqa-suite/actions"
    if executors:
        run_number = executors[0].get("buildOrder")
        build_url = executors[0].get("buildUrl", build_url)

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
    all_green = failed == 0 and total > 0
    status_word = f"ALL {total} TESTS PASSING" if all_green else f"{failed} OF {total} TESTS FAILING"
    status_class = "ok" if all_green else "bad"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PyQA Suite | Live Test Automation Dashboard | Nkululeko Mpofu</title>
<meta name="description" content="Live CI test results for PyQA Suite - a Python + Selenium WebDriver automation framework by Nkululeko Mpofu, QA Engineer. Updated automatically on every push.">
<meta property="og:title" content="PyQA Suite | Live Test Automation Dashboard">
<meta property="og:description" content="{total} automated tests, {pass_pct}% passing. Python, Selenium WebDriver, pytest, Allure, GitHub Actions.">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>&#129514;</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg: #020617; --surface: #0a0f1e; --card: #0f172a; --card-hover: #131d35;
    --border: rgba(30,41,59,0.7); --border-h: rgba(6,182,212,0.45);
    --accent: #06b6d4; --accent-l: #22d3ee; --accent-g: rgba(6,182,212,0.10);
    --violet: #8b5cf6; --text: #f1f5f9; --muted: #94a3b8; --faint: #334155;
    --radius: 12px; --radius-lg: 20px;
    --mono: 'Space Mono', monospace; --sans: 'Inter', sans-serif;
    --pass: #34d399; --fail: #f87171;
  }}
  html {{ scroll-behavior: smooth; }}
  body {{
    background: linear-gradient(145deg, #020617 0%, #0a0f1e 40%, #0f172a 100%);
    background-attachment: fixed;
    color: var(--text); font-family: var(--sans); line-height: 1.6; min-height: 100vh;
  }}
  .glow {{
    position: fixed; top: -220px; left: 50%; transform: translateX(-50%);
    width: 780px; height: 460px; border-radius: 50%; pointer-events: none;
    background: radial-gradient(ellipse, rgba(6,182,212,0.13) 0%, transparent 65%);
  }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px 72px; position: relative; }}

  nav {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 26px 0 0;
  }}
  .brand {{ font-family: var(--mono); font-weight: 700; font-size: 16px; color: var(--text); text-decoration: none; }}
  .brand span {{ color: var(--accent-l); }}
  .nav-links {{ display: flex; gap: 22px; align-items: center; }}
  .nav-links a {{ color: var(--muted); text-decoration: none; font-size: 14px; transition: color 0.2s; }}
  .nav-links a:hover {{ color: var(--accent-l); }}

  header {{ padding: 72px 0 0; }}
  .kicker {{
    font-family: var(--mono); font-size: 12.5px; letter-spacing: 0.28em;
    color: var(--accent-l); text-transform: uppercase; margin-bottom: 16px;
    display: flex; align-items: center; gap: 12px;
  }}
  .kicker::before {{ content: ''; width: 34px; height: 1px; background: var(--accent); }}
  h1 {{ font-size: clamp(36px, 5.5vw, 58px); font-weight: 800; letter-spacing: -0.025em; line-height: 1.06; }}
  h1 .grad {{
    background: linear-gradient(90deg, var(--accent), var(--accent-l), var(--violet));
    -webkit-background-clip: text; background-clip: text; color: transparent;
  }}
  .sub {{ color: var(--muted); margin-top: 18px; max-width: 640px; font-size: 16.5px; }}
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

  .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 52px; }}
  .card {{
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-lg);
    padding: 26px; transition: border-color 0.25s, transform 0.25s;
  }}
  .card:hover {{ border-color: var(--border-h); transform: translateY(-3px); }}
  .card .label {{ font-family: var(--mono); font-size: 11px; letter-spacing: 0.22em; color: var(--muted); text-transform: uppercase; }}
  .card .value {{ font-size: 44px; font-weight: 800; margin-top: 10px; letter-spacing: -0.02em; line-height: 1; }}
  .card .hint {{ color: var(--faint); font-size: 13px; margin-top: 8px; }}
  .value.pass {{ color: var(--pass); }}
  .value.fail {{ color: {'var(--fail)' if failed else 'var(--text)'}; }}

  .ring-card {{ grid-column: span 1; display: flex; flex-direction: column; align-items: flex-start; gap: 18px; }}
  .ring {{
    width: 116px; height: 116px; border-radius: 50%;
    background: conic-gradient(var(--pass) {ring_deg}deg, var(--faint) {ring_deg}deg);
    display: flex; align-items: center; justify-content: center;
  }}
  .ring-inner {{
    width: 88px; height: 88px; border-radius: 50%; background: var(--card);
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; font-weight: 800;
  }}

  .pipeline {{ margin-top: 56px; }}
  .pipe-track {{
    display: flex; align-items: stretch; gap: 0; overflow-x: auto;
    border: 1px solid var(--border); border-radius: var(--radius-lg);
    background: var(--card); padding: 22px 10px;
  }}
  .pipe-step {{ flex: 1; min-width: 130px; text-align: center; position: relative; padding: 0 10px; }}
  .pipe-step:not(:last-child)::after {{
    content: '\\2192'; position: absolute; right: -8px; top: 8px;
    color: var(--faint); font-size: 16px;
  }}
  .pipe-num {{
    width: 34px; height: 34px; margin: 0 auto; border-radius: 50%;
    border: 1px solid var(--border-h); color: var(--accent-l);
    font-family: var(--mono); font-size: 13px; font-weight: 700;
    display: flex; align-items: center; justify-content: center; background: var(--accent-g);
  }}
  .pipe-title {{ font-weight: 600; font-size: 14px; margin-top: 10px; }}
  .pipe-desc {{ color: var(--muted); font-size: 12.5px; margin-top: 3px; }}

  .section {{ margin-top: 56px; }}
  .section h2 {{
    font-family: var(--mono); font-size: 12.5px; letter-spacing: 0.28em;
    color: var(--accent-l); text-transform: uppercase; margin-bottom: 20px;
    display: flex; align-items: center; gap: 12px;
  }}
  .section h2::before {{ content: ''; width: 34px; height: 1px; background: var(--accent); }}
  .panel {{ background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 30px; }}

  .feat-row {{ display: grid; grid-template-columns: 40px 190px 1fr 64px; gap: 14px; align-items: center; padding: 12px 0; }}
  .feat-row + .feat-row {{ border-top: 1px solid var(--border); }}
  .feat-icon {{ font-size: 18px; text-align: center; }}
  .feat-name {{ font-weight: 600; font-size: 15px; }}
  .feat-bar {{ height: 9px; border-radius: 999px; background: rgba(51,65,85,0.5); overflow: hidden; }}
  .feat-fill {{ height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--accent), var(--accent-l)); }}
  .feat-fill.full {{ background: linear-gradient(90deg, var(--accent), var(--pass)); }}
  .feat-count {{ font-family: var(--mono); font-size: 13px; color: var(--muted); text-align: right; }}

  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .env-row {{ display: flex; justify-content: space-between; gap: 14px; padding: 10px 0; border-bottom: 1px solid var(--border); font-size: 14px; }}
  .env-row:last-child {{ border-bottom: none; }}
  .env-key {{ color: var(--muted); font-family: var(--mono); font-size: 12.5px; letter-spacing: 0.04em; }}
  .env-val {{ text-align: right; font-weight: 500; }}

  .about-list {{ list-style: none; }}
  .about-list li {{ padding: 8px 0 8px 26px; position: relative; color: var(--muted); font-size: 14.5px; }}
  .about-list li::before {{ content: '\\2713'; position: absolute; left: 0; color: var(--pass); font-weight: 700; }}
  .about-list strong {{ color: var(--text); font-weight: 600; }}

  .cta-row {{ display: flex; flex-wrap: wrap; gap: 14px; margin-top: 52px; }}
  .btn {{
    display: inline-flex; align-items: center; gap: 10px;
    padding: 15px 28px; border-radius: var(--radius); font-weight: 700; font-size: 15px;
    text-decoration: none; transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
  }}
  .btn:hover {{ transform: translateY(-2px); }}
  .btn-primary {{ background: linear-gradient(90deg, var(--accent), var(--accent-l)); color: #04121a; box-shadow: 0 8px 28px rgba(6,182,212,0.25); }}
  .btn-ghost {{ border: 1px solid var(--border); color: var(--text); background: var(--accent-g); }}
  .btn-ghost:hover {{ border-color: var(--border-h); }}

  footer {{
    margin-top: 72px; padding-top: 26px; border-top: 1px solid var(--border);
    display: flex; flex-wrap: wrap; gap: 10px; justify-content: space-between;
    color: var(--faint); font-family: var(--mono); font-size: 12px; letter-spacing: 0.06em;
  }}
  footer a {{ color: var(--muted); text-decoration: none; }}
  footer a:hover {{ color: var(--accent-l); }}

  @media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr 1fr; }} .two-col {{ grid-template-columns: 1fr; }} }}
  @media (max-width: 560px) {{
    .grid {{ grid-template-columns: 1fr; }}
    .feat-row {{ grid-template-columns: 30px 1fr 60px; }}
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
      <a href="./report/">Full report</a>
      <a href="https://github.com/Nkuempoofu/pyqa-suite">GitHub</a>
      <a href="https://nkululeko-portfolio.vercel.app">Portfolio</a>
    </div>
  </nav>

  <header>
    <div class="kicker">Live CI &middot; Automated Test Report</div>
    <h1>Quality, proven<br>on <span class="grad">every push.</span></h1>
    <p class="sub">PyQA Suite is a Python + Selenium WebDriver automation framework built by
      <a href="https://nkululeko-portfolio.vercel.app">Nkululeko Mpofu</a>. Every commit triggers
      the full suite on GitHub Actions - the numbers below are the latest live run, not a mock-up.</p>
    <div class="chips">
      <span class="chip">Python</span><span class="chip">Selenium WebDriver</span>
      <span class="chip">pytest</span><span class="chip">Page Object Model</span>
      <span class="chip">REST API Testing</span><span class="chip">Allure</span>
      <span class="chip">GitHub Actions</span>
    </div>
    <div class="status-row">
      <span class="status {status_class}"><span class="dot"></span>{status_word}</span>
      <a class="run-chip" href="{build_url}">{run_chip} &middot; view build &#8599;</a>
    </div>
  </header>

  <div class="grid">
    <div class="card ring-card">
      <div class="label">Pass rate</div>
      <div class="ring"><div class="ring-inner">{pass_pct}%</div></div>
    </div>
    <div class="card"><div class="label">Test cases</div><div class="value">{total}</div><div class="hint">UI + API combined</div></div>
    <div class="card"><div class="label">Passed</div><div class="value pass">{passed}</div><div class="hint">verified this run</div></div>
    <div class="card"><div class="label">Failures</div><div class="value fail">{failed}</div><div class="hint">including broken</div></div>
  </div>

  <div class="pipeline">
    <div class="section" style="margin-top:0;"><h2>The pipeline</h2></div>
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
        </ul>
      </div>
    </div>
  </div>

  <div class="cta-row">
    <a class="btn btn-primary" href="./report/">Open full Allure report &rarr;</a>
    <a class="btn btn-ghost" href="https://github.com/Nkuempoofu/pyqa-suite">View source on GitHub</a>
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
    print(f"Dashboard written to {out} ({total} tests, {pass_pct}% pass)")


if __name__ == "__main__":
    main()
