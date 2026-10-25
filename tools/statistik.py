"""Holt die Besucherzahlen von GoatCounter (kulturtoepfe.goatcounter.com) und legt sie in statistik/goatcounter.json ab.
Läuft als GitHub Action mit dem Secret GOATCOUNTER_TOKEN (API-Schlüssel nur mit Leserecht)."""
import datetime, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://kulturtoepfe.goatcounter.com/api/v0"
TOKEN = os.environ.get("GOATCOUNTER_TOKEN")


def hole(pfad):
    req = urllib.request.Request(API + pfad, headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    if not TOKEN:
        sys.exit("GOATCOUNTER_TOKEN fehlt")
    heute = datetime.date.today()
    start = (heute - datetime.timedelta(days=28)).isoformat()
    ende = heute.isoformat()
    q = f"?start={start}&end={ende}"
    out = {"abgerufen": datetime.datetime.utcnow().isoformat(timespec="minutes") + "Z", "zeitraum": [start, ende]}
    out["gesamt"] = hole("/stats/total" + q)
    out["seiten"] = hole("/stats/hits" + q + "&limit=20")
    out["herkunft"] = hole("/stats/toprefs" + q + "&limit=20")
    os.makedirs(os.path.join(ROOT, "statistik"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "statistik", "goatcounter.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ok", out["gesamt"].get("total"))


if __name__ == "__main__":
    main()
