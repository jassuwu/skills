#!/bin/sh
cd "${1:-.claude-html}" 2>/dev/null || exit 0
{ printf '<!doctype html><meta charset=utf-8><meta http-equiv=refresh content=2><title>htmlize</title><style>body{font:16px/1.6 system-ui,sans-serif;max-width:720px;margin:40px auto;padding:0 16px}a{display:flex;justify-content:space-between;gap:12px;padding:13px 15px;margin:7px 0;border:1px solid #8883;border-radius:11px;text-decoration:none;color:inherit}a:hover{border-color:#4f46e5}small{color:#8889;font:.8rem ui-monospace,monospace}</style>'
  n=0
  for f in $(ls -t -- *.html 2>/dev/null); do [ "$f" = index.html ] && continue; [ -f "$f" ] || continue; n=1
    t=$(sed -n 's/.*<title>\(.*\)<\/title>.*/\1/p' "$f" | head -1); [ -z "$t" ] && t=$f
    printf '<a href="./%s"><span>%s</span><small>%s</small></a>' "$f" "$t" "$f"; done
  [ "$n" = 0 ] && printf '<p style=color:#888>Waiting for the first artifact…</p>'
  true
} > ".ix.$$" && mv ".ix.$$" index.html
