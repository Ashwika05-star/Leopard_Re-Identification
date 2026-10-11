"""
Chatbot self-test (needs no models or data):  python test_chatbot.py
Checks that realistic questions reach the right topic, that off-topic questions do not, that every suggestion is
answerable, and that registry look-ups behave.
"""
import pandas as pd

import chatbot_logic as C

failed = 0


def check(cond, label):
    global failed
    print(("PASS  " if cond else "FAIL  ") + label)
    failed += 0 if cond else 1


ID_A = "11111111-1111-4111-8111-111111111111"
ID_B = "22222222-2222-4222-8222-222222222222"
ID_C = "33333333-3333-4333-8333-333333333333"
ID_D = "44444444-4444-4444-8444-444444444444"
DF = pd.DataFrame({
    "filename": ["a1.jpg", "a2.jpg", "b1.jpg", "c1.jpg", "d1.jpg"],
    "individual_id": [ID_A, ID_A, ID_B, ID_C, ID_D],
    "viewpoint": ["left", "right", "front", None, "back"],
    "leopard_name": ["Nawab (Panthera-326)", "Nawab (Panthera-326)", "Nawab (Panthera-017)",
                     "Tara (Panthera-042)", "Leopard Four"],
})


def topic_of(q):
    return C.reply(q, DF)["topic"]


