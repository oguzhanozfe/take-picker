/* Standalone browser view for the computed project report. */
window.drawProjectView = function (host, report, input) {
  "use strict";
  function el(tag, text, css) {
    const item = document.createElement(tag);
    if (text != null) item.textContent = String(text);
    if (css) item.style.cssText = css;
    return item;
  }
  const figure = el("figure", null, "box-sizing:border-box;margin:12px 0 16px;padding:12px 14px;border-radius:9px;background:#172329;color:#f4f5f2;max-height:210px;overflow:auto;font:13px/1.35 system-ui,sans-serif;text-align:left");
  const head = el("figcaption", "Take comparison · script coverage and edit score", "font-size:15px;font-weight:700;letter-spacing:-.015em;color:#f5d48c;margin-bottom:7px");
  figure.append(head);
  host.replaceChildren(figure);
  const rows = Array.isArray(report && report.rows) ? report.rows : [];
  if (!rows.length) {
    figure.append(el("p", "No findings to display.", "margin:0"));
    return;
  }

  figure.append(el("div","Teal bar = script covered (%) · gold diamond = edit score /100 · right = duration", "font-size:11px;color:#d5e0de;margin-bottom:6px"));
  for (const row of rows.slice(0,5)) {
    const lane = el("div", null, "display:grid;grid-template-columns:minmax(60px,20%) minmax(0,1fr) 66px;gap:8px;align-items:center;margin:5px 0");
    const tag = el("span",row.Take,"font:650 12px/1.2 ui-monospace,monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap");
    tag.title = row.Take+" · "+row["Logged defects"];
    const rail = el("div", null,"height:12px;position:relative;background:#34434a;border-radius:2px");
    const covered=Number(row["Script covered (%)"]),score=Number(row.Score);
    rail.append(el("span",null,"position:absolute;left:0;top:4px;height:4px;border-radius:2px;background:#80d1be;width:"+Math.min(100,Math.max(0,covered))+"%"),
      el("span",null,"position:absolute;top:2px;height:8px;width:8px;background:#f5d48c;transform:rotate(45deg);left:clamp(0px,calc("+Math.min(100,Math.max(0,score))+"% - 4px),calc(100% - 8px))"));
    rail.setAttribute("aria-label",row.Take+": "+covered+" percent of script, "+score+" points, "+row["Logged defects"]+".");
    lane.append(tag,rail,el("span",row["Duration (s)"]+" s","font:11px ui-monospace,monospace;text-align:right"));
    figure.append(lane);
  }
  figure.append(el("div","Target "+report.metrics["Target (s)"]+" s · "+report.metrics.Eligible+" eligible · first "+Math.min(5,rows.length)+" ranked takes","font-size:10px;color:#c5d2d0"));

};
