#!/usr/bin/env python3
"""
htmlize: a tiny live-reloading server for self-contained HTML artifacts.

Serves a folder of self-contained HTML "posts" as a personal reading list:
a calm, scannable index you can drag to reorder, pin, soft-delete (to a
recoverable Trash), and filter. New/edited posts appear live over SSE.
Stdlib only. Binds to 127.0.0.1.

  python3 serve.py [--dir .htmlize] [--port 7878] [--no-open]

State (custom order / pins / trash) persists to <dir>/.state.json.
This is the only view for the skill: the agent copies it to .htmlize/.serve.py
and runs that. Stdlib only, so it runs anywhere python3 does.
"""
import argparse, html, http.server, json, mimetypes, os, posixpath, re
import socketserver, sys, threading, time, urllib.parse, webbrowser

V = 0          # bumped by the watcher whenever a *visible* file changes
D = None       # absolute path of the folder we serve
STATE = ".state.json"

# Injected into every served HTML page: live-reload over SSE + a quiet,
# self-styled "back to the reading list" link (so on-disk/offline copies
# stay clean — the nav only exists when served).
SNIP = (
    "<script>(function(){function c(){try{var e=new EventSource('/__reload');"
    "e.onmessage=function(m){if(m.data==='reload')location.reload()};"
    "e.onerror=function(){e.close();setTimeout(c,1000)}}catch(_){setTimeout(c,1000)}}"
    "c()})();</script>"
    "<a href='/' id='__hzback' title='Reading list'>&larr;&#8202;reading list</a>"
    "<style>#__hzback{position:fixed;top:14px;left:16px;z-index:99999;"
    "font:600 12px/1 ui-monospace,SFMono-Regular,Menlo,monospace;text-decoration:none;"
    "color:var(--muted,#6b685f);background:var(--surface,#fff);"
    "border:1px solid var(--border,#e6e3dc);border-radius:99px;padding:7px 12px;"
    "box-shadow:0 2px 10px rgba(0,0,0,.10);"
    "transition:color .14s,transform .14s,border-color .14s}"
    "#__hzback:hover{color:var(--accent-text,#2e3a96);border-color:var(--accent-border,#c3c8ec);transform:translateX(-2px)}"
    "@media print{#__hzback{display:none}}</style>"
)

TAGS = re.compile(r"(?is)<(script|style)\b.*?</\1>|<[^>]+>")
TITLE = re.compile(r"(?is)<title[^>]*>(.*?)</title>")
META_TAG = re.compile(r"(?is)<meta\b((?:\"[^\"]*\"|'[^']*'|[^>])*)>")
ATTR_RE = re.compile(r"""(?is)([\w:-]+)\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)""")


def _attrs(inner):
    d = {}
    for k, v in ATTR_RE.findall(inner):
        if v and v[0] in "\"'":
            v = v[1:-1]
        d.setdefault(k.lower(), v)
    return d


def _meta(head, name):
    """Content of <meta name=NAME …>, robust to attribute order, quoting, and '>' in values."""
    name = name.lower()
    for inner in META_TAG.findall(head):
        a = _attrs(inner)
        if a.get("name", "").lower() == name:
            return html.unescape(a.get("content", "").strip())
    return ""


def meta_of(fp, name):
    """Title, summary, type, reading-time, mtime for one artifact."""
    try:
        raw = open(fp, "r", encoding="utf-8", errors="replace").read()
    except OSError:
        raw = ""
    head = raw[:20000]
    tm = TITLE.search(head)
    title = html.unescape(tm.group(1).strip()) if tm and tm.group(1).strip() else name
    summary = _meta(head, "description")
    kind = _meta(head, "htmlize-type").lower()
    words = len(TAGS.sub(" ", raw).split())
    mins = max(1, round(words / 220)) if words else 1
    try:
        mtime = os.stat(fp).st_mtime
    except OSError:
        mtime = 0
    return {"name": name, "title": title, "summary": summary,
            "kind": kind, "mins": mins, "mtime": mtime}


