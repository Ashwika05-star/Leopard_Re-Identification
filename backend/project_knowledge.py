"""
Chatbot topics about the PANTHERA system itself (same format as leopard_knowledge.py).
Wording follows pipeline.py / decision.py so the bot never claims more than the system does.
{leopards} and {photos} in an answer are replaced with live registry counts.
"""

TOPICS = [
    {
        "id": "about_project",
        "example": "What is PANTHERA?",
        "triggers": ["project", "website", "who made", "who built", "who created", "who develop", "creator",
                     "developer", "panthera"],
        "patterns": [r"^(what (is|s)|whats) (this|panthera)( (site|website|project|app|system|platform))?$"],
        "answer": ("PANTHERA is a leopard individual-identification system. It combines classical image processing "
                   "(IVP: SIFT keypoints and RANSAC geometric verification) with four AI models to recognise "
                   "individual leopards from photographs of their unique rosette patterns, and keeps a growing "
                   "registry of the individuals it has seen."),
        "ask": ["how_it_works", "accuracy", "how_to_use"],
    },
    {
        "id": "how_it_works",
        "example": "How does PANTHERA identify a leopard?",
        "triggers": ["how work", "how identify", "how recognise", "how recognize", "pipeline", "process", "step",
                     "method", "algorithm", "technique", "how system", "how detect", "how match", "how know",
                     "how panthera identify", "how panthera work"],
        "answer": ("Here is the pipeline:\n"
                   "1. An AI model checks the photo really shows a leopard.\n"
                   "2. Two more AI models judge the image condition (dark, grayscale, red-tinted...) and which side "
                   "of the leopard is visible.\n"
                   "3. IVP enhances the image (CLAHE contrast enhancement) and extracts SIFT keypoints from the "
                   "rosette pattern.\n"
                   "4. Those keypoints are compared with gallery photos from the same viewpoint, and RANSAC keeps "
                   "only matches that form a consistent geometry. These are the 'verified match points'.\n"
                   "5. A fourth AI model gives an independent identity estimate.\n"
                   "6. A decision step fuses both signals into MATCH, POSSIBLE MATCH or NEW LEOPARD."),
        "ask": ["sift", "ransac", "decisions"],
    },
    {
        "id": "ivp",
        "example": "What is IVP?",
        "triggers": ["ivp", "image video processing", "how ivp work"],
        "answer": ("IVP (Image and Video Processing) refers to the classical computer-vision techniques we use: "
                   "image enhancement, SIFT keypoint extraction and RANSAC geometric verification. It forms the "
                   "core identification method in our system and, unlike the AI models, involves no learned "
                   "model."),
        "ask": ["sift", "ransac", "ai_models"],
    },
    {
        "id": "sift",
        "example": "What is SIFT?",
        "triggers": ["sift", "scale invariant", "how sift work"],
        "answer": ("SIFT (Scale-Invariant Feature Transform) is a classical computer-vision algorithm that finds "
                   "distinctive landmark points ('keypoints') in an image that stay recognisable despite changes in "
                   "scale or rotation. We use it to pick out landmark points on a leopard's rosette pattern. This is "
                   "the core IVP technique used for identification."),
        "ask": ["ransac", "keypoints_image"],
    },
    {
        "id": "ransac",
        "example": "What does RANSAC do?",
        "triggers": ["ransac", "random sample consensus", "geometric verification", "how ransac work"],
        "answer": ("RANSAC (Random Sample Consensus) is a classical geometric verification technique. It checks "
                   "whether matched keypoints between two leopard photos form a consistent spatial arrangement, "
                   "filtering out coincidental matches. It is part of our IVP pipeline, not an AI component."),
        "ask": ["sift", "decisions"],
    },
    {
        "id": "ai_models",
        "example": "How is AI used here?",
        "triggers": ["ai", "artificial intelligence", "neural network", "model", "deep learning",
                     "machine learning", "resnet", "classifier", "ai use", "ai model", "how ai", "ai work"],
        "answer": ("AI is used in four ways in this system: (1) validating that the image shows a leopard, (2) "
                   "classifying image condition with 92.8% accuracy, (3) predicting the leopard's viewpoint with "
                   "81.8% accuracy, and (4) an identity classifier that directly predicts which leopard it is, with "
                   "81.9% accuracy. The primary identification decision uses IVP-based SIFT and RANSAC matching, "
                   "which testing showed to be more reliable at large-scale search."),
        "ask": ["ivp", "accuracy"],
    },
    {
        "id": "accuracy",
        "example": "How accurate is it?",
        "triggers": ["accuracy", "accurate", "how good", "reliable", "reliability", "precision", "correct",
                     "trust", "success rate", "how good system"],
        "answer": ("Our system correctly identifies the right leopard as the top match 73.7% of the time, and within "
                   "the top 5 guesses 82.6% of the time. When the system reports high confidence, it is correct 92% "
                   "of the time."),
        "ask": ["limitations", "decisions"],
    },
    {
        "id": "limitations",
        "example": "When can the system get it wrong?",
        "triggers": ["limitation", "wrong", "mistake", "fail", "incorrect", "error", "not match"],
        "answer": ("No system is perfect: identification is correct about 73.7% of the time at the top match. "
                   "Low-quality photos, unusual angles, partial views, or leopards that are not in the registry can "
                   "give a wrong or uncertain result. That is why uncertain results are labelled POSSIBLE MATCH "
                   "instead of being forced into a MATCH, and why you can review the photos and keypoints yourself."),
        "ask": ["accuracy", "photo_tips"],
    },
    {
        "id": "new_leopard",
        "example": "What happens when a new leopard is found?",
        "triggers": ["new leopard", "new individual", "unknown leopard", "no match", "new discovery", "discover",
                     "confirm", "save registry", "add registry", "add gallery", "register"],
        "answer": ("When a photo doesn't match any leopard in our registry with enough confidence, the result is "
                   "NEW LEOPARD with a provisional ID and name (like 'Discovery-425'). If you click 'Confirm & Save "
                   "to Registry', the photo is added to the gallery so future photos of that leopard can be "
                   "recognised. In our testing, genuinely new leopards were correctly flagged 84% of the time."),
        "ask": ["decisions", "registry_stats"],
    },
    {
        "id": "decisions",
        "example": "What does 'possible match' mean?",
        "triggers": ["possible match", "decision", "confident match", "confidence", "confident", "threshold",
                     "verified point", "verified match", "match mean", "possible mean", "upgrade", "uncertain"],
        "answer": ("Results rest on 'verified match points': keypoints that survive RANSAC verification between "
                   "your photo and a gallery photo.\n"
                   "- 20 or more: a confident MATCH.\n"
                   "- 6 to 19: an uncertain zone. If the independent AI identity estimate agrees with at least 50% "
                   "confidence the result is upgraded to a MATCH; otherwise it is shown as a POSSIBLE MATCH for you "
                   "to review.\n"
                   "- Fewer than 6: the AI can only suggest a POSSIBLE MATCH if it is at least 70% confident; "
                   "otherwise the photo is treated as a NEW LEOPARD.\n"
                   "The confidence label reads high for confident results, medium for possible matches and 'new' "
                   "when nothing matched."),
        "ask": ["ransac", "new_leopard"],
    },
    {
        "id": "how_to_use",
        "example": "How do I use this site?",
        "triggers": ["how use", "get started", "upload", "how analyze", "how analyse", "identify photo", "submit photo",
                     "start analysis", "user guide", "how begin"],
        "answer": ("Open the Analyse page, drop in (or browse for) a JPG, PNG or WEBP photo up to 25 MB, and click Analyze "
                   "Image. You will see the decision (match, possible match or new leopard), the closest registry "
                   "leopard with its photo, the SIFT keypoint matches, and the confidence of each signal. If a new "
                   "leopard is found, you can confirm it to add it to the registry."),
        "ask": ["photo_tips", "decisions"],
    },
    {
        "id": "photo_tips",
        "example": "What kind of photo works best?",
        "triggers": ["best photo", "good photo", "photo quality", "photo tip", "which photo", "blurry", "blur",
                     "resolution", "night vision photo", "infrared", "camera trap photo", "tip", "quality",
                     "clear photo", "requirement", "whole photo", "bounding box", "crop", "warning"],
        "answer": ("For the best results use a sharp photo where the leopard fills most of the frame, ideally "
                   "showing the flank (side) with the rosettes clearly visible. Night-vision and infrared "
                   "camera-trap frames work too. If you upload a photo that isn't already in our dataset, the "
                   "whole photo is used (you will see a warning), so cluttered backgrounds or a very small leopard "
                   "in the frame can lower accuracy; a tighter crop around the animal helps."),
        "ask": ["file_formats", "viewpoint"],
    },
    {
        "id": "file_formats",
        "example": "What file types can I upload?",
        "triggers": ["file type", "file format", "format", "file size", "maximum size", "size limit", "jpg", "jpeg",
                     "png", "webp", "upload limit", "supported"],
        "answer": "You can upload JPG, PNG or WEBP images up to 25 MB.",
        "ask": ["how_to_use", "photo_tips"],
    },
    {
        "id": "viewpoint",
        "example": "What does viewpoint mean?",
        "triggers": ["viewpoint", "angle", "view point", "orientation", "side"],
        "answer": ("Viewpoint is which side of the leopard is visible: front, back, left, right or down. The "
                   "rosette pattern differs on each flank, so the system only compares your photo with gallery "
                   "photos taken from the same viewpoint. An AI model predicts it automatically (for photos already "
                   "in our dataset the recorded viewpoint is used)."),
        "ask": ["how_it_works", "photo_tips"],
    },
    {
        "id": "keypoints_image",
        "example": "What do the green lines in the result mean?",
        "triggers": ["green line", "keypoint image", "matched keypoint", "visualization", "visualisation",
                     "connect line"],
        "answer": ("That picture shows your photo next to the matched gallery photo, with a green line joining each "
                   "pair of verified keypoints: landmark points on the rosette pattern that SIFT found in both "
                   "photos and that passed RANSAC's geometry check. The more consistent lines, the stronger the "
                   "match."),
        "ask": ["sift", "decisions"],
    },
    {
        "id": "registry_stats",
        "example": "How many leopards are in the registry?",
        "triggers": ["how many database", "how many registry", "how many gallery", "how many photo",
                     "how many individual", "how many catalogued", "how many record", "registry size",
                     "database size", "gallery size", "how big database", "how big gallery", "how big registry", "catalogue", "catalog", "registry",
                     "database", "gallery"],
        "answer": ("The registry currently holds {photos} photos of {leopards} individual leopards. It grows "
                   "whenever a newly discovered leopard is confirmed after an analysis."),
        "ask": ["new_leopard", "how_it_works"],
    },
    {
        "id": "exact_record",
        "example": "What if I upload a photo that is already in the gallery?",
        "triggers": ["same photo", "duplicate", "exact copy", "exact record", "upload twice", "already gallery",
                     "hash"],
        "answer": ("If you upload an exact copy of a photo that is already in the gallery, the system recognises "
                   "it by its file fingerprint (an MD5 hash). It then uses that photo's recorded bounding box and "
                   "viewpoint, and it will not match the photo against itself. If it is the only photo we hold of "
                   "that leopard, the result is flagged as an exact record."),
        "ask": ["decisions", "viewpoint"],
    },
    {
        "id": "privacy",
        "example": "Are my uploaded photos stored?",
        "triggers": ["privacy", "store photo", "delete photo", "save photo", "keep photo", "data safe", "stored"],
        "answer": ("Photos you upload are saved on the server so the result page can show them and the keypoint "
                   "view. A photo is only added to the leopard registry if you explicitly confirm a new leopard."),
        "ask": ["new_leopard", "how_to_use"],
    },
    {
        "id": "analysis_time",
        "example": "How long does an analysis take?",
        "triggers": ["how long analyze", "how long analyse", "how long analysis", "analyze take", "analysis take",
                     "analyse take", "slow", "wait", "loading", "take long", "fast system", "fast analysis",
                     "response time", "processing time", "speed analysis"],
        "answer": ("An analysis usually takes several seconds, because the server runs several AI models and "
                   "searches the whole gallery for matching keypoints. The first request after the server starts "
                   "can be slower."),
        "ask": ["how_it_works", "how_to_use"],
    },
    {
        "id": "capabilities",
        "example": "What can you help me with?",
        "triggers": ["help", "ask", "capability", "topic", "do anything"],
        "patterns": [r"^what can (you|i) (do|ask)", r"^what (do|can) you (know|answer)"],
        "answer": ("I can answer questions about leopards (diet, habitat, behaviour, spots, conservation, "
                   "subspecies and more), explain how PANTHERA identifies individuals (IVP, SIFT, RANSAC, the AI "
                   "models, accuracy and what the results mean), help you use the site, and look up a leopard in "
                   "the registry by name or ID."),
        "ask": ["diet", "habitat", "how_it_works"],
    },
    {
        "id": "who_are_you",
        "example": "Who are you?",
        "triggers": ["chatgpt", "gpt", "llm", "chatbot", "bot", "real person", "your name"],
        "patterns": [r"^(who|what) are you$", r"^are you (a |an )?(bot|ai|human|robot|real)"],
        "answer": ("I'm the PANTHERA assistant, a rule-based chatbot that answers from a curated set of leopard "
                   "facts and information about this project. I don't generate answers freely, so I only say what I "
                   "can stand behind."),
        "ask": ["capabilities", "about_project"],
    },
    {
        "id": "greeting",
        "example": "Hello",
        "triggers": [],
        "patterns": [r"^(hi|hello|hey|hiya|howdy|greetings|good (morning|afternoon|evening))"
                     r"( there| panthera| assistant| bot)*$"],
        "answer": ("Hello! I'm the PANTHERA assistant. Ask me about leopards, how our identification works, or look "
                   "up a leopard by name or ID."),
        "ask": ["diet", "habitat", "how_it_works"],
    },
    {
        "id": "thanks",
        "example": "Thanks",
        "triggers": [],
        "patterns": [r"^(thanks|thank you|thx|ty|cheers|great|awesome|cool|nice|perfect)"
                     r"( a lot| so much| very much)?( panthera| bot| assistant)?$"],
        "answer": "You're welcome! Ask me anything else about leopards or how identification works.",
        "ask": ["diet", "how_it_works"],
    },
    {
        "id": "goodbye",
        "example": "Goodbye",
        "triggers": [],
        "patterns": [r"^(bye|goodbye|see you|see ya|cya|good night)( panthera| bot| assistant)?$"],
        "answer": "Goodbye! Come back any time.",
        "ask": [],
    },
]
