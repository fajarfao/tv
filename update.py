import json, os, urllib.request, urllib.error, datetime
KEY = os.environ["FD_KEY"].strip()
BASE = "https://api.football-data.org/v4"
TEAM = 81

def get(path):
    req = urllib.request.Request(BASE + path, headers={"X-Auth-Token": KEY})
    try:
        return json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        print("GAGAL", path, e.code, e.read().decode()[:300])
        raise

def nm(t):
    return t.get("shortName") or t["name"]

def opp(m):
    home = m["homeTeam"]["id"] == TEAM
    return nm(m["awayTeam"] if home else m["homeTeam"]), home

table = [[nm(r["team"]), r["won"], r["lost"], r["draw"], r["points"]]
         for r in get("/competitions/PD/standings")["standings"][0]["table"]]

fixtures = []
for m in get("/teams/%d/matches?status=SCHEDULED,TIMED" % TEAM)["matches"][:6]:
    o, home = opp(m)
    fixtures.append([m["utcDate"], "vs" if home else "@", o, m["competition"]["code"]])

results = []
for m in reversed(get("/teams/%d/matches?status=FINISHED" % TEAM)["matches"][-5:]):
    o, home = opp(m)
    ft = m["score"]["fullTime"]
    results.append([o, "H" if home else "T", ft["home"], ft["away"]])

wib = datetime.timezone(datetime.timedelta(hours=7))
out = {"updated": datetime.datetime.now(wib).strftime("%d/%m %H:%M WIB"),
       "table": table, "fixtures": fixtures, "results": results}
json.dump(out, open("data.json", "w", encoding="utf-8"), ensure_ascii=False)
print("OK", len(table), len(fixtures), len(results))
