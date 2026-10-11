"""
Tests app.py (all endpoints) and verify_demo_set.py on synthetic data with stand-in AI models.
Run:  python test_app.py
"""
import io, os, sys, types, shutil, tempfile
import cv2, numpy as np, pandas as pd

import ivp_core, chatbot_logic
from pipeline import Pipeline
from smoke_test import make_pattern, make_sparse_pattern, make_photo, StubAI

tmp = tempfile.mkdtemp()
imgs, viz, ups = [os.path.join(tmp, d) for d in ("images", "viz", "uploads")]
for d in (imgs, viz, ups):
    os.makedirs(d)
rng = np.random.RandomState(3)
ids = {"L1": "aaaaaaaa-0000-0000-0000-000000000001", "L2": "bbbbbbbb-0000-0000-0000-000000000002",
       "N": "cccccccc-0000-0000-0000-000000000003"}
rows, feats = [], {}


def add(k, j, pat):
    photo, (x, y, w, h) = make_photo(pat, rng)
    fn = f"{k}_{j}.jpg"
    path = os.path.join(imgs, fn)
    cv2.imwrite(path, photo)
    rows.append(dict(filename=fn, individual_id=ids[k], bbox_x=x, bbox_y=y, bbox_width=w, bbox_height=h,
                     viewpoint="left", leopard_name=f"Leopard {k}"))
    feats[f"{fn}|{ids[k]}"] = ivp_core.extract_keypoints(ivp_core.prep_gray(cv2.imread(path), (x, y, w, h)))
    return fn


p1, p2 = make_pattern(11), make_pattern(12)
f_L1 = [add("L1", j, p1) for j in range(3)]
f_L2 = [add("L2", j, p2) for j in range(3)]
pn = make_sparse_pattern(41)
f_N = [add("N", j, pn) for j in range(2)]
df = pd.DataFrame(rows)
hash_index = ivp_core.load_or_build_hash_index([(r.filename, r.individual_id) for r in df.itertuples()], imgs, None)
ai = StubAI()
ai.identity_answer = (ids["L1"], 0.9)
pipe = Pipeline(df, [ids["N"]], feats, hash_index, imgs, viz, ai)

fake = types.ModuleType("backend")
fake.pipeline, fake.VIEWPOINTS, fake.VIZ_DIR = pipe, ["back", "down", "front", "left", "right"], viz
fake.chatbot_reply = lambda q: chatbot_logic.reply(q, pipe.gallery_df)
fake.chatbot_respond = lambda q: chatbot_logic.respond(q, pipe.gallery_df)
sys.modules["backend"] = fake
os.environ["PANTHERA_UPLOAD_DIR"] = ups
import app as appmod
client = appmod.app.test_client()

failed = 0
def check(c, label):
    global failed
    print(("PASS  " if c else "FAIL  ") + label)
    failed += 0 if c else 1

def post_image(fn, **extra):
    with open(os.path.join(imgs, fn), "rb") as f:
        return client.post("/analyze", data={"image": (io.BytesIO(f.read()), fn), **extra}, content_type="multipart/form-data")

# --- endpoints ---
h = client.get("/health").get_json()
check(h["status"] == "ok" and h["live_leopards"] == 2, f"/health ok, live leopards = {h['live_leopards']} (holdout excluded)")

r = post_image(f_L1[0]).get_json()
check(r["status"] == "success" and r["decision"] == "MATCH" and r["leopard"]["name"] == "Leopard L1", "/analyze: known photo -> MATCH with leopard name")
for key in ("uploaded_image_url", "matched_image_url", "keypoint_image_url", "upload_id"):
    check(key in r, f"/analyze response has {key}")
for key in ("uploaded_image_url", "matched_image_url", "keypoint_image_url"):
    resp = client.get(r[key])
    check(resp.status_code == 200 and resp.data[:2] == b"\xff\xd8", f"GET {key} serves a real JPEG")

bad = client.post("/analyze", data={"image": (io.BytesIO(b"hello"), "x.txt")}, content_type="multipart/form-data")
check(bad.status_code == 400, "/analyze rejects non-image file types")
check(client.post("/analyze", data={}).status_code == 400, "/analyze rejects a request with no file")
check(post_image(f_L1[0], viewpoint="sideways").status_code == 400, "/analyze rejects an invalid viewpoint")
check(client.get("/image?path=uploads/../../etc/passwd").status_code == 404, "path traversal blocked on /image")

