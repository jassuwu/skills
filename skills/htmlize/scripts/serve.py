#!/usr/bin/env python3
"""
htmlize: a tiny live-reloading server for Claude Code HTML artifacts.
Stdlib only. Serves a folder of HTML files and refreshes the browser whenever
anything in it changes. Binds to 127.0.0.1 only.

  python3 serve.py [--dir .claude-html] [--port 7878] [--no-open]

This exact file is also embedded inside SKILL.md as a fallback, so the skill
works even if this sibling file is missing. Keep the two copies in sync.
"""
import argparse, hashlib, http.server, mimetypes, os, posixpath
import socketserver, sys, threading, time, urllib.parse, webbrowser

V = 0          # bumped by the watcher whenever the folder changes
D = None       # absolute path of the folder we serve

SNIP = ("<script>(function(){function c(){try{var e=new EventSource('/__reload');"
        "e.onmessage=function(m){if(m.data==='reload')location.reload()};"
        "e.onerror=function(){e.close();setTimeout(c,1000)}}catch(_){setTimeout(c,1000)}}"
        "c()})();</script>")

CSS = ("*{box-sizing:border-box}html,body{margin:0}"
       "body{background:#fbfbfa;color:#1b1b1a;font:16px/1.6 -apple-system,BlinkMacSystemFont,"
       "'Segoe UI',Inter,Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;padding:46px 20px}"
       "@media(prefers-color-scheme:dark){body{background:#0e0f12;color:#e9eaec}.row{background:#16181d!important;border-color:#262a31!important}.empty{background:#16181d!important;border-color:#262a31!important}.when{color:#9aa0a8!important}.empty h2{color:#e9eaec!important}}"
       ".wrap{max-width:760px;margin:0 auto}"
       ".brand{color:#6b6b68;font-size:.82rem;letter-spacing:.06em;text-transform:uppercase;margin-bottom:24px}"
       ".brand b{color:inherit;font-weight:700;letter-spacing:-.01em;text-transform:none;font-size:1rem}"
       ".brand em{font-style:normal;opacity:.7}"
       ".row{display:flex;justify-content:space-between;align-items:center;gap:14px;background:#fff;"
       "border:1px solid #e7e7e3;border-radius:12px;padding:15px 18px;text-decoration:none;color:inherit;margin-bottom:8px;transition:border-color .12s,transform .12s}"
       ".row:hover{border-color:#4f46e5;transform:translateX(2px)}.row b{font-weight:600}"
       ".when{color:#6b6b68;font-size:.82rem;white-space:nowrap}"
       ".empty{text-align:center;background:#fff;border:1px solid #e7e7e3;border-radius:18px;padding:54px 30px;color:#6b6b68}"
       ".empty h2{color:#1b1b1a;margin:.2em 0 .3em;font-size:1.3rem}.empty p{margin:.4em auto;max-width:46ch}"
       ".dot{width:9px;height:9px;border-radius:50%;background:#4f46e5;margin:0 auto 18px;animation:p 1.4s ease-in-out infinite}"
       "@keyframes p{0%,100%{opacity:.35;transform:scale(.85)}50%{opacity:1;transform:scale(1.15)}}")


def sig(path):
    h = hashlib.sha1()
    try:
        for r, _d, fs in os.walk(path):
            for n in sorted(fs):
                try:
                    s = os.stat(os.path.join(r, n))
                    h.update((r + n).encode("utf-8", "replace"))
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


def index():
    rows = []
    try:
        fs = [n for n in os.listdir(D) if n.lower().endswith((".html", ".htm")) and n != "index.html"]
        fs.sort(key=lambda n: os.stat(os.path.join(D, n)).st_mtime, reverse=True)
        for n in fs:
            t = time.strftime("%b %d, %H:%M", time.localtime(os.stat(os.path.join(D, n)).st_mtime))
            rows.append('<a class="row" href="./%s"><b>%s</b><span class="when">%s</span></a>'
                        % (urllib.parse.quote(n), n, t))
    except OSError:
        pass
    body = "".join(rows) if rows else (
        '<div class="empty"><div class="dot"></div><h2>Waiting for your first artifact</h2>'
        "<p>Keep working in Claude Code. When it writes a plan, review, or explainer here, "
        "it appears on this page automatically.</p></div>")
    return ("<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>htmlize</title><style>" + CSS + "</style><div class=wrap>"
            "<div class=brand><b>htmlize</b> <em>live</em></div>" + body + "</div>" + SNIP)


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
        if rel in ("", "."):
            idx = os.path.join(D, "index.html")
            return self.html_file(idx) if os.path.isfile(idx) else self.send(200, index().encode(), "text/html; charset=utf-8")
        fp = os.path.join(D, rel)
        if not os.path.realpath(fp).startswith(os.path.realpath(D)):
            return self.send(403, b"forbidden", "text/plain")
        if os.path.isfile(fp):
            return self.html_file(fp) if fp.lower().endswith((".html", ".htm")) else self.static(fp)
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
    ap.add_argument("--dir", default=os.environ.get("CLAUDE_HTML_DIR", ".claude-html"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("CLAUDE_HTML_PORT", "7878")))
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
