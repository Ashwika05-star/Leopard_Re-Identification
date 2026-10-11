"""
Verified, rule-based chatbot: no free text generation, so no hallucinated facts.

How a question is answered (see reply()):
  1. A leopard ID or 'Panthera-###' code in the question -> registry lookup.
  2. Otherwise every topic in leopard_knowledge.py / project_knowledge.py is scored against the question.
     A topic's trigger matches when all of its words appear in the question (plurals and tenses are ignored);
     rarer words count for more, so 'eat' beats 'leopard'. The best topic above MIN_SCORE answers.
     Leopard-fact topics are 'gated': generic triggers ('eat', 'how big') only count when the question is about
     leopards, so 'what should I eat for dinner?' is not answered with leopard diet facts. A trigger written
     with a leading '!' (e.g. '!cheetah') is specific enough to count on its own.
  3. Otherwise a leopard first name ('Tell me about Nawab') -> registry lookup.
  4. Otherwise a polite fallback with suggestions.
"""
import math
import re
from collections import Counter

import leopard_knowledge
import project_knowledge

_UUID = re.compile(r"[0-9a-z]{1,8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}")   # shape only; not hex-checked
_CODE = re.compile(r"\bpanthera (\d{1,4})\b")                  # matched on the normalised question
_WORD = re.compile(r"[a-z0-9]+")

FALLBACK = ("I'm specifically built to help with leopards and this identification project. I can answer questions "
            "about leopard biology (diet, habitat, behaviour, spots, conservation), how our identification works, "
            "our accuracy, or look up a leopard in our registry. Try one of the suggestions below.")
UNKNOWN_LEOPARD = ("I don't have a verified answer to that one yet. I only share facts I can stand behind, so I'd "
                   "rather not guess. Here are some things I can answer:")

MIN_SCORE = 2.5            # a single common word ('leopard', 'how') is never enough to answer
DOMAIN_WORDS = ("leopard", "panther", "cub", "rosette", "jaguar", "cheetah")
STARTER_IDS = ["diet", "habitat", "rosettes", "how_it_works"]
MAX_QUESTION_CHARS = 500

_STOP = frozenset("""a an the is are was were be am do does did can could would will shall should may might you
your yours me my mine i we us our it its of to in on at for and or with about tell please this that there some any
have has had what which s t""".split())
_IRREGULAR = {"ate": "eat", "eaten": "eat", "ran": "run", "faster": "fast", "fastest": "fast", "bigger": "big",
              "biggest": "big", "larger": "large", "largest": "large", "older": "old", "oldest": "old",
              "heavier": "heavy", "heaviest": "heavy", "stronger": "strong", "strongest": "strong",
              "identified": "identify", "using": "use", "used": "use", "made": "make", "built": "build",
              "known": "know", "found": "find", "saw": "see", "seen": "see", "died": "die"}


def _stem(w):
    """Crude stemmer. Triggers and questions go through the same function, so only consistency matters."""
    w = _IRREGULAR.get(w, w)
    if len(w) > 4 and w.endswith("ies"):
        w = w[:-3] + "y"
    elif len(w) > 4 and w.endswith(("ches", "shes", "sses", "xes", "zes")):
        w = w[:-2]
    elif len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is")):
        w = w[:-1]
    for suffix in ("ing", "ed"):
        if len(w) > len(suffix) + 2 and w.endswith(suffix):
            w = w[:-len(suffix)]
            break
    if len(w) > 3 and w.endswith("e"):
        w = w[:-1]
    if len(w) > 2 and w[-1] == w[-2] and w[-1] not in "aeiou":      # swimm -> swim, spott -> spot
        w = w[:-1]
    return w


def _normalise(text):
    return " ".join(_WORD.findall(text.lower()))


def _tokens(text):
    return [_stem(w) for w in _WORD.findall(text.lower()) if w not in _STOP and len(w) > 1]


# ---------------------------------------------------------------- topic index (built once at import)
TOPICS = ([dict(t, gated=False) for t in project_knowledge.TOPICS] +       # project first: wins ties
          [dict(t, gated=True) for t in leopard_knowledge.TOPICS])
BY_ID = {t["id"]: t for t in TOPICS}
DOMAIN = frozenset(_stem(w) for w in DOMAIN_WORDS)


def _build_index():
    doc_freq = Counter()
    for t in TOPICS:
        doc_freq.update({tok for trig in t["triggers"] for tok in _tokens(trig)})
    idf = {tok: math.log(1 + len(TOPICS) / n) for tok, n in doc_freq.items()}
    for t in TOPICS:
        trigs = [(frozenset(_tokens(trig)), trig.startswith("!")) for trig in t["triggers"]]
        t["_trigs"] = [(toks, sum(idf[x] for x in toks), strong) for toks, strong in trigs if toks]
        t["_pats"] = [re.compile(p) for p in t.get("patterns", [])]


_build_index()


def _about_leopards(qtokens):
    return bool(qtokens & DOMAIN) or {"big", "cat"} <= qtokens


def _score(topic, norm, qtokens, about_leopards):
    if any(p.search(norm) for p in topic["_pats"]):
        return 100.0
    open_topic = about_leopards or not topic["gated"]
    hits = sorted((w for toks, w, strong in topic["_trigs"] if toks <= qtokens and (strong or open_topic)),
                  reverse=True)
    return hits[0] + 0.3 * sum(hits[1:]) if hits else 0.0


