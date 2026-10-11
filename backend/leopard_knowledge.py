"""
Curated leopard facts for the chatbot (plain data, edit freely).

Each topic:
  id        unique key
  example   the canonical question for this topic (also shown as a suggestion chip)
  triggers  phrases; a trigger matches when ALL its words appear in the question (any order, plurals/tenses ignored)
  patterns  optional regexes run on the lower-cased, punctuation-free question (for exact-shape questions)
  answer    the reply
  ask       ids of topics to suggest next
Numbers are deliberately given as rounded ranges; they are general field-biology values, not figures from our dataset.
"""

TOPICS = [
    {
        "id": "overview",
        "example": "Tell me about leopards",
        "triggers": ["leopard fact", "fun fact", "interesting fact", "leopard overview", "leopard introduction",
                     "general information"],
        "patterns": [r"^(tell me (something |more )?about|what (is|are)|describe|explain|facts? about|"
                     r"info(rmation)? (on|about)|learn about)( (a|an|the))? leopards?$", r"^leopards?$"],
        "answer": ("Leopards (Panthera pardus) are medium-sized big cats famous for their rosette-patterned coats, "
                   "strength and stealth. They live across sub-Saharan Africa and parts of Asia, are mostly solitary "
                   "and nocturnal, and are listed as Vulnerable on the IUCN Red List. Ask me about their diet, "
                   "habitat, behaviour, spots or conservation, or how PANTHERA identifies individual leopards."),
        "ask": ["diet", "habitat", "rosettes"],
    },
    {
        "id": "taxonomy",
        "example": "What is the scientific name of a leopard?",
        "triggers": ["scientific name", "latin name", "species name", "panthera pardus", "genus", "taxonomy",
                     "big cat family", "classification"],
        "answer": ("The leopard's scientific name is Panthera pardus. It belongs to the genus Panthera, the 'big "
                   "cats', together with lions, tigers, jaguars and snow leopards."),
        "ask": ["subspecies", "size"],
    },
    {
        "id": "size",
        "example": "How big is a leopard?",
        "triggers": ["how big", "how large", "how heavy", "how tall", "size", "weight", "weigh", "length", "height"],
        "answer": ("Leopards are medium-sized big cats. Adult males typically weigh roughly 30-90 kg and females "
                   "roughly 25-60 kg, with a head-and-body length of about 1-1.9 m plus a tail of 60-110 cm. Size "
                   "varies a lot by region, and males are noticeably bigger than females."),
        "ask": ["speed", "lifespan"],
    },
    {
        "id": "lifespan",
        "example": "How long do leopards live?",
        "triggers": ["lifespan", "life span", "how long live", "how old", "life expectancy", "year live",
                     "how many year", "oldest leopard"],
        "answer": ("In the wild, leopards typically live around 12-15 years; in captivity they can reach 20 years "
                   "or more. Injuries, competition with other predators and human-caused threats mean many wild "
                   "leopards never reach old age."),
        "ask": ["threats", "reproduction"],
    },
    {
        "id": "diet",
        "example": "What do leopards eat?",
        "triggers": ["eat", "diet", "prey", "food", "feed", "meal", "carnivore", "herbivore", "omnivore",
                     "animal hunt", "animal eat", "hunt eat", "kind food"],
        "answer": ("Leopards are carnivores and very opportunistic hunters. They eat everything from rodents, birds "
                   "and reptiles to monkeys, warthogs and antelope such as impala and gazelle; researchers have "
                   "recorded more than 90 prey species across their range. In much of Africa, medium-sized "
                   "antelope make up a big share of the diet."),
        "ask": ["hunting", "trees"],
    },
    {
        "id": "hunting",
        "example": "How do leopards hunt?",
        "triggers": ["hunt", "stalk", "ambush", "kill", "predator", "attack prey", "hunter", "how catch"],
        "answer": ("Leopards are stealth ambush hunters. They stalk prey silently, get as close as they can, then "
                   "pounce, usually at night or around dusk and dawn, and kill with a powerful bite to the throat "
                   "or muzzle. They often drag a kill up into a tree to keep it away from lions and hyenas."),
        "ask": ["trees", "speed", "diet"],
    },
    {
        "id": "trees",
        "example": "Do leopards climb trees?",
        "triggers": ["tree", "climb", "climber", "branch", "sleep tree"],
        "answer": ("Leopards are superb climbers. They rest in trees during the day, use branches as lookouts, and "
                   "haul kills, sometimes heavier than themselves, up into the canopy to protect them from "
                   "scavengers like hyenas and lions. Powerful shoulders and forelimbs and sharp, retractable "
                   "claws make this possible."),
        "ask": ["hunting", "rosettes"],
    },
    {
        "id": "habitat",
        "example": "Where do leopards live?",
        "triggers": ["habitat", "where live", "where find", "range", "distribution", "environment", "terrain",
                     "savanna", "jungle", "rainforest", "desert", "mountain", "country", "continent", "africa"],
        "answer": ("Leopards have one of the widest ranges of any wild cat. They live across sub-Saharan Africa and "
                   "in parts of Asia, from India and Sri Lanka to Southeast Asia and the Russian Far East. They are "
                   "highly adaptable: savanna, woodland, rainforest, mountains, semi-desert, even areas close to "
                   "towns. In Africa they occur in places like the Serengeti and Maasai Mara, Kruger and the "
                   "Okavango Delta. Even so, leopards have lost most of their historic range to habitat loss."),
        "ask": ["subspecies", "threats"],
    },
    {
        "id": "subspecies",
        "example": "What are the leopard subspecies?",
        "triggers": ["subspecies", "type leopard", "kind leopard", "african leopard", "indian leopard", "amur",
                     "persian leopard", "arabian", "javan", "sri lankan", "indochinese"],
        "answer": ("Eight leopard subspecies are generally recognised: the African leopard (P. p. pardus), Indian "
                   "(fusca), Indochinese (delacouri), Javan (melas), Sri Lankan (kotiya), Amur (orientalis), "
                   "Persian (tulliana) and Arabian (nimr). The African leopard is the most widespread; the Amur, "
                   "Arabian and Javan leopards are Critically Endangered."),
        "ask": ["status", "habitat"],
    },
    {
        "id": "rosettes",
        "example": "Why do leopards have spots?",
        "triggers": ["spot", "rosette", "pattern", "marking", "coat", "fur", "skin", "stripe", "camouflage",
                     "fingerprint", "unique", "colour", "color"],
        "answer": ("A leopard's coat is covered in rosettes, rose-shaped clusters of spots with no dot in the "
                   "centre, along the flanks and back, with solid spots on the head, legs and belly. The pattern "
                   "is camouflage, and it is unique to every individual, like a fingerprint, which is exactly what "
                   "makes photo identification possible."),
        "ask": ["black_panther", "how_it_works"],
    },
    {
        "id": "black_panther",
        "example": "What is a black panther?",
        "triggers": ["black panther", "!melanistic", "!melanism", "black leopard", "panther"],
        "answer": ("A 'black panther' is not a separate species. It is a leopard (in Africa and Asia) or a jaguar "
                   "(in the Americas) with melanism, a genetic trait that produces a dark coat. The rosettes are "
                   "still there and can be seen in the right light. Black leopards are far more common in humid "
                   "forests of Southeast Asia than in Africa, where they are rare."),
        "ask": ["rosettes", "vs_jaguar"],
    },
    {
        "id": "vs_cheetah",
        "example": "What is the difference between a leopard and a cheetah?",
        "triggers": ["cheetah"],
        "answer": ("Cheetahs are slender and long-legged, built for speed, with solid black spots and dark 'tear "
                   "lines' running from the eyes to the mouth. Leopards are stockier and more powerful, with "
                   "rosette-patterned coats, and they climb trees, which cheetahs rarely do. Leopards hunt mostly at "
                   "night, cheetahs mostly by day."),
        "ask": ["speed", "vs_jaguar"],
    },
    {
        "id": "vs_jaguar",
        "example": "What is the difference between a leopard and a jaguar?",
        "triggers": ["jaguar"],
        "answer": ("Jaguars live in the Americas, leopards in Africa and Asia. Jaguars are stockier with a bigger "
                   "head and heavier build, and their rosettes usually have a small dot inside, which a leopard's "
                   "rosettes don't. Jaguars are also more at home in water."),
        "ask": ["black_panther", "rosettes"],
    },
    {
        "id": "vs_lion_tiger",
        "example": "How do leopards compare to lions and tigers?",
        "triggers": ["lion", "tiger", "largest cat", "biggest cat"],
        "answer": ("Leopards are smaller than lions, tigers and jaguars, but they are among the most adaptable big "
                   "cats, able to live in far more habitats, and the best climbers. Unlike lions, leopards live and "
                   "hunt alone rather than in prides, and unlike tigers they are found in both Africa and Asia."),
        "ask": ["size", "social"],
    },
    {
        "id": "social",
        "example": "Are leopards social animals?",
        "triggers": ["solitary", "social", "territory", "territorial", "alone", "pride", "pack", "group",
                     "how big territory", "territory size", "big territory", "home range"],
        "answer": ("Leopards are mostly solitary and territorial. An adult male's territory usually overlaps those "
                   "of several females; they mark it with scent, claw marks and calls and generally meet only to "
                   "mate. Mothers stay with their cubs until the young are ready to go off on their own."),
        "ask": ["reproduction", "nocturnal"],
    },
    {
        "id": "nocturnal",
        "example": "Are leopards nocturnal?",
        "triggers": ["nocturnal", "night", "dusk", "dawn", "crepuscular", "sleep", "rest", "active day",
                     "when active", "when hunt", "when sleep"],
        "answer": ("Leopards are mainly nocturnal and crepuscular, most active at night and around dusk and dawn. "
                   "By day they rest in trees, dense thickets or rocky outcrops, which is one reason camera traps "
                   "are so valuable for studying them."),
        "ask": ["camera_traps", "hunting"],
    },
    {
        "id": "reproduction",
        "example": "How many cubs does a leopard have?",
        "triggers": ["cub", "baby", "mate", "breed", "pregnant", "pregnancy", "gestation", "litter", "young",
                     "birth", "born", "reproduce", "baby leopard", "mother", "cub eat"],
        "answer": ("After a gestation of roughly 90-105 days, a female usually gives birth to 2-3 cubs (litters of "
                   "1-4 are possible) in a hidden den. Cubs are born blind, nurse at first and gradually move on "
                   "to meat, and stay with their mother for roughly 18-24 months before leaving to find their own "
                   "territory. Many cubs do not survive their first year."),
        "ask": ["lifespan", "social"],
    },
    {
        "id": "speed",
        "example": "How fast can a leopard run?",
        "triggers": ["fast", "speed", "sprint", "run", "jump", "leap", "mph", "how quick"],
        "answer": ("Leopards can sprint at up to roughly 55-60 km/h (about 35 mph) in short bursts, and can leap "
                   "around 6 m horizontally and 3 m straight up. They rely on stealth and a short, explosive rush "
                   "rather than long chases."),
        "ask": ["hunting", "trees"],
    },
    {
        "id": "senses",
        "example": "How strong are leopards and what are their senses like?",
        "triggers": ["strong", "strength", "sense", "eyesight", "vision", "hearing", "smell", "swim",
                     "night vision", "see dark"],
        "answer": ("Leopards are exceptionally strong for their size; they can carry prey heavier than themselves "
                   "up a tree. Their senses are sharp: excellent night vision and hearing and a good sense of "
                   "smell. They are also capable swimmers."),
        "ask": ["trees", "speed"],
    },
    {
        "id": "vocalization",
        "example": "What sounds do leopards make?",
        "triggers": ["roar", "sound", "call", "noise", "growl", "purr", "vocal", "scream", "communicate"],
        "answer": ("A leopard's signature call is a hoarse, rasping 'sawing' cough, often described as a rough "
                   "roar, used to announce its presence. They also growl, snarl and grunt. Unlike domestic cats, big "
                   "cats of the genus Panthera don't purr continuously."),
        "ask": ["social", "nocturnal"],
    },
    {
        "id": "threats",
        "example": "What threatens leopards?",
        "triggers": ["threat", "threaten", "poach", "decline", "why endangered", "why vulnerable", "habitat loss",
                     "conflict", "kill livestock", "trophy", "snare", "fur trade", "skin trade", "extinction",
                     "decrease", "why declining"],
        "answer": ("Leopards face several threats: loss and fragmentation of habitat, a shrinking prey base, "
                   "retaliatory killing over livestock, poaching and illegal trade for skins and body parts, "
                   "trophy hunting, and snares set for other animals. Because leopards are elusive and live at low "
                   "densities, population trends are hard to track, which is one reason individual-identification "
                   "work like ours matters."),
        "ask": ["status", "help_conservation"],
    },
    {
        "id": "status",
        "example": "Are leopards endangered?",
        "triggers": ["endanger", "extinct", "iucn", "red list", "conservation status", "vulnerable", "protected",
                     "legal", "cites", "status"],
        "answer": ("Leopards are listed as Vulnerable on the IUCN Red List, and their numbers are declining. Some "
                   "subspecies are in worse shape: the Amur, Arabian and Javan leopards are Critically Endangered. "
                   "Leopards are also listed under CITES Appendix I, which prohibits international commercial trade "
                   "in the animals and their parts."),
        "ask": ["threats", "population"],
    },
    {
        "id": "population",
        "example": "How many leopards are left in the wild?",
        "triggers": ["how many world", "how many wild", "how many left", "how many remain", "how many exist",
                     "how many alive", "population", "number world", "number wild", "number left"],
        "answer": ("Nobody knows exactly. Leopards are secretive and spread across enormous areas, so there is no "
                   "reliable global count, only regional estimates that vary widely. What is clear is that their "
                   "range has shrunk drastically and populations are declining. That uncertainty is a big reason "
                   "camera-trap surveys and individual identification are so important."),
        "ask": ["status", "camera_traps"],
    },
    {
        "id": "human_safety",
        "example": "Are leopards dangerous to humans?",
        "triggers": ["dangerous", "attack", "man eater", "safe", "harm", "afraid", "hurt", "aggressive", "human"],
        "answer": ("Leopards are generally elusive and avoid people, and attacks on humans are rare. Most incidents "
                   "happen where leopards live close to settlements, or when an animal is cornered, injured or "
                   "surprised. If you are ever in leopard country: keep a safe distance, never approach or feed "
                   "wildlife, stay calm, back away slowly, and follow local rangers' guidance."),
        "ask": ["threats", "social"],
    },
    {
        "id": "help_conservation",
        "example": "How can I help protect leopards?",
        "triggers": ["protect", "save", "help protect", "help leopard", "donate", "volunteer",
                     "conservation effort"],
        "answer": ("You can help by supporting reputable conservation organisations and anti-poaching efforts, "
                   "never buying products made from wildlife, choosing responsible wildlife tourism, and backing "
                   "programmes that help communities live alongside predators (for example predator-proof livestock "
                   "enclosures). Individual-identification tools like PANTHERA help researchers monitor "
                   "populations without collars or capture."),
        "ask": ["threats", "why_identify"],
    },
    {
        "id": "camera_traps",
        "example": "What are camera traps?",
        "triggers": ["!camera trap", "!trail camera", "camera"],
        "answer": ("Camera traps are weatherproof cameras triggered by motion or body heat, mounted along trails "
                   "and waterholes. They photograph elusive animals like leopards day and night without disturbing "
                   "them, and because each leopard's rosette pattern is unique, the photos can be used to recognise "
                   "individuals and estimate population size."),
        "ask": ["why_identify", "how_it_works"],
    },
    {
        "id": "why_identify",
        "example": "Why identify individual leopards?",
        "triggers": ["!why identify", "!why individual", "!individual identification", "purpose", "importance", "important", "why track",
                     "benefit", "research", "monitor"],
        "answer": ("Knowing which individual is which lets researchers estimate how many leopards live in an area, "
                   "follow survival and breeding, see how animals use their territories, and spot conflict "
                   "hotspots, all without collars or tranquillising animals. Rosette patterns stay stable "
                   "throughout life, so a photo from years ago can still be matched to the same animal."),
        "ask": ["camera_traps", "how_it_works"],
    },
    {
        "id": "tracks",
        "example": "What do leopard tracks look like?",
        "triggers": ["track", "paw", "print", "footprint", "pugmark", "claw", "scat"],
        "answer": ("A leopard's paw print is roughly 7-10 cm across, rounded, with four toes and a large "
                   "three-lobed pad. Like other cats, leopards keep their claws retracted when walking, so claw "
                   "marks rarely show in the tracks. Prints are one way field researchers confirm that leopards "
                   "are present."),
        "ask": ["camera_traps", "habitat"],
    },
    {
        "id": "pet",
        "example": "Can leopards be kept as pets?",
        "triggers": ["pet", "tame", "domestic", "keep leopard"],
        "answer": ("Leopards are wild animals and make dangerous, unsuitable pets. Keeping them is illegal in many "
                   "places, and the exotic-pet trade harms wild populations. If you love leopards, the best way to "
                   "help is to support their protection in the wild."),
        "ask": ["help_conservation", "human_safety"],
    },
    {
        "id": "ecology",
        "example": "What is the leopard's role in the ecosystem?",
        "triggers": ["ecosystem", "apex", "top predator", "ecological", "food chain", "keystone"],
        "answer": ("As large predators, leopards help keep herbivore populations in balance, and in many "
                   "ecosystems they are an apex or near-apex predator. Their presence is often a sign of a healthy "
                   "ecosystem with enough prey and cover."),
        "ask": ["diet", "threats"],
    },
]