# ---------------------------------------------------------------- 1. question -> topic
ROUTES = {
    "overview": ["Tell me about leopards", "What is a leopard?", "what are leopards", "leopard facts", "Leopards"],
    "taxonomy": ["What is the scientific name of a leopard?", "latin name for leopard", "which genus is a leopard in"],
    "size": ["How big is a leopard?", "how much does a leopard weigh", "What is the average size of a leopard?",
             "How heavy are leopards?"],
    "lifespan": ["How long do leopards live?", "What is a leopard's lifespan?", "how old can a leopard get",
                 "how many years do leopards live in the wild"],
    "diet": ["What do leopards eat?", "what is the leopard diet", "What animals do leopards hunt?",
             "what prey do leopards go for", "Are leopards carnivores?"],
    "hunting": ["How do leopards hunt?", "how does a leopard catch its prey", "do leopards stalk their prey",
                "Are leopards predators?"],
    "trees": ["Do leopards climb trees?", "why do leopards drag kills into trees", "can leopards climb"],
    "habitat": ["Where do leopards live?", "What is the leopard's habitat?", "Where are leopards found?",
                "which countries have leopards", "do leopards live in africa", "Where do leopards live in Africa?"],
    "subspecies": ["How many leopard subspecies are there?", "what are the types of leopards",
                   "Tell me about the African leopard", "what is an amur leopard"],
    "rosettes": ["Why do leopards have spots?", "what are leopard rosettes", "what colour are leopards",
                 "Is every leopard's pattern unique?", "do leopards have stripes"],
    "black_panther": ["What is a black panther?", "are black leopards real", "what is melanism"],
    "vs_cheetah": ["What is the difference between a leopard and a cheetah?", "leopard vs cheetah"],
    "vs_jaguar": ["leopard or jaguar?", "What is the difference between a leopard and a jaguar?"],
    "vs_lion_tiger": ["Is a leopard bigger than a lion?", "leopard vs tiger"],
    "social": ["Are leopards social animals?", "do leopards live in groups", "are leopards solitary",
               "do leopards live alone", "how big is a leopard's territory"],
    "nocturnal": ["Are leopards nocturnal?", "do leopards sleep during the day", "when are leopards active"],
    "reproduction": ["How many cubs does a leopard have?", "how long are leopards pregnant",
                     "what do you call a baby leopard", "when do leopards mate", "what do leopard cubs eat"],
    "speed": ["How fast can a leopard run?", "how high can a leopard jump", "what is a leopard's top speed"],
    "senses": ["Can leopards see in the dark?", "are leopards strong", "can leopards swim"],
    "vocalization": ["What sounds do leopards make?", "do leopards roar", "do leopards purr"],
    "threats": ["What threatens leopards?", "why are leopards endangered", "is poaching a problem for leopards",
                "why are leopard populations declining", "what is the biggest threat to leopards"],
    "status": ["Are leopards endangered?", "What is the IUCN status of the leopard?", "are leopards protected",
               "are leopards going extinct"],
    "population": ["How many leopards are left in the wild?", "how many leopards are there in the world",
                   "what is the leopard population"],
    "human_safety": ["Are leopards dangerous to humans?", "do leopards attack people", "are leopards man-eaters"],
    "help_conservation": ["How can I help protect leopards?", "how do I save leopards", "can I donate to leopard "
                          "conservation"],
    "camera_traps": ["What are camera traps?", "how do trail cameras work for leopards"],
    "why_identify": ["Why identify individual leopards?", "why is individual identification important",
                     "what is the purpose of identifying leopards"],
    "tracks": ["What do leopard tracks look like?", "what does a leopard paw print look like"],
    "pet": ["Can leopards be kept as pets?", "can you tame a leopard"],
    "ecology": ["What is the leopard's role in the ecosystem?", "is the leopard an apex predator"],
    # --- project
    "about_project": ["What is PANTHERA?", "what is this website", "who built this", "what is this project about"],
    "how_it_works": ["How does PANTHERA identify a leopard?", "how does it work", "how does the system work",
                     "explain the pipeline", "what are the steps", "how do you recognise leopards"],
    "ivp": ["What is IVP?", "what does IVP stand for", "tell me about ivp"],
    "sift": ["What is SIFT?", "how does sift work", "what does SIFT do"],
    "ransac": ["What does RANSAC do?", "what is ransac", "explain geometric verification"],
    "ai_models": ["How is AI used here?", "which AI models do you use", "do you use machine learning",
                  "what neural networks are used"],
    "accuracy": ["How accurate is it?", "how good is the system", "can I trust the results", "what is the accuracy"],
    "limitations": ["When can the system get it wrong?", "what are the limitations", "why was the result wrong"],
    "new_leopard": ["What happens when a new leopard is found?", "what is a new leopard result",
                    "how do I add a leopard to the registry", "what does confirm and save do"],
    "decisions": ["What does 'possible match' mean?", "what is a confident match", "what are verified match points",
                  "what does the confidence label mean", "what is the threshold for a match"],
    "how_to_use": ["How do I use this site?", "how do I upload a photo", "how do I get started",
                   "how do I analyze a leopard photo"],
    "photo_tips": ["What kind of photo works best?", "tips for a good photo", "does it work with blurry photos",
                   "do night vision photos work", "why did I get a bounding box warning"],
    "file_formats": ["What file types can I upload?", "what is the maximum file size", "can I upload a png"],
    "viewpoint": ["What does viewpoint mean?", "which side of the leopard is used", "why does the angle matter"],
    "keypoints_image": ["What do the green lines in the result mean?", "what is the matched keypoints image"],
    "registry_stats": ["How many leopards are in the registry?", "how many photos are in the database",
                       "how many individuals do you have", "how big is the gallery"],
    "exact_record": ["What if I upload a photo that is already in the gallery?", "what happens if I upload the "
                     "same photo twice", "what is an exact record"],
    "privacy": ["Are my uploaded photos stored?", "do you keep my photos", "is my data safe"],
    "analysis_time": ["How long does an analysis take?", "why is the analysis slow", "how fast is the system"],
    "capabilities": ["What can you help me with?", "help", "what can I ask you"],
    "who_are_you": ["Who are you?", "are you a bot", "are you chatgpt"],
    "greeting": ["Hello", "hi", "Hey there", "good morning"],
    "thanks": ["Thanks", "thank you so much", "great"],
    "goodbye": ["Goodbye", "bye"],
}
for tid, questions in ROUTES.items():
    for q in questions:
        got = topic_of(q)
        check(got == tid, f"'{q}' -> {tid}" + ("" if got == tid else f"   (got {got})"))