def ago(ts, now):
    d = now - ts
    if d < 45:
        return "just now"
    if d < 3600:
        return "%dm ago" % max(1, int(d // 60))
    if d < 86400:
        return "%dh ago" % int(d // 3600)
    if d < 172800:
        return "yesterday"
    if d < 604800:
        return "%dd ago" % int(d // 86400)
    return time.strftime("%b %d", time.localtime(ts))


def artifacts():
    """Visible HTML artifacts in D (no index, no dotfiles)."""
    try:
        ns = [n for n in os.listdir(D)
              if n.lower().endswith((".html", ".htm"))
              and n != "index.html" and not n.startswith(".")]
    except OSError:
        return []
    return ns


def load_state():
    try:
        s = json.load(open(os.path.join(D, STATE), encoding="utf-8"))
        return {"order": list(s.get("order", [])),
                "pinned": list(s.get("pinned", [])),
                "trashed": list(s.get("trashed", []))}
    except (OSError, ValueError):
        return {"order": [], "pinned": [], "trashed": []}


def save_state(s):
    known = set(artifacts())
    clean = {k: [n for n in s.get(k, []) if isinstance(n, str) and n in known]
             for k in ("order", "pinned", "trashed")}
    tmp = os.path.join(D, STATE + ".tmp")
    try:
        json.dump(clean, open(tmp, "w", encoding="utf-8"))
        os.replace(tmp, os.path.join(D, STATE))
    except OSError:
        pass
    return clean


def chip(kind):
    if not kind:
        return ""
    return '<span class="chip">%s</span>' % html.escape(kind)


def row(m, now, pinned=False, trash=False):
    name = m["name"]
    href = "./" + urllib.parse.quote(name)
    search = html.escape((m["title"] + " " + m["summary"] + " " + m["kind"]).lower(), quote=True)
    summary = ('<p class="r-sum">%s</p>' % html.escape(m["summary"])) if m["summary"] else ""
    meta = '<span class="r-meta">%s min&#8202;&middot;&#8202;%s</span>' % (m["mins"], ago(m["mtime"], now))
    if trash:
        acts = ('<div class="acts">'
                '<button class="ic" data-act="restore" title="Restore">&#8617;</button>'
                '<button class="ic warn" data-act="purge" title="Delete forever">&times;</button></div>')
        return ('<li class="row trashed" data-name="%s" data-search="%s">'
                '<a class="open" href="%s"><span class="r-title">%s</span>%s</a>%s</li>'
                % (html.escape(name, True), search, href, html.escape(m["title"]), summary, acts))
    acts = ('<div class="acts">'
            '<button class="ic" data-act="pin" title="Pin to top">%s</button>'
            '<button class="ic warn" data-act="del" title="Delete">&times;</button></div>'
            % ("&#9679;" if pinned else "&#9675;"))
    return ('<li class="row%s" draggable="true" data-name="%s" data-search="%s">'
            '<span class="grip" aria-hidden="true">&#8942;&#8942;</span>'
            '<a class="open" href="%s">'
            '<span class="r-head"><span class="r-title">%s</span>%s</span>'
            '%s%s</a>%s</li>'
            % (" pinned" if pinned else "", html.escape(name, True), search, href,
               html.escape(m["title"]), chip(m["kind"]), summary, meta, acts))


def ordered(metas, st):
    names = [m["name"] for m in metas]
    nameset = set(names)
    ps = set()
    pinned = [n for n in st["pinned"] if n in nameset and not (n in ps or ps.add(n))]
    pset = set(pinned)
    normal = [n for n in names if n not in pset]
    nset = set(normal)
    ks = set()
    known = [n for n in st["order"] if n in nset and not (n in ks or ks.add(n))]
    kset = set(known)
    fresh = [n for n in normal if n not in kset]
    fresh.sort(key=lambda n: next(m["mtime"] for m in metas if m["name"] == n), reverse=True)
    return pinned, fresh + known


def index():
    now = time.time()
    files = artifacts()
    st = load_state()
    trashed = [n for n in st["trashed"] if n in set(files)]
    tset = set(trashed)
    live = [meta_of(os.path.join(D, n), n) for n in files if n not in tset]
    bym = {m["name"]: m for m in live}
    pinned, normal = ordered(live, st)

    rows = "".join(row(bym[n], now, pinned=True) for n in pinned)
    rows += "".join(row(bym[n], now) for n in normal)

    if not live:
        rows_html = (
            '<div class="empty"><svg width="46" height="46" viewBox="0 0 46 46" fill="none" '
            'stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">'
            '<rect x="9" y="7" width="24" height="30" rx="3"/><rect x="13" y="11" width="24" height="30" rx="3"/>'
            '<line x1="18" y1="20" x2="32" y2="20"/><line x1="18" y1="26" x2="29" y2="26"/></svg>'
            '<h2>Nothing here yet.</h2>'
            '<p>Substantial replies show up here as you work &mdash; plans, reviews, specs, explainers.</p></div>')
    else:
        rows_html = '<ul id="list" class="list">%s</ul><p id="nomatch" class="nomatch" hidden></p>' % rows

    tmetas = [meta_of(os.path.join(D, n), n) for n in trashed]
    trows = "".join(row(m, now, trash=True) for m in tmetas)
    trash_html = ""
    if trashed:
        trash_html = ('<details class="trash" id="trash"%s><summary>Trash <span class="tn">%d</span></summary>'
                      '<ul id="trash-list" class="list">%s</ul>'
                      '<button id="empty-trash" class="link-btn warn">Empty trash</button></details>'
                      % ("", len(trashed), trows))

    count = "%d post%s" % (len(live), "" if len(live) == 1 else "s")
    safe_state = json.dumps(st).replace("<", "\\u003c")
    return (PAGE.replace("__COUNT__", count)
                .replace("__ROWS__", rows_html)
                .replace("__TRASH__", trash_html)
                .replace("__STATE__", safe_state))


PAGE = r"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>htmlize &middot; reading list</title>
<style>
:root{
 --bg:#faf9f7;--surface:#fff;--surface-2:#f3f1ec;--fg:#1c1b19;--fg-strong:#100f0e;
 --muted:#6b685f;--faint:#6e6a61;--border:#e6e3dc;--border-2:#d8d4ca;
 --accent:#3a4ab8;--accent-text:#2e3a96;--accent-weak:#e9ebf7;--accent-border:#c3c8ec;
 --warn:#b4422a;--warn-weak:#f7e8e3;
 --display:"Iowan Old Style","Palatino Linotype","URW Palladio L",Palatino,P052,Georgia,serif;
 --body:Seravek,"Gill Sans Nova",Ubuntu,Calibri,"Source Sans Pro",-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
 --mono:ui-monospace,"Cascadia Code","SF Mono",Menlo,Consolas,"DejaVu Sans Mono",monospace;
 --shadow:0 1px 2px rgba(28,27,25,.04),0 6px 20px rgba(28,27,25,.06);
 --ring:0 0 0 3px var(--accent-weak),0 0 0 1px var(--accent);
}
@media(prefers-color-scheme:dark){:root{
 --bg:#0e0f12;--surface:#15171c;--surface-2:#1b1e24;--fg:rgba(237,238,240,.92);--fg-strong:#f4f5f6;
 --muted:rgba(237,238,240,.58);--faint:rgba(237,238,240,.5);--border:rgba(237,238,240,.10);--border-2:rgba(237,238,240,.18);
 --accent:#97a4f0;--accent-text:#aab4f4;--accent-weak:#1e2236;--accent-border:#353c63;
 --warn:#e08266;--warn-weak:#2c1c18;
 --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 28px rgba(0,0,0,.5);
}}
*{box-sizing:border-box}html{font-size:16px;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:1.0625rem/1.7 var(--body);
 -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;padding:4.5rem 1.25rem 6rem}
.wrap{max-width:46rem;margin:0 auto}
.top{display:flex;align-items:baseline;gap:.6rem;margin-bottom:1.5rem}
.brand{font:700 1rem/1 var(--mono);color:var(--fg-strong);letter-spacing:-.01em}
.brand .live{color:var(--faint);font-weight:400}
.count{margin-left:auto;font:.8125rem/1 var(--mono);color:var(--faint)}
.filter-wrap{position:relative;margin-bottom:1.75rem}
#filter{width:100%;border:none;border-bottom:1px solid var(--border);background:transparent;color:var(--fg);
 font:1.0625rem/1.5 var(--body);padding:.55rem .1rem;outline:none;transition:border-color .15s}
#filter::placeholder{color:var(--faint)}
#filter:focus{border-color:var(--accent)}
.clearf{position:absolute;right:0;top:50%;transform:translateY(-50%);border:none;background:none;color:var(--faint);
 font:.8125rem var(--mono);cursor:pointer;padding:.3rem .4rem}.clearf:hover{color:var(--accent-text)}
.list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:.35rem}
.row{display:flex;align-items:flex-start;gap:.2rem;padding:.85rem .9rem;border:1px solid transparent;border-radius:10px;
 transition:background .15s,border-color .15s,box-shadow .15s,opacity .2s}
.row:hover{background:var(--surface);border-color:var(--border);box-shadow:var(--shadow)}
.row.pinned{background:var(--accent-weak);border-left:3px solid var(--accent);padding-left:.7rem}
.grip{flex:0 0 1rem;align-self:center;color:transparent;cursor:grab;font:.7rem/1 var(--mono);letter-spacing:-3px;
 user-select:none;transition:color .15s;margin-right:.1rem}
.row:hover .grip{color:var(--faint)}.row.dragging{opacity:.5}
.row.dragging .grip,.grip:active{cursor:grabbing}
.open{flex:1 1 auto;min-width:0;text-decoration:none;color:inherit;display:block}
.r-head{display:flex;align-items:baseline;gap:.6rem}
.r-title{font:1.15rem/1.35 var(--display);color:var(--fg-strong);letter-spacing:-.01em}
.chip{flex:0 0 auto;font:.7rem/1.3 var(--mono);text-transform:uppercase;letter-spacing:.06em;
 color:var(--muted);background:var(--surface-2);border-radius:99px;padding:.2em .6em;margin-left:auto;white-space:nowrap}
.r-sum{margin:.2rem 0 0;font-size:.9375rem;line-height:1.55;color:var(--muted);
 overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:1;-webkit-box-orient:vertical}
.r-meta{display:block;margin-top:.4rem;font:.8125rem/1.4 var(--mono);color:var(--faint)}
.acts{flex:0 0 auto;display:flex;gap:.15rem;align-self:center;opacity:0;transition:opacity .14s}
.row:hover .acts,.row:focus-within .acts{opacity:1}
.ic{border:none;background:none;cursor:pointer;color:var(--faint);font:1rem/1 var(--body);
 width:1.85rem;height:1.85rem;border-radius:7px;display:grid;place-items:center;transition:background .12s,color .12s}
.ic:hover{background:var(--surface-2);color:var(--fg)}.ic.warn:hover{color:var(--warn);background:var(--warn-weak)}
.row.pinned .ic[data-act=pin]{color:var(--accent-text)}
:focus-visible{outline:none;box-shadow:var(--ring)}
.nomatch{color:var(--muted);font-size:.9375rem;padding:.5rem .9rem}
.empty{text-align:center;max-width:34ch;margin:5rem auto;color:var(--muted)}
.empty svg{color:var(--accent-border);margin-bottom:1.1rem}
.empty h2{font:400 1.5rem/1.2 var(--display);color:var(--fg-strong);margin:0 0 .4rem}
.empty p{margin:0;font-size:.9375rem;line-height:1.6}
.trash{margin-top:2.5rem;border-top:1px solid var(--border);padding-top:1rem}
.trash summary{cursor:pointer;font:.8125rem/1 var(--mono);text-transform:uppercase;letter-spacing:.1em;
 color:var(--faint);list-style:none;padding:.3rem 0}.trash summary::-webkit-details-marker{display:none}
.trash summary:hover{color:var(--muted)}.trash .tn{color:var(--accent-text)}
.trash[open] summary{margin-bottom:.6rem}.trash .row{opacity:.7}.trash .r-title{font-size:1rem}
.link-btn{border:none;background:none;cursor:pointer;font:.8125rem var(--mono);color:var(--faint);padding:.5rem .9rem;margin-top:.3rem}
.link-btn.warn:hover{color:var(--warn)}
.undo{position:fixed;left:50%;bottom:1.4rem;transform:translateX(-50%) translateY(140%);
 display:flex;align-items:center;gap:1rem;background:var(--fg-strong);color:var(--bg);
 padding:.7rem .8rem .7rem 1.1rem;border-radius:10px;box-shadow:var(--shadow);font-size:.9rem;
 transition:transform .25s cubic-bezier(.2,.9,.3,1);z-index:9999;max-width:calc(100vw - 2rem)}
.undo.show{transform:translateX(-50%) translateY(0)}
.undo b{font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:18ch}
.undo button{border:none;background:var(--accent);color:#fff;font:600 .82rem var(--mono);
 padding:.4rem .8rem;border-radius:7px;cursor:pointer}
@keyframes pulse{0%{background:var(--accent-weak)}45%{background:var(--accent-weak)}100%{background:transparent}}
.row.new{animation:pulse 1.8s ease-out 1}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important}}
@media(max-width:560px){.chip{margin-left:.4rem}.r-head{flex-wrap:wrap}.acts{opacity:1}}
</style></head><body>
<div class="wrap">
 <div class="top"><span class="brand">htmlize <span class="live">reading list</span></span><span class="count" id="count">__COUNT__</span></div>
 <div class="filter-wrap"><input id="filter" type="text" placeholder="Filter posts&hellip;" autocomplete="off" spellcheck="false"><button class="clearf" id="clearf" hidden>&times; clear</button></div>
 __ROWS__
 __TRASH__
