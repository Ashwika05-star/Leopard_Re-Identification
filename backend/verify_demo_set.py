"""
Re-runs EVERY demo image through the real pipeline and checks it lands where its folder says it should.
Run this on your real data before the demo:

    python verify_demo_set.py --demo data/demo_examples            # check everything
    python verify_demo_set.py --demo data/demo_examples --prune    # also MOVE failures into demo_examples/_failed/

Nothing is ever deleted; --prune only moves files.
"""
import argparse, os, re, shutil, tempfile
import pandas as pd
import ivp_core

EXPECTED = {
    "1_confident_match_both_agree": {"confident_both_agree"},
    "1_confident_match_ivp_alone": {"confident_ivp_alone"},
    "2_possible_upgraded_by_ai": {"possible_upgraded_by_ai"},
    "3_possible_ai_disagrees": {"possible_ivp_led"},
    "4_low_ivp_ai_confident": {"possible_ai_led"},
}


def check_single(pipeline, demo_dir, folder, ok_paths, limit=None):
    rows, d = [], os.path.join(demo_dir, folder)
    if not os.path.isdir(d):
        return rows
    files = sorted(f for f in os.listdir(d) if f.lower().endswith((".jpg", ".jpeg", ".png")))
    for fn in files[:limit]:
        p = os.path.join(d, fn)
        truth = pipeline.hash_index.get(ivp_core.md5_file(p))
        r = pipeline.analyze_photo(p)
        got_path = r.get("path")
        got_id = (r.get("leopard") or {}).get("id")
        ok = r.get("status") == "success" and got_path in ok_paths and truth is not None and got_id == truth[1]
        rows.append(dict(folder=folder, file=fn, ok=ok, expected=sorted(ok_paths)[0], got=got_path,
                         ivp_points=(r.get("ivp") or {}).get("verified_match_points"),
                         correct_leopard=(truth is not None and got_id == truth[1]),
                         known_photo=truth is not None))
    return rows


def check_pairs(pipeline, demo_dir):
    """New leopard first photo -> register -> second photo must be recognised as that new leopard."""
    rows = []
    fa = os.path.join(demo_dir, "5_new_leopard_both_uncertain")
    fb = os.path.join(demo_dir, "5_new_leopard_second_photo_recognized")
    if not (os.path.isdir(fa) and os.path.isdir(fb)):
        return rows
    pipeline.registered_dir = tempfile.mkdtemp()        # keep the real data folders untouched
    key = lambda fn: (re.search(r"([0-9a-f]{8})_\d+\.\w+$", fn) or [None, None])[1]
    second = {key(f): f for f in os.listdir(fb)}
    for f1 in sorted(os.listdir(fa)):
        k = key(f1)
        if k not in second:
            continue
        r1 = pipeline.analyze_photo(os.path.join(fa, f1))
        ok1 = r1.get("decision") == "NEW_LEOPARD"
        ok2, got2 = False, None
        if ok1:
            reg = r1["registration"]
            pipeline.register_new_leopard(os.path.join(fa, f1), reg["leopard_id"], reg["leopard_name"],
                                          reg["viewpoint"], reg["category"])
            r2 = pipeline.analyze_photo(os.path.join(fb, second[k]))
            got2 = r2.get("decision")
            ok2 = got2 in ("MATCH", "POSSIBLE_MATCH") and (r2.get("leopard") or {}).get("id") == reg["leopard_id"]
        rows.append(dict(folder="5_new_then_recognised", file=f"{f1} + {second[k]}", ok=ok1 and ok2,
                         expected="NEW then match", got=f"{r1.get('decision')} then {got2}",
                         ivp_points=None, correct_leopard=ok2, known_photo=True))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", required=True)
    ap.add_argument("--limit", type=int, default=None, help="max images per folder (for a quick check)")
    ap.add_argument("--prune", action="store_true")
    a = ap.parse_args()
    import backend                                       # loads data + models
    rows = []
    for folder, ok_paths in EXPECTED.items():
        rows += check_single(backend.pipeline, a.demo, folder, ok_paths, a.limit)
    rows += check_pairs(backend.pipeline, a.demo)        # last: it modifies the in-memory gallery
    df = pd.DataFrame(rows)
    out = os.path.join(a.demo, "verification_report.csv")
    df.to_csv(out, index=False)
    print("\n=== Demo-set verification ===")
    print(df.groupby("folder")["ok"].agg(["sum", "count"]).rename(columns={"sum": "reproduced", "count": "total"}))
    bad = df[~df["ok"]]
    print(f"\n{len(df) - len(bad)}/{len(df)} demo items reproduce as labelled. Report: {out}")
    if a.prune and len(bad):
        failed_dir = os.path.join(a.demo, "_failed")
        for r in bad.itertuples():
            if r.folder.startswith("5_new_then"):
                continue
            os.makedirs(os.path.join(failed_dir, r.folder), exist_ok=True)
            shutil.move(os.path.join(a.demo, r.folder, r.file), os.path.join(failed_dir, r.folder, r.file))
        print(f"Moved {len(bad)} non-reproducing items to {failed_dir} (nothing deleted).")


if __name__ == "__main__":
    main()
