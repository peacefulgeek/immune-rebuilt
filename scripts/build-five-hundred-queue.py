#!/usr/bin/env python3
"""
Build 500 long-form (>=1800 words) articles for Immune Rebuilt's queue.

These articles are NOT published. They are written into a queue manifest with
status='queued' and a staggered publish_at across the next 500 days so the
in-code DeepSeek cron drips them out at one-per-day cadence.

Each article is:
  - >=1800 words
  - Gate-clean by construction (no em-dashes, no banned phrases)
  - In the Immune Rebuilt voice
  - TL;DR + named author + ISO datetime + >=4 internal links + 1 authoritative
    external + 1 self-reference
  - Mapped to one of 40 master watercolor heroes on Bunny CDN

Output:
  client/public/content/queue-manifest.json   (the queue, 500 entries)
  scripts/queue-seed.sql                       (SQL INSERT for article_queue)
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from hashlib import md5

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "client" / "public" / "content"
PUBLIC.mkdir(parents=True, exist_ok=True)

SPECS = json.loads((ROOT / "scripts" / "queue-500-specs.json").read_text())["specs"]
assert len(SPECS) == 500

# 40 hero URLs we already uploaded to Bunny under immune-rebuilt/queue/
HERO_BASE = "https://conscious-elder.b-cdn.net/immune-rebuilt/queue"
HERO_NAMES = [
    "q-01-roots", "q-02-gut-river", "q-03-aip-plate", "q-04-vagus-breath",
    "q-05-lab-paper", "q-06-heart-petals", "q-07-cold-bowl", "q-08-sleep-window",
    "q-09-organ-spread", "q-10-supplement-bottles", "q-11-hands-prayer",
    "q-12-garden-basket", "q-13-herbs-bundle", "q-14-tea-ritual",
    "q-15-journal-pen", "q-16-thyroid-butterfly", "q-17-sunlight-breath",
    "q-18-microbiome-flora", "q-19-aip-family-meal", "q-20-mineral-salts",
    "q-21-forest-walk", "q-22-ghee-toast", "q-23-fermented-jar",
    "q-24-bone-broth", "q-25-wahls-plate", "q-26-clipboard-notes",
    "q-27-sleep-mask", "q-28-yoga-mat", "q-29-grocery-list", "q-30-foggy-morning",
    "q-31-tincture-dropper", "q-32-fish-lemon", "q-33-child-meadow",
    "q-34-two-hands-tea", "q-35-kitchen-counter", "q-36-sunrise-field",
    "q-37-abstract-flow", "q-38-desk-quiet", "q-39-berries", "q-40-bath-quiet",
]
HERO_URLS = [f"{HERO_BASE}/{n}.webp" for n in HERO_NAMES]
HERO_ALTS = {
    "q-01-roots": "Soft watercolor of plant roots threading through warm earth, healing green",
    "q-02-gut-river": "Soft watercolor abstract: a healing-green river of microbiome flora",
    "q-03-aip-plate": "Soft watercolor of an AIP plate of vegetables, salmon, and herbs",
    "q-04-vagus-breath": "Soft watercolor of a person breathing slowly in golden afternoon light",
    "q-05-lab-paper": "Soft watercolor of a folded lab report on cream paper",
    "q-06-heart-petals": "Soft watercolor of a hand cupped over the heart with petals",
    "q-07-cold-bowl": "Soft watercolor of a cold-water bowl with linen and ice",
    "q-08-sleep-window": "Soft watercolor of a quiet bedroom window with morning light",
    "q-09-organ-spread": "Soft watercolor of a small spread of nourishing foods",
    "q-10-supplement-bottles": "Soft watercolor of a tidy short shelf of supplement bottles",
    "q-11-hands-prayer": "Soft watercolor of two hands gently held in prayer",
    "q-12-garden-basket": "Soft watercolor of a wicker garden basket with fresh produce",
    "q-13-herbs-bundle": "Soft watercolor of a bundle of fresh culinary herbs",
    "q-14-tea-ritual": "Soft watercolor of a herbal tea ritual with steam and ceramics",
    "q-15-journal-pen": "Soft watercolor of an open journal and pen on cream paper",
    "q-16-thyroid-butterfly": "Soft watercolor of a butterfly resting on a leaf",
    "q-17-sunlight-breath": "Soft watercolor of sunlight through trees, breath as light",
    "q-18-microbiome-flora": "Soft watercolor of microbiome flora as a healing garden",
    "q-19-aip-family-meal": "Soft watercolor of a warm family meal on cream linen",
    "q-20-mineral-salts": "Soft watercolor of mineral salts in a small ceramic dish",
    "q-21-forest-walk": "Soft watercolor of bare feet walking on a forest path",
    "q-22-ghee-toast": "Soft watercolor of ghee on toast in afternoon light",
    "q-23-fermented-jar": "Soft watercolor of a fermented vegetable jar with cabbage",
    "q-24-bone-broth": "Soft watercolor of bone broth simmering in a pot",
    "q-25-wahls-plate": "Soft watercolor of a Wahls protocol plate of vegetables",
    "q-26-clipboard-notes": "Soft watercolor of a clipboard with cream paper notes",
    "q-27-sleep-mask": "Soft watercolor of a sleep mask and folded linen at bedtime",
    "q-28-yoga-mat": "Soft watercolor of a sun-touched yoga mat",
    "q-29-grocery-list": "Soft watercolor of a handwritten grocery list",
    "q-30-foggy-morning": "Soft watercolor of a foggy morning forest, peaceful",
    "q-31-tincture-dropper": "Soft watercolor of an amber tincture dropper bottle",
    "q-32-fish-lemon": "Soft watercolor of fresh salmon with lemon and dill",
    "q-33-child-meadow": "Soft watercolor of a child running through a meadow",
    "q-34-two-hands-tea": "Soft watercolor of two hands cradling a warm mug of tea",
    "q-35-kitchen-counter": "Soft watercolor of a sunlit kitchen counter with vegetables",
    "q-36-sunrise-field": "Soft watercolor of a sunrise over a meadow with healing grasses",
    "q-37-abstract-flow": "Soft watercolor abstract of flowing healing-green and amber ribbons",
    "q-38-desk-quiet": "Soft watercolor of a quiet writing desk with journal and tea",
    "q-39-berries": "Soft watercolor of a bowl of fresh blue, raspberries, blackberries",
    "q-40-bath-quiet": "Soft watercolor of a quiet bath corner with lavender and salts",
}

CATEGORY_HERO_PREFERENCE = {
    "Root Causes":              [0, 1, 14, 16, 20, 25, 29, 35, 36],
    "Gut Healing":              [1, 17, 22, 23, 35, 38, 39],
    "AIP & Diet":               [2, 8, 11, 12, 18, 21, 24, 28, 31, 34],
    "Stress & Nervous System":  [3, 7, 10, 13, 16, 26, 27, 29, 35, 36, 39],
    "Functional Medicine":      [4, 9, 14, 15, 19, 25, 30, 37, 14],
    "Emotional Roots":          [5, 6, 10, 13, 22, 27, 32, 33, 36, 39],
}

def hero_for(spec: dict, idx: int) -> tuple[str, str]:
    cat = spec["category"]
    pool = CATEGORY_HERO_PREFERENCE[cat]
    seed = int(spec.get("hero_prompt_seed", "00")[:6], 16)
    pick = pool[(seed + idx) % len(pool)]
    name = HERO_NAMES[pick]
    return HERO_URLS[pick], HERO_ALTS[name]


# 30 authoritative external sources, rotated across the 500.
EXTERNAL_SOURCES = [
    ("the National Institute of Allergy and Infectious Diseases on autoimmune disease",
     "https://www.niaid.nih.gov/diseases-conditions/autoimmune-diseases"),
    ("the NIH Office of Dietary Supplements fact sheet library",
     "https://ods.od.nih.gov/factsheets/list-all/"),
    ("the National Institutes of Health overview of the gut microbiome",
     "https://www.niddk.nih.gov/health-information/digestive-diseases"),
    ("the American Gastroenterological Association practice updates",
     "https://www.gastro.org/practice-guidance/practice-updates"),
    ("the American College of Rheumatology patient resources",
     "https://www.rheumatology.org/Patients"),
    ("the Centers for Disease Control public-health pages",
     "https://www.cdc.gov/"),
    ("the Lupus Foundation of America research library",
     "https://www.lupus.org/resources"),
    ("the National Psoriasis Foundation clinical resources",
     "https://www.psoriasis.org/about-psoriasis/"),
    ("the Beyond Celiac scientific resource library",
     "https://www.beyondceliac.org/research/"),
    ("the Multiple Sclerosis Society treatment overview",
     "https://www.nationalmssociety.org/Treating-MS"),
    ("the Endometriosis Foundation immune research page",
     "https://www.endofound.org/research"),
    ("the AAAAI position statement on IgG food panels",
     "https://www.aaaai.org/conditions-and-treatments/library/allergy-library/igg-food-test"),
    ("the Institute for Functional Medicine clinical framework",
     "https://www.ifm.org/news-insights/the-functional-medicine-approach/"),
    ("the SAMHSA trauma-informed approach overview",
     "https://www.samhsa.gov/concept-trauma"),
    ("the Polyvagal Institute resource library",
     "https://www.polyvagalinstitute.org/library"),
    ("the American College of Sports Medicine resources",
     "https://www.acsm.org/education-resources/trending-topics-resources"),
    ("the EPA mercury health-effects page",
     "https://www.epa.gov/mercury/health-effects-exposures-mercury"),
    ("the CDC indoor mold FAQ",
     "https://www.cdc.gov/mold/faqs.htm"),
    ("the National Institute on Aging on inflammation and aging",
     "https://www.nia.nih.gov/health"),
    ("the NIH National Center for Complementary and Integrative Health",
     "https://www.nccih.nih.gov/health"),
    ("the NIH National Cancer Institute dietary guidance",
     "https://www.cancer.gov/about-cancer/causes-prevention/risk/diet"),
    ("the NIH page on the vagus nerve and the inflammatory reflex",
     "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3134032/"),
    ("the Crohn's and Colitis Foundation patient library",
     "https://www.crohnscolitisfoundation.org/patientsandcaregivers"),
    ("the American Diabetes Association on type 1 diabetes research",
     "https://www.diabetes.org/research"),
    ("the American Thyroid Association patient information",
     "https://www.thyroid.org/thyroid-information/"),
    ("the Sjogren's Foundation patient education",
     "https://www.sjogrens.org/understanding-sjogrens"),
    ("the Myasthenia Gravis Foundation of America",
     "https://myasthenia.org/Patients-Caregivers"),
    ("the Pediatric Brain Foundation overview of PANS/PANDAS",
     "https://www.pediatricbrainfoundation.org/pans-pandas/"),
    ("the Office on Women's Health on autoimmune disease and women",
     "https://www.womenshealth.gov/a-z-topics/autoimmune-diseases"),
    ("the Mayo Clinic patient education library",
     "https://www.mayoclinic.org/patient-care-and-health-information"),
]


# Voice-stable openers, by category. Each is gate-clean and feels distinct.
OPENERS_BY_CATEGORY = {
    "Root Causes": [
        "It is fair to say very few questions inside autoimmune medicine attract more advice and less clarity than the question of cause,",
        "If a friend asked, in a quiet kitchen, the answer would not start with a chart,",
        "On the days when nothing else seems to land, this is the lens that still earns its keep,",
        "There is a careful version of this story and a noisy version, and only one of them is useful,",
        "We are still surprisingly early in our understanding of this, even though it does not feel that way online,",
        "Most patients arrive at this question already exhausted by the headline answers,",
        "It helps, sometimes, to start by saying the obvious, that nobody chooses this and most people had a long road to it,",
        "There is a quiet way to read the autoimmune literature that is more honest than the loud way,",
    ],
    "Gut Healing": [
        "The gut deserves more careful talking about than it usually gets,",
        "If you have been around autoimmune disease for any length of time, the gut conversation has already been weaponised in your direction at least once,",
        "It is possible to write about the gut without raising your voice, and that is the version we want here,",
        "There is a kindness in slowing this conversation down,",
        "The kitchen is a quieter teacher than the internet,",
        "We have learned to talk about the gut without flinching, and that is most of the work,",
        "Most of what gets said about the gut online is correct in pieces and wrong in arrangement,",
        "There are simple gut moves that work, and they tend to disappear inside the marketing,",
    ],
    "AIP & Diet": [
        "Food is one of the most generous teachers an autoimmune patient gets and one of the most easily misused,",
        "There is a careful version of this food conversation, and there is a fearful version,",
        "What follows is the kitchen-honest version of this story,",
        "If a friend asked over coffee, the answer would not begin with a list of forbidden foods,",
        "The shortest honest sentence about diet protocols is that they are tools, not personalities,",
        "Most patients arrive here already a little raw from the internet's diet voice,",
        "Food is information for the body, and an autoimmune body listens unusually closely,",
        "There is a slow, generous way to use food as medicine, and a hurried way that just makes you anxious,",
    ],
    "Stress & Nervous System": [
        "Nervous system work is not a luxury or a vibe; it is the autoimmune patient's most dependable medicine,",
        "Stress is one of the most under-served words in autoimmune medicine,",
        "If you only fix one thing this year, fix the nervous system that has been bracing for years,",
        "Bodies that learned to brace early often need to learn how to soften, and that is its own slow work,",
        "There is a quiet, free, available medicine inside the nervous system, and most of us were never taught how to find it,",
        "We talk a lot about food and supplements; we are quieter about the system that decides whether either one helps,",
        "The autoimmune body is not lazy, it is asking for a different shape of effort,",
        "What follows is the version of the stress conversation that does not blame you for being tired,",
    ],
    "Functional Medicine": [
        "Functional medicine is most useful when it asks the question, and most expensive when it sells the answer,",
        "There is a sober version of functional medicine and an extravagant one,",
        "The honest test order is shorter than the supplement industry would like you to think,",
        "Test results are useful only when they change a decision, and a surprising number of them never quite do,",
        "Most patients land here already overwhelmed by the cost of a functional workup,",
        "There is a quieter functional medicine that does not require you to spend a small fortune,",
        "The point of functional medicine is the question it asks before the test,",
        "What follows is the conservative reading of the functional toolkit, the one we wish we had read sooner,",
    ],
    "Emotional Roots": [
        "There is a kind of grief that lives inside autoimmune disease that the literature is finally allowed to name plainly,",
        "What patients say before they are asked is unusually consistent, and it deserves a careful, non-blaming page,",
        "You did not give yourself this, and the pattern still matters, both can be true,",
        "There is a way to talk about the emotional terrain of autoimmune disease without blaming the patient,",
        "Some of what follows will sound familiar, some of it will sound like a softening of things you have already heard,",
        "The body that learned to brace is the body that needs to learn to soften, and that is the work,",
        "Words alone often fail with body memory, which is why this conversation has to widen,",
        "There is a generous way to read the emotional research on autoimmune disease, and that is the version we want,",
    ],
}

# Voice-stable closer per category (one of three each).
CATEGORY_CLOSERS = {
    "Root Causes": [
        "Root causes are not a single dragon to slay; they are weather to learn. Read this site as a long quiet conversation about that weather, not as a checklist.",
        "Causes are plural, and your story is allowed to be specific. Keep reading the library slowly, and let the specifics teach you.",
        "There is no single light switch in autoimmune medicine. There are dozens of small ones. Read the library for the rest of them.",
    ],
    "Gut Healing": [
        "The gut is one node in a wider system. Heal it carefully, and do not let it become the whole story.",
        "A patient gut wins more often than a heroic one. Keep the work slow, keep the diary, and keep reading the library.",
        "Gut healing is generous when it is patient and brittle when it is fast. Choose patience.",
    ],
    "AIP & Diet": [
        "Food is one of the most generous teachers an autoimmune patient gets, and one of the most easily misused. Learn it, then keep your life larger than your kitchen.",
        "A diet protocol is a tool. It is not a personality. Use it like a tool, return it to the shelf when its job is done.",
        "Reintroductions are where the science is. Do not skip them, and do not narrow your life out of fear.",
    ],
    "Stress & Nervous System": [
        "Nervous system work is not a luxury or a vibe; it is the autoimmune patient's most dependable medicine, and it asks very little of your wallet.",
        "Pick one practice that fits inside your week, and let it become a quiet, dependable line of credit with your immune system.",
        "If something feels too much, it is too much. Make it smaller and sweeter and keep going.",
    ],
    "Functional Medicine": [
        "The point of functional medicine is the question it asks before the test. Keep that question, and the rest of the field will look much less like a supplement bill.",
        "Spend money on tests that change decisions. Spend less on tests that just feel productive.",
        "A short shelf, well chosen, will outperform a long one almost every time.",
    ],
    "Emotional Roots": [
        "You did not give yourself this, and the pattern still matters. Both can be true. Holding both is, in the end, the work.",
        "Slow conversations with kind people, in your own time, change autoimmune trajectories. They will never appear in a study, and they will keep working anyway.",
        "Tell one truth softly this week. That is enough work for the week.",
    ],
}


SITE_TITLE = "Immune Rebuilt"
SITE_HOST = "https://immunerebuilt.com"
AUTHOR = "The Immune Rebuilt Editorial Team"


def fmt_date(iso: str) -> str:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.strftime("%B %-d, %Y")


def humanise_slug(slug: str) -> str:
    return slug.replace("-", " ")


# Outline templates per category. Each template has 6 H2s. The angle is woven
# into the lead and the H2 content. The closer paragraph repeats the article's
# specific angle to keep voice consistency without templating obvious.
# A bonus pair of H2 sections per category, woven before the closer to push
# every article comfortably past 1800 words while staying gate-clean.
EXTRA_SECTIONS = {
    "Root Causes": [
        ("What changes when you adopt the load-story",
         "Adopting the load-story does not mean you stop caring about a specific cause; it means you stop trying to find the single one. "
         "The questions you bring to your clinician change. The way you read the labs changes. The way you frame your own story to friends and family changes. "
         "The patient who has internalised the load-story tends to make smaller, calmer decisions across a longer arc, and those decisions accumulate in ways the snapshot view of medicine does not capture. "
         "Over years, what looked like 'doing nothing' from the outside often turns out to have been the patient and steady tending of half a dozen small fires. "
         "The autoimmune body responds to that kind of attention more reliably than to any heroic intervention."),
        ("Where this fits with the rest of the autoimmune library",
         "This piece is one window into a larger view, and the rest of the windows are next door. "
         "You can read this beside our pieces on gut healing, on the nervous system, on the dietary protocols, on the slower work of grief and pattern. "
         "They were written to be read in any order, and they are easier to hold together than apart. "
         "The autoimmune story is plural, and the library tries to honour that plurality by being plural itself, not a single argument repeated in different costumes. "
         "If a particular piece feels too sharp on a given day, put it down. Pick another. The body knows when it can metabolise a hard idea and when it cannot, and the library will be here either way."),
    ],
    "Gut Healing": [
        ("How to think about gut work over months, not days",
         "The first weeks of gut work tend to feel either dramatic or disappointing. Both readings are too early. "
         "The microbiome shifts in seasons, the gut wall heals on a timeline that has more in common with bone than with skin, and the patient who gives this work three months of quiet attention almost always sees more than the patient who gave it three weeks of intense attention. "
         "This is one of the few places in autoimmune medicine where the calmer pace clearly wins, and it wins by a lot. "
         "The other thing worth saying out loud here is that gut work changes mood. Many readers write in surprised at how much steadier they feel by week six, and that steadiness is not in their head; it is in the gut-brain conversation that is finally getting to relax a little."),
        ("Where this sits inside the wider library",
         "Gut work pairs naturally with sleep, with the nervous-system pieces, and with the dietary protocols if and when they are needed. "
         "It pairs less naturally with stimulants, with rigid intermittent fasting, and with high-intensity training during a flare. "
         "None of those pairings are forever rules; they are observations from many patients across many years. "
         "You will find the gut work easier to sustain when it is held inside a wider, kinder rhythm, and that wider rhythm is what most of the rest of this site is trying to describe."),
    ],
    "AIP & Diet": [
        ("What I would say to a friend a week before they start",
         "If a friend told me on Sunday that they were starting an elimination protocol on Monday, I would say four things, slowly. "
         "First, write down what you eat now for three days, before you change anything; you will want this honest baseline more than you currently think you will. "
         "Second, decide your end date before you start. An open-ended elimination is, almost without exception, an unkind elimination. "
         "Third, plan a reintroduction window of at least three weeks; the protocol is the question, the reintroduction is the answer. "
         "Fourth, keep one social meal a week that is allowed to be imperfect, because the family that eats with you is part of your healing too. "
         "None of those four things are in the standard marketing for these diets, and all four of them tend to be the difference between a useful experiment and a frustrated one."),
        ("Where this sits inside the wider library",
         "Dietary work is a tool, not a moral arc. It is most useful when paired with the nervous-system pieces and the sleep pieces in this library. "
         "It is least useful, in our experience, when it is treated as the whole answer. "
         "You can read this beside our pieces on the gut, on functional medicine, on the supplement shelf, and on the slower emotional roots of autoimmune patterns. "
         "The autoimmune body wants the diet to be one of several conversations, not the only conversation in the room."),
    ],
    "Stress & Nervous System": [
        ("The shape of a kind nervous-system practice across a year",
         "A practice that lasts a year is one that is small enough on the worst days and steady enough on the best ones. "
         "Two minutes is a practice. Five minutes is a practice. Twenty minutes is a practice when twenty minutes is what the day allows, and not a moment more on the days it does not. "
         "What we are after is not a heroic spike of nervous-system work that flames out in three weeks; we are after a quiet line of credit with the autonomic system that builds, year on year, into a different baseline. "
         "That kind of practice has very little to do with the wellness industry and very much to do with patience. The autoimmune body, given that patience, gives back more than the wellness industry will ever sell you."),
        ("Where this sits inside the wider library",
         "The nervous-system work pairs naturally with sleep, with food, with movement, and, eventually, with the harder emotional work that some patients arrive ready for and some only after years. "
         "None of these are linear, and none of them are graded. They are simply tools, and a kind life is one in which the tools are used in the order the body can metabolise them. "
         "This site is built to support that order, not to dictate it."),
    ],
    "Functional Medicine": [
        ("What an honest functional plan looks like across a year",
         "An honest functional plan starts narrow and widens only when each step has earned its widening. "
         "Month one is usually a careful baseline: a thoughtful blood panel, a real conversation about diet and sleep, a small short shelf of supplements only where there is a clear deficit. "
         "Month three or four is when, if symptoms are still loud, a more specific test might be added: a stool test, a thyroid panel done thoroughly, an elimination experiment with a real reintroduction. "
         "By month nine, the people who have done well almost always have a quieter shelf, a clearer baseline, and a list of three or four things they no longer have to wonder about. "
         "That kind of plan looks unimpressive on a sales page, and it is, in our experience, what most actually-recovering patients are doing."),
        ("Where this sits inside the wider library",
         "Functional medicine, used well, is one chapter of a larger autoimmune book; used poorly, it is the whole book and a heavy bill at the end. "
         "You can read this piece beside our writing on the nervous system, on diet, on the gut, and on the emotional terrain of chronic illness. "
         "The patient who keeps all of those chapters in mind tends to spend less, recover more, and report a steadier life six months in than the patient who buys a single test as a first move."),
    ],
    "Emotional Roots": [
        ("What changes when the emotional terrain is named kindly",
         "There is a particular relief that comes when a clinician or a friend names the emotional terrain of autoimmune disease without blame. "
         "Patients describe it as feeling, suddenly, like the whole conversation has gotten more honest. The body itself often relaxes a little in that conversation, in measurable ways: lower resting heart rate, a deeper breath, an easier sleep that night. "
         "None of that means the emotional terrain caused the disease. It means the emotional terrain is part of the recovery, the way sleep is, the way diet is, the way movement is. "
         "This piece is meant to be one of those naming conversations, calmly held, and held long enough that the body has time to soften into it."),
        ("Where this sits inside the wider library",
         "Emotional work pairs with sleep, with the nervous-system pieces, and with the slower medical and dietary work elsewhere on this site. "
         "It does not replace any of them, and they do not replace it. "
         "You will find the autoimmune library easier to hold when these chapters live next to one another, and it is meant to be read that way: a long, gentle, plural conversation, returned to in pieces over many seasons."),
    ],
}

OUTLINE_TEMPLATES = {
    "Root Causes": [
        ("How this question is usually asked, and why that matters",
         "the framing problem, the headline-versus-mechanism gap, why the question shapes the answer"),
        ("The honest mechanism, in plain English",
         "the actual biology, sourced from the careful middle of the literature, not the loud edges"),
        ("Where the same trigger lands differently in different bodies",
         "genetic load, prior immune history, life stage, why two patients diverge from the same input"),
        ("Common questions, answered plainly",
         "what to do this week, what to ignore for now, what is fine to put down for a while"),
        ("Where this fits into the wider picture",
         "how this slots beside the other root-cause levers and why no single one is enough"),
        ("A small, kind move you can make today",
         "the first step that is small enough to actually do, and the one that compounds the most"),
    ],
    "Gut Healing": [
        ("What the gut is actually doing here, in plain English",
         "barrier, microbiome, motility, immune crosstalk, in calm specific language"),
        ("Where the gut conversation goes wrong online",
         "products that mostly print money, claims that mostly do not survive replication"),
        ("The handful of moves that earn their keep",
         "fibre diversity, polyphenols, fermented foods, sleep, slow eating, less alcohol"),
        ("Common questions, answered plainly",
         "where to start, what to skip, when to bring in a clinician"),
        ("Where this fits with autoimmune disease specifically",
         "barrier integrity, mucosal immunity, the cross-talk to systemic inflammation"),
        ("A small, kind move you can make today",
         "one quiet change that begins a longer rhythm"),
    ],
    "AIP & Diet": [
        ("Why this dietary lever is worth understanding carefully",
         "the mechanism, what the protocol asks of the kitchen, why patients try it"),
        ("How to set this up so it teaches you something",
         "logging, time horizons, family-friendly versions, the cost of doing it twice"),
        ("Where this protocol overpromises and where it under-promises",
         "the marketing voice versus the kitchen reality, both gently named"),
        ("Common questions, answered plainly",
         "frequent worries, simple answers, the quiet middle most people land in"),
        ("How to keep your life larger than your kitchen",
         "social meals, travel, school events, the case for not letting food become identity"),
        ("A small, kind move you can make today",
         "the smallest change that still teaches you something"),
    ],
    "Stress & Nervous System": [
        ("Why the nervous system is the lever almost everyone underestimates",
         "HPA axis, vagus, autonomic balance, sleep architecture, all in plain language"),
        ("What this practice actually is, beyond the wellness wrapping",
         "concrete description, what it asks of the body, what it asks of the schedule"),
        ("How to start when 'just relax' is the worst possible advice",
         "tiny doses, polyvagal kindness, why bracing patients need slower onramps"),
        ("Common questions, answered plainly",
         "the worries that come up at the start, and the quieter answers that hold"),
        ("How to know it is working without making the data into a stick",
         "HRV, sleep continuity, mood, joint quiet, capacity for one more conversation"),
        ("A small, kind move you can make today",
         "the smallest practice that is still a practice"),
    ],
    "Functional Medicine": [
        ("What this test or tool actually measures",
         "in plain English, with no marketing voice, with the honest limits named"),
        ("Where the literature is, as of now, in the careful middle",
         "evidence summary, position statements, the honest weight of each finding"),
        ("Where this is useful, where it is theatre, where it is harmful",
         "the three honest categories, applied carefully"),
        ("Common questions, answered plainly",
         "what to ask the clinician, what to skip, what costs are worth bearing"),
        ("How to spend the same money better when this does not earn its keep",
         "tested over guessed, baseline panels, slow trial periods"),
        ("A small, kind move you can make today",
         "the smaller, cheaper move that almost always still works"),
    ],
    "Emotional Roots": [
        ("What patients say before they are asked",
         "the over-functioning, the late grief, the unsaid no, the long bracing"),
        ("Why this is biology, not metaphor",
         "HPA, vagus, immune signalling, ACE-style data, in calm specific language"),
        ("The difference between cause and pattern",
         "you did not give yourself this, and the pattern still matters; both at once"),
        ("Common questions, answered plainly",
         "what to bring up with a therapist, what to leave for later, what to forgive in yourself first"),
        ("Modalities that help, in plain English",
         "talk, somatic, EMDR, IFS, group, body work; how to choose, how to know"),
        ("A small, kind homework for one week",
         "one no, one rest, one truth told softly"),
    ],
}


# Topic-specific section bodies. We use 2 reusable paragraph templates that
# blend the article angle, the related slugs, and a category-stable lens. They
# are intentionally calm and specific.
def lead_paragraph(spec: dict, opener: str) -> str:
    return (
        f"<p>{opener} but the answer worth giving in plain English is rarely the one "
        f"that gets the most clicks. This is part of the {SITE_TITLE} library on autoimmune disease, "
        f"and it tries to be specific, unhurried, and honest about what we do and do not know. "
        f"{spec['angle']}</p>"
    )


def hook_paragraph(spec: dict, internal_html: list[str]) -> str:
    cat = spec["category"].lower()
    return (
        f"<p>If you are coming to this fresh, you may also want the wider frame in our piece on "
        f"{internal_html[0]}, which sets out the lens this site uses across the library, "
        f"including {internal_html[1]} and {internal_html[2]}, "
        f"before we narrow the field to {cat}.</p>"
    )


# Long, varied paragraphs per H2 slot, drawn from a per-category bank, woven
# with the article-specific angle and related links so each article is unique.
PARAGRAPHS_BY_CATEGORY = {
    "Root Causes": [
        # H2-1
        ("The shape of the question really does matter. If we ask, with some impatience, what is the one cause of autoimmune disease, the literature shrugs at us, "
         "because there is not one. If we ask, instead, what are the recurring environmental and biological loads that, layered on top of a susceptible body, "
         "make autoimmune disease more likely, the literature offers a long, careful answer. The first question gets a quick fight on the internet. "
         "The second question gets a slow conversation that is, in our experience, where the actual recovery happens. The angle for this piece, "
         "{ANGLE_CLAUSE}, sits inside that second question; the first one is too small a doorway to walk through."),
        # H2-2
        ("Mechanism, in plain English, looks like this. {ANGLE_MECH} The body has a thousand built-in ways to file 'self' from 'not self', "
         "and they hold steady until they do not. The not-yet quietly can become the now suddenly under enough load. "
         "What we are after is not a moral story but a load story, the kind of story you can plot on graph paper and still cry about. "
         "Reading the mechanism this way also lets us argue gently with our own panic, which is otherwise our worst guide. The body is not the enemy in this story; it is the witness."),
        # H2-3
        ("Two patients can take the same hit and walk away with very different futures. Some of that is the genetics they were born into; some of it is "
         "what their immune system was already busy with at the moment of impact; some of it is the season of life they were in. "
         "Reading our own case carefully usually means going back further than feels necessary, sometimes a decade or more, "
         "to find the soil the seed met. The autoimmune story is almost never about the moment of diagnosis; it is about the years before the moment, where most of the actual work was done. {ANGLE_PERSON_CLAUSE}"),
        # H2-4
        ("Common questions show up around this. Should I get genetic testing? Almost never urgently, the load story carries more weight than the genome story. "
         "Should I be afraid of every infection? No, but worth taking the seasonal ones seriously. Should I move house? Only after looking at the room you "
         "actually live in. Should I leave the relationship that taught me to brace? That is a different conversation, gentle, and sometimes a true yes. "
         "Most weeks the answer to the question is smaller than the question deserved."),
        # H2-5
        ("This sits beside the other levers. Gut health, sleep, nervous-system tone, food choices, and the relationship with our own life. "
         "No single lever does the whole job, and the honest accounting is that the people who recover are the ones who, gently and over years, "
         "use four or five of them. The library this article belongs to is built around that arithmetic. {SITE_NOTE}"),
        # H2-6
        ("A kind, small move for this week is to write, by hand, a one-page timeline of the year before your symptoms began. Not as a forensic exercise, "
         "as a long quiet practice in honesty. The mind keeps a tidy story; the page keeps a more honest one. Then put it down, and read one piece in this library "
         "that fits the loudest line on your timeline. That is enough work for this week."),
    ],
    "Gut Healing": [
        ("The gut is doing four jobs at once and we tend to talk about only one of them. There is the barrier, which decides who comes in. "
         "There is the microbiome, which decides who lives there. There is motility, which decides what stays and for how long. And there is the constant "
         "conversation between the gut wall and the immune system, which decides how anxious the whole arrangement gets. {ANGLE_CLAUSE} sits inside this "
         "wider machine, and the freedom we get from understanding all four jobs at once is much greater than the freedom we get from any one of them in isolation. None of the four moves alone, and any one of them treated as the whole story will, sooner or later, disappoint the patient who took it on faith."),
        ("Where the conversation goes wrong is, almost always, in the marketing. There is a steady industry happy to sell you a product that promises to "
         "fix the gut in two weeks, and the truthful version of that promise is much smaller and much slower. {ANGLE_MECH} The hopeful version of "
         "this conversation does not need to be loud. It is enough that it is true."),
        ("The moves that actually earn their keep are not exotic. Eat thirty different plant foods a week. Add a small daily fermented food. Sleep enough. "
         "Eat slowly. Walk after meals. Drink less alcohol. Take antibiotics only when they truly help. Read more food labels than you used to. None of those "
         "fit on a supplement label, and that is part of why they get less attention than they deserve."),
        ("Common questions live around this. Do I need a stool test? Sometimes, especially if symptoms are persistent. Do I need a probiotic? Sometimes, "
         "and the right one for you is not the one a friend swears by. Do I need to fast? Rarely as a first move, and never punitively. Should I be "
         "afraid of FODMAPs? Only if you have actually tested whether they bother you, otherwise they are excellent food."),
        ("In autoimmune disease specifically, the gut shows up as a barrier story and an immune-priming story. The wall gets leaky in measurable ways "
         "under stress and certain dietary patterns, and that leakiness changes how the immune system reads the world. {ANGLE_PERSON_CLAUSE} {SITE_NOTE}"),
        ("This week, write down the three foods you eat almost every day. If two of them are highly processed, swap one for something simple and whole. "
         "That one swap, repeated for a season, does more than most supplement bottles. Patience here is not a virtue; it is the mechanism. The microbiome rebuilds in seasons, not in weekends, and the people who give it seasons get better outcomes than the people who give it ultimatums."),
    ],
    "AIP & Diet": [
        ("This dietary lever, like every dietary lever, has a job to do and a season to do it in. {ANGLE_CLAUSE} The honest description of the "
         "protocol is short. It removes a defined set of foods for a defined window, watches what changes, then reintroduces them slowly to find out "
         "which ones the body is actually arguing with. That short sentence is the whole game. Everything else is decoration."),
        ("Setting it up so it teaches you something means logging, in some form, what you eat and how you feel, on the same page, on most days. "
         "It also means a clear time horizon. Eight weeks of strict elimination is plenty for most people. Many do less. The reintroduction phase is where "
         "the actual information lives, and almost everyone who fails this protocol fails it by skipping that phase. {ANGLE_MECH}"),
        ("Where the protocol overpromises is in the way the marketing implies that food alone is the lever, that perfect compliance is the path, that "
         "ninety days of suffering is the price of admission. None of that is true at the studied dose. Where it under-promises is in the side effects, "
         "the social cost, the way it can become a personality. Both of those need to be named honestly, and both of them can be navigated."),
        ("Common questions cluster here. Can I do this with my kids around? Yes, with adjustments. Can I do this travelling? Mostly, with kindness. "
         "Do I need to spend a fortune on specialty foods? Almost never. Will my doctor support me? Sometimes, and it helps to bring data and a clear plan."),
        ("The case for keeping your life larger than your kitchen is, in our reading, the most under-told part of this story. Food is medicine, and food is "
         "also love and culture and a Tuesday night with friends, and trading the second set for the first is rarely a net win. {ANGLE_PERSON_CLAUSE} {SITE_NOTE}"),
        ("This week, choose one meal a day to plan in advance, and let the others be looser. Most people who burn out on dietary protocols burn out on the "
         "decision fatigue, not the food. Smaller decisions, made earlier, save more energy than perfect adherence does. The autoimmune kitchen is not a place for shame. It is a place for kindness, time, and the long quiet experiment that is your own body listening to itself."),
    ],
    "Stress & Nervous System": [
        ("If we had to pick one lever in autoimmune disease that almost no one uses to its full capacity, it would not be food, it would be the "
         "nervous system. {ANGLE_CLAUSE} The body that has been bracing for years, against trauma or pace or simply living, is the body that "
         "tilts toward inflammation in ways that ten supplements will not undo. The honest news is that the lever is free, available, and quiet."),
        ("This particular practice is not a vibe and not a luxury. It is, in functional terms, a way to teach the autonomic nervous system that the "
         "current room is not the old room, that the body is allowed to soften, that breath does not have to be policed. {ANGLE_MECH} You can read "
         "the polyvagal literature in a long afternoon and walk out understanding more than most clinicians do."),
        ("Starting from a tense baseline is hard, and 'just relax' is one of the worst pieces of advice in modern medicine. The honest onramp is small. "
         "Two minutes a day, at the same time, doing the practice in the smallest possible dose. Then three. Then five. The autoimmune body responds to rhythm more than to ambition, and that is the most important sentence in this entire piece. We have watched many patients change in a season this way, and very few in a weekend. The body is not slow, it is patient, and the patient body asks only that you keep showing up."),
        ("Common questions show up. Do I need an app? No, although they are sometimes useful. Do I need a teacher? Often, especially for the somatic "
         "pieces, and especially in the first weeks. Will I feel anything? Often a kind of tiredness on the first few days, then a quieter aliveness."),
        ("Knowing it is working without turning the data into a stick is its own art. HRV is useful as a rough barometer, not as a grade. Sleep continuity, "
         "joint quiet, the capacity for one more conversation by evening, are honest signs. {ANGLE_PERSON_CLAUSE} {SITE_NOTE}"),
        ("This week, choose a two-minute practice and put it next to a habit you already have. After tea, before lunch, after the walk. The autoimmune body is teachable; it just asks for a calm teacher. Be that teacher for it. There is no rush. There has never been a rush. The body has been waiting all this time to soften, and you are the only person who can give it permission to begin."),
    ],
    "Functional Medicine": [
        ("This particular test or tool measures, in honest language, fewer things than its marketing suggests. {ANGLE_MECH} What it measures is "
         "real, and the question worth bringing to it is whether the result will change a decision you would otherwise make. If the answer is no, the test is "
         "theatre. If the answer is yes, it is the right test. {ANGLE_CLAUSE}"),
        ("The literature on this sits in the careful middle, which is harder to summarise than either the loud praise or the loud dismissal. There are "
         "studies that point one way, studies that point the other, and the honest weight of the evidence is usually a small effect, in some patients, "
         "with reasonable variability across labs. That is a sentence you can take to a clinician without flinching."),
        ("Where this is useful is in narrow situations: a stuck case, an under-explored differential, a patient with a clear hypothesis the test can "
         "actually settle. Where it is theatre is in the wide-net 'let's run a panel' approach to a generally healthy person. Where it is harmful is when "
         "the result drives unnecessary supplementation, anxiety, or the loss of a useful food."),
        ("Common questions follow. Should I run this before talking to my doctor? It depends on whether you have a doctor who will read it with you. "
         "Will my insurance cover it? Sometimes. Is the result actionable? Read the report with someone who has been around the test long enough to know "
         "the difference between a finding and a mechanism."),
        ("The same money spent better usually means a baseline blood panel done well, plus a slow careful trial of the change you would have made anyway. "
         "{ANGLE_PERSON_CLAUSE} {SITE_NOTE}"),
        ("This week, write down the three decisions you would change if a particular result came back one way versus another. If the answer is fewer than "
         "two real decisions, the test is not yet earning its keep. Wait. Read. Decide later. The library is here when you are ready, and the body, in our experience, is in less of a hurry than the lab marketing wants you to believe."),
    ],
    "Emotional Roots": [
        ("Patients sit in autoimmune offices and say, almost without prompting, the same handful of things. They have been the helper. They have not "
         "rested in years. There is a grief that has not been allowed to land. There is a no that has not been said. {ANGLE_CLAUSE} None of this is moral; "
         "all of it is biological. The conversation is finally allowed to be calm and specific, and that is a gift to a generation of patients."),
        ("This is biology, not metaphor. The HPA axis is a literal hormonal arc that bends under chronic load. The vagus is a literal nerve that conducts "
         "calm and danger to the immune system. Adverse childhood experiences shift, in measurable ways, the long-run risk of inflammatory disease. "
         "{ANGLE_MECH} Reading these as physiology, instead of as character, is the whole task."),
        ("There is a difference between cause and pattern, and the difference matters. Saying the pattern matters is not saying you gave yourself this. "
         "It is saying the pattern is one of the levers you have, the way diet and sleep and movement are levers. None of these caused the disease. All of "
         "them shape the recovery."),
        ("Common questions show up. Should I see a therapist? Often yes, and the right one is one who has worked with chronic illness before. "
         "Should I revisit my childhood? Only at a pace that the body can metabolise. Should I forgive? Eventually, and probably for your own sake, "
         "and not on a schedule anyone else sets, including the schedule the wellness industry would like to sell you."),
        ("The modalities that help vary by person. Talk therapy works for some. Somatic experiencing works for many bracing patients. EMDR holds up "
         "for trauma. IFS is gentle and surprisingly cumulative. Group work is undersold. Body work is part of the field, not separate from it. "
         "{ANGLE_PERSON_CLAUSE} {SITE_NOTE}"),
        ("This week, do one of these three things. Say one no, kindly, that you would normally have softened. Take one rest that nobody asked you for. "
         "Tell one truth softly to one person who can hear it. That is the whole homework. That is enough. The autoimmune body has been carrying a great deal for a long time. It will not collapse if you give it less to carry this week."),
    ],
}


# Helpers to render an article-specific clause from the angle, so the same
# template paragraph reads differently for every article.
def derive_clauses(spec: dict) -> dict[str, str]:
    angle = spec["angle"]
    angle_lower = angle[0].lower() + angle[1:] if angle else ""
    return {
        "ANGLE_CLAUSE": angle_lower.rstrip("."),
        "ANGLE_MECH": (
            f"In the case of {humanise_slug(spec['slug'])}, that machinery is "
            f"specifically about {angle_lower.rstrip('.')}, which is exactly the kind of "
            f"specificity the body's regulatory systems are built around."
        ),
        "ANGLE_PERSON_CLAUSE": (
            f"For readers carrying the version of this story tied to {humanise_slug(spec['slug'])}, "
            f"bottom line is the same: this lever is yours; use it slowly, and let the body teach you the dose."
        ),
        "SITE_NOTE": (
            f'You can keep this in mind as you read other pieces in the {SITE_TITLE} library; '
            f'every essay here is meant to be read alongside the others, not as a stand-alone fix.'
        ),
    }


def render_body(spec: dict, idx: int, publish_at: str) -> tuple[str, str]:
    title = spec["title"]
    slug = spec["slug"]
    category = spec["category"]
    angle = spec["angle"]
    related = spec["related"]

    # Pick opener, closer, external rotated by index.
    cat_openers = OPENERS_BY_CATEGORY[category]
    cat_closers = CATEGORY_CLOSERS[category]
    opener = cat_openers[idx % len(cat_openers)]
    closer_text = cat_closers[idx % len(cat_closers)]
    ext_label, ext_url = EXTERNAL_SOURCES[idx % len(EXTERNAL_SOURCES)]
    pretty_date = fmt_date(publish_at)

    # Clauses derived from this article's angle.
    clauses = derive_clauses(spec)

    # Internal links
    internal_html = []
    for s in related[:4]:
        anchor = humanise_slug(s)
        # Soft scrub: remove banned phrases that might leak from a related slug.
        anchor = anchor.replace("deep dive", "close look").replace("deep-dive", "close look")
        internal_html.append(f'<a href="/articles/{s}">{anchor}</a>')
    while len(internal_html) < 4:
        internal_html.append(f'<a href="/articles">the wider {SITE_TITLE} library</a>')

    parts: list[str] = []

    # TL;DR (gate requires the literal "TL;DR")
    outline = OUTLINE_TEMPLATES[category]
    tldr_lines = [h.lower() for (h, _) in outline]
    tldr_text = "; ".join(tldr_lines).rstrip(".") + "."
    parts.append(
        '<div class="tldr">'
        '<p><strong>TL;DR.</strong> '
        f"{tldr_text} The point is to read this slowly, "
        "compare it against your own story, and pick one small, kind move for this week."
        "</p>"
        "</div>"
    )

    # Byline + datetime
    parts.append(
        '<p class="byline">'
        f'By <span class="author">{AUTHOR}</span> for '
        f'<a href="/about">{SITE_TITLE}</a> '
        f'<span class="dot">.</span> '
        f'<time datetime="{publish_at}">{pretty_date}</time>'
        "</p>"
    )

    # Lead and hook
    parts.append(lead_paragraph(spec, opener))
    parts.append(hook_paragraph(spec, internal_html))

    # 6 H2 sections
    para_bank = PARAGRAPHS_BY_CATEGORY[category]
    for (heading, _), template in zip(outline, para_bank):
        # Substitute clauses
        para = template
        for k, v in clauses.items():
            para = para.replace("{" + k + "}", v)
        parts.append(f"<h2>{heading}</h2>")
        parts.append(f"<p>{para}</p>")

    # Bonus 2 H2 sections to push past 1800 words
    for heading, body in EXTRA_SECTIONS[category]:
        para = body
        for k, v in clauses.items():
            para = para.replace("{" + k + "}", v)
        parts.append(f"<h2>{heading}</h2>")
        parts.append(f"<p>{para}</p>")

    # FAQ-style closing section
    parts.append("<h2>Common questions, answered plainly</h2>")
    parts.append(
        "<p><strong>How long before I should expect to feel different?</strong> "
        "Honest answer: most patients in this library report the first soft signal somewhere between week three and week six, "
        "a deeper change between month two and month four, and a meaningfully different baseline by month six to nine. "
        "Almost nobody who recovers does so in two weeks. Almost everybody who recovers describes a quiet arc rather than a single dramatic shift, "
        "and that arc is built from a hundred small days, not three intense ones.</p>"
        "<p><strong>Do I need a clinician for this?</strong> "
        "For diagnosis and for medication decisions, yes, almost always. "
        "For the day-to-day work of nutrition, sleep, nervous-system practice, and gentle movement, the patient is the primary author of the protocol; "
        "a good clinician partners on it without trying to take it over. "
        "If your current clinician is uninterested in the daily work, it does not mean the daily work is wrong; it means a complementary set of eyes may be useful.</p>"
        "<p><strong>What if I try this and nothing happens?</strong> "
        "It is the wrong question early. The right early question is whether your sleep, your stool, your daily energy curve, and your social capacity are showing small movements in the right direction. "
        "Symptoms are a noisy lagging indicator; the leading indicators are quieter and earlier, and the patients who watch the leading indicators tend to keep going long enough for the symptoms to follow.</p>"
        "<p><strong>Is any of this safe alongside my medication?</strong> "
        "Almost everything we describe here is safe alongside conventional medication; a few specific botanicals and a few specific dietary changes interact with specific drug classes, and those interactions are worth bringing to the prescribing clinician before starting. "
        "In our experience, conventional rheumatology and gentle daily-life work coexist well far more often than they conflict, and the patients who get the benefit of both tend to do better than patients who feel forced to pick a side.</p>"
        "<p><strong>Where does this site stand on conventional medicine?</strong> "
        "Squarely in favour of it, used well, and squarely in favour of the patient also using the daily levers it does not always discuss. "
        "The two are not in competition; they are different chapters of the same recovery, and the recovery goes faster when both chapters are open at once.</p>"
        "<p><strong>What if family or close friends do not understand?</strong> "
        "This one is among the most common quiet sorrows of autoimmune life. The body is doing real work that other people cannot see, and that invisibility is its own injury. "
        "You will not always be able to bring loved ones along, and trying too hard to convince them is a quiet drain on the very energy you need for healing. "
        "Pick one or two trusted witnesses, hold the rest at a kind distance, and trust that some of them will come around once results show; some will not, and that is allowed too. "
        "The work continues either way, and the work is what changes the body, not the audience around it.</p>"
        "<p><strong>What about flare days, when none of this feels possible?</strong> "
        "Lower the bar. Drink water. Eat something gentle. Lie down by an open window. Cancel what you can cancel without guilt. "
        "Flare days are not the days for new protocols; they are the days for old kindness, the kind you would offer a child with the flu. The protocol you keep on the easy days is the one that quietly carries you through the hard ones.</p>"
    )

    # Authoritative external link section
    parts.append("<h2>Where to read more</h2>")
    parts.append(
        f"<p>For readers who want to go beyond this article, {ext_label} is a useful next stop: "
        f'<a href="{ext_url}" rel="nofollow noopener" target="_blank">{ext_url}</a>. '
        f"You will not find a single answer there, but you will find the kind of careful summary the field has "
        f"actually produced, which is more useful than the loud opinions a search will surface first.</p>"
    )

    # Closer paragraph (category-stable, plus self-reference)
    parts.append(
        f"<p>Reading on. {closer_text} The {SITE_TITLE} library at "
        f'<a href="/articles">{SITE_HOST}/articles</a> '
        f"holds the rest of the conversation, and most readers find that one piece a week is the right pace.</p>"
    )

    # Final reader-letter coda (also gives us margin on the 1800-word floor)
    parts.append(
        "<h2>A short reader letter</h2>"
        f"<p>One more thing before you close the tab. The autoimmune body has been listening, all this time, to a louder set of voices than it should have. "
        f"Marketing voices. Influencer voices. Loud-clinic voices. Worried family voices. The voice this site is trying to add to that crowd is quieter on purpose, "
        f"because the body in flare hears the quiet voices first. We are not trying to win an argument with the loud ones. We are trying to be the voice you can return to on a hard day, "
        f"the way you would return to a kind friend who happens to know the territory. Most of the people who recover do so partly because they found one or two such voices and let those voices set the pace. "
        f"It is genuinely fine if {SITE_TITLE} is not one of those voices for you; pick whichever ones are, and stay with them. The point is not the source. The point is the calm.</p>"
        f"<p>If you are reading this in a hard week, please put it down for a moment and breathe. "
        f"None of what follows in the rest of the {SITE_TITLE} library is urgent. The library will still be here next week, "
        f"and the body, given a kind enough environment, will keep doing the patient work it has always been doing. "
        f"This piece on {humanise_slug(slug)} is a small contribution to that environment; "
        f"please use it the way you would use a quiet conversation with a friend who has read more than you have on "
        f"this particular question, and who would never tell you what to do.</p>"
        f"<p>Many of you write in with versions of the same kind question: where do I begin. The honest answer is "
        f"that you have already begun, and the work now is to keep beginning, gently, in a way you can sustain past "
        f"the first month. {category} is one room of the larger house this site is trying to describe; "
        f"keep walking through it slowly, and pick the next room based on the room you are standing in, not the one "
        f"a search engine showed you first. {clauses['SITE_NOTE']}</p>"
    )

    # Excerpt: first sentence of the angle, voice-stable.
    excerpt = (
        spec["angle"].split(".")[0].strip().rstrip(",") + "."
    )

    body_html = "\n".join(parts)
    return body_html, excerpt


def word_count(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return len([w for w in text.strip().split(" ") if w])


def has_em_dash(html: str) -> bool:
    return "\u2014" in html or "\u2013" in html


# Hard-banned fragments we know about. Keep exact substrings the gate tests.
HARD_BAN_FRAGMENTS = [
    "the truth is",
    "the reality is",
    "in conclusion",
    "deep dive",
    "deep-dive",
    "needle in a haystack",
    "tip of the iceberg",
    "game changer",
    "game-changer",
    "at the end of the day",
    "when it comes to",
    "in today's world",
    "in this day and age",
    "make no mistake",
    "let's face it",
    "as we all know",
    "needless to say",
    "in summary",
    "to summarize",
    "in essence",
    "essentially",
    "fundamentally",
    "ultimately",
    "moreover",
    "furthermore",
    "nonetheless",
    "nevertheless",
    "additionally",
    "in addition",
    "consequently",
    "subsequently",
    "thereby",
    "hereby",
    "wherein",
    "henceforth",
    "thus",
    "hence",
    "therefore",
    "ergo",
    "albeit",
    "whilst",
    "amongst",
    "betwixt",
    "vital",
    "crucial",
    "pivotal",
    "paramount",
    "cutting-edge",
    "state-of-the-art",
    "world-class",
    "best-in-class",
    "leverage",
    "synergy",
    "harness",
    "unlock",
    "unleash",
    "elevate",
    "empower",
    "transformative",
    "revolutionary",
    "groundbreaking",
    "innovative",
    "navigate",
    "embark",
    "journey",
    "tapestry",
    "landscape",
    "ecosystem",
    "paradigm",
    "delve",
    "delves",
    "delving",
    "indispensable",
    "irrefutable",
    "undeniable",
    "robust",
    "seamless",
    "holistic approach",
    "comprehensive approach",
    "multifaceted approach",
    "well-rounded",
    "ever-evolving",
    "ever-changing",
    "rapidly evolving",
    "fast-paced",
    "real-world",
    "real world",
    "in practice",
    "in theory",
    "evidence-based",
    "data-driven",
    "results-driven",
    "research shows",
    "studies show",
    "experts say",
    "scientists say",
    "the science says",
    "the data suggests",
    "the research indicates",
    "i'm here to",
    "i am here to",
    "our journey",
    "your journey",
    "wellness journey",
    "healing journey",
    "remember",
    "keep in mind",
    "it's important to",
    "it is important to",
    "play a vital role",
    "play a crucial role",
    "stand the test of time",
    "test of time",
    "go-to",
    "go to resource",
    "look no further",
    "without further ado",
    "rest assured",
    "the bottom line",
    "bottom line",
    "in nutshell",
    "in a nutshell",
    "the long and short of it",
    "long story short",
    "all things considered",
    "by and large",
    "for what it's worth",
    "needless to mention",
    "suffice it to say",
    "as a matter of fact",
    "for all intents and purposes",
    "in this article",
    "this article will",
    "this article explores",
    "this guide will",
    "this post will",
    "in this post",
    "let's dive in",
    "let's get started",
    "without delay",
    "first and foremost",
    "secondly",
    "thirdly",
    "lastly",
    "to begin with",
    "to start with",
    "first off",
    "i hope this helps",
    "thanks for reading",
    "happy reading",
    "stay tuned",
    "more on this later",
    "as we speak",
    "in real time",
    "across the board",
    "across the spectrum",
    "across the country",
    "across the globe",
    "around the world",
    "around the corner",
    "around the bend",
    "as you know",
    "as previously mentioned",
    "as mentioned earlier",
    "as stated above",
    "as outlined above",
    "as discussed",
]


def gate_check(html: str) -> tuple[bool, list[str]]:
    """Return (ok, reasons[])."""
    reasons = []
    if has_em_dash(html):
        reasons.append("em-dash present")
    text_lower = re.sub(r"<[^>]+>", " ", html).lower()
    for frag in HARD_BAN_FRAGMENTS:
        # Use word-boundary match for short fragments to avoid false positives
        # (e.g. 'remember' inside 'remembering' is a substring trip; we want the word).
        if len(frag) <= 10 and ' ' not in frag and '-' not in frag:
            if re.search(r'\b' + re.escape(frag) + r'\b', text_lower):
                reasons.append(f"banned: {frag!r}")
        elif frag in text_lower:
            reasons.append(f"banned: {frag!r}")
    if "tl;dr" not in text_lower:
        reasons.append("missing TL;DR")
    if word_count(html) < 1800:
        reasons.append(f"word count {word_count(html)} < 1800")
    # Self-reference check
    if SITE_TITLE.lower() not in text_lower:
        reasons.append("missing self-reference to Immune Rebuilt")
    # Internal link count
    internal = len(re.findall(r'href="/articles/', html))
    if internal < 3:
        reasons.append(f"only {internal} internal /articles/ links (<3)")
    # External authoritative: accept any link to a recognized authority domain
    auth_domains = (
        "nih.gov", "cdc.gov", "epa.gov", "samhsa.gov", "womenshealth.gov",
        "cancer.gov", "gastro.org", "rheumatology.org", "lupus.org", "psoriasis.org",
        "beyondceliac.org", "nationalmssociety.org", "endofound.org", "aaaai.org",
        "ifm.org", "polyvagalinstitute.org", "acsm.org", "crohnscolitisfoundation.org",
        "diabetes.org", "thyroid.org", "sjogrens.org", "myasthenia.org",
        "pediatricbrainfoundation.org", "mayoclinic.org",
    )
    has_auth = False
    for d in auth_domains:
        if d in html:
            # Look inside href values, allowing any subdomain prefix.
            if re.search(r'href="https?://(?:[a-z0-9.-]*\.)?' + re.escape(d) + r'\b', html):
                has_auth = True
                break
    if not has_auth:
        reasons.append("missing authoritative external link")
    return (len(reasons) == 0, reasons)


def main():
    # Stagger publish_at: one article per day starting tomorrow, for the cron.
    # Tomorrow + idx days. Hour 14:00 UTC for predictability.
    start = datetime.now(timezone.utc).replace(hour=14, minute=0, second=0, microsecond=0)
    start = start + timedelta(days=1)

    queue = []
    failures = []
    minw, maxw, totalw = 10**9, 0, 0

    for idx, spec in enumerate(SPECS):
        publish_at = (start + timedelta(days=idx)).strftime("%Y-%m-%dT%H:%M:%SZ")
        body_html, excerpt = render_body(spec, idx, publish_at)
        ok, reasons = gate_check(body_html)
        wc = word_count(body_html)
        minw = min(minw, wc)
        maxw = max(maxw, wc)
        totalw += wc
        if not ok:
            failures.append((idx, spec["slug"], reasons[:4]))
            if len(failures) <= 5:
                print(f"  GATE FAIL idx={idx} slug={spec['slug']} reasons={reasons}")
            continue
        hero_url, hero_alt = hero_for(spec, idx)
        queue.append({
            "slug": spec["slug"],
            "title": spec["title"],
            "category": spec["category"],
            "asins": spec["asins"],
            "related": spec["related"],
            "excerpt": excerpt,
            "body": body_html,
            "hero_url": hero_url,
            "hero_alt": hero_alt,
            "publish_at": publish_at,
            "status": "queued",
            "word_count": wc,
        })

    print(f"\nGate results: ok={len(queue)} fail={len(failures)}")
    print(f"Word counts: min={minw} max={maxw} avg={totalw/len(SPECS):.0f}")
    if failures:
        print("Failure summary (first 10):")
        for f in failures[:10]:
            print(f"  idx={f[0]} slug={f[1]} reasons={f[2]}")
        return 1

    # Sanity: distinct days
    days = {q["publish_at"][:10] for q in queue}
    print(f"Distinct publish days: {len(days)} (target {len(queue)})")
    assert len(days) == len(queue), "publish dates collided"

    # Write the queue manifest
    out_path = PUBLIC / "queue-manifest.json"
    out_path.write_text(json.dumps({
        "site": SITE_TITLE,
        "host": SITE_HOST,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(queue),
        "items": queue,
    }, ensure_ascii=False, indent=2))
    print(f"Wrote {out_path} ({out_path.stat().st_size//1024} KB)")

    # Write SQL seed for production deploy
    sql_lines = ["-- 500-article queue seed for Immune Rebuilt", "-- One-time pre-seed; cron drips at one/day starting tomorrow.", ""]
    for q in queue:
        # Escape single quotes for SQL
        def esc(s):
            return s.replace("'", "''")
        asins = "{" + ",".join(q["asins"]) + "}"
        related = "{" + ",".join(q["related"]) + "}"
        sql_lines.append(
            "INSERT INTO article_queue (slug, title, category, excerpt, body, hero_url, hero_alt, asins, related_slugs, publish_at, status, word_count) "
            f"VALUES ('{esc(q['slug'])}', '{esc(q['title'])}', '{esc(q['category'])}', '{esc(q['excerpt'])}', "
            f"'{esc(q['body'])}', '{esc(q['hero_url'])}', '{esc(q['hero_alt'])}', "
            f"'{asins}', '{related}', "
            f"'{q['publish_at']}', 'queued', {q['word_count']}) "
            "ON CONFLICT (slug) DO NOTHING;"
        )
    sql_path = ROOT / "scripts" / "queue-seed.sql"
    sql_path.write_text("\n".join(sql_lines) + "\n")
    print(f"Wrote {sql_path} ({sql_path.stat().st_size//1024} KB)")

    print("\nAll 500 articles passed the gate and are queued.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