# ---------------------------------------------------------------- 2. off-topic must NOT be answered
for q in ["What's the weather today?", "What is the capital of France?", "Who won the football match?",
          "Tell me a joke", "what is 2 + 2", "How do I bake bread?", "gift ideas for my sister",
          "what is the meaning of life", "swift programming tutorial"]:
    r = C.reply(q, DF)
    check(r["topic"] is None and "specifically built" in r["answer"], f"off-topic refused: '{q}'")

# ---------------------------------------------------------------- 3. leopard question we have no fact for
r = C.reply("What is a leopard's favourite song?", DF)
check(r["topic"] is None and "verified answer" in r["answer"], "unknown leopard question admits it has no answer")

# ---------------------------------------------------------------- 4. original behaviour kept
check("IVP" in C.respond("What is IVP?", DF), "respond(): IVP")
check("RANSAC" in C.respond("What does RANSAC do?", DF), "respond(): RANSAC")
check("73.7" in C.respond("How accurate is it?", DF), "respond(): accuracy numbers")
check("specifically built" in C.respond("What's the weather today?", DF), "respond(): off-topic wording")
check("sift" not in C.respond("any gift ideas", DF).lower() or "specifically built" in C.respond("any gift ideas", DF),
      "'gift' no longer triggers the SIFT answer")

# ---------------------------------------------------------------- 5. registry look-ups
check("Nawab (Panthera-326)" in C.respond(f"Tell me about {ID_A}", DF) and "2 photos" in C.respond(ID_A, DF),
      "lookup by full ID")
check("couldn't find" in C.respond("tell me about 99999999-9999-4999-8999-999999999999", DF), "unknown ID handled")
check("Tara (Panthera-042)" in C.respond("who is Panthera-042?", DF), "lookup by Panthera code")
check("Tara (Panthera-042)" in C.respond("tell me about panthera 42", DF), "code without zero padding / hyphen")
a = C.respond("tell me about Nawab", DF)
check("2 leopards" in a and "Panthera-326" in a and "Panthera-017" in a, "shared first name lists the candidates")
check("Tara (Panthera-042)" in C.respond("tell me about Tara", DF), "single first name resolves directly")
check("Panthera-32" not in C.respond("panthera-32", DF) or "couldn't find" in C.respond("panthera-32", DF),
      "'Panthera-32' does not match 'Panthera-326'")

# ---------------------------------------------------------------- 6. dynamic registry numbers
check("5 photos of 4 individual" in C.respond("how many leopards are in the registry", DF), "counts from the data")
r = C.reply("how many leopards are in the registry", DF, {"photos": 6767, "leopards": 425})
check("6,767 photos of 425 individual" in r["answer"], "live stats override the dataframe counts")

# ---------------------------------------------------------------- 7. suggestions
for tid, t in C.BY_ID.items():
    for follow in t["ask"]:
        check(follow in C.BY_ID, f"{tid}: follow-up '{follow}' exists")
    check(topic_of(t["example"]) == tid, f"{tid}: its own example question resolves to it")
for sid in C.STARTER_IDS:
    check(sid in C.BY_ID, f"starter '{sid}' exists")
r = C.reply("What do leopards eat?", DF)
check(1 <= len(r["suggestions"]) <= 3 and all(topic_of(s) is not None for s in r["suggestions"]),
      "every suggestion after an answer is itself answerable")
check(len(C.reply("zzz qqq", DF)["suggestions"]) >= 1, "fallback still offers suggestions")
check(all(topic_of(s) is not None for s in C.reply("zzz qqq", DF)["suggestions"]), "fallback suggestions answerable")
check(C.reply("", DF)["topic"] is None and C.reply(None, DF)["topic"] is None, "empty / None question is safe")
check(C.reply("leopard " * 400, DF)["answer"] != "", "very long input is safe")

print(f"\n{'ALL CHECKS PASSED' if failed == 0 else str(failed) + ' CHECK(S) FAILED'}")
raise SystemExit(failed)
