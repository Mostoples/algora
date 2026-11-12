"""Download Sketchfab models (glb) + write CREDITS.json (CC-BY attribution).
python tools/sf_download.py   -> downloads everything in ASSETS into assets/sketchfab/<key>.glb"""
import json, os, sys, urllib.request, zipfile, io, socket
socket.setdefaulttimeout(60)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOK = os.environ.get("SKETCHFAB_TOKEN") or open(os.path.join(ROOT, "tools", ".sketchfab_token")).read().strip()
OUT = os.path.join(ROOT, "assets", "sketchfab")
ASSETS = {
    "sofa": "ac92f6e97eaa43c4ad6cb8f7c65ac43f",
    "monstera": "1ab9bf841df04c07b1819be596327629",
    "pothos": "e9832f38484f4f85b3f9081b51fa3799",
    "palm": "92f75abd656049608248cf76a8c88136",
    "armchair_set": "fcce92a09de84456a071ea6117b57cbc",
    "maple": "b6eb627413ed40fdb8b0a1e1c9038fa9",
    "lounge": "cd2c67402ea8426c90d0fcebb0fa60b4",
    "bench": "caa4515e36444e4c8c100296463e83c1",
    "dining": "61275205fe084208887d74876919aac6",
    "phone": "4328dea00e47497dbeac73c556121bc9",
    "prayer_plant": "236bd37aa47b43e49c34360b3d5b854f",
}
def get(url, auth=True):
    h = {"Authorization": "Token " + TOK} if auth else {}
    return urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=120)
os.makedirs(OUT, exist_ok=True)
cred_path = os.path.join(OUT, "CREDITS.json")
credits = json.load(open(cred_path)) if os.path.exists(cred_path) else {}
for key, uid in ASSETS.items():
    if sys.argv[1:] and key not in sys.argv[1:]:
        continue
    dst = os.path.join(OUT, key + ".glb")
    try:
        info = json.load(get(f"https://api.sketchfab.com/v3/models/{uid}"))
        credits[key] = {"name": info["name"], "author": info["user"]["displayName"], "user": info["user"]["username"],
                        "license": (info.get("license") or {}).get("label"), "url": info["viewerUrl"]}
        if os.path.exists(dst) or os.path.isdir(dst[:-4]):
            print("skip", key); continue
        d = json.load(get(f"https://api.sketchfab.com/v3/models/{uid}/download"))
        if "glb" in d:
            open(dst, "wb").write(get(d["glb"]["url"], False).read())
            print("glb", key, os.path.getsize(dst) // 1024, "KB")
        else:
            z = zipfile.ZipFile(io.BytesIO(get(d["gltf"]["url"], False).read()))
            z.extractall(dst[:-4]); print("gltf", key)
    except Exception as e:
        print("FAIL", key, e)
json.dump(credits, open(cred_path, "w"), indent=1, ensure_ascii=False)
