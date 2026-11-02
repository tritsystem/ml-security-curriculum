"""Build a single self-contained interactive HTML study app from the course + both library volumes.
No network or server needed at runtime; state is kept in the browser's localStorage (exportable)."""
import html, json, re, pathlib
import markdown

DRIVE = pathlib.Path(__file__).resolve().parent.parent
COURSE = (DRIVE / "ML_Security_8h_Power_Course.md").read_text(encoding="utf-8")
VOL1 = (DRIVE / "ML_Security_Reading_Curriculum_1000h.md").read_text(encoding="utf-8")
VOL2 = (DRIVE / "ML_Security_Reading_Curriculum_Vol2.md").read_text(encoding="utf-8")
OUT = DRIVE / "ML_Security_Course_App.html"

def _indent4(s):
    # Python-Markdown nests lists only at 4-space indents; the course uses 2, so double leading spaces.
    return "\n".join(re.sub(r"^( +)", lambda m: " " * (len(m.group(1)) * 2), ln) for ln in s.split("\n"))

md = lambda s: markdown.markdown(_indent4(s), extensions=["tables", "fenced_code"])

def fix_links(h):
    return re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', h)

# ---------- course ----------
body, _, answers_md = COURSE.partition("\n## Answer key")
answers = {int(n): a.strip() for n, a in re.findall(r"^(\d+)\.\s+(.+?)(?=^\d+\.\s|\Z|^---)", answers_md, re.S | re.M)}
mod_chunks = re.split(r"\n## Module (\d+): ", body)
modules = []
for i in range(1, len(mod_chunks), 2):
    num = int(mod_chunks[i]); chunk = mod_chunks[i + 1].rstrip().rstrip("-").rstrip()
    title, _, rest = chunk.partition("\n")
    title = re.sub(r"\s*\(\d+ min\)\s*$", "", title.strip())
    parts = re.split(r"\n\*\*(Learn|Read|Do|Check)(?: \((\d+) min\))?\*\*\n", "\n" + rest)
    sections = []
    for j in range(1, len(parts), 3):
        name, mins, content = parts[j], parts[j + 1], parts[j + 2].strip()
        if name == "Check":
            qs = [(int(n), q.strip()) for n, q in re.findall(r"^(\d+)\.\s+(.+)$", content, re.M)]
            sections.append({"name": name, "mins": None, "questions": [{"n": n, "q": q, "a": answers.get(n, "")} for n, q in qs]})
        else:
            sections.append({"name": name, "mins": int(mins) if mins else None, "html": fix_links(md(content))})
    modules.append({"num": num, "title": title, "sections": sections})
assert len(modules) == 8, len(modules)
assert sum(len(s["questions"]) for m in modules for s in m["sections"] if s["name"] == "Check") == 16

