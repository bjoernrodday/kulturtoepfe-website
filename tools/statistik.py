"""Holt die Besucherzahlen von GoatCounter (kulturtoepfe.goatcounter.com) und legt sie in statistik/goatcounter.json ab.
Läuft als GitHub Action mit dem Secret GOATCOUNTER_TOKEN (API-Schlüssel nur mit Leserecht)."""
import datetime, json, os, sys, time, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://kulturtoepfe.goatcounter.com/api/v0"
TOKEN = os.environ.get("GOATCOUNTER_TOKEN")


def hole(pfad, versuche=4):
    """GoatCounter antwortet gelegentlich vorübergehend mit 404 oder 5xx (so am 27.10.2026 bei /stats/total); dann mit Pause erneut versuchen."""
    for n in range(versuche):
        req = urllib.request.Request(API + pfad, headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if n == versuche - 1 or e.code not in (404, 429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError):
            if n == versuche - 1:
                raise
        time.sleep(20 * (n + 1))


def main():
    if not TOKEN:
        sys.exit("GOATCOUNTER_TOKEN fehlt")
    heute = datetime.date.today()
    start = (heute - datetime.timedelta(days=28)).isoformat()
    ende = heute.isoformat()
    q = f"?start={start}&end={ende}"
    out = {"abgerufen": datetime.datetime.utcnow().isoformat(timespec="minutes") + "Z", "zeitraum": [start, ende]}
    for feld, pfad in (("gesamt", "/stats/total" + q), ("seiten", "/stats/hits" + q + "&limit=20"), ("herkunft", "/stats/toprefs" + q + "&limit=20")):
        try:
            out[feld] = hole(pfad)
        except urllib.error.HTTPError as e:
            out[feld] = None
            out.setdefault("fehler", []).append(f"{pfad}: HTTP {e.code} {e.read()[:300].decode('utf-8', 'replace')}")
        except Exception as e:
            out[feld] = None
            out.setdefault("fehler", []).append(f"{pfad}: {type(e).__name__}: {e}")
    os.makedirs(os.path.join(ROOT, "statistik"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "statistik", "goatcounter.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("fehler" in out and out["fehler"] or "ok")


if __name__ == "__main__":
    main()
