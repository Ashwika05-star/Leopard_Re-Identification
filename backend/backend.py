"""
Loads everything (data + models) once and exposes `pipeline`, used by app.py.

Folder layout expected under PANTHERA_DATA_DIR (default ./data):
  models/        category_classifier_BEST.pth, viewpoint_classifier_BEST.pth, identity_classifier_v2_BEST.pth,
                 resnet_leopard_classifier.pkl, resnet_classifier_threshold.npy
  gallery_data/  leopard_final_master.csv, sift_shards/shard_*.pkl,
                 holdout_leopard_ids.txt (optional), identity_classes.txt (optional)
  images/        the original photos (000000000001.jpg, ...)
"""
import os
import glob
import pickle
import random
import time

import cv2
import numpy as np
import pandas as pd

import ivp_core
import chatbot_logic
from pipeline import Pipeline
from ai_models import AIModels, VIEWPOINTS

DATA_DIR = os.environ.get("PANTHERA_DATA_DIR", "./data")
MODELS_DIR = os.path.join(DATA_DIR, "models")
GALLERY_DIR = os.path.join(DATA_DIR, "gallery_data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
VIZ_DIR = os.environ.get("PANTHERA_VIZ_DIR", "./viz")
HASH_CACHE = os.environ.get("PANTHERA_HASH_CACHE", os.path.join(DATA_DIR, "gallery_hashes.pkl"))
VALIDATOR_FAIL_OPEN = os.environ.get("PANTHERA_VALIDATOR_FAIL_OPEN", "0") == "1"

t0 = time.time()
print("[1/6] Reading gallery table...")
cols = ["filename", "individual_id", "bbox_x", "bbox_y", "bbox_width", "bbox_height", "viewpoint", "leopard_name"]
full_df = pd.read_csv(os.path.join(GALLERY_DIR, "leopard_final_master.csv"), usecols=cols)
full_df = full_df[full_df["individual_id"].notna() & (full_df["individual_id"] != "____")]
full_df = full_df.drop_duplicates(subset=["filename", "individual_id"]).reset_index(drop=True)
print(f"      {len(full_df)} photos, {full_df['individual_id'].nunique()} leopards")

print("[2/6] Loading SIFT keypoints...")
features = {}
for shard in sorted(glob.glob(os.path.join(GALLERY_DIR, "sift_shards", "shard_*.pkl"))):
    with open(shard, "rb") as f:
        features.update(pickle.load(f))
features = {k: v for k, v in features.items() if v is not None}
expected = {f"{r.filename}|{r.individual_id}" for r in full_df.itertuples()}
print(f"      {len(features)} keypoint sets loaded ({len(expected - set(features))} photos have none)")
if len(features) < 0.9 * len(expected):
    raise RuntimeError("Most gallery photos have no keypoints - check that sift_shards/ is complete.")

holdout_file = os.path.join(GALLERY_DIR, "holdout_leopard_ids.txt")
holdout_ids = []
if os.path.exists(holdout_file):
    holdout_ids = [l.strip() for l in open(holdout_file) if l.strip()]
    print(f"      {len(holdout_ids)} holdout leopards kept OUT of the live gallery (for the 'new leopard' demo)")
else:
    print("      NOTE: no holdout_leopard_ids.txt found -> the 'new leopard then recognised' demo pairs will not behave as tested.")

print("[3/6] Building exact-duplicate index (first run reads every image, then it is cached)...")
hash_index = ivp_core.load_or_build_hash_index(
    [(r.filename, r.individual_id) for r in full_df.itertuples()], IMAGES_DIR, HASH_CACHE)
print(f"      {len(hash_index)} images indexed")

print("[4/6] Loading AI models...")
classes_file = os.path.join(GALLERY_DIR, "identity_classes.txt")
if os.path.exists(classes_file):
    identity_ids = [l.strip() for l in open(classes_file) if l.strip()]
else:
    vc = full_df["individual_id"].value_counts()
    identity_ids = sorted(vc[vc >= 10].index.tolist())
ai = AIModels(MODELS_DIR, identity_ids, validator_fail_open=VALIDATOR_FAIL_OPEN)

print("[5/6] Building pipeline...")
pipeline = Pipeline(full_df, holdout_ids, features, hash_index, IMAGES_DIR, VIZ_DIR, ai)

print("[6/6] Validator self-test on 30 real gallery photos...")
random.seed(0)
sample = random.sample(list(pipeline.gallery_df.itertuples()), min(30, len(pipeline.gallery_df)))
accepted = tested = 0
for r in sample:
    img = cv2.imread(os.path.join(IMAGES_DIR, r.filename))
    if img is None:
        continue
    crop = ivp_core.crop_to_bbox(img, pipeline.meta.get(r.filename))
    try:
        ok, _ = ai.validate(crop)
        accepted += int(ok)
        tested += 1
    except Exception as e:
        print(f"      validator error: {e}")
        break
if tested:
    rate = accepted / tested
    print(f"      validator accepted {accepted}/{tested} real leopard photos ({rate:.0%})")
    if rate < 0.8:
        print("      !!! WARNING: validator is rejecting real leopards - its feature extraction probably differs "
              "from how it was trained. Fix before demo (or set PANTHERA_VALIDATOR_FAIL_OPEN=1 as a stop-gap).")
print(f"Ready in {time.time() - t0:.0f}s.\n")


def chatbot_reply(question):
    """Answer + follow-up suggestions. Counts come from the live registry (it grows when leopards are confirmed)."""
    stats = {"photos": len(pipeline.live_owner), "leopards": len(set(pipeline.live_owner.values()))}
    return chatbot_logic.reply(question, pipeline.gallery_df, stats)


def chatbot_respond(question):
    return chatbot_reply(question)["answer"]
