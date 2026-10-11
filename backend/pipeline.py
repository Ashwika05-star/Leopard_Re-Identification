"""
The identification pipeline (no torch imports here; AI models are injected, so this file is testable).

Flow (matches the frozen design):
  validate (AI) -> category (AI) -> viewpoint (AI) -> enhance + SIFT (IVP) -> gallery search + RANSAC (IVP)
  -> identity estimate (AI) -> decision fusion -> result
"""
import os
import uuid
import shutil
import threading
from collections import defaultdict

import cv2
import numpy as np
import pandas as pd

import ivp_core
import decision

CORRECTION_LABEL = "CLAHE contrast enhancement"


class Pipeline:
    def __init__(self, full_df, holdout_ids, features, hash_index, images_dir, viz_dir, ai, registered_dir=None):
        """
        full_df     : ALL photos (filename, individual_id, bbox_*, viewpoint, leopard_name)
        holdout_ids : leopards deliberately kept OUT of the live gallery (for the 'new leopard' demo)
        features    : {"filename|individual_id": (points, descriptors)}
        hash_index  : {md5: (filename, individual_id)}  (built over ALL photos)
        ai          : object with validate/category/viewpoint/identity (each takes a BGR crop)
        """
        self.ai, self.features, self.hash_index = ai, features, hash_index
        self.images_dir, self.viz_dir = images_dir, viz_dir
        self.registered_dir = registered_dir or os.path.join(images_dir, '_registered')
        self.path_of = {}                     # filename -> full path, for newly registered photos
        os.makedirs(viz_dir, exist_ok=True)
        self._lock = threading.Lock()
        self.new_counter = 0

        df = full_df.copy().drop_duplicates(subset=["filename", "individual_id"]).reset_index(drop=True)
        self.full_df = df
        self.names = dict(zip(df["individual_id"], df["leopard_name"]))
        self.meta, self.viewpoint_of, self.key_of = {}, {}, {}
        for r in df.itertuples():
            vals = (r.bbox_x, r.bbox_y, r.bbox_width, r.bbox_height)
            self.meta[r.filename] = None if any(pd.isna(v) for v in vals) else tuple(float(v) for v in vals)
            self.viewpoint_of[r.filename] = None if pd.isna(r.viewpoint) else str(r.viewpoint)
            self.key_of[r.filename] = f"{r.filename}|{r.individual_id}"

        holdout = set(holdout_ids)
        self.gallery_df = df[~df["individual_id"].isin(holdout)].reset_index(drop=True)
        self.by_view = defaultdict(list)           # viewpoint -> [(key, filename, individual_id)]
        self.photo_count = defaultdict(int)        # live photos per leopard
        self.views_of = defaultdict(set)
        self.live_owner = {}                       # live filename -> individual_id
        for r in self.gallery_df.itertuples():
            self._index(r.filename, r.individual_id, self.viewpoint_of[r.filename], self.key_of[r.filename])

    # ---------- helpers ----------
    def image_path(self, filename):
        return self.path_of.get(filename) or os.path.join(self.images_dir, filename)

    def _index(self, filename, iid, viewpoint, key):
        if viewpoint:
            self.by_view[viewpoint].append((key, filename, iid))
            self.views_of[iid].add(viewpoint)
        self.photo_count[iid] += 1
        self.live_owner[filename] = iid

    def search(self, q_feat, viewpoint, exclude_filename=None):
        best_score, best_id, best_file = 0, None, None
        if q_feat is None:
            return best_score, best_id, best_file
        for key, fn, iid in self.by_view.get(viewpoint, []):
            if fn == exclude_filename:
                continue
            f = self.features.get(key)
            if f is None:
                continue
            s = ivp_core.verified_matches(q_feat, f)
            if s > best_score:
                best_score, best_id, best_file = s, iid, fn
        return best_score, best_id, best_file

    def representative_photo(self, lid, viewpoint):
        for _, fn, iid in self.by_view.get(viewpoint, []):
            if iid == lid:
                return fn
        for fn, iid in self.live_owner.items():
            if iid == lid:
                return fn
        return None

    def _leopard_block(self, lid):
        return {"id": lid, "name": self.names.get(lid, "Unknown"), "is_new": False,
                "photo_count": self.photo_count.get(lid, 0),
                "viewpoints_on_record": sorted(self.views_of.get(lid, set()))}

    def _make_viz(self, gray_q, q_feat, matched_file):
        try:
            g_feat = self.features.get(self.key_of[matched_file])
            img_g = cv2.imread(self.image_path(matched_file))
            if g_feat is None or img_g is None:
                return None
            gray_g = ivp_core.prep_gray(img_g, self.meta.get(matched_file))
            out = ivp_core.draw_matches(gray_q, q_feat, gray_g, g_feat)
            if out is None:
                return None
            name = f"{uuid.uuid4().hex}.jpg"
            cv2.imwrite(os.path.join(self.viz_dir, name), out)
            return name
        except Exception:
            return None

    # ---------- main entry point ----------
    def analyze_photo(self, image_path, manual_viewpoint=None):
        img = cv2.imread(image_path)
        if img is None:
            return {"status": "error", "message": "Could not read image file."}
        warnings = []

        fhash = ivp_core.md5_file(image_path)
        dup = self.hash_index.get(fhash)                     # exact copy of a photo we already hold?
        bbox = self.meta.get(dup[0]) if dup else None
        if dup is None:
            warnings.append("No bounding box available: the whole photo was used. Results are most reliable on "
                            "photos where the leopard fills most of the frame.")
        crop = ivp_core.crop_to_bbox(img, bbox)

        # AI 1: validator
        try:
            is_leopard, v_conf = self.ai.validate(crop)
        except Exception as e:
            return {"status": "error", "message": f"Leopard validator failed: {e}"}
        if not is_leopard:
            return {"status": "rejected", "message": "This does not appear to contain a leopard.",
                    "validator": {"confidence": round(float(v_conf), 3)}}

        # AI 2/3: condition + viewpoint
        category, cat_conf = self.ai.category(crop)
        vp_ai, vp_conf = self.ai.viewpoint(crop)
        viewpoint, vp_source = vp_ai, "ai"
        if manual_viewpoint:
            viewpoint, vp_source = manual_viewpoint, "user"
        elif dup and self.viewpoint_of.get(dup[0]):
            viewpoint, vp_source = self.viewpoint_of[dup[0]], "dataset_record"

        # IVP: enhance + keypoints + gallery search
        gray_q = ivp_core.prep_gray(img, bbox)
        q_feat = ivp_core.extract_keypoints(gray_q)
        if q_feat is None:
            warnings.append("Too few distinctive pattern points were found in this photo.")
        exclude = dup[0] if dup else None
        score, ivp_leopard, ivp_file = self.search(q_feat, viewpoint, exclude_filename=exclude)
        n_candidates = sum(1 for _, fn, _ in self.by_view.get(viewpoint, []) if fn != exclude)

        # AI 4: independent identity estimate
        ai_id, ai_conf = self.ai.identity(crop)

        d = decision.decide(score, ivp_leopard, ai_id, ai_conf)

        # Exact-record rule: this exact photo is the ONLY photo we hold for its leopard
        exact_record = False
        if dup and self.live_owner.get(dup[0]) == dup[1] and self.photo_count.get(dup[1]) == 1:
            d = dict(decision="MATCH", path="exact_record", confidence_level="high",
                     leopard_id=dup[1], ai_agrees=(ai_id == dup[1]))
            ivp_file, exact_record = dup[0], True

        resp = {
            "status": "success",
            "decision": d["decision"], "path": d["path"],
            "demo_category": decision.DEMO_CATEGORY.get(d["path"]),
            "confidence_level": d["confidence_level"],
            "validator": {"confidence": round(float(v_conf), 3)},
            "category": {"detected": category, "confidence": round(float(cat_conf), 3)},
            "correction_applied": CORRECTION_LABEL,
            "viewpoint": {"used": viewpoint, "source": vp_source, "ai_predicted": vp_ai,
                          "ai_confidence": round(float(vp_conf), 3)},
            "ivp": {"verified_match_points": int(score), "matched_leopard_id": ivp_leopard,
                    "matched_photo_file": ivp_file, "keypoints_extracted": 0 if q_feat is None else len(q_feat[0]),
                    "candidates_searched": n_candidates},
            "ai": {"predicted_leopard_id": ai_id, "predicted_leopard_name": self.names.get(ai_id, "Unknown"),
                   "confidence": round(float(ai_conf), 3), "agrees_with_ivp": d["ai_agrees"]},
            "exact_record": exact_record,
            "warnings": warnings,
        }

        if d["decision"] in ("MATCH", "POSSIBLE_MATCH"):
            lid = d["leopard_id"]
            resp["leopard"] = self._leopard_block(lid)
            matched = ivp_file if (d["path"] in ("confident_both_agree", "confident_ivp_alone",
                                                 "possible_upgraded_by_ai", "possible_ivp_led", "exact_record")
                                   ) else self.representative_photo(lid, viewpoint)
            resp["matched_photo_file"] = matched
            if matched and not exact_record and d["path"] != "possible_ai_led":
                viz = self._make_viz(gray_q, q_feat, matched)
                if viz:
                    resp["viz_file"] = viz
        else:
            self.new_counter += 1
            new_id = str(uuid.uuid4())
            new_name = f"Discovery-{len(set(self.live_owner.values())) + self.new_counter}"
            resp["leopard"] = {"id": new_id, "name": new_name, "is_new": True, "photo_count": 0,
                               "viewpoints_on_record": []}
            resp["registration"] = {"leopard_id": new_id, "leopard_name": new_name,
                                    "viewpoint": viewpoint, "category": category}
        return resp

    # ---------- adding a newly discovered leopard to the live gallery ----------
    def register_new_leopard(self, image_path, new_id, new_name, viewpoint, category=None):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read image file.")
        fhash = ivp_core.md5_file(image_path)
        dup = self.hash_index.get(fhash)
        bbox = self.meta.get(dup[0]) if dup else None
        feat = ivp_core.extract_keypoints(ivp_core.prep_gray(img, bbox))
        if feat is None:
            raise ValueError("Not enough distinctive pattern points to register this photo.")
        with self._lock:
            fname = f"new_{new_id[:8]}_{os.path.basename(image_path)}"
            os.makedirs(self.registered_dir, exist_ok=True)
            dest = os.path.join(self.registered_dir, fname)
            shutil.copy(image_path, dest)
            self.path_of[fname] = dest
            key = f"{fname}|{new_id}"
            self.features[key] = feat
            self.meta[fname], self.viewpoint_of[fname], self.key_of[fname] = bbox, viewpoint, key
            self.names[new_id] = new_name
            self._index(fname, new_id, viewpoint, key)
            self.hash_index[fhash] = (fname, new_id)
