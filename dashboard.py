import html
import re
import sys
from datetime import datetime

LOG_FILE = sys.argv[1] if len(sys.argv) > 1 else "health.log"
OUT_FILE = sys.argv[2] if len(sys.argv) > 2 else "status.html"
HISTORY = 30

CHECK_RE = re.compile(r"^(\S+ \S+) (UP|DOWN)\s+(\S+) -> HTTP (\d+)(?: in ([\d.]+)s)?")
SUMMARY_RE = re.compile(r"^(\S+ \S+) SUMMARY (healthy|UNHEALTHY) \((.*)\)")


def parse(path):
    checks, summaries = [], []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if m := CHECK_RE.match(line):
                    ts, status, url, code, secs = m.groups()
                    checks.append(
                        {
                            "ts": ts,
                            "status": status,
                            "url": url,
                            "code": code,
                            "ms": f"{float(secs) * 1000:.0f} ms" if secs else "-",
                        }
                    )
                elif m := SUMMARY_RE.match(line):
                    summaries.append(
                        {
                            "ts": m.group(1),
                            "ok": m.group(2) == "healthy",
                            "base": m.group(3),
                        }
                    )
    except FileNotFoundError:
        pass
    return checks, summaries


def badge(status):
    cls = "up" if status == "UP" else "down"
    return f'<span class="badge {cls}">{status}</span>'


def build(checks, summaries):
    if summaries:
        last = summaries[-1]
        overall_ok, base, last_ts = last["ok"], last["base"], last["ts"]
        uptime = 100 * sum(s["ok"] for s in summaries) / len(summaries)
    else:
        overall_ok, base, last_ts, uptime = None, "no data", "-", 0.0

    if overall_ok is None:
        headline, cls = "NO DATA", "nodata"
    elif overall_ok:
        headline, cls = "ALL SYSTEMS OPERATIONAL", "up"
    else:
        headline, cls = "SERVICE DOWN", "down"

    latest = {}
    for c in checks:
        path = "/" + c["url"].split("/", 3)[-1] if c["url"].count("/") >= 3 else "/"
        latest[path] = c

    endpoint_rows = (
        "".join(
            f"<tr><td><code>{html.escape(p)}</code></td><td>{badge(c['status'])}</td>"
            f"<td>{c['code']}</td><td>{c['ms']}</td><td>{c['ts']}</td></tr>"
            for p, c in sorted(latest.items())
        )
        or '<tr><td colspan="5">No checks recorded yet.</td></tr>'
    )

    history_rows = (
        "".join(
            f"<tr><td>{c['ts']}</td><td><code>{html.escape(c['url'])}</code></td>"
            f"<td>{badge(c['status'])}</td><td>{c['code']}</td><td>{c['ms']}</td></tr>"
            for c in reversed(checks[-HISTORY:])
        )
        or '<tr><td colspan="5">No checks recorded yet.</td></tr>'
    )

    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Status Dashboard</title>
<style>
  :root {{ --bg:#f6f7f9; --card:#fff; --text:#1c2128; --muted:#656d76; --line:#d8dee4;
          --up:#1a7f37; --up-bg:#dafbe1; --down:#cf222e; --down-bg:#ffebe9; --nodata:#656d76; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#0d1117; --card:#161b22; --text:#e6edf3; --muted:#8b949e; --line:#30363d;
            --up:#3fb950; --up-bg:#12261a; --down:#f85149; --down-bg:#2d1315; --nodata:#8b949e; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; padding:24px 16px; background:var(--bg); color:var(--text);
         font:15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width:860px; margin:0 auto; }}
  h1 {{ font-size:20px; margin:0 0 16px; }}
  h2 {{ font-size:15px; margin:28px 0 8px; color:var(--muted); font-weight:600; }}
  .hero {{ border:1px solid var(--line); border-left:6px solid var(--{cls}); background:var(--card);
          border-radius:8px; padding:18px 20px; }}
  .hero .state {{ font-size:22px; font-weight:700; color:var(--{cls}); }}
  .hero .meta {{ color:var(--muted); margin-top:4px; word-break:break-all; }}
  .stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin-top:12px; }}
  .stat {{ background:var(--card); border:1px solid var(--line); border-radius:8px; padding:12px 16px; }}
  .stat b {{ display:block; font-size:20px; }}
  .stat span {{ color:var(--muted); font-size:13px; }}
  .wrap {{ overflow-x:auto; background:var(--card); border:1px solid var(--line); border-radius:8px; }}
  table {{ width:100%; border-collapse:collapse; }}
  th, td {{ text-align:left; padding:8px 14px; border-bottom:1px solid var(--line); white-space:nowrap; }}
  th {{ color:var(--muted); font-weight:600; font-size:13px; }}
  tr:last-child td {{ border-bottom:0; }}
  .badge {{ padding:2px 8px; border-radius:10px; font-size:12px; font-weight:700; }}
  .badge.up {{ color:var(--up); background:var(--up-bg); }}
  .badge.down {{ color:var(--down); background:var(--down-bg); }}
  footer {{ color:var(--muted); font-size:12px; margin-top:20px; }}
</style>
</head>
<body>
<main>
  <h1>Status Dashboard</h1>
  <section class="hero">
    <div class="state">{headline}</div>
    <div class="meta">{html.escape(base)} &middot; last check {last_ts}</div>
  </section>
  <section class="stats">
    <div class="stat"><b>{uptime:.0f}%</b><span>healthy runs</span></div>
    <div class="stat"><b>{len(summaries)}</b><span>runs recorded</span></div>
    <div class="stat"><b>{sum(1 for s in summaries if not s["ok"])}</b><span>failed runs</span></div>
  </section>

  <h2>Endpoints (latest result)</h2>
  <div class="wrap"><table>
    <tr><th>Endpoint</th><th>Status</th><th>HTTP</th><th>Response time</th><th>Checked at</th></tr>
    {endpoint_rows}
  </table></div>

  <h2>Recent checks</h2>
  <div class="wrap"><table>
    <tr><th>Time</th><th>URL</th><th>Status</th><th>HTTP</th><th>Response time</th></tr>
    {history_rows}
  </table></div>

  <footer>Generated {generated} from {html.escape(LOG_FILE)}</footer>
</main>
</body>
</html>
"""


def main():
    checks, summaries = parse(LOG_FILE)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(build(checks, summaries))
    print(f"Wrote {OUT_FILE} ({len(checks)} checks, {len(summaries)} runs)")


if __name__ == "__main__":
    main()
