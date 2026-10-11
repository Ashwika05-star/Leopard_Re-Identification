# CLAUDE.md: handoff notes for Claude (and humans)

Leopard Re-Identification (PANTHERA). A university project: identify individual leopards from photos with a
classical image-processing pipeline (IVP: SIFT + RANSAC) plus four small neural networks (AI).

> If a `CLAUDE.md` exists in a parent folder (e.g. `~/Downloads/CLAUDE.md` describes an unrelated HR-analytics
> project), it does **not** apply here. This file is the spec for this repository.

## Layout

| Path | What |
|---|---|
| `backend/` | Flask API + pipeline + rule-based chatbot + self-tests |
| `backend/data/models/` | the trained weights (committed, ~128 MB, 5 files, see below) |
| `frontend/` | React + TypeScript, TanStack Start/Router, Tailwind (Lovable-scaffolded) |

Not in the repo (too big): `backend/data/gallery_data/` (CSV + SIFT shards, ~450 MB) and `backend/data/images/`
(~8 GB of photos). Without them the backend cannot start. They live on the author's Mac.

## Run (local demo, the only fully working setup)

```bash
cd backend && PORT=8090 python app.py        # loads models + gallery (about a minute)
cd frontend && npm install && npm run dev    # http://localhost:8080
```
On the author's Mac: `~/Downloads/start-panthera.sh` starts both (backend on 8090, site on 8080).
Dev server needs `LOVABLE_PREVIEW_HOST=id-preview--62064289-02d5-4259-abb7-f555870f4ae9.lovable.app`.

Tests (need no models or data): `cd backend && python test_chatbot.py && python test_app.py && python smoke_test.py`.
Frontend type-check: `cd frontend && npx tsc --noEmit`.

## Pipeline and decision rules (`backend/pipeline.py`, `backend/decision.py`, frozen)

upload -> AI validator -> AI category -> AI viewpoint -> IVP (crop, grayscale, CLAHE, SIFT) -> same-viewpoint
gallery search + RANSAC -> AI identity estimate -> decision.

- 20 or more verified points: MATCH.
- 6-19: MATCH if the AI names the same leopard at >= 0.5, otherwise POSSIBLE_MATCH.
- fewer than 6: POSSIBLE_MATCH only if the AI is >= 0.7, otherwise NEW_LEOPARD.
- A photo that is the only one held for a leopard and is an exact file copy returns `path: exact_record`.

Measured on the held-out test set: 73.7% top-1, 82.6% top-5, 92% correct when confidence is "high".

## Models (`backend/data/models/`)

`category_classifier_BEST.pth`, `viewpoint_classifier_BEST.pth`, `identity_classifier_v2_BEST.pth` (ResNet-18
state dicts), `resnet_leopard_classifier.pkl` + `resnet_classifier_threshold.npy` (the "is this a leopard"
validator). They need the same scikit-learn / torch / OpenCV versions pinned in `backend/requirements.txt`.

## API (`backend/app.py`)

`POST /analyze` (multipart `image`, optional `viewpoint`), `POST /confirm-new {"upload_id"}`,
`POST /chat {"question"}` -> `{answer, suggestions[]}`, `GET /image?path=gallery|uploads|viz/<file>`, `GET /health`.
A confirmed new leopard is added **in memory** (plus a copy in `data/images/_registered/`); it is forgotten on
restart, which is also how the registry is "reset" for demos. Analysing alone never changes the registry.

## Chatbot (rewritten in this work)

Deliberately **not** an LLM: it must not invent facts. Files: `backend/chatbot_logic.py` (engine),
`leopard_knowledge.py` (~30 leopard-biology topics), `project_knowledge.py` (~25 project topics),
`test_chatbot.py` (~250 checks).

- Each topic is a dict: `id`, `example`, `triggers`, optional `patterns` (regex), `answer`, `ask` (follow-up ids).
- A trigger matches when **all** its words are in the question (light stemming, stopwords removed). Rarer words
  weigh more (IDF); the best topic scoring >= `MIN_SCORE` (2.5) answers; regex `patterns` score 100.
