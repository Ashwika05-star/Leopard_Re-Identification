# Panthera backend (v2) - follows the frozen IVP + AI pipeline

```
upload -> AI validator -> AI category -> AI viewpoint
       -> IVP: crop, grayscale, CLAHE, SIFT keypoints -> IVP: same-viewpoint gallery search + RANSAC
       -> AI identity estimate -> fusion: MATCH / POSSIBLE_MATCH / NEW_LEOPARD
```
Thresholds (validated in testing): >=20 verified points = confident; 6-19 = uncertain (AI agreeing at >=0.5 upgrades it);
<6 = AI can lead only at >=0.7, otherwise NEW LEOPARD.

## Files
| file | purpose |
|---|---|
| `app.py` | Flask API (`/analyze`, `/confirm-new`, `/chat`, `/image`, `/health`) |
| `backend.py` | loads data + models once, builds the pipeline, runs a validator self-test at start-up |
| `pipeline.py` | the pipeline + decision fusion + new-leopard registration |
| `ivp_core.py` | classical part: crop, CLAHE, SIFT, RANSAC, keypoint-line picture (same preprocessing as the gallery) |
| `ai_models.py` | the 4 neural networks |
| `decision.py` | frozen decision rules |
| `chatbot_logic.py` | chatbot engine: scores a question against the curated topics, registry look-ups, follow-up suggestions |
| `leopard_knowledge.py`, `project_knowledge.py` | the chatbot's curated answers (plain data: edit to add or fix an answer) |
| `make_holdout_ids.py`, `verify_demo_set.py` | demo tooling (below) |
| `smoke_test.py`, `test_app.py`, `test_chatbot.py` | self-tests, need NO models or data |

## Data folder (`PANTHERA_DATA_DIR`, default `./data`)
```
data/models/        category_classifier_BEST.pth  viewpoint_classifier_BEST.pth  identity_classifier_v2_BEST.pth
                    resnet_leopard_classifier.pkl  resnet_classifier_threshold.npy
data/gallery_data/  leopard_final_master.csv   sift_shards/shard_*.pkl
data/images/        the original photos (000000000001.jpg ...)
data/demo_examples/ your 408 demo images (only needed for the tools below)
```

## Before first run: match Colab's versions
In Colab run `!pip freeze | grep -iE "opencv|scikit-learn|torch|numpy"` and install the SAME versions of
opencv-python-headless, scikit-learn, torch, torchvision. The gallery keypoints were made with Colab's OpenCV;
a different SIFT build shifts scores slightly. The validator .pkl must be read by the same scikit-learn.

## Run
```bash
pip install -r requirements.txt
python make_holdout_ids.py --csv data/gallery_data/leopard_final_master.csv \
   --first data/demo_examples/5_new_leopard_both_uncertain \
   --second data/demo_examples/5_new_leopard_second_photo_recognized \
   --out data/gallery_data/holdout_leopard_ids.txt        # once
export PANTHERA_DATA_DIR=./data
python app.py                                             # or: gunicorn app:app --workers 1 --threads 2 --timeout 300
```
The first start reads every image once to build `gallery_hashes.pkl` (minutes); afterwards it is cached.
Start-up prints 6 steps and ends with the validator self-test. **If it says the validator rejects real leopards, stop and fix that first.**
If it says the identity classifier expects a different number of leopards, write the exact training list into
`data/gallery_data/identity_classes.txt` (one id per line, sorted, from Colab's `id_list`).

## Check the demo images on YOUR data (important)
```bash
python verify_demo_set.py --demo data/demo_examples --limit 20   # quick
python verify_demo_set.py --demo data/demo_examples --prune      # full; moves non-reproducing images to _failed/ (never deletes)
```
Only images that reproduce their folder's outcome are safe for a live demo.

## Behaviour to know
* Photos that are exact copies of dataset images use the dataset's bounding box and viewpoint (as in our tests).
  Any other upload uses the whole photo (a warning is returned) and the AI-predicted viewpoint - expect lower accuracy there.
* An exact copy of the only photo we hold of a leopard returns `path: exact_record`.
* Newly registered leopards live in memory + `_registered/`; a restart on a host with a temporary disk forgets them.
* Unseen leopards often score 4-14 by chance, so many land in POSSIBLE_MATCH rather than NEW (as in the holdout test).

## Result JSON (main fields)
`decision` (MATCH/POSSIBLE_MATCH/NEW_LEOPARD/rejected), `path`, `confidence_level`, `leopard{id,name,photo_count,viewpoints_on_record,is_new}`,
`ivp{verified_match_points,matched_photo_file,keypoints_extracted,candidates_searched}`, `ai{predicted_leopard_name,confidence,agrees_with_ivp}`,
`category`, `viewpoint{used,source,ai_predicted}`, `matched_image_url`, `keypoint_image_url`, `uploaded_image_url`, `upload_id`, `warnings`.
For NEW_LEOPARD call `POST /confirm-new {"upload_id": ...}` to add it to the gallery.
