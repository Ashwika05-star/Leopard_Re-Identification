"""
Smoke test on SYNTHETIC data (random spot patterns). It checks the plumbing and decision logic
of pipeline.py / decision.py / ivp_core.py / chatbot_logic.py. It does NOT measure real accuracy.
Run:  python smoke_test.py
"""
import os, shutil, tempfile
import cv2, numpy as np, pandas as pd

import ivp_core, decision, chatbot_logic
from pipeline import Pipeline

BASE_BG = (150, 175, 205)


def make_pattern(seed, h=700, w=1000):
    rng = np.random.RandomState(seed)
    img = np.full((h, w, 3), BASE_BG, np.uint8)
    for _ in range(260):
        c = (int(rng.randint(30, w - 30)), int(rng.randint(30, h - 30)))
        ax = (int(rng.randint(8, 22)), int(rng.randint(8, 22)))
        ang = int(rng.randint(0, 180))
        cv2.ellipse(img, c, ax, ang, 0, 360, (30, 40, 60), -1)
        if rng.rand() < 0.5:
            cv2.ellipse(img, c, (ax[0] // 2, ax[1] // 2), ang, 0, 360, BASE_BG, -1)
    return cv2.GaussianBlur(img, (0, 0), 1.2)


def make_stroke_pattern(seed, h=700, w=1000):
    """A different texture family (curved strokes) - used for the holdout leopard."""
    rng = np.random.RandomState(seed)
    img = np.full((h, w, 3), BASE_BG, np.uint8)
    for _ in range(220):
        start = np.array([rng.randint(50, w - 50), rng.randint(50, h - 50)])
        pts = np.cumsum(rng.randint(-25, 26, (5, 2)), axis=0) + start
        pts = np.clip(pts, 5, [w - 5, h - 5]).astype(np.int32)
        cv2.polylines(img, [pts.reshape(-1, 1, 2)], False, (35, 45, 70), int(rng.randint(3, 9)))
    return cv2.GaussianBlur(img, (0, 0), 1.2)


def make_dot_pattern(seed, h=700, w=1000):
    """A third texture family (small irregular dots) - used for the 'unknown new leopard' photo."""
    rng = np.random.RandomState(seed)
    img = np.full((h, w, 3), BASE_BG, np.uint8)
    for _ in range(900):
        c = (int(rng.randint(10, w - 10)), int(rng.randint(10, h - 10)))
        col = tuple(int(v) for v in rng.randint(20, 90, 3))
        cv2.circle(img, c, int(rng.randint(3, 7)), col, -1)
    return cv2.GaussianBlur(img, (0, 0), 1.0)


def make_sparse_pattern(seed, h=700, w=1000):
    """Few, large, distinctive blobs -> few keypoints -> almost no accidental matches (used for 'unseen' leopards)."""
    rng = np.random.RandomState(seed)
    img = np.full((h, w, 3), BASE_BG, np.uint8)
    for _ in range(28):
        c = (int(rng.randint(60, w - 60)), int(rng.randint(60, h - 60)))
        r = int(rng.randint(25, 55))
        cv2.circle(img, c, r, tuple(int(v) for v in rng.randint(20, 80, 3)), -1)
        cv2.circle(img, (c[0] + int(rng.randint(-8, 9)), c[1] + int(rng.randint(-8, 9))), r // 2,
                   tuple(int(v) for v in rng.randint(120, 220, 3)), -1)
    return cv2.GaussianBlur(img, (0, 0), 1.5)


def make_photo(pattern, rng, H=1000, W=1400):
    bg = np.full((H, W, 3), (120, 140, 150), np.int16) + rng.randint(-6, 7, (H, W, 3))
    ph, pw = pattern.shape[:2]
    M = cv2.getRotationMatrix2D((pw / 2, ph / 2), rng.uniform(-6, 6), rng.uniform(0.92, 1.08))
    warped = cv2.warpAffine(pattern, M, (pw, ph), borderValue=BASE_BG)
    warped = cv2.convertScaleAbs(warped, alpha=rng.uniform(0.85, 1.15), beta=rng.uniform(-10, 10))
    x0, y0 = int(rng.randint(80, W - pw - 80)), int(rng.randint(40, H - ph - 40))
    bg[y0:y0 + ph, x0:x0 + pw] = warped
    bg = np.clip(bg + rng.randint(-4, 5, bg.shape), 0, 255).astype(np.uint8)
    return bg, (x0, y0, pw, ph)


class StubAI:
    """Stands in for the neural networks; scenario tests set .identity_answer."""
    identity_answer = (None, 0.2)
    def validate(self, crop): return True, 0.99
    def category(self, crop): return "normal", 0.9
    def viewpoint(self, crop): return "left", 0.9
    def identity(self, crop): return self.identity_answer


def check(cond, label):
    print(("PASS  " if cond else "FAIL  ") + label)
    if not cond:
        check.failed += 1
check.failed = 0


def main():
    tmp = tempfile.mkdtemp()
    imgs, viz, ups = [os.path.join(tmp, d) for d in ("images", "viz", "uploads")]
    for d in (imgs, viz, ups): os.makedirs(d)

    plan = {"L1": 3, "L2": 3, "L3": 3, "L4": 3, "L6": 1, "L5": 3}   # photos per leopard; L5 = holdout (built last)
    ids = {k: f"{k}-0000-0000-0000-000000000000" for k in plan}
    patterns, rows, feats, files = {}, [], {}, {}
    rng = np.random.RandomState(0)

    def write_reload(fn, photo):
        path = os.path.join(imgs, fn)
        cv2.imwrite(path, photo)
        return cv2.imread(path)          # what a real gallery file looks like after JPEG round-trip

    def cross_max(feat):
        return max([ivp_core.verified_matches(feat, f) for f in feats.values()] or [0])

    def best_of(gen, n_tries, n_photos, eval_feats, seed0):
        best = None
        for s in range(seed0, seed0 + n_tries):
            pat = gen(s)
            photos_raw = [make_photo(pat, rng) for _ in range(n_photos)]
            ep = os.path.join(tmp, "eval.jpg"); cv2.imwrite(ep, photos_raw[0][0])
            f0 = ivp_core.extract_keypoints(ivp_core.prep_gray(cv2.imread(ep), photos_raw[0][1]))
            cm = max([ivp_core.verified_matches(f0, f) for f in eval_feats] or [0]) if f0 is not None else 99
            if best is None or cm < best[0]:
                best = (cm, pat, photos_raw)
            if cm <= 2:
                break
        return best

    seed = 1
    for k in plan:
        if k == "L5":
            cm, pat, raw = best_of(make_sparse_pattern, 30, plan[k], list(feats.values()), 1000)
            print(f"  fixture: holdout leopard chosen with best accidental score {cm}")
            photos = [(f"{k}_{j}.jpg", write_reload(f"{k}_{j}.jpg", ph), bb) for j, (ph, bb) in enumerate(raw)]
            patterns[k] = pat
            for fn, photo, (x, y, w, h) in photos:
                rows.append(dict(filename=fn, individual_id=ids[k], bbox_x=x, bbox_y=y, bbox_width=w, bbox_height=h,
                                 viewpoint="left", category="normal", leopard_name=f"Leopard {k}"))
                feats[f"{fn}|{ids[k]}"] = ivp_core.extract_keypoints(ivp_core.prep_gray(photo, (x, y, w, h)))
                files.setdefault(k, []).append(fn)
            continue
        limit = 6
        for attempt in range(12):
            pat = (make_stroke_pattern if k == 'L5' else make_pattern)(seed); seed += 1
            photos = []
            for j in range(plan[k]):
                photo, bbox = make_photo(pat, rng)
                photos.append((f"{k}_{j}.jpg", write_reload(f"{k}_{j}.jpg", photo), bbox))
            f0 = ivp_core.extract_keypoints(ivp_core.prep_gray(photos[0][1], photos[0][2]))
            cm = cross_max(f0) if f0 is not None else 99
            if cm < limit:
                break
        patterns[k] = pat
        for fn, photo, (x, y, w, h) in photos:
            rows.append(dict(filename=fn, individual_id=ids[k], bbox_x=x, bbox_y=y, bbox_width=w, bbox_height=h,
                             viewpoint="left", category="normal", leopard_name=f"Leopard {k}"))
            feats[f"{fn}|{ids[k]}"] = ivp_core.extract_keypoints(ivp_core.prep_gray(photo, (x, y, w, h)))
            files.setdefault(k, []).append(fn)
    df = pd.DataFrame(rows)
    check(all(v is not None for v in feats.values()), "keypoints extracted for every synthetic gallery photo")
    hash_index = ivp_core.load_or_build_hash_index([(r.filename, r.individual_id) for r in df.itertuples()],
                                                   imgs, os.path.join(tmp, "hashes.pkl"))
    check(len(hash_index) == len(df), "hash index built and cached")
    check(os.path.exists(os.path.join(tmp, "hashes.pkl")), "hash cache file written")

    def new_pipe(holdout=()):
        return Pipeline(df, holdout, dict(feats), dict(hash_index), imgs, viz, StubAI_inst)
    StubAI_inst = StubAI()

    def upload(fn):
        p = os.path.join(ups, f"up_{fn}")
        shutil.copy(os.path.join(imgs, fn), p)      # byte-identical copy of a dataset photo
        return p

    # ---- 1. known photo, AI agrees -> confident_both_agree, never matches itself
    P = new_pipe(holdout=[ids["L5"]])
    StubAI_inst.identity_answer = (ids["L1"], 0.9)
    r = P.analyze_photo(upload(files["L1"][0]))
    check(r["status"] == "success" and r["decision"] == "MATCH" and r["path"] == "confident_both_agree",
          f"known photo + AI agrees -> confident_both_agree (got {r.get('path')}, score {r['ivp']['verified_match_points']})")
    check(r["leopard"]["id"] == ids["L1"], "matched the correct leopard")
    check(r["ivp"]["matched_photo_file"] != files["L1"][0], "did NOT match the photo against itself")
    check(r.get("viz_file") and os.path.getsize(os.path.join(viz, r["viz_file"])) > 1000, "keypoint-line image generated")
    check(r["viewpoint"]["source"] == "dataset_record", "used the dataset viewpoint label for a known photo")

    # ---- 2. AI disagrees -> confident_ivp_alone
    StubAI_inst.identity_answer = (ids["L3"], 0.9)
    r = P.analyze_photo(upload(files["L2"][0]))
    check(r["path"] == "confident_ivp_alone" and r["leopard"]["id"] == ids["L2"], f"AI disagrees -> confident_ivp_alone (got {r['path']})")

    # ---- 3. holdout leopard -> NEW, register, then second photo recognised
    StubAI_inst.identity_answer = (ids["L1"], 0.2)
    r = P.analyze_photo(upload(files["L5"][0]))
    check(r["decision"] == "NEW_LEOPARD" and "registration" in r, f"holdout leopard -> NEW_LEOPARD (got {r['decision']}, ivp {r['ivp']['verified_match_points']})")
    reg = r["registration"]
    P.register_new_leopard(upload(files["L5"][0]), reg["leopard_id"], reg["leopard_name"], reg["viewpoint"], reg["category"])
    StubAI_inst.identity_answer = (ids["L1"], 0.2)
    r2 = P.analyze_photo(upload(files["L5"][1]))
    check(r2["decision"] == "MATCH" and r2["leopard"]["id"] == reg["leopard_id"],
          f"second photo of the just-registered leopard is recognised (got {r2['decision']}, score {r2['ivp']['verified_match_points']})")
    r3 = P.analyze_photo(upload(files["L5"][0]))
    check(r3["decision"] == "MATCH" and r3["path"] == "exact_record" and r3["leopard"]["id"] == reg["leopard_id"],
          f"re-uploading the registered photo itself -> exact_record (got {r3['path']})")

    # ---- 4. single-photo leopard uploaded exactly -> exact_record
    r = P.analyze_photo(upload(files["L6"][0]))
    check(r["path"] == "exact_record" and r["leopard"]["id"] == ids["L6"], f"single-photo leopard -> exact_record (got {r['path']})")

    # ---- 5. brand-new pattern, AI unsure -> NEW ; AI very sure -> possible_ai_led
    fp = os.path.join(ups, "fresh.jpg")
    best_s, best_cm = 500, 99
    for s in range(500, 530):
        fr_img, _ = make_photo(make_sparse_pattern(s), np.random.RandomState(5))
        cv2.imwrite(fp, fr_img)
        ff = ivp_core.extract_keypoints(ivp_core.prep_gray(cv2.imread(fp), None))
        cm = max(ivp_core.verified_matches(ff, f) for f in feats.values()) if ff is not None else 99
        if cm < best_cm:
            best_s, best_cm = s, cm
        if cm <= 2:
            break
    fr_img, _ = make_photo(make_sparse_pattern(best_s), np.random.RandomState(5))
    cv2.imwrite(fp, fr_img)
    print(f"  fixture: unknown photo chosen with best accidental score {best_cm}")
    StubAI_inst.identity_answer = (ids["L1"], 0.2)
    r = P.analyze_photo(fp)
    check(r["decision"] == "NEW_LEOPARD" and any("bounding box" in w.lower() for w in r["warnings"]),
          f"unknown pattern, AI unsure -> NEW_LEOPARD with bbox warning (got {r['decision']}, ivp {r['ivp']['verified_match_points']})")
    StubAI_inst.identity_answer = (ids["L1"], 0.95)
    r = P.analyze_photo(fp)
    check(r["path"] == "possible_ai_led" and r["decision"] == "POSSIBLE_MATCH", f"AI very sure, IVP nothing -> possible_ai_led (got {r['path']})")

    # ---- 6. not a leopard
    class NoLeopard(StubAI):
        def validate(self, crop): return False, 0.1
    P2 = Pipeline(df, [], dict(feats), dict(hash_index), imgs, viz, NoLeopard())
    r = P2.analyze_photo(fp)
    check(r["status"] == "rejected", "validator rejects a non-leopard")

    # ---- 7. photo with no bbox, fresh capture of a known leopard (informational)
    newshot, _ = make_photo(patterns["L2"], np.random.RandomState(77))
    sp = os.path.join(ups, "shot.jpg"); cv2.imwrite(sp, newshot)
    StubAI_inst.identity_answer = (ids["L2"], 0.9)
    r = P.analyze_photo(sp)
    print(f"INFO  fresh whole-photo upload of L2 (no bbox): decision={r['decision']} path={r['path']} ivp={r['ivp']['verified_match_points']}")

    # ---- 8. decision boundaries
    D = decision.decide
    check(D(20, "a", "a", .1)["decision"] == "MATCH", "boundary: 20 points is a confident match")
    check(D(19, "a", "b", .9)["path"] == "possible_ivp_led", "boundary: 19 points, AI disagrees -> possible")
    check(D(19, "a", "a", .5)["path"] == "possible_upgraded_by_ai", "boundary: 19 points, AI agrees at 0.5 -> upgraded")
    check(D(19, "a", "a", .49)["path"] == "possible_ivp_led", "boundary: AI agrees but only 0.49 -> not upgraded")
    check(D(6, "a", "b", .1)["decision"] == "POSSIBLE_MATCH", "boundary: 6 points is the uncertain zone")
    check(D(5, "a", "b", .7)["path"] == "possible_ai_led", "boundary: 5 points, AI 0.7 -> AI-led")
    check(D(5, "a", "b", .69)["decision"] == "NEW_LEOPARD", "boundary: 5 points, AI 0.69 -> new leopard")

    # ---- 9. chatbot
    for q, must in [("What is IVP?", "IVP"), ("What does RANSAC do?", "RANSAC"), ("How accurate is it?", "73.7"),
                    ("What's the weather today?", "specifically built")]:
        check(must in chatbot_logic.respond(q, P.gallery_df), f"chatbot: '{q}'")
    check("Leopard L1" in chatbot_logic.respond(f"Tell me about {ids['L1']}", P.gallery_df), "chatbot: leopard lookup by ID")

    shutil.rmtree(tmp)
    print(f"\n{'ALL CHECKS PASSED' if check.failed == 0 else str(check.failed) + ' CHECK(S) FAILED'}")
    raise SystemExit(check.failed)


if __name__ == "__main__":
    main()
