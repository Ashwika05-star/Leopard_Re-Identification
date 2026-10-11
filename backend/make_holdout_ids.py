"""
Creates gallery_data/holdout_leopard_ids.txt = the leopards used for the 'new leopard, then recognised' demo.
These leopards are kept OUT of the live gallery, exactly like in our holdout test.

  python make_holdout_ids.py --csv data/gallery_data/leopard_final_master.csv \
      --first  data/demo_examples/5_new_leopard_both_uncertain \
      --second data/demo_examples/5_new_leopard_second_photo_recognized \
      --out    data/gallery_data/holdout_leopard_ids.txt
"""
import argparse, os, re
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--csv", required=True)
ap.add_argument("--first", required=True)
ap.add_argument("--second", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()

df = pd.read_csv(a.csv, usecols=["individual_id"])
all_ids = df["individual_id"].dropna().unique()
prefixes = set()
for folder in (a.first, a.second):
    for fn in os.listdir(folder):
        m = re.search(r"([0-9a-f]{8})_\d+\.\w+$", fn)
        if m:
            prefixes.add(m.group(1))
full = []
for p in sorted(prefixes):
    hits = [i for i in all_ids if i.startswith(p)]
    if len(hits) != 1:
        raise SystemExit(f"Prefix {p} matches {len(hits)} leopards - cannot resolve.")
    full.append(hits[0])
os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
open(a.out, "w").write("\n".join(full) + "\n")
print(f"Wrote {len(full)} holdout leopard IDs to {a.out}")
