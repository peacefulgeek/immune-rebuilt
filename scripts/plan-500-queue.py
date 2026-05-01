#!/usr/bin/env python3
"""Build 500 unique queue specs for Immune Rebuilt.

Each spec carries:
  - slug (unique vs. published 30 + within the 500)
  - title
  - category (one of the existing 6)
  - angle (1-2 sentence editorial framing in our voice)
  - asins (rotated subset of the apothecary)
  - related (4 slugs from published 30 OR earlier in the 500)
  - hero_prompt (specific watercolor prompt, light palette, no dark imagery)

We do NOT auto-call any LLM here; this is a deterministic Python builder so the
same seed -> same 500 specs.
"""
from __future__ import annotations
import json, hashlib, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "scripts" / "queue-500-specs.json"

# The six categories (mirrored from article-plan.mjs).
CATEGORIES = [
    "Root Causes",
    "Gut Healing",
    "AIP & Diet",
    "Stress & Nervous System",
    "Functional Medicine",
    "Emotional Roots",
]

# Apothecary ASIN pool (50 verified). Rotated 3 per article.
APOTHECARY_ASINS = [
    "B07ZFK6V8F","B01M0WX29B","B07JHHJVLD","B07PMLR4P5","B07VTJTWGN",
    "B0B1PYV3GH","B084CHS1GM","B0851T4P8M","B07KSQXCMG","B074MGB2YG",
    "B003B3OOPA","B074H5YL18","B003WOZJ44","B00W4O8R0K","B003B3P0WW",
    "B00LH3DPFW","B00JEKYNZA","B0011865IQ","B003WOZJ44","B07TMTC4HN",
    "B07GTZL2LW","B086V44J9X","B084DRDSDX","B003B3OQ04","B07KFM98CW",
    "B00CGMJEN8","B07GR4N9P3","B0009TM3GA","B0014DCXRA","B003JZQEC2",
    "B0058AASOA","B07VHJM4S5","B07L7QXG8J","B003ZBVLY8","B0019IM2D2",
    "B003ZBVMM4","B074FCV99F","B084H7LBGD","B00OYPYB3Y","B071S4P2J5",
    "B0BR9JM7H4","B073KP78NM","B00WBRX2ZE","B07RKL44TW","B086P8VVWZ",
    "B0BJ8L7GBR","B083R6QHK7","B07J5XMJL3","B07ZB9HX7J","B0CG34M4PF",
]

