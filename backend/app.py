"""
Panthera Flask API.

  POST /analyze      form-data: image (file), viewpoint (optional: back/down/front/left/right)
  POST /confirm-new  json: {"upload_id": "..."}   -> saves a 'NEW_LEOPARD' result into the live gallery
  POST /chat         json: {"question": "..."}
  GET  /image?path=gallery/<file> | uploads/<file> | viz/<file>
  GET  /health
"""
import os
import uuid
import threading
from collections import OrderedDict

from flask import Flask, request, jsonify, send_file

try:
    from flask_cors import CORS
except ImportError:          # only used so tests can run without flask-cors installed
    CORS = None

import backend

app = Flask(__name__)
if CORS:
    CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

UPLOAD_DIR = os.environ.get("PANTHERA_UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
PENDING = OrderedDict()                  # upload_id -> data needed to register a new leopard
LOCK = threading.Lock()                  # one analysis at a time (CPU-bound, keeps memory predictable)


@app.errorhandler(413)
def too_big(_):
    return jsonify({"status": "error", "message": "Image is larger than 25 MB."}), 413


@app.route("/health")
def health():
    p = backend.pipeline
    return jsonify({"status": "ok", "live_gallery_photos": len(p.live_owner),
                    "live_leopards": len(set(p.live_owner.values()))})


@app.route("/analyze", methods=["POST"])
def analyze():
    f = request.files.get("image")
    if f is None or not f.filename:
        return jsonify({"status": "error", "message": "No image file provided."}), 400
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED:
        return jsonify({"status": "error", "message": "Please upload a JPG, PNG or WEBP image."}), 400
    vp = (request.form.get("viewpoint") or "").strip().lower() or None
    if vp and vp not in backend.VIEWPOINTS:
        return jsonify({"status": "error", "message": f"viewpoint must be one of {backend.VIEWPOINTS}"}), 400

    upload_id = uuid.uuid4().hex
    saved_name = f"{upload_id}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, saved_name)
    f.save(saved_path)

    try:
        with LOCK:
            result = backend.pipeline.analyze_photo(saved_path, manual_viewpoint=vp)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Analysis failed: {e}"}), 500

    result["upload_id"] = upload_id
    result["uploaded_image_url"] = f"/image?path=uploads/{saved_name}"
    if result.get("matched_photo_file"):
        result["matched_image_url"] = f"/image?path=gallery/{result['matched_photo_file']}"
    if result.get("viz_file"):
        result["keypoint_image_url"] = f"/image?path=viz/{result['viz_file']}"
    if result.get("registration"):
        PENDING[upload_id] = {"path": saved_path, **result["registration"]}
        while len(PENDING) > 200:
            PENDING.popitem(last=False)
    return jsonify(result)


@app.route("/confirm-new", methods=["POST"])
def confirm_new():
    data = request.get_json(silent=True) or {}
    pending = PENDING.get(data.get("upload_id"))
    if not pending:
        return jsonify({"status": "error", "message": "Unknown or expired upload_id."}), 404
    try:
        with LOCK:
            backend.pipeline.register_new_leopard(pending["path"], pending["leopard_id"], pending["leopard_name"],
                                                  pending["viewpoint"], pending.get("category"))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    PENDING.pop(data["upload_id"], None)
    return jsonify({"status": "success", "leopard_id": pending["leopard_id"],
                    "leopard_name": pending["leopard_name"],
                    "message": f"{pending['leopard_name']} was added to the gallery."})


@app.route("/chat", methods=["POST"])
def chat():
    q = (request.get_json(silent=True) or {}).get("question", "").strip()
    if not q:
        return jsonify({"status": "error", "message": "No question provided."}), 400
    r = backend.chatbot_reply(q)
    return jsonify({"status": "success", "answer": r["answer"], "suggestions": r["suggestions"]})


@app.route("/image")
def image():
    rel = request.args.get("path", "")
    kind, _, name = rel.partition("/")
    name = os.path.basename(name)                       # blocks path traversal
    if kind == "gallery":
        full = backend.pipeline.image_path(name)
    elif kind == "uploads":
        full = os.path.join(UPLOAD_DIR, name)
    elif kind == "viz":
        full = os.path.join(backend.VIZ_DIR, name)
    else:
        return jsonify({"status": "error", "message": "Unknown path."}), 400
    if not name or not os.path.exists(full):
        return jsonify({"status": "error", "message": "Image not found."}), 404
    return send_file(full)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