# ---------- library ----------
link_re = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
def parse_volume(text, vol):
    items = []
    part = None
    for line in text.splitlines():
        m = re.match(r"^## ([A-Z])\. (.+)$", line)
        if m:
            part = f"{m.group(1)}. {m.group(2)}"; continue
        if not part or not line.startswith("|") or line.startswith("|---") or line.startswith("| ID"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        groups = []
        if len(cells) == 6 and re.match(r"^[A-Z]\d+$", cells[0]) and re.match(r"^[A-Z]\d+$", cells[3]):
            groups = [cells[0:3] + [""], cells[3:6] + [""]]
        elif len(cells) >= 3 and re.match(r"^[A-Z]\d+$", cells[0]):
            groups = [cells[:3] + [cells[3] if len(cells) > 3 else ""]]
        for g in groups:
            iid, res, hrs, why = g
            links = link_re.findall(res)
            if not links:
                continue
            title = re.sub(r"\s*ⓑ", "", link_re.sub(lambda mm: mm.group(1), res)).strip()
            items.append({"id": iid, "vol": vol, "part": part, "title": title,
                          "links": [{"t": t, "u": u} for t, u in links], "bot": "ⓑ" in res,
                          "hours": int(hrs.replace(",", "")) if hrs.replace(",", "").isdigit() else 0, "why": why})
    return items
library = parse_volume(VOL1, "I") + parse_volume(VOL2, "II")
ids = [x["id"] for x in library]
assert len(ids) == len(set(ids)), "duplicate ids"


# ---------- static (no-JavaScript) rendering, for viewers like Google Drive's preview ----------
def _inl(t):
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    return re.sub(r"\*([^*]+)\*", r"<i>\1</i>", t)

def static_course():
    out = ['<p class="nojs-note card">You are viewing the <b>read-only version</b>: this viewer does not run the '
           'interactive features. Everything below is readable; tap <b>Reveal answer</b> to see answers. For ticks, '
           'timers, flashcards and saved progress, open the file in Chrome (in Google Drive: ⋮ → Download, then open '
           'it from the Files app with Chrome).</p>']
    for m in modules:
        out.append(f'<div class="card"><div class="modhead"><span class="pill st">M{m["num"]}</span><h2>{html.escape(m["title"])}</h2></div><div class="modbody">')
        for sct in m["sections"]:
            mins = f' <span class="pill">{sct["mins"]} min</span>' if sct.get("mins") else ""
            if sct["name"] != "Check":
                out.append(f'<div class="sec"><h3>{sct["name"]}{mins}</h3>{sct["html"]}</div>')
            else:
                qs = "".join(f'<div class="q"><b>{q["n"]}.</b> {_inl(q["q"])}<details><summary>Reveal answer</summary>'
                             f'<div class="ans-static">{_inl(q["a"])}</div></details></div>' for q in sct["questions"])
                out.append(f'<div class="sec"><h3>Check</h3>{qs}</div>')
        out.append("</div></div>")
    return "\n".join(out)

def static_library():
    out, part = [], None
    for x in library:
        p = f"Vol {x['vol']} · {x['part']}"
        if p != part:
            if part: out.append("</div>")
            out.append(f'<h3 class="libpart">{html.escape(p)}</h3><div class="card">'); part = p
        links = " · ".join(f'<a href="{l["u"]}" target="_blank" rel="noopener">{html.escape(l["t"])}</a>' for l in x["links"])
        out.append(f'<div class="lib-row"><div><div class="t"><b>{x["id"]}</b> {links}{" ⓑ" if x["bot"] else ""}</div>'
                   f'<div class="meta">~{x["hours"]} h{(" · " + _inl(x["why"])) if x["why"] else ""}</div></div></div>')
    out.append("</div>")
    return "\n".join(out)

DATA = {"modules": modules, "library": library, "built": "2026-10-30"}

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ML Systems Security: 8-hour course + library</title>
<style>
:root{--bg:#fbfaf7;--fg:#1d1d1f;--mut:#6b6b70;--card:#fff;--line:#e4e2dc;--acc:#2f5bd3;--ok:#1f8a4c;--warn:#b5651d;--chip:#f0eee8}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--fg:#ececf0;--mut:#9a9aa3;--card:#1d1d21;--line:#2e2e34;--acc:#7da2ff;--ok:#4cc27e;--warn:#e0a060;--chip:#26262b}}
*{box-sizing:border-box}body{margin:0;font:16px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--fg)}
header{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px}
h1{font-size:18px;margin:0 0 6px}nav{display:flex;gap:6px;flex-wrap:wrap}
nav a,.btn{text-decoration:none;display:inline-block;border:1px solid var(--line);background:var(--card);color:var(--fg);padding:6px 12px;border-radius:999px;cursor:pointer;font:inherit;font-size:14px}
nav a.on{background:var(--acc);color:#fff;border-color:var(--acc)}
.btn.ok{border-color:var(--ok);color:var(--ok)}.btn.warn{border-color:var(--warn);color:var(--warn)}.btn.pri{background:var(--acc);border-color:var(--acc);color:#fff}
main{max-width:920px;margin:0 auto;padding:16px}
.bar{height:8px;background:var(--chip);border-radius:6px;overflow:hidden}.bar>i{display:block;height:100%;background:var(--ok);width:0}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:12px 0}
.modhead{display:flex;align-items:center;gap:10px;cursor:pointer}.modhead h2{font-size:17px;margin:0;flex:1}
.pill{font-size:12px;background:var(--chip);border-radius:999px;padding:2px 8px;color:var(--mut)}
.done .pill.st{background:var(--ok);color:#fff}
.sec{border-top:1px dashed var(--line);margin-top:12px;padding-top:10px}
.sec h3{font-size:15px;margin:0 0 6px;display:flex;align-items:center;gap:8px}
.sec h3 label{font-weight:400;font-size:13px;color:var(--mut);margin-left:auto;cursor:pointer}
table{border-collapse:collapse;width:100%;font-size:14px;margin:8px 0}td,th{border:1px solid var(--line);padding:5px 7px;text-align:left;vertical-align:top}
code{background:var(--chip);padding:1px 4px;border-radius:4px;font-size:.92em}a{color:var(--acc)}
.q{background:var(--chip);border-radius:8px;padding:8px 10px;margin:8px 0}.a{display:none;margin-top:6px;border-left:3px solid var(--acc);padding-left:8px}
.q.show .a{display:block}.qbtns{display:flex;gap:6px;margin-top:6px;flex-wrap:wrap}
textarea{width:100%;min-height:90px;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:8px;font:inherit;font-size:14px}
.timer{font-variant-numeric:tabular-nums;font-size:14px;display:flex;gap:6px;align-items:center}
.flash{min-height:180px;display:flex;flex-direction:column;justify-content:center;text-align:center;font-size:18px;cursor:pointer}
.flash .ans{display:none;font-size:15px;color:var(--mut);margin-top:12px}.flash.flip .ans{display:block}
.lib-row{display:flex;gap:10px;padding:8px 0;border-bottom:1px solid var(--line)}.lib-row:last-child{border:0}
.lib-row input{margin-top:5px}.lib-row .meta{font-size:12px;color:var(--mut)}.lib-row.d .t{text-decoration:line-through;color:var(--mut)}
.controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.controls input[type=search],select{padding:6px 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);font:inherit;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}.stat{font-size:26px;font-weight:600}
.hide{display:none}details{margin-top:6px}details summary{cursor:pointer;color:var(--acc)}.ans-static{border-left:3px solid var(--acc);padding-left:8px;margin-top:6px}.libpart{margin:18px 0 0;font-size:15px}.js .nojs-only,.js .nojs-note{display:none}@media print{header,nav,.qbtns,.timer,textarea{display:none}.a{display:block!important}.modbody{display:block!important}}
</style></head><body>
<header><h1>ML Systems Security: 8-hour power course</h1>
<div class="bar" title="course progress"><i id="topbar"></i></div>
<nav style="margin-top:8px"><a href="#course" data-tab="course" class="on">Course</a><a href="#cards" data-tab="cards">Flashcards</a><a href="#lib" data-tab="lib">Library (237)</a><a href="#prog" data-tab="prog">Progress &amp; backup</a></nav></header>
<main>
<section id="course">__STATIC_COURSE__</section>
<section id="cards"><h2 class="nojs-only">Flashcards</h2><p class="nojs-only card">Flashcards need the interactive version (open in Chrome). The same 16 questions are in each module's <b>Check</b> section above.</p></section>
<section id="lib"><h2 class="nojs-only">Library: 237 items</h2>__STATIC_LIB__</section>
<section id="prog"><p class="nojs-only card">Progress tracking and backup need the interactive version (open in Chrome).</p></section>
</main>
<script>
const DATA = __DATA__;
const KEY = "mlsec_course_v1";
// Storage can be blocked (file opened from Drive/Files on a phone, private mode): fall back to memory.
const STORE = (() => { try { const t = "__t"; localStorage.setItem(t, t); localStorage.removeItem(t); return localStorage; } catch (e) { return null; } })();
let S = {}; try { S = JSON.parse((STORE && STORE.getItem(KEY)) || "{}"); } catch (e) { S = {}; }
S.sec ??= {}; S.q ??= {}; S.notes ??= {}; S.lib ??= {}; S.box ??= {}; S.timer ??= {}; S.open ??= {};
const save = () => { if (STORE) try { STORE.setItem(KEY, JSON.stringify(S)); } catch (e) {} };
const $ = (s, r = document) => r.querySelector(s), esc = s => s.replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const inline = s => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/\*([^*]+)\*/g, "<i>$1</i>");

// ---------- tabs ----------
document.documentElement.classList.add("js");
["cards","lib","prog"].forEach(t => $("#" + t).classList.add("hide"));
document.querySelectorAll("nav a").forEach(b => b.onclick = (ev) => { ev.preventDefault();
  document.querySelectorAll("nav a").forEach(x => x.classList.toggle("on", x === b));
  ["course","cards","lib","prog"].forEach(t => $("#" + t).classList.toggle("hide", t !== b.dataset.tab));
  if (b.dataset.tab === "prog") renderProg(); if (b.dataset.tab === "cards") nextCard();
});

// ---------- course ----------
function modDone(m){ return m.sections.every(s => S.sec[m.num + s.name]); }
function renderCourse(){
  const el = $("#course");
  el.innerHTML = `<p style="color:var(--mut)">Eight 60-minute modules. Tick each part as you finish it; your ticks, notes, timers and quiz results are saved in this browser (use <b>Progress &amp; backup</b> to move them). Works offline; links need internet.</p>`;
  DATA.modules.forEach(m => {
    const c = document.createElement("div"); c.className = "card" + (modDone(m) ? " done" : "");
    const t = S.timer[m.num] || 0;
    c.innerHTML = `<div class="modhead"><span class="pill st">${modDone(m) ? "done" : "M" + m.num}</span><h2>${esc(m.title)}</h2><span class="pill" id="mp${m.num}"></span><span>▾</span></div>
    <div class="modbody ${S.open[m.num] ? "" : "hide"}">
      <div class="timer" style="margin-top:10px">⏱ <span id="t${m.num}">${fmt(t)}</span> / 60:00
        <button class="btn" data-tm="${m.num}">start</button><button class="btn" data-tr="${m.num}">reset</button></div>
      ${m.sections.map(s => secHTML(m, s)).join("")}
      <div class="sec"><h3>My notes</h3><textarea data-note="${m.num}" placeholder="Takeaways, questions, things to try on my own code…">${esc(S.notes[m.num] || "")}</textarea></div>
    </div>`;
    c.querySelector(".modhead").onclick = () => { S.open[m.num] = !S.open[m.num]; save(); c.querySelector(".modbody").classList.toggle("hide"); };
    el.appendChild(c);
  });
  el.querySelectorAll("input[data-sec]").forEach(i => i.onchange = () => { S.sec[i.dataset.sec] = i.checked; save(); refresh(); });
  el.querySelectorAll("textarea[data-note]").forEach(t => t.oninput = () => { S.notes[t.dataset.note] = t.value; save(); });
  el.querySelectorAll("[data-reveal]").forEach(b => b.onclick = () => b.closest(".q").classList.add("show"));
  el.querySelectorAll("[data-grade]").forEach(b => b.onclick = () => { const [n, g] = b.dataset.grade.split(":"); S.q[n] = g; S.box[n] = g === "ok" ? Math.min((S.box[n] || 1) + 1, 3) : 1; save(); refresh(); });
  el.querySelectorAll("[data-tm]").forEach(b => b.onclick = () => toggleTimer(+b.dataset.tm, b));
  el.querySelectorAll("[data-tr]").forEach(b => b.onclick = () => { stopTimer(); S.timer[b.dataset.tr] = 0; save(); $("#t" + b.dataset.tr).textContent = fmt(0); });
  refresh();
}
function secHTML(m, s){
  const id = m.num + s.name, chk = `<label><input type="checkbox" data-sec="${id}" ${S.sec[id] ? "checked" : ""}> done</label>`;
  if (s.name !== "Check") return `<div class="sec"><h3>${s.name}${s.mins ? ` <span class="pill">${s.mins} min</span>` : ""}${chk}</h3>${s.html}</div>`;
  return `<div class="sec"><h3>Check${chk}</h3>` + s.questions.map(q => `<div class="q" id="q${q.n}"><b>${q.n}.</b> ${inline(q.q)}
     <div class="qbtns"><button class="btn" data-reveal>Reveal answer</button><button class="btn ok" data-grade="${q.n}:ok">I knew it</button><button class="btn warn" data-grade="${q.n}:no">Review again</button><span class="pill" data-qs="${q.n}"></span></div>
     <div class="a">${inline(q.a)}</div></div>`).join("") + `</div>`;
}
function refresh(){
  let done = 0, total = 0;
  DATA.modules.forEach(m => { const d = m.sections.filter(s => S.sec[m.num + s.name]).length; done += d; total += m.sections.length; const p = $("#mp" + m.num); if (p) p.textContent = `${d}/${m.sections.length}`; });
  $("#topbar").style.width = (100 * done / total) + "%";
  document.querySelectorAll("[data-qs]").forEach(p => { const g = S.q[p.dataset.qs]; p.textContent = g === "ok" ? "✓ knew it" : g === "no" ? "↺ reviewing" : ""; });
}
// timers
let tick = null, running = null;
const fmt = s => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
function stopTimer(){ clearInterval(tick); tick = null; if (running) { const b = document.querySelector(`[data-tm="${running}"]`); if (b) b.textContent = "start"; } running = null; }
function toggleTimer(n, b){
  if (running === n) return stopTimer();
  stopTimer(); running = n; b.textContent = "pause";
  tick = setInterval(() => { S.timer[n] = (S.timer[n] || 0) + 1; $("#t" + n).textContent = fmt(S.timer[n]); if (S.timer[n] % 10 === 0) save(); if (S.timer[n] === 3600) { stopTimer(); save(); alert(`Module ${n}: 60 minutes done.`); } }, 1000);
}

// ---------- flashcards (3-box Leitner) ----------
const CARDS = DATA.modules.flatMap(m => m.sections.filter(s => s.name === "Check").flatMap(s => s.questions.map(q => ({...q, mod: m.num}))));
let cur = null;
function nextCard(){
  const el = $("#cards"); const counts = [1,2,3].map(b => CARDS.filter(c => (S.box[c.n] || 1) === b).length);
  // weight box 1 most: pick lowest non-empty box, random within it
  const box = [1,2,3].find(b => CARDS.some(c => (S.box[c.n] || 1) === b));
  const pool = CARDS.filter(c => (S.box[c.n] || 1) === box); cur = pool[Math.floor(Math.random() * pool.length)];
  el.innerHTML = `<p style="color:var(--mut)">Leitner boxes: a card you know moves up (1→2→3); a miss sends it back to box 1. Lower boxes come up first. Box 1: ${counts[0]} · Box 2: ${counts[1]} · Box 3: ${counts[2]}</p>
   <div class="card flash" id="fc"><div><span class="pill">Module ${cur.mod} · Q${cur.n} · box ${S.box[cur.n] || 1}</span></div><div style="margin-top:10px">${inline(cur.q)}</div><div class="ans">${inline(cur.a)}</div><div class="pill" style="margin:12px auto 0">tap to flip</div></div>
   <div class="controls" style="justify-content:center"><button class="btn ok" id="fy">I knew it</button><button class="btn warn" id="fn">Missed it</button><button class="btn" id="fr">Reset boxes</button></div>`;
  $("#fc").onclick = () => $("#fc").classList.toggle("flip");
  $("#fy").onclick = () => { S.box[cur.n] = Math.min((S.box[cur.n] || 1) + 1, 3); S.q[cur.n] = "ok"; save(); refresh(); nextCard(); };
  $("#fn").onclick = () => { S.box[cur.n] = 1; S.q[cur.n] = "no"; save(); refresh(); nextCard(); };
  $("#fr").onclick = () => { if (confirm("Put every card back in box 1?")) { S.box = {}; save(); nextCard(); } };
}

// ---------- library ----------
function renderLib(){
  const el = $("#lib"); const parts = [...new Set(DATA.library.map(x => `Vol ${x.vol} · ${x.part}`))];
  el.innerHTML = `<div class="controls"><input type="search" id="ls" placeholder="Search 237 items (262 links): title, topic, why…" style="flex:1;min-width:200px">
    <select id="lp"><option value="">All parts</option>${parts.map(p => `<option>${esc(p)}</option>`).join("")}</select>
    <select id="ld"><option value="">All</option><option value="todo">Not done</option><option value="done">Done</option></select></div>
    <p id="lsum" style="color:var(--mut)"></p><div class="card" id="llist"></div>
    <p style="color:var(--mut);font-size:13px">Hours are estimates. ⓑ = the site blocks automated checks but is the official page (verified 2026-10-30).</p>`;
  const draw = () => {
    const q = $("#ls").value.toLowerCase(), p = $("#lp").value, d = $("#ld").value;
    const rows = DATA.library.filter(x => (!p || `Vol ${x.vol} · ${x.part}` === p) && (!q || (x.id + " " + x.title + " " + x.why + " " + x.part).toLowerCase().includes(q)) && (!d || (d === "done") === !!S.lib[x.id]));
    $("#llist").innerHTML = rows.map(x => `<div class="lib-row ${S.lib[x.id] ? "d" : ""}"><input type="checkbox" data-lib="${x.id}" ${S.lib[x.id] ? "checked" : ""}>
      <div><div class="t"><b>${x.id}</b> ${x.links.map(l => `<a href="${l.u}" target="_blank" rel="noopener">${esc(l.t)}</a>`).join(" · ")}${x.bot ? " ⓑ" : ""}</div>
      <div class="meta">Vol ${x.vol} · ${esc(x.part)} · ~${x.hours} h${x.why ? " · " + inline(x.why) : ""}</div></div></div>`).join("") || "<p>No matches.</p>";
    $("#llist").querySelectorAll("[data-lib]").forEach(i => i.onchange = () => { S.lib[i.dataset.lib] = i.checked ? new Date().toISOString().slice(0, 10) : undefined; if (!i.checked) delete S.lib[i.dataset.lib]; save(); draw(); });
    const done = DATA.library.filter(x => S.lib[x.id]); const hd = done.reduce((a, x) => a + x.hours, 0), ht = DATA.library.reduce((a, x) => a + x.hours, 0);
    $("#lsum").textContent = `Showing ${rows.length} · done ${done.length}/${DATA.library.length} items · ~${hd.toLocaleString()} of ~${ht.toLocaleString()} hours`;
  };
  ["ls","lp","ld"].forEach(i => $("#" + i).oninput = draw); draw();
}

// ---------- progress & backup ----------
function renderProg(){
  const secs = DATA.modules.reduce((a, m) => a + m.sections.length, 0), sd = Object.values(S.sec).filter(Boolean).length;
  const mins = Math.round(Object.values(S.timer).reduce((a, b) => a + b, 0) / 60), ok = Object.values(S.q).filter(g => g === "ok").length;
  const libd = DATA.library.filter(x => S.lib[x.id]), libh = libd.reduce((a, x) => a + x.hours, 0);
  $("#prog").innerHTML = `<div class="grid">
    <div class="card"><div class="stat">${sd}/${secs}</div>course parts done</div>
    <div class="card"><div class="stat">${DATA.modules.filter(modDone).length}/8</div>modules complete</div>
    <div class="card"><div class="stat">${mins} min</div>timed study</div>
    <div class="card"><div class="stat">${ok}/16</div>questions known</div>
    <div class="card"><div class="stat">${libd.length}</div>library items done (~${libh.toLocaleString()} h)</div></div>
    <div class="card"><h3 style="margin-top:0">Backup &amp; move between devices</h3>
    <p style="color:var(--mut)">Your progress lives in this browser only. Export it to a file (e.g. save it in your Drive) and import it on another device or after clearing the browser.</p>
    <div class="controls"><button class="btn pri" id="ex">Export progress</button><label class="btn">Import progress<input type="file" id="im" accept=".json" class="hide"></label><button class="btn warn" id="rs">Reset everything</button></div></div>
    <p style="color:var(--mut);font-size:13px">Built ${DATA.built} from ML_Security_8h_Power_Course.md + both curriculum volumes in this folder.</p>`;
  $("#ex").onclick = () => { const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([JSON.stringify(S, null, 1)], {type: "application/json"})); a.download = `mlsec-progress-${new Date().toISOString().slice(0, 10)}.json`; a.click(); };
  $("#im").onchange = e => { const f = e.target.files[0]; if (!f) return; f.text().then(t => { try { S = JSON.parse(t); ["sec","q","notes","lib","box","timer","open"].forEach(k => S[k] ??= {}); save(); renderCourse(); renderLib(); renderProg(); alert("Progress imported."); } catch { alert("That file isn't a progress export."); } }); };
  $("#rs").onclick = () => { if (confirm("Erase all ticks, notes, timers and quiz results in this browser?")) { if (STORE) STORE.removeItem(KEY); S = {sec:{},q:{},notes:{},lib:{},box:{},timer:{},open:{}}; renderCourse(); renderLib(); renderProg(); } };
}

if (!STORE) { const w = document.createElement("div"); w.className = "card"; w.style.borderColor = "var(--warn)";
  w.innerHTML = "<b>Progress can't be saved automatically here.</b> This browser is blocking storage for files opened this way. Everything works, but before closing use <b>Progress &amp; backup → Export</b>, and Import next time. (Opening the app from its web address avoids this.)";
  document.querySelector("main").prepend(w); }
renderCourse(); renderLib();
window.addEventListener("beforeunload", save);
</script></body></html>"""

OUT.write_text(HTML.replace("__DATA__", json.dumps(DATA, ensure_ascii=False)).replace("__STATIC_COURSE__", static_course()).replace("__STATIC_LIB__", static_library()), encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB): {len(modules)} modules, "
      f"{sum(len(s['questions']) for m in modules for s in m['sections'] if s['name']=='Check')} questions, "
      f"{len(library)} library items (vol I {sum(x['vol']=='I' for x in library)}, vol II {sum(x['vol']=='II' for x in library)}), "
      f"{sum(x['hours'] for x in library):,} h")
