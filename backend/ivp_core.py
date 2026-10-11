"""
IVP core (classical computer vision only, no torch).

IMPORTANT: prep_gray() reproduces EXACTLY the preprocessing that was used when the
gallery keypoints (sift_shards) were built in Colab:
    crop to bounding box -> grayscale -> shrink so longest side <= 800 -> CLAHE(2.0, 8x8) -> SIFT(500)
Using the same steps for uploaded photos is what makes the tested accuracy apply.
"""
import os
import pickle
import hashlib
import cv2
import numpy as np

MAX_SIDE = 800


def crop_to_bbox(img_bgr, bbox):
    """bbox = (x, y, w, h) or None. Falls back to the full image if the box is empty."""
    if bbox is None:
        return img_bgr
    x, y, w, h = [int(v) for v in bbox]
    H, W = img_bgr.shape[:2]
    crop = img_bgr[max(0, y):min(H, y + h), max(0, x):min(W, x + w)]
    return crop if crop.size else img_bgr


def prep_gray(img_bgr, bbox=None):
    crop = crop_to_bbox(img_bgr, bbox)
    g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    s = MAX_SIDE / max(g.shape)
    if s < 1:
        g = cv2.resize(g, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(g)


def extract_keypoints(gray):
    """Returns (points float32 [n,2], descriptors uint8 [n,128]) or None if too few keypoints."""
    kp, des = cv2.SIFT_create(nfeatures=500).detectAndCompute(gray, None)
    if des is None or len(kp) < 10:
        return None
    return np.float32([k.pt for k in kp]), des.astype(np.uint8)


def _ransac_inliers(f1, f2, ratio=0.75):
    if f1 is None or f2 is None:
        return None
    p1, d1 = f1
    p2, d2 = f2
    if len(d1) < 2 or len(d2) < 2:
        return None
    knn = cv2.BFMatcher(cv2.NORM_L2).knnMatch(d1.astype(np.float32), d2.astype(np.float32), k=2)
    good = [m[0] for m in knn if len(m) == 2 and m[0].distance < ratio * m[1].distance]
    if len(good) < 6:
        return None
    src = p1[[g.queryIdx for g in good]]
    dst = p2[[g.trainIdx for g in good]]
    M, mask = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=8)
    if mask is None:
        return None
    keep = mask.ravel().astype(bool)
    return [g for g, k in zip(good, keep) if k]


def verified_matches(f1, f2, ratio=0.75):
    """Number of RANSAC-verified matching keypoints (the 'IVP score')."""
    inl = _ransac_inliers(f1, f2, ratio)
    return 0 if inl is None else len(inl)


def draw_matches(gray_q, f_q, gray_g, f_g, max_lines=80):
    """Green lines between verified keypoints. Both images MUST be the prep_gray() outputs
    (same crop + resize as the keypoints were computed on), otherwise lines land in wrong places."""
    inl = _ransac_inliers(f_q, f_g)
    if not inl:
        return None
    kq = [cv2.KeyPoint(float(x), float(y), 8) for x, y in f_q[0]]
    kg = [cv2.KeyPoint(float(x), float(y), 8) for x, y in f_g[0]]
    inl = sorted(inl, key=lambda m: m.distance)[:max_lines]
    a = cv2.cvtColor(gray_q, cv2.COLOR_GRAY2BGR)
    b = cv2.cvtColor(gray_g, cv2.COLOR_GRAY2BGR)
    return cv2.drawMatches(a, kq, b, kg, inl, None, matchColor=(0, 255, 0), flags=2)


def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_or_build_hash_index(rows, images_dir, cache_path):
    """rows: iterable of (filename, individual_id). Built once, then cached on disk,
    so server start-up does not have to read every gallery image again."""
    if cache_path and os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return pickle.load(f)
    idx = {}
    for fn, iid in rows:
        p = os.path.join(images_dir, fn)
        if os.path.exists(p):
            idx[md5_file(p)] = (fn, iid)
    if cache_path:
        try:
            with open(cache_path, "wb") as f:
                pickle.dump(idx, f)
        except OSError:
            pass
    return idx
