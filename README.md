# Leopard Re-Identification (PANTHERA)

Identifying individual leopards from photographs by their unique rosette patterns, using a classical
image-processing pipeline (IVP) together with four neural networks (AI).

The project has two parts:

| Folder | What it is |
|---|---|
| [`backend/`](backend) | Python / Flask API: validation, SIFT keypoints, RANSAC geometric verification, AI identity estimate, decision fusion, registry and a rule-based chatbot |
| [`frontend/`](frontend) | React + TypeScript website (TanStack Router): upload page, analysis result, IVP explainer, research page and a chat widget |

## How an identification works

```
upload -> AI validator -> AI category -> AI viewpoint
       -> IVP: crop, grayscale, CLAHE, SIFT keypoints
       -> IVP: same-viewpoint gallery search + RANSAC verification
       -> AI identity estimate
       -> decision: MATCH / POSSIBLE_MATCH / NEW_LEOPARD
```

| Verified match points | Decision |
|---|---|
| 20 or more | MATCH |
| 6 to 19 | MATCH if the AI agrees (confidence 0.5 or more), otherwise POSSIBLE_MATCH |
| fewer than 6 | POSSIBLE_MATCH only if the AI is confident (0.7 or more), otherwise NEW_LEOPARD |

Measured on our held-out test set: 73.7% top-1 accuracy, 82.6% top-5, and 92% correct when the system reports high confidence.

## Chatbot

The chat widget is deliberately **not** a language model. It matches the question against curated, verified
topics (leopard biology and this project), so it cannot invent facts. Anything outside those topics is politely
declined, and leopards in the registry can be looked up by ID, `Panthera-###` code or first name.

## Run it locally

Backend (needs the model/gallery files described in `backend/README.md`, which are too large for this repository):

```bash
cd backend
pip install -r requirements.txt
PORT=8090 python app.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The frontend reads the backend address from `API_BASE_URL` in `frontend/src/lib/panthera.ts` (default `http://localhost:8090`).

## Tests

These need no models or data:

```bash
cd backend
python test_chatbot.py && python test_app.py && python smoke_test.py
```

## Contributors

- Ashwika ([@Ashwika05-star](https://github.com/Ashwika05-star))
- Apar ([@aparyadav27-star](https://github.com/aparyadav27-star))