ai.identity_answer = (ids["L1"], 0.2)
n = post_image(f_N[0]).get_json()
check(n["decision"] == "NEW_LEOPARD" and "registration" in n and "path" not in n["registration"], "/analyze: holdout photo -> NEW_LEOPARD (server path not leaked)")
c = client.post("/confirm-new", json={"upload_id": n["upload_id"]}).get_json()
check(c["status"] == "success", "/confirm-new registers the new leopard")
check(client.post("/confirm-new", json={"upload_id": n["upload_id"]}).status_code == 404, "/confirm-new cannot be replayed")
n2 = post_image(f_N[1]).get_json()
check(n2["decision"] == "MATCH" and n2["leopard"]["id"] == n["registration"]["leopard_id"], f"second photo recognised after registering (score {n2['ivp']['verified_match_points']})")
check(client.get(n2["matched_image_url"]).status_code == 200, "matched image of a newly registered leopard is served")
check("IVP" in client.post("/chat", json={"question": "What is IVP?"}).get_json()["answer"], "/chat answers")
r = client.post("/chat", json={"question": "What do leopards eat?"}).get_json()
check("antelope" in r["answer"].lower() or "prey" in r["answer"].lower(), "/chat answers leopard-fact questions")
check(isinstance(r["suggestions"], list) and 1 <= len(r["suggestions"]) <= 3, "/chat returns follow-up suggestions")
check(client.post("/chat", json={}).status_code == 400, "/chat rejects empty question")

# --- verify_demo_set ---
import verify_demo_set as V
pipe2 = Pipeline(df, [ids["N"]], dict(feats), dict(hash_index), imgs, viz, ai)
demo = os.path.join(tmp, "demo")
for d in ("1_confident_match_both_agree", "1_confident_match_ivp_alone", "2_possible_upgraded_by_ai",
          "5_new_leopard_both_uncertain", "5_new_leopard_second_photo_recognized"):
    os.makedirs(os.path.join(demo, d))
cp = lambda fn, d, name: shutil.copy(os.path.join(imgs, fn), os.path.join(demo, d, name))
cp(f_L1[0], "1_confident_match_both_agree", f"aaaaaaaa_{f_L1[0][3:4].zfill(12)}.jpg")
cp(f_L2[0], "1_confident_match_ivp_alone", "bbbbbbbb_000000000002.jpg")
cp(f_L1[1], "2_possible_upgraded_by_ai", "aaaaaaaa_000000000009.jpg")       # deliberately mislabelled folder
cp(f_N[0], "5_new_leopard_both_uncertain", "cccccccc_000000000010.jpg")
cp(f_N[1], "5_new_leopard_second_photo_recognized", "cccccccc_000000000011.jpg")

ai.identity_answer = (ids["L1"], 0.9)
rows_a = V.check_single(pipe2, demo, "1_confident_match_both_agree", V.EXPECTED["1_confident_match_both_agree"])
rows_b = V.check_single(pipe2, demo, "1_confident_match_ivp_alone", V.EXPECTED["1_confident_match_ivp_alone"])
rows_c = V.check_single(pipe2, demo, "2_possible_upgraded_by_ai", V.EXPECTED["2_possible_upgraded_by_ai"])
check(rows_a and rows_a[0]["ok"], "verifier: correctly-filed 'both agree' image passes")
check(rows_b and rows_b[0]["ok"], "verifier: correctly-filed 'IVP alone' image passes")
check(rows_c and not rows_c[0]["ok"], "verifier: a mis-filed image is FLAGGED as not reproducing")
ai.identity_answer = (ids["L1"], 0.2)
rows_p = V.check_pairs(pipe2, demo)
check(rows_p and rows_p[0]["ok"], f"verifier: new-then-recognised pair reproduces ({rows_p[0]['got'] if rows_p else None})")
check(all(not v.startswith(imgs) for v in pipe2.path_of.values()) and pipe2.path_of, "verifier registered photos in a temp folder, not the real images folder")
check(len([f for f in os.listdir(imgs) if f.endswith(".jpg")]) == len(df), "real images folder still holds exactly the original photos")

shutil.rmtree(tmp, ignore_errors=True)
print(f"\n{'ALL CHECKS PASSED' if failed == 0 else str(failed) + ' CHECK(S) FAILED'}")
sys.exit(failed)