- Project topics come first in the list, so they win ties against leopard topics.
- Leopard topics are *gated*: generic triggers only count if the question mentions a leopard word
  (`DOMAIN_WORDS`), so "what should I eat for dinner" is refused. A trigger starting with `!` counts on its own
  (e.g. `!melanism`, `!camera trap`).
- Registry look-ups: a UUID-shaped ID, a `Panthera-###` code, or a leopard's first name.
- Dynamic placeholders in answers: `{photos}`, `{leopards}` (live registry counts).
- Out-of-scope questions get a polite refusal plus suggestions. Unknown leopard questions say so honestly.
- To add or fix an answer: edit one of the knowledge files, then run `python test_chatbot.py`. The suite also
  checks that every topic's own `example` question resolves to that topic and that every follow-up id exists.

Frontend: `frontend/src/components/ChatWidget.tsx` (floating button, starter chips, follow-up chips).

## Frontend flow

- **Analyse** (`/vision-ai`, label renamed from "Vision AI"): upload; result stored in `sessionStorage`
  (`panthera:upload`, `panthera:result`).
- **Result** (`/analysis`): decision, matched photo, keypoint image, meters; "Confirm & Save to Registry" for new
  leopards; button **View full IVP & AI details** -> `/ivp-system?view=result`.
- **Pipeline** (`/ivp-system`, label renamed from "IVP System"): plain visit = the general explanation page.
  With `?view=result` and a stored successful result it shows `components/ResultDetails.tsx`: a per-photo report
  with a "By the numbers" grid (photo resolution/size measured in the browser, keypoints, candidates searched,
  verified points, % verified, vs the 20-point threshold, AI confidences, prior records), a plain-language
  explanation of the decision path, the six IVP stages with this photo's values, and the four AI estimates.
  Every number is read from the result or derived from it; "-" when missing. No hardcoded results.
- Backend address: `VITE_API_BASE_URL` env var, default `http://localhost:8090` (`src/lib/panthera.ts`).
  Images are fetched as blobs with the ngrok skip header (harmless elsewhere).
- Route paths were intentionally **not** renamed (only labels), so links and bookmarks keep working.

## Work log (what changed, newest first)

- Added trained model weights to the repo; `backend/.gitignore` now ignores `data/*` except `data/models/`.
- Renamed menu/footer/page labels: Vision AI -> Analyse, IVP System -> Pipeline.
- Added the per-photo IVP & AI report and the "By the numbers" section.
- Frontend: upgraded `@tanstack/react-start` / router packages and cleared `npm audit` findings.
- Chatbot: replaced the old keyword matcher with the verified topic engine described above, added follow-up
  suggestions to `/chat`, and the chat widget chips.
- Backend v2 integration: nested response shape, `upload_id` + `/confirm-new`, keypoint visualisation.
- Home page content, dataset figures, rounded buttons and the pre-upload landing page on the Analyse page.

## Known issues / decisions for the author

- **Home page shows "98.2% re-identification accuracy"**, which contradicts the measured 73.7% top-1 used on the
  Analyse page and in the chatbot. Its source is unknown. Resolve before any viva or report.
- "431 individuals catalogued" is the full dataset; the live registry holds fewer because some leopards are held
  out for the "new leopard" demo.
- In the Pipeline page "Categorize" is listed as an IVP stage, but the image-condition classifier is an AI model.
- Analysis and chat need the backend, which is run locally; the website alone only shows the pages.
- The old `panthera-backend` GitHub repo and its Render service from earlier attempts are still to be deleted by
  the owner (needs the `delete_repo` scope / the Render dashboard).

## Hosting facts (so nobody re-researches them)

The backend needs about 1.1 GB RAM and ~9 GB of data. Free tiers checked: Render free (512 MB) runs out of memory;
Hugging Face free CPU Spaces appear gated for Docker on new accounts. The agreed plan is to demo from the
author's Mac. Always-on hosting would need a paid server (~$9/month) and uploading the data.

## Conventions

- Commits are authored alternately by the two team members (`Ashwika05-star`, `aparyadav27-star`). **Do not add
  `Co-Authored-By: Claude` lines**, the owner asked for them to be removed.
- Never hardcode results: every number shown for a photo must come from the backend response.
- Pushing needs `gh auth setup-git`. The repo is private.
- npm may fail with cache permission errors; use `npm install --cache <a fresh dir>`.