def _ranked(norm, qtokens):
    about = _about_leopards(qtokens)
    scored = [(_score(t, norm, qtokens, about), i, t) for i, t in enumerate(TOPICS)]
    return [(s, t) for s, i, t in sorted(scored, key=lambda x: (-x[0], x[1])) if s > 0]


def _suggestions(topic_ids, asked_norm):
    out = []
    for tid in topic_ids:
        ex = BY_ID[tid]["example"]
        if _normalise(ex) != asked_norm and ex not in out:
            out.append(ex)
    return out[:3]


# ---------------------------------------------------------------- registry lookups
def _profile(df, lid):
    rows = df[df["individual_id"] == lid]
    names = rows["leopard_name"].dropna()
    return {"name": names.iloc[0] if len(names) else "Unknown", "id": lid, "photo_count": len(rows),
            "viewpoints_seen": sorted(rows["viewpoint"].dropna().unique().tolist())}


def lookup(df, text):
    """First leopard whose name or ID contains `text` (kept for backward compatibility)."""
    hit = df[df["leopard_name"].astype(str).str.contains(text, case=False, na=False, regex=False) |
             df["individual_id"].astype(str).str.contains(text, case=False, na=False, regex=False)]
    return _profile(df, hit.iloc[0]["individual_id"]) if len(hit) else None


def _fmt(r):
    angles = ", ".join(r["viewpoints_seen"]) or "no recorded angle"
    return (f"I found this leopard: {r['name']} (ID: {r['id']}). We have {r['photo_count']} photos on record, "
            f"captured from these angles: {angles}.")


def _fmt_many(label, rows, extra):
    shown = ", ".join(rows[:5])
    more = f" and {len(rows) - 5} more" if len(rows) > 5 else ""
    return (f"There are {len(rows)} leopards matching '{label}' in the registry, for example {shown}{more}. "
            f"Ask about one by its full name or ID for details.{extra}")


def _unique_leopards(df):
    return df.drop_duplicates("individual_id")[["individual_id", "leopard_name"]].dropna()


def _answer_leopards(df, ids, label):
    if len(ids) == 1:
        return _fmt(_profile(df, ids[0]))
    names = [str(n) for n in _unique_leopards(df).set_index("individual_id").loc[ids, "leopard_name"]]
    return _fmt_many(label, names, "")


def _find_by_code(df, norm):
    m = _CODE.search(norm)
    if not m:
        return None, None
    pattern = rf"panthera-0*{int(m.group(1))}\b"
    uniq = _unique_leopards(df)
    ids = uniq[uniq["leopard_name"].astype(str).str.contains(pattern, case=False, regex=True)]["individual_id"]
    return m.group(0), ids.tolist()


def _find_by_first_name(df, raw_words):
    uniq = _unique_leopards(df)
    first = uniq["leopard_name"].astype(str).str.split(" (", regex=False).str[0]
    single = first[~first.str.contains(" ", regex=False)].str.lower()
    for w in raw_words:
        ids = uniq.loc[single[single == w].index, "individual_id"].tolist()
        if ids:
            return w.capitalize(), ids
    return None, None


# ---------------------------------------------------------------- public API
def _context(df, stats):
    stats = stats or {}
    return {"photos": f"{stats.get('photos', len(df)):,}",
            "leopards": f"{stats.get('leopards', df['individual_id'].nunique()):,}"}


def reply(question, df, stats=None):
    """Return {'answer': str, 'suggestions': [str, ...], 'topic': topic id or None}."""
    q = (question or "").strip()[:MAX_QUESTION_CHARS]
    norm = _normalise(q)
    qtokens = frozenset(_tokens(q))
    starters = _suggestions(STARTER_IDS, norm)

    def result(answer, suggestions, topic=None):
        return {"answer": answer, "suggestions": suggestions, "topic": topic}

    uuid_hit = _UUID.search(q.lower())
    if uuid_hit:
        r = lookup(df, uuid_hit.group())
        return result(_fmt(r) if r else "I couldn't find a leopard with that ID in the registry.", starters,
                      "lookup")
    label, ids = _find_by_code(df, norm)
    if label:
        text = _answer_leopards(df, ids, label) if ids else f"I couldn't find '{label}' in the registry."
        return result(text, starters, "lookup")

    ranked = _ranked(norm, qtokens)
    if ranked and ranked[0][0] >= MIN_SCORE:
        topic = ranked[0][1]
        ctx = _context(df, stats)
        answer = topic["answer"].replace("{photos}", ctx["photos"]).replace("{leopards}", ctx["leopards"])
        return result(answer, _suggestions(topic["ask"], norm), topic["id"])

    label, ids = _find_by_first_name(df, _WORD.findall(q.lower()))
    if label:
        return result(_answer_leopards(df, ids, label), starters, "lookup")

    near = _suggestions([t["id"] for _, t in ranked[:3]], norm)
    return result(UNKNOWN_LEOPARD if _about_leopards(qtokens) else FALLBACK, near or starters)


def respond(question, df, stats=None):
    """Answer text only (what the original chatbot returned)."""
    return reply(question, df, stats)["answer"]
