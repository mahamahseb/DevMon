INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f7f7f8;
      color: #171717;
    }}
    body {{
      margin: 0;
      padding: 32px;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
    }}
    h1 {{
      color: #dc2626;
      margin: 0;
      font-size: 34px;
      letter-spacing: 0;
    }}
    .meta {{
      margin: 6px 0 24px;
      color: #525252;
      font-size: 14px;
    }}
    .tabs, .toolbar {{
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }}
    .tab, button, select {{
      border: 1px solid #d4d4d4;
      background: #fff;
      color: #171717;
      min-height: 38px;
      border-radius: 8px;
      padding: 0 14px;
      font: inherit;
    }}
    .tab.active {{
      border-color: #dc2626;
      color: #dc2626;
      font-weight: 700;
    }}
    button {{
      cursor: pointer;
      display: inline-flex;
      gap: 8px;
      align-items: center;
    }}
    .spinner {{
      width: 14px;
      height: 14px;
      border: 2px solid #fecaca;
      border-top-color: #dc2626;
      border-radius: 999px;
      animation: spin .8s linear infinite;
      display: none;
    }}
    button.loading .spinner {{
      display: inline-block;
    }}
    @keyframes spin {{
      to {{ transform: rotate(360deg); }}
    }}
    section {{
      margin-top: 18px;
      background: #fff;
      border: 1px solid #e5e5e5;
      border-radius: 8px;
      padding: 18px;
    }}
    pre {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      background: #111827;
      color: #f9fafb;
      border-radius: 8px;
      padding: 16px;
      line-height: 1.45;
      min-height: 360px;
    }}
    .fold {{
      margin-top: 14px;
    }}
    summary {{
      cursor: pointer;
      font-weight: 700;
    }}
    @media (max-width: 640px) {{
      body {{ padding: 18px; }}
      h1 {{ font-size: 28px; }}
      section {{ padding: 14px; }}
    }}
  </style>
</head>
<body>
  <main>
    <h1>{title}</h1>
    <div class="meta">Branch: {branch} | Version: {version}</div>
    <div class="tabs" role="tablist">
      <button class="tab active" data-tab="traffic-flow">Traffic Flow</button>
      <button class="tab" data-tab="deploy-flow">Deploy Flow</button>
    </div>
    <section>
      <div class="toolbar">
        <label>
          Server
          <select id="server">
            <option value="lab1">lab1</option>
          </select>
        </label>
        <button id="refresh" type="button"><span class="spinner"></span><span>Refresh</span></button>
      </div>
      <details class="fold" open>
        <summary>Result</summary>
        <pre id="result">Click Refresh to collect read-only state from lab1.</pre>
      </details>
    </section>
  </main>
  <script>
    const result = document.querySelector("#result");
    const refresh = document.querySelector("#refresh");
    let activeTab = "traffic-flow";

    document.querySelectorAll(".tab").forEach((tab) => {{
      tab.addEventListener("click", () => {{
        document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
        tab.classList.add("active");
        activeTab = tab.dataset.tab;
        result.textContent = "Click Refresh to collect read-only state from lab1.";
      }});
    }});

    refresh.addEventListener("click", async () => {{
      const target = document.querySelector("#server").value;
      refresh.classList.add("loading");
      refresh.disabled = true;
      result.textContent = "Collecting...";
      try {{
        const response = await fetch(`/api/${{activeTab}}?target=${{encodeURIComponent(target)}}`);
        const payload = await response.json();
        if (!response.ok || !payload.ok) {{
          throw new Error(payload.error || "Request failed");
        }}
        result.textContent = payload.result.flow;
      }} catch (error) {{
        result.textContent = `Error: ${{error.message}}`;
      }} finally {{
        refresh.classList.remove("loading");
        refresh.disabled = false;
      }}
    }});
  </script>
</body>
</html>
"""