</div>
<div class="undo" id="undo"><b id="undo-label"></b><button id="undo-btn">Undo</button></div>
<script>
(function(){
var S=__STATE__;
var list=document.getElementById('list');
var trash=document.getElementById('trash');
var post=function(p,b){try{fetch(p,{method:'POST',headers:{'Content-Type':'application/json','X-Htmlize':'1'},body:JSON.stringify(b)})['catch'](function(){})}catch(_){}}
function snap(){var o=[],pn=[],tr=[];
 if(list)list.querySelectorAll('.row').forEach(function(r){(r.classList.contains('pinned')?pn:o).push(r.dataset.name)});
 var tl=document.getElementById('trash-list');if(tl)tl.querySelectorAll('.row').forEach(function(r){tr.push(r.dataset.name)});
 return {order:o,pinned:pn,trashed:tr}}
function persist(){post('/__state',snap())}
function normalize(){if(!list)return;var rows=[].slice.call(list.querySelectorAll('.row'));
 rows.filter(function(r){return r.classList.contains('pinned')}).concat(rows.filter(function(r){return !r.classList.contains('pinned')}))
 .forEach(function(r){r.style.animation='none';list.appendChild(r)})}
function setcount(){var n=list?list.querySelectorAll('.row').length:0;var c=document.getElementById('count');if(c)c.textContent=n+' post'+(n==1?'':'s')}
var EMPTY='<svg width="46" height="46" viewBox="0 0 46 46" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="7" width="24" height="30" rx="3"/><rect x="13" y="11" width="24" height="30" rx="3"/><line x1="18" y1="20" x2="32" y2="20"/><line x1="18" y1="26" x2="29" y2="26"/></svg><h2>Nothing here yet.</h2><p>Substantial replies show up here as you work — plans, reviews, specs, explainers.</p>';
function refreshEmpty(){var n=list?list.querySelectorAll('.row').length:0;var emp=document.querySelector('.empty');
 if(n===0){if(list){list.remove();list=null;}var nm=document.getElementById('nomatch');if(nm)nm.remove();
  if(!emp){emp=document.createElement('div');emp.className='empty';emp.innerHTML=EMPTY;document.querySelector('.wrap').insertBefore(emp,trash||null);}}
 else if(emp){emp.remove();}}

/* ---- drag reorder ---- */
var drag=null;
if(list){
 list.addEventListener('dragstart',function(e){var r=e.target.closest&&e.target.closest('.row');if(!r)return;drag=r;r.classList.add('dragging');e.dataTransfer.effectAllowed='move';try{e.dataTransfer.setData('text/plain','')}catch(_){}});
 list.addEventListener('dragend',function(){if(!drag)return;drag.classList.remove('dragging');drag=null;normalize();persist()});
 list.addEventListener('dragover',function(e){e.preventDefault();if(!drag)return;
  var dp=drag.classList.contains('pinned');
  var seg=[].slice.call(list.querySelectorAll('.row:not(.dragging)')).filter(function(r){return r.classList.contains('pinned')===dp});
  var a=after(seg,e.clientY);
  if(a==null){if(seg.length)list.insertBefore(drag,seg[seg.length-1].nextSibling);else list.appendChild(drag);}
  else list.insertBefore(drag,a);});
}
function after(els,y){var best={o:-Infinity,el:null};
 els.forEach(function(ch){var b=ch.getBoundingClientRect();var o=y-b.top-b.height/2;if(o<0&&o>best.o)best={o:o,el:ch}});return best.el}

/* ---- pin / delete ---- */
if(list)list.addEventListener('click',function(e){
 var p=e.target.closest('[data-act=pin]'),d=e.target.closest('[data-act=del]');
 if(p){e.preventDefault();var r=p.closest('.row');var on=r.classList.toggle('pinned');p.innerHTML=on?'&#9679;':'&#9675;';normalize();persist();return}
 if(d){e.preventDefault();del(d.closest('.row'));return}
});

/* ---- soft delete + undo ---- */
var undoTimer,lastDeleted;
function ensureTrash(){
 if(trash){trash.querySelector('.tn').textContent=trash.querySelectorAll('#trash-list .row').length;return trash}
 trash=document.createElement('details');trash.className='trash';trash.id='trash';
 trash.innerHTML='<summary>Trash <span class="tn">0</span></summary><ul id="trash-list" class="list"></ul><button id="empty-trash" class="link-btn warn">Empty trash</button>';
 document.querySelector('.wrap').appendChild(trash);wireTrash();return trash}
function toTrash(r){var t=ensureTrash();r.classList.remove('pinned');r.removeAttribute('draggable');r.classList.add('trashed');
 var pin=r.querySelector('[data-act=pin]'),del=r.querySelector('[data-act=del]');
 if(pin)pin.outerHTML='<button class="ic" data-act="restore" title="Restore">&#8617;</button>';
 if(del)del.outerHTML='<button class="ic warn" data-act="purge" title="Delete forever">&times;</button>';
 var grip=r.querySelector('.grip');if(grip)grip.remove();
 trash.querySelector('#trash-list').insertBefore(r,trash.querySelector('#trash-list').firstChild);
 trash.querySelector('.tn').textContent=trash.querySelectorAll('#trash-list .row').length}
function del(r){lastDeleted={name:r.dataset.name,title:(r.querySelector('.r-title')||{}).textContent||r.dataset.name};
 toTrash(r);setcount();refreshEmpty();persist();applyFilter();showUndo()}
function showUndo(){var u=document.getElementById('undo');document.getElementById('undo-label').textContent='Deleted '+lastDeleted.title;
 u.classList.add('show');clearTimeout(undoTimer);undoTimer=setTimeout(function(){u.classList.remove('show')},6000)}
document.getElementById('undo-btn').addEventListener('click',function(){
 if(!lastDeleted)return;var r=document.querySelector('#trash-list .row[data-name="'+css(lastDeleted.name)+'"]');
 if(r)restore(r);document.getElementById('undo').classList.remove('show');lastDeleted=null});

/* ---- trash actions ---- */
function wireTrash(){if(!trash)return;
 trash.addEventListener('click',function(e){
  var rs=e.target.closest('[data-act=restore]'),pg=e.target.closest('[data-act=purge]');
  if(rs){restore(rs.closest('.row'));return}
  if(pg){purge(pg.closest('.row'));return}
  if(e.target.id==='empty-trash'){[].slice.call(trash.querySelectorAll('#trash-list .row')).forEach(purge);return}
 })}
function restore(r){r.classList.remove('trashed');r.setAttribute('draggable','true');
 var rs=r.querySelector('[data-act=restore]'),pg=r.querySelector('[data-act=purge]');
 if(rs)rs.outerHTML='<button class="ic" data-act="pin" title="Pin to top">&#9675;</button>';
 if(pg)pg.outerHTML='<button class="ic warn" data-act="del" title="Delete">&times;</button>';
 if(!r.querySelector('.grip')){var g=document.createElement('span');g.className='grip';g.setAttribute('aria-hidden','true');g.innerHTML='&#8942;&#8942;';r.insertBefore(g,r.firstChild)}
 (list||makeList()).appendChild(r);normalize();trashCount();setcount();persist();applyFilter()}
function purge(r){post('/__purge',{name:r.dataset.name});r.remove();trashCount();persist()}
function trashCount(){if(!trash)return;var n=trash.querySelectorAll('#trash-list .row').length;
 if(n===0){trash.remove();trash=null}else{trash.querySelector('.tn').textContent=n}}
function makeList(){var emp=document.querySelector('.empty');if(emp)emp.remove();
 list=document.createElement('ul');list.id='list';list.className='list';
 nomatch=document.createElement('p');nomatch.id='nomatch';nomatch.className='nomatch';nomatch.hidden=true;
 var w=document.querySelector('.wrap');w.insertBefore(list,trash||null);w.insertBefore(nomatch,trash||null);return list}
if(trash)wireTrash();

/* ---- filter ---- */
var f=document.getElementById('filter'),clf=document.getElementById('clearf'),nomatch=document.getElementById('nomatch');
function applyFilter(){var q=(f.value||'').trim().toLowerCase();clf.hidden=!q;var shown=0;
 if(list)list.querySelectorAll('.row').forEach(function(r){var hit=!q||(r.dataset.search||'').indexOf(q)>=0;r.style.display=hit?'':'none';if(hit)shown++});
 if(nomatch){if(q&&shown===0){nomatch.hidden=false;nomatch.textContent='No posts match “'+q+'”'}else nomatch.hidden=true}}
var ft;if(f)f.addEventListener('input',function(){clearTimeout(ft);ft=setTimeout(applyFilter,80)});
if(clf)clf.addEventListener('click',function(){f.value='';applyFilter();f.focus()});

/* what's-new: flash rows that appeared since this tab last rendered */
try{var K='hz:seen',seen=JSON.parse(sessionStorage.getItem(K)||'[]'),cur=[];
 if(list)list.querySelectorAll('.row').forEach(function(r){cur.push(r.dataset.name);
  if(seen.length&&seen.indexOf(r.dataset.name)<0)r.classList.add('new')});
 var tl0=document.getElementById('trash-list');if(tl0)tl0.querySelectorAll('.row').forEach(function(r){cur.push(r.dataset.name)});
 sessionStorage.setItem(K,JSON.stringify(cur))}catch(_){}

function css(s){return (window.CSS&&CSS.escape)?CSS.escape(s):s.replace(/["\\]/g,'\\$&')}
})();
</script>
</body></html>"""


def sig(path):
    """Hash of visible files only — dotfiles (state, pid, log) don't trigger reloads."""
    h = __import__("hashlib").sha1()
    try:
        for n in sorted(os.listdir(path)):
            if n.startswith(".") or n == "index.html":
                continue
            try:
                s = os.stat(os.path.join(path, n))
                h.update(n.encode("utf-8", "replace"))
                h.update(str(s.st_mtime_ns).encode()); h.update(str(s.st_size).encode())
            except OSError:
                pass
    except OSError:
        pass
    return h.hexdigest()


def watch():
    global V
    last = sig(D)
    while True:
        time.sleep(0.4)
        cur = sig(D)
        if cur != last:
            last = cur; V += 1


def safe_name(name):
    """A bare .html basename that resolves inside D, or None."""
    if not isinstance(name, str):
        return None
    name = os.path.basename(name)
    if not name.lower().endswith((".html", ".htm")) or name.startswith("."):
        return None
    fp = os.path.join(D, name)
    if os.path.realpath(fp).startswith(os.path.realpath(D) + os.sep):
        return name
    return None


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_a):
        pass

    def do_GET(self):
        p = urllib.parse.urlparse(self.path).path
        if p == "/__alive":
            return self.send(200, b"ok", "text/plain")
        if p == "/__reload":
            return self.sse()
        rel = posixpath.normpath(urllib.parse.unquote(p)).lstrip("/")
        if rel in ("", ".", "index.html", "index.htm"):
            return self.send(200, index().encode("utf-8"), "text/html; charset=utf-8")
        fp = os.path.join(D, rel)
        if not os.path.realpath(fp).startswith(os.path.realpath(D) + os.sep):
            return self.send(403, b"forbidden", "text/plain")
        if os.path.isfile(fp):
            return self.html_file(fp) if fp.lower().endswith((".html", ".htm")) else self.static(fp)
        return self.send(404, b"not found", "text/plain")

    def _same_origin(self):
        # The in-page fetch() always sends X-Htmlize:1 — a non-safelisted header,
        # so a cross-origin page must preflight (OPTIONS), which we never answer.
        # Absent header == a native client (curl). Origin, when present, must be us.
        if self.headers.get("X-Htmlize") != "1":
            return False
        o = self.headers.get("Origin")
        if o:
            host = self.headers.get("Host", "")
            return o in ("http://" + host, "https://" + host)
        return True

    def do_POST(self):
        p = urllib.parse.urlparse(self.path).path
        if p in ("/__state", "/__purge") and not self._same_origin():
            return self.send(403, b"forbidden", "text/plain")
        try:
            n = int(self.headers.get("Content-Length", 0))
        except ValueError:
            return self.send(400, b"bad", "text/plain")
        if n < 0 or n > 1_000_000:
            return self.send(413, b"too large", "text/plain")
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, OSError):
            return self.send(400, b"bad", "text/plain")
        if p == "/__state":
            save_state(body if isinstance(body, dict) else {})
            return self.send(200, b'{"ok":true}', "application/json")
        if p == "/__purge":
            name = safe_name(body.get("name")) if isinstance(body, dict) else None
            if name:
                try:
                    os.remove(os.path.join(D, name))
                except OSError:
                    pass
                st = load_state()
                for k in ("order", "pinned", "trashed"):
                    st[k] = [x for x in st[k] if x != name]
                save_state(st)
            return self.send(200, b'{"ok":true}', "application/json")
        return self.send(404, b"not found", "text/plain")

    def html_file(self, fp):
        try:
            t = open(fp, "rb").read().decode("utf-8", "replace")
        except OSError:
            return self.send(404, b"not found", "text/plain")
        t = t.replace("</body>", SNIP + "</body>", 1) if "</body>" in t else t + SNIP
        self.send(200, t.encode("utf-8"), "text/html; charset=utf-8")

    def static(self, fp):
        ct = mimetypes.guess_type(fp)[0] or "application/octet-stream"
        try:
            self.send(200, open(fp, "rb").read(), ct)
        except OSError:
            self.send(404, b"not found", "text/plain")

    def send(self, code, body, ct):
        self.send_response(code)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        seen, ping = V, time.time()
        try:
            self.wfile.write(b": connected\n\n"); self.wfile.flush()
            while True:
                time.sleep(0.3)
                if V != seen:
                    seen = V; self.wfile.write(b"data: reload\n\n"); self.wfile.flush()
                elif time.time() - ping > 15:
                    ping = time.time(); self.wfile.write(b": ping\n\n"); self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            return


class S(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    global D
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.environ.get("HTMLIZE_DIR", ".htmlize"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("HTMLIZE_PORT", "7878")))
    ap.add_argument("--no-open", action="store_true")
    a = ap.parse_args()
    D = os.path.abspath(a.dir)
    os.makedirs(D, exist_ok=True)
    port, httpd = a.port, None
    for _ in range(25):
        try:
            httpd = S(("127.0.0.1", port), H); break
        except OSError:
            port += 1
    if httpd is None:
        print("htmlize: no free port", file=sys.stderr); sys.exit(1)
    threading.Thread(target=watch, daemon=True).start()
    url = "http://127.0.0.1:%d/" % port
    print("htmlize: serving %s at %s" % (D, url))
    if not a.no_open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nhtmlize: stopped")


if __name__ == "__main__":
    main()