# Per-category slug seed lists. We expand each to ~83 unique slugs (500/6).
# Each slug below is a stable kebab-case key. We then add modifier suffixes
# ("part-2", "in-women", "in-perimenopause", "for-flares", etc.) to scale.
SEEDS: dict[str, list[tuple[str, str, str]]] = {
    "Root Causes": [
        ("genetic-load-vs-environment", "Genes load the gun, environment pulls the trigger", "What twin studies actually show, and why your environment carries more weight than your DNA."),
        ("the-multi-hit-hypothesis", "The multi-hit hypothesis, in plain language", "Why one cause is rarely enough, and why two or three together flip the switch."),
        ("the-threshold-model-of-autoimmunity", "The threshold model of autoimmunity", "What it means that your immune system has a tipping point, and how to give it room."),
        ("infection-as-trigger-overview", "When an infection becomes the spark", "How specific microbes plausibly seed autoimmune disease, and why timing matters."),
        ("environmental-toxicants-and-the-immune-system", "Environmental load and immune drift", "A careful look at what plastics, solvents, and metals can plausibly do to a tired immune system."),
        ("vitamin-d-and-autoimmunity", "Vitamin D, sun, and autoimmune risk", "What the literature actually supports, what it doesn't, and where the supplement crowd gets ahead of the data."),
        ("estrogen-and-autoimmune-prevalence", "Why so many of us are women", "The estrogen and X-chromosome story, told without panic."),
        ("circadian-rhythm-and-immune-function", "Sleep timing and the immune clock", "Why the same number of hours at the wrong time hits differently."),
        ("cortisol-and-immune-dysregulation", "Cortisol's quiet role in autoimmune flares", "Beyond the adrenal-fatigue story to the boring, slow physiology that actually matters."),
        ("food-sensitivities-vs-allergies", "Sensitivity, intolerance, allergy: the language matters", "Why mixing these up sends people to the wrong tests and the wrong fixes."),
        ("the-gut-immune-axis-overview", "How the gut and the immune system actually talk", "GALT, M-cells, sIgA, and why a little vocabulary helps a lot."),
        ("dental-amalgams-and-mercury-fears", "Mercury fillings: what's evidence and what's worry", "A measured tour of the literature so you can decide without selling your house."),
        ("breast-implants-and-autoimmune-symptoms", "Breast implants and autoimmune symptoms", "Where the data actually sits and how to think about your own situation."),
        ("childhood-infections-and-adult-autoimmunity", "What childhood infections may have set in motion", "Why your strep, your mono, your bouts of flu can echo decades later."),
        ("c-section-birth-and-immune-development", "Birth mode and the infant immune blueprint", "Why C-section babies often need a little more microbial help."),
        ("antibiotic-exposure-as-cumulative-load", "How antibiotic history adds up", "Each course is a little hand on the scale, even when you needed it."),
        ("the-hygiene-hypothesis-update", "The hygiene hypothesis, revisited", "What the original idea got right, what it got wrong, and where it stands now."),
        ("vaccine-questions-and-autoimmunity-risk", "Reasonable questions about vaccines and autoimmunity", "A non-tribal walkthrough of the actual evidence base."),
        ("genetic-testing-23andme-and-autoimmunity", "What 23andMe can and cannot tell you about autoimmunity", "Useful, limited, and easy to misread."),
        ("hla-genes-and-autoimmune-disease", "HLA genes, plain English", "The polymorphisms that show up over and over, and what to do with that information."),
        ("microchimerism-and-pregnancy", "Microchimerism: the cells we keep from each other", "How a baby's cells can stay in the mother for decades and what that may mean."),
        ("the-old-friends-hypothesis", "The old friends hypothesis", "Why missing organisms may matter more than missing infections."),
        ("nature-deficit-and-immune-tolerance", "Touching dirt, again", "What walking in the woods plausibly does for an inflamed immune system."),
        ("mast-cells-as-mediators", "Mast cells, the underrated middleman", "Where mast-cell activation fits in the autoimmune puzzle."),
        ("th17-and-treg-balance", "Th17 vs. Treg, the immune seesaw", "What this balance is and why so many flares look like a tilt toward inflammation."),
        ("complement-system-and-lupus", "The complement system in plain English", "Why C3 and C4 numbers matter for some autoimmune patterns."),
        ("inflammaging-and-late-onset-autoimmunity", "Inflammaging and late-onset disease", "Why some people don't get diagnosed until their 50s and 60s."),
        ("the-autoimmune-clusters-explained", "Why one autoimmune disease often brings another", "Polyglandular patterns and the family-of-conditions phenomenon."),
        ("epigenetics-of-autoimmunity", "Epigenetics, briefly", "How experience writes on top of your genes, and what that means for change."),
        ("microbial-translocation-as-fuel", "Microbial translocation, in plain words", "Why what crosses the gut barrier may matter more than what's in the gut."),
    ],
    "Gut Healing": [
        ("zonulin-and-tight-junctions", "Zonulin and tight junctions, demystified", "What Alessio Fasano's work actually said and where it landed in the literature."),
        ("sibo-and-autoimmune-flares", "SIBO and autoimmune flares", "Why a small-intestine overgrowth can present as a thyroid problem or a joint problem."),
        ("low-stomach-acid-symptoms", "Low stomach acid, real and overstated", "The uncomfortable middle ground between the wellness internet and the gastroenterologist."),
        ("h-pylori-and-autoimmune-gastritis", "H. pylori and autoimmune gastritis", "When eradication is wise, when it's not, and how to think about it."),
        ("bile-acids-and-gut-health", "Bile acids and the gut you forgot about", "The unsung river that keeps the small intestine working."),
        ("gallbladder-removed-now-what", "Without a gallbladder, then what?", "What changes in digestion and what to do about it."),
        ("constipation-and-autoimmune-burden", "When constipation becomes an autoimmune problem", "Why moving the bowels matters more than people think."),
        ("the-low-fodmap-diet-honest-look", "The low-FODMAP diet, an honest look", "What it does, what it does not do, and how to use it without becoming afraid of food."),
        ("specific-carbohydrate-diet-vs-aip", "SCD, GAPS, AIP: the family tree of healing diets", "How they overlap, where they differ, and which one fits which person."),
        ("the-elemental-diet", "The elemental diet, in plain language", "When a short fast from real food may help, and when it's overkill."),
        ("polyphenols-and-the-microbiome", "Polyphenols and the microbiome", "Why berries, olives, and tea may matter more than the next probiotic."),
        ("postbiotics-explained", "Postbiotics: the next layer", "What they are and why some of the gut benefits aren't about live bugs at all."),
        ("histamine-intolerance-and-the-gut", "Histamine intolerance and the gut connection", "What's overstated, what's real, and how to test the idea on yourself."),
        ("oxalates-controversy-honest-look", "The oxalate question", "Why the wellness internet has split, and what the evidence actually supports."),
        ("salicylate-sensitivity-and-aip", "Salicylate sensitivity in autoimmune people", "How to recognize it, how to test it, and why the cure is rarely lifelong avoidance."),
        ("lectin-sensitivity-overstated-or-not", "Lectins: overstated or not", "A measured walk through the lectin debate."),
        ("the-bristol-stool-scale-quietly", "What your stool is telling you, gently", "A practical, non-squeamish look at the Bristol scale and what 4 means."),
        ("digestive-bitters-and-aip-friendly", "Digestive bitters that are AIP-friendly", "The old apothecary tradition that keeps showing up in modern protocols."),
        ("ox-bile-when-it-helps", "Ox bile: when it helps and when it doesn't", "A simple decision tree for a much-misused supplement."),
        ("betaine-hcl-the-gentle-way", "Betaine HCl, the gentle way", "How to think about it without scaring yourself."),
        ("digestive-enzymes-overview", "Digestive enzymes, demystified", "What they actually do, when they help, and the brands that quietly do the work."),
        ("colostrum-for-the-gut-lining", "Colostrum for the gut lining", "The biology, the limits, and the people who tend to do well on it."),
        ("l-glutamine-for-leaky-gut", "L-glutamine for leaky gut", "What it can and cannot do, and how to dose it without overdoing it."),
        ("zinc-carnosine-overview", "Zinc carnosine, quiet workhorse", "An understated supplement with a real evidence base."),
        ("aloe-vera-inner-leaf-vs-whole", "Aloe vera inner leaf vs. whole leaf", "Why one helps and the other can hurt."),
        ("dgl-licorice-for-the-stomach", "DGL licorice for the stomach", "The form of licorice that works for autoimmune people without raising blood pressure."),
        ("slippery-elm-and-marshmallow-root", "Slippery elm and marshmallow root", "Two old herbs that earn their place in modern protocols."),
        ("bone-broth-quietly-debunked", "Bone broth, gently", "What it actually does, what it doesn't, and why you don't need a gallon."),
        ("fermented-foods-for-immune-people", "Fermented foods for immune people", "When sauerkraut helps, when it backfires, and which one to choose first."),
        ("the-sauerkraut-test", "The sauerkraut test", "A simple homemade probe of your gut's tolerance."),
        ("kefir-vs-yogurt-for-autoimmunity", "Kefir vs. yogurt for autoimmune people", "Two ferments, two different stories."),
        ("probiotic-strains-that-actually-have-data", "Probiotic strains that actually have data", "The handful with real human trials, separated from the marketing."),
        ("the-bathroom-test-for-gut-health", "The bathroom test for gut health", "Eight quiet daily signs more useful than any expensive test."),
    ],
    "AIP & Diet": [
        ("aip-grocery-list-printable", "An AIP grocery list that won't break you", "What goes in the cart, week one to month three."),
        ("the-30-day-aip-trial", "The 30-day AIP trial, with kindness", "How to do it without becoming a person nobody can have over for dinner."),
        ("aip-breakfast-ideas-without-eggs", "Twenty AIP breakfasts without eggs", "Because morning food is where most people quit."),
        ("aip-friendly-batch-cooking-sunday", "Sunday batch cooking for an AIP week", "A two-hour rhythm that makes the rest of the week kind."),
        ("the-aip-condiments-that-make-it-livable", "AIP condiments that make food taste like food", "Five compliant flavor moves that change everything."),
        ("aip-restaurant-survival-guide", "AIP at restaurants without making it weird", "How to eat out and still feel cared for the next morning."),
        ("aip-for-vegetarians-honest-take", "AIP for vegetarians: an honest, careful take", "Where it gets hard, where it stops working, and the workarounds that exist."),
        ("modified-aip-for-busy-parents", "Modified AIP for busy parents", "When 'good enough' beats 'perfect AIP every meal.'"),
        ("when-aip-isnt-working-troubleshooting", "When AIP isn't working: ten honest questions", "A troubleshooting tree before you give up on it."),
        ("nightshades-the-real-story", "Nightshades, the real story", "Why some autoimmune people do better without them and some are fine."),
        ("eggs-and-autoimmune-flares", "Eggs and autoimmune flares", "The reintroduction-failure pattern most people miss."),
        ("dairy-the-aip-conversation", "Dairy on AIP", "Why it's out, when ghee is okay, and what reintroduction actually shows."),
        ("nuts-and-seeds-staged-reintroduction", "Nuts and seeds, staged reintroduction", "A sensible order to bring them back, one at a time."),
        ("legumes-and-the-aip-debate", "Legumes and the AIP debate", "Beans aren't a moral question. The reintroduction pattern decides."),
        ("nightshade-free-spice-blends", "Nightshade-free spice blends", "Five blends that make compliant cooking taste like more than rosemary."),
        ("aip-friendly-soup-rotation", "An AIP soup rotation for cold weeks", "Eight soups so you don't repeat yourself in a flare."),
        ("the-ten-most-tolerated-vegetables", "The ten vegetables most autoimmune people tolerate", "A gentle starting list."),
        ("organ-meats-without-the-ick", "Organ meats without the ick", "Liver pâté and pasture-meatballs that no one calls 'liver pâté.'"),
        ("oysters-the-quiet-superfood", "Oysters, the quiet autoimmune superfood", "Zinc, copper, B12, in a shell."),
        ("sardines-and-mackerel-week", "A sardines-and-mackerel week, for the joints", "A small, steady, omega-3 nudge."),
        ("collagen-and-gelatin-the-difference", "Collagen vs. gelatin, the practical difference", "Two forms, two uses, one common confusion."),
        ("aip-baking-without-grain-or-egg", "AIP baking without grain or egg", "Tigernut flour, cassava flour, and the tricks that hold them together."),
        ("aip-friendly-treats-for-occasion-eating", "AIP-friendly treats for occasion eating", "Birthday cakes that don't ruin the next two weeks."),
        ("salt-thyroid-and-fatigue", "Salt, thyroid, and fatigue", "Why the low-salt advice can backfire in some autoimmune patterns."),
        ("iodine-the-careful-conversation", "Iodine, the careful conversation", "Where the wellness internet gets ahead of the Hashimoto's literature."),
        ("seaweed-and-thyroid-balance", "Seaweed and thyroid balance", "How to use it without overdoing iodine."),
        ("cooking-fats-the-short-list", "Cooking fats, the short list", "Avocado oil, coconut oil, ghee for some, animal fats from good sources."),
        ("sugar-and-autoimmune-flares", "Sugar and autoimmune flares", "Where the link is real, where it's lifestyle, and how to think about reintroducing it."),
        ("alcohol-on-aip-and-after", "Alcohol on AIP, and after", "When wine is okay, when it isn't, and the cleaner forms when it is."),
        ("caffeine-and-the-autoimmune-body", "Caffeine and the autoimmune body", "Why some people thrive on it and some don't, and how to tell."),
        ("intermittent-fasting-for-autoimmune-people", "Intermittent fasting for autoimmune people", "Where it helps, where it backfires, and how to know which you are."),
        ("the-five-day-fasting-mimicking-diet", "The five-day fasting-mimicking diet", "Valter Longo's protocol, with autoimmune caveats."),
        ("ketogenic-diet-for-autoimmune-flares", "The ketogenic diet for autoimmune flares", "An honest read of where it helps and where it doesn't."),
        ("carnivore-diet-skeptical-look", "The carnivore diet, a skeptical and fair look", "What people experience, what the data don't yet say, and how to think about it."),
        ("mediterranean-diet-and-ra", "The Mediterranean diet and rheumatoid arthritis", "The most-studied diet for joint disease, in plain language."),
        ("dash-diet-and-lupus", "The DASH diet and lupus", "Where its blood-pressure focus quietly helps the kidney."),
    ],
    "Stress & Nervous System": [
        ("the-vagus-nerve-without-the-mysticism", "The vagus nerve, without the mysticism", "What we actually know, what we don't, and what to try."),
        ("hrv-monitoring-honest-take", "HRV monitoring, an honest take", "When the wristband helps and when it gets in the way."),
        ("the-polyvagal-theory-debate", "The polyvagal theory, a measured walk-through", "Useful, contested, and easy to mistake for settled."),
        ("box-breathing-for-flare-days", "Box breathing on flare days", "Four counts in, four hold, four out, four hold, ten rounds."),
        ("the-physiological-sigh", "The physiological sigh, in plain English", "The single fastest down-regulation move I know."),
        ("cold-exposure-without-becoming-a-bro", "Cold exposure without becoming a bro", "Practical, gentle, autoimmune-aware."),
        ("contrast-showers-for-the-rest-of-us", "Contrast showers for the rest of us", "The on-ramp for cold-water work."),
        ("yoga-nidra-for-flare-rest", "Yoga nidra for flare rest", "Body-based rest deeper than scrolling."),
        ("non-sleep-deep-rest-protocol", "Non-sleep deep rest, the practical protocol", "Twenty minutes of NSDR that pays you back."),
        ("breathing-and-thyroid-symptoms", "Breathing and thyroid symptoms", "Why mouth-breathing can quietly worsen Hashimoto's."),
        ("nasal-breathing-as-baseline", "Nasal breathing as baseline", "A small habit shift with measurable autonomic effects."),
        ("the-buteyko-method-overview", "The Buteyko method overview", "An old breathing tradition with modern relevance."),
        ("walking-as-medicine", "Walking as medicine, again", "Why thirty minutes outside still beats most interventions."),
        ("forest-bathing-and-immune-tolerance", "Forest bathing and immune tolerance", "What the Japanese researchers actually measured."),
        ("mindfulness-mbsr-for-autoimmune-people", "MBSR for autoimmune people", "Jon Kabat-Zinn's program, adapted for flare-aware living."),
        ("self-compassion-as-physiology", "Self-compassion as physiology", "Why the way you talk to yourself changes inflammation."),
        ("trauma-informed-yoga", "Trauma-informed yoga", "The forms of yoga that don't ask too much of a flared body."),
        ("emdr-and-chronic-illness", "EMDR for the body that's been holding too much", "Where the evidence sits and how to find a competent practitioner."),
        ("ifs-internal-family-systems", "Internal Family Systems for autoimmune folks", "A surprisingly gentle map of inner experience."),
        ("somatic-experiencing-overview", "Somatic experiencing, an overview", "Peter Levine's work, in usable language."),
        ("brainspotting-for-stuck-patterns", "Brainspotting for stuck patterns", "A newer modality, with autoimmune-relevant applications."),
        ("dnrs-and-limbic-retraining", "DNRS and limbic retraining, a fair look", "What it claims, what people experience, and what's evidence."),
        ("gupta-program-overview", "The Gupta program, briefly and honestly", "Where it helps and where the marketing oversteps."),
        ("polyvagal-exercises-daily-five", "Five polyvagal exercises for the morning", "Tiny moves with autonomic effects."),
        ("sighing-and-yawning-as-tools", "Sighing and yawning as tools", "The body knows; we just keep interrupting it."),
        ("the-orienting-response", "The orienting response, simply", "A 30-second practice for an over-revved nervous system."),
        ("cold-face-immersion-trick", "The cold-face immersion trick", "When a panic loop needs an immediate exit."),
        ("hand-on-heart-as-protocol", "Hand on heart as protocol", "Sounds simple. The biology is not."),
        ("co-regulation-with-a-pet", "Co-regulation with a pet", "Why your dog calms your immune system, and what that means."),
        ("the-three-circles-model", "The three circles model of stress", "Soothe, threat, drive: where you tend to live."),
    ],
    "Functional Medicine": [
        ("how-to-pick-a-functional-doctor", "How to pick a functional doctor without being scammed", "Green flags, red flags, and the questions to ask."),
        ("ifm-certified-vs-the-rest", "IFM-certified vs. the rest", "What the credentials actually mean."),
        ("dutch-test-walk-through", "The DUTCH test, a walk-through", "When it's worth running, when it isn't."),
        ("genova-organic-acids-test", "Organic acids testing in plain English", "What the OAT panel is and how to read it."),
        ("methylation-genes-and-supplements", "Methylation genes and supplements, carefully", "Where MTHFR talk gets ahead of the data."),
        ("homocysteine-as-a-quiet-marker", "Homocysteine, a quiet marker worth checking", "Cheap test, useful information."),
        ("crp-vs-hs-crp-difference", "CRP vs. hs-CRP, the practical difference", "Which to ask for and why."),
        ("ferritin-and-autoimmune-flares", "Ferritin and autoimmune flares", "When low matters, when high matters, and when to act."),
        ("vitamin-d-25-vs-1-25", "Vitamin D 25 vs. 1,25, what each tells you", "The two tests and what their pattern means together."),
        ("rt3-and-thyroid-conversion", "Reverse T3 and thyroid conversion", "Where this number earns its place in your panel."),
        ("tpo-and-tg-antibodies-explained", "TPO and Tg antibodies, explained", "What they mean, what they don't, and the trend that matters."),
        ("ana-titer-meaning", "ANA titers, briefly", "What 1:80 vs. 1:1280 actually means in practice."),
        ("ena-panel-for-lupus-suspicion", "The ENA panel for lupus suspicion", "What it covers and how doctors read it."),
        ("ccp-vs-rf-for-ra", "Anti-CCP vs. RF for rheumatoid arthritis", "Two antibodies, different specificities."),
        ("wbc-and-autoimmune-people", "WBC patterns in autoimmune people", "The neutrophil-lymphocyte ratio and other quiet signals."),
        ("a1c-and-systemic-inflammation", "A1c, beyond diabetes", "Why this number is worth tracking even if your sugar is fine."),
        ("uric-acid-and-flare-risk", "Uric acid and flare risk", "Where it links to autoimmune patterns, briefly and honestly."),
        ("apo-b-and-cardiovascular-risk", "ApoB and cardiovascular risk in autoimmune people", "Why your inflamed body deserves a better lipid panel."),
        ("trimethylamine-n-oxide-tmao", "TMAO and the gut-heart conversation", "What this microbial metabolite is and why it matters."),
        ("zonulin-as-a-blood-marker", "Zonulin as a blood marker, carefully", "Useful in research, less so in routine care."),
        ("calprotectin-stool-test", "Fecal calprotectin, a quiet workhorse", "When this stool marker is exactly the right test."),
        ("lactoferrin-stool-test", "Fecal lactoferrin, briefly", "Cousin to calprotectin, sometimes more useful."),
        ("sibo-breath-test-walk-through", "The SIBO breath test, a walk-through", "Methane, hydrogen, hydrogen sulfide: what each pattern suggests."),
        ("h2s-sibo-the-third-pattern", "H2S SIBO, the third pattern", "Why labs that don't measure it miss a third of cases."),
        ("methane-dominant-sibo-imo", "Methane-dominant SIBO and constipation", "How methanogens slow your bowels."),
        ("rifaximin-when-it-makes-sense", "Rifaximin, when it makes sense", "The non-absorbable antibiotic, demystified."),
        ("herbal-antimicrobials-for-sibo", "Herbal antimicrobials for SIBO", "Berberine, oregano, neem, allicin: what the data say."),
        ("biofilm-disruptors-overview", "Biofilm disruptors, briefly", "What they are, what they aren't, and where to be skeptical."),
        ("low-dose-naltrexone-honest-look", "Low-dose naltrexone, an honest look", "Where it helps autoimmune people, and the cautions."),
        ("hydroxychloroquine-without-a-rheumatologist", "Hydroxychloroquine: what to ask your rheumatologist", "Plain-English questions for a long-term medication conversation."),
        ("biologics-and-autoimmune-disease", "Biologics: a measured introduction", "What they are, what they target, and how to think about them."),
    ],
    "Emotional Roots": [
        ("ace-scores-and-autoimmune-risk", "ACE scores and autoimmune risk, in plain English", "Adverse childhood experiences and the quiet signal in the literature."),
        ("the-perfectionist-and-the-flare", "The perfectionist and the flare", "A pattern many autoimmune people recognize."),
        ("the-people-pleaser-pattern", "The people-pleaser pattern, gently", "Where the body might be saying no on your behalf."),
        ("emotional-suppression-and-illness", "Emotional suppression and illness", "What Gabor Maté got right, and where to be careful."),
        ("the-body-keeps-the-score-revisited", "The Body Keeps the Score, revisited", "Bessel van der Kolk's book, useful and limited."),
        ("when-the-flare-isnt-about-food", "When the flare isn't about food", "The emotional triggers nobody charts."),
        ("grief-and-the-immune-system", "Grief and the immune system", "Why bereavement can fold a body sideways."),
        ("loneliness-as-physiology", "Loneliness as physiology", "The inflammation signature of disconnection."),
        ("workaholism-and-cortisol", "Workaholism and cortisol", "How the 60-hour week becomes a flare."),
        ("rage-as-medicine-honest-take", "Rage as medicine, an honest take", "The strange role of anger in healing chronic illness."),
        ("when-your-body-says-no", "When your body says no", "Reading the no your body has been saying for years."),
        ("inner-child-work-for-autoimmunity", "Inner child work for autoimmune people", "Where it actually helps, where it gets cliché."),
        ("attachment-styles-and-flares", "Attachment styles and flares", "Anxious, avoidant, secure: how each shows up in chronic illness."),
        ("nervous-system-mapping-exercise", "A nervous-system mapping exercise", "Forty minutes that show you your patterns."),
        ("self-betrayal-as-trigger", "Self-betrayal as trigger", "The small daily ways we override our own knowing."),
        ("boundaries-and-immune-tolerance", "Boundaries and immune tolerance", "A quiet thread between what you say no to and how you feel."),
        ("the-good-girl-and-her-thyroid", "The good girl and her thyroid", "A pattern almost too obvious to take seriously, until you do."),
        ("religious-trauma-and-the-body", "Religious trauma and the body", "Specific echoes that show up in autoimmune presentations."),
        ("perfection-recovery-30-day", "A 30-day recovery from perfection", "A small program for autoimmune people who can't relax."),
        ("the-weeping-day-protocol", "The weeping-day protocol", "Sometimes the body just needs the morning off."),
        ("grief-and-thyroid", "Grief and the thyroid", "Why losses cluster around onset of Hashimoto's and Graves'."),
        ("anger-and-rheumatoid-arthritis", "Anger and rheumatoid arthritis", "An old pattern in the literature, freshly considered."),
        ("the-rescuer-and-her-flares", "The rescuer and her flares", "When everyone else is your job."),
        ("learned-helplessness-and-cortisol", "Learned helplessness and cortisol", "Why the way you talk to yourself becomes physiology."),
        ("post-traumatic-growth-after-diagnosis", "Post-traumatic growth after diagnosis", "Where chronic illness can become a hinge."),
        ("the-grief-list", "The grief list", "Naming everything chronic illness has cost, on paper, where it can be witnessed."),
        ("self-witness-as-practice", "Self-witness as a daily practice", "Three minutes that change the next eight hours."),
        ("the-no-list-for-flare-week", "The no-list for flare week", "What you are not doing this week, in writing."),
        ("the-yes-list-for-tender-weeks", "The yes-list for tender weeks", "What is allowed when you're not okay."),
        ("therapist-vs-coach-vs-practitioner", "Therapist, coach, practitioner: who does what", "Choosing the right person for the right kind of work."),
    ],
}

