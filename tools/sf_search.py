import json, sys, urllib.request, urllib.parse, os
TOK = open(os.path.join(os.path.dirname(__file__), ".sketchfab_token")).read().strip()
def get(url):
    r = urllib.request.Request(url, headers={"Authorization": "Token " + TOK})
    return json.load(urllib.request.urlopen(r, timeout=30))
for q in sys.argv[1:]:
    p = urllib.parse.urlencode({"type": "models", "q": q, "downloadable": "true", "sort_by": "-likeCount", "count": 8, "max_face_count": 300000})
    d = get("https://api.sketchfab.com/v3/search?" + p)
    print("==", q)
    for m in d["results"]:
        print(f'  {m["uid"]} faces={m.get("faceCount")} likes={m.get("likeCount")} lic={(m.get("license") or {}).get("label","?")[:12]} | {m["name"][:50]}')
