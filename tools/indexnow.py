"""Meldet geänderte Seiten an IndexNow (Bing, Yandex, Seznam u. a.). Google liest stattdessen die Sitemap.
Aufruf: python tools/indexnow.py [--alle]   (ohne --alle: Dateien aus dem letzten Commit)"""
import glob, json, os, re, subprocess, sys, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "kulturtoepfe.de"
keys = [os.path.basename(p)[:-4] for p in glob.glob(os.path.join(ROOT, "*.txt")) if re.fullmatch(r"[0-9a-f]{32}", os.path.basename(p)[:-4])]
if not keys:
    print("kein IndexNow-Schlüssel gefunden"); sys.exit(0)
key = keys[0]
if "--alle" in sys.argv:
    urls = re.findall(r"<loc>(.*?)</loc>", open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read())
else:
    try:
        geaendert = subprocess.run(["git", "diff", "--name-only", "HEAD~1", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    except subprocess.CalledProcessError:
        geaendert = []
    urls = []
    for f in geaendert:
        if f.endswith(".html") and f != "404.html" and os.path.exists(os.path.join(ROOT, f)):
            urls.append(f"https://{HOST}/" + ("" if f == "index.html" else f))
if not urls:
    print("nichts zu melden"); sys.exit(0)
body = json.dumps({"host": HOST, "key": key, "keyLocation": f"https://{HOST}/{key}.txt", "urlList": urls[:10000]}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow:", r.status, len(urls), "Adressen")
except urllib.error.HTTPError as e:
    print("IndexNow-Fehler:", e.code, e.read()[:300])