# Modifiers used to scale base seeds when needed.
MODIFIERS = [
    ("part-2", "Part 2", "More on the same theme, with the questions readers wrote in after the first piece."),
    ("for-women", "For women", "How this looks in female bodies, where the literature has more to say."),
    ("for-men", "For men", "How this looks in male bodies, where it is often missed."),
    ("in-perimenopause", "In perimenopause", "Why this hits differently in the years before the change."),
    ("after-pregnancy", "After pregnancy", "Postpartum patterns and the windows that follow."),
    ("for-the-newly-diagnosed", "For the newly diagnosed", "What to know in week one and what to skip for now."),
    ("the-second-year", "The second year", "When the early enthusiasm fades and the slow work begins."),
    ("a-skeptical-second-look", "A skeptical second look", "Returning to the topic with what we have learned since."),
    ("flare-week-version", "Flare-week version", "How to apply this when you have nothing left to give."),
    ("a-real-readers-question", "A reader's question", "Building an essay from the email I keep getting."),
]

def fingerprint(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:6]

def scale_to(seeds: list[tuple[str,str,str]], target: int) -> list[tuple[str,str,str]]:
    out = list(seeds)
    i = 0
    while len(out) < target:
        base = seeds[i % len(seeds)]
        mod = MODIFIERS[(i // len(seeds)) % len(MODIFIERS)]
        new_slug = f"{base[0]}-{mod[0]}-{fingerprint(base[0]+mod[0])}"
        new_title = f"{base[1]}, {mod[1].lower()}"
        new_angle = f"{base[2]} {mod[2]}"
        out.append((new_slug, new_title, new_angle))
        i += 1
    return out[:target]

# Build the 500 specs.
PER_CAT = 500 // len(CATEGORIES)
REMAINDER = 500 - PER_CAT * len(CATEGORIES)

random.seed(86)

def asin_rotation(idx: int) -> list[str]:
    base = idx * 3
    return [APOTHECARY_ASINS[(base + k) % len(APOTHECARY_ASINS)] for k in range(3)]

# Already-published 30 (from the seed manifest); we will build relateds against them too.
PUBLISHED_30 = [
    "what-actually-causes-autoimmune-disease","leaky-gut-without-the-hype","aip-protocol-honest-guide",
    "stress-and-the-hpa-axis","hashimotos-deep-dive","molecular-mimicry-explained","ebv-and-autoimmunity",
    "wahls-protocol-the-mitochondria-bet","trauma-and-autoimmune-disease","the-five-supplements-i-actually-recommend",
    "the-vagus-nerve-and-immune-tolerance","selenium-and-the-thyroid","gi-map-and-stool-testing",
    "rheumatoid-arthritis-the-honest-version","lupus-and-the-quiet-life","psoriasis-as-an-autoimmune-pattern",
    "celiac-vs-non-celiac-gluten-sensitivity","food-reintroduction-without-fear","igg-food-tests-the-honest-version",
    "the-supplements-i-stopped-recommending","mitochondria-and-fatigue","sleep-architecture-and-autoimmunity",
    "the-emotional-roots-people-dont-talk-about","somatic-practices-for-flare-days","exercise-during-a-flare",
    "mold-and-the-environment-question","ebv-reactivation-and-the-hpa-axis","perimenopause-and-autoimmune-flares",
    "men-and-autoimmune-disease","kids-teens-and-autoimmunity",
]

specs = []
slugs_seen = set(PUBLISHED_30)

per_cat_targets = {c: PER_CAT for c in CATEGORIES}
for i in range(REMAINDER):
    per_cat_targets[CATEGORIES[i]] += 1

global_idx = 0
for cat in CATEGORIES:
    seeds = SEEDS[cat]
    target = per_cat_targets[cat]
    scaled = scale_to(seeds, target)
    for sl, title, angle in scaled:
        # Ensure uniqueness; if collision, suffix the fingerprint.
        slug = sl
        n = 0
        while slug in slugs_seen:
            n += 1
            slug = f"{sl}-{n}"
        slugs_seen.add(slug)

        # Related: 2 from already-published 30, 2 from earlier in 500 (or 4 from published if early).
        rng = random.Random(fingerprint(slug) + cat)
        from_published = rng.sample(PUBLISHED_30, 2)
        if len(specs) >= 2:
            from_500 = rng.sample([s["slug"] for s in specs[-min(50, len(specs)):]], 2)
        else:
            from_500 = rng.sample(PUBLISHED_30, 2)
        related = list(dict.fromkeys(from_published + from_500))[:4]

        specs.append({
            "slug": slug,
            "title": title,
            "category": cat,
            "angle": angle,
            "asins": asin_rotation(global_idx),
            "related": related,
            "hero_prompt_seed": fingerprint(slug),
        })
        global_idx += 1

assert len(specs) == 500, f"expected 500, got {len(specs)}"
assert len(set(s['slug'] for s in specs)) == 500, "duplicate slugs"

OUT.write_text(json.dumps({"count": len(specs), "specs": specs}, indent=2))
print(f"wrote {OUT} with {len(specs)} unique slugs")
print("category distribution:")
from collections import Counter
for cat, n in Counter(s['category'] for s in specs).items():
    print(f"  {cat:30s}  {n}")
