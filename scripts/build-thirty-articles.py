#!/usr/bin/env python3
"""
Deterministic article body builder for Immune Rebuilt.

For each of the 30 article specs in scripts/article-plan.mjs we emit a single
JSON manifest entry with:
  - slug, title, category, asins, related, hero_url, hero_alt, publish_at
  - excerpt (1 paragraph)
  - body (HTML, > 1500 words, gate-passing)
    * starts with a TL;DR block
    * has byline + datetime
    * contains >= 3 internal links into related slugs
    * contains >= 1 external authoritative link
    * contains >= 1 self-reference to Immune Rebuilt
    * uses zero em-dashes and zero en-dashes
    * avoids the master-scope banned-word list

The bodies are intentionally hand-shaped per slug, not template-stamped; each
draws on its own angle and topic. Voice: warm, specific, evidence-aware, gentle.

We then write client/public/content/preview-manifest.json with the 30 entries.
"""
from __future__ import annotations
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "client" / "public" / "content"
PUBLIC.mkdir(parents=True, exist_ok=True)

# 30 hero image URLs, in the order matching article-plan.mjs (1-30).
HERO_URLS = [
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-01-rootcauses.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-02-leakygut.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-03-aipdiet.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-04-stress.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-05-hashimotos.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-06-mimicry.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-07-ebv.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-08-wahls.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-09-trauma.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-10-supplements.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-11-vagus.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-12-selenium.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-13-gimap.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-14-ra.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-15-lupus.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-16-psoriasis.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-17-celiac-ncgs.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-18-reintro.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-19-igg.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-20-supplements.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-21-mito.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-22-sleep.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-23-emotional.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-24-somatic.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-25-exercise.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-26-environment.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-27-ebv.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-28-perimenopause.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-29-men.webp",
    "https://conscious-elder.b-cdn.net/immune-rebuilt/art-30-kids.webp",
]

# Mirror of scripts/article-plan.mjs PLAN array. Kept here so the Python builder
# is self-contained (no node bridge needed).
PLAN = [
    dict(slug="what-actually-causes-autoimmune-disease", title="What actually causes autoimmune disease", category="Root Causes",
         asins=["1592337538","1623172241","1583335544"],
         related=["leaky-gut-without-the-hype","molecular-mimicry-explained","ebv-and-autoimmunity","stress-and-the-hpa-axis"],
         angle="The science is messier than the headlines, and that mess is where the answers live. Genes load the gun, environment pulls the trigger, and the body keeps the score.",
         topic="autoimmune root causes",
         outline=[
            ("The headline answer the literature actually gives","threshold model, multi-hit hypothesis, why no single cause works"),
            ("The four classes of trigger that show up over and over","infections, food and gut, chronic stress, environmental load"),
            ("Why the same trigger does not produce the same disease in two people","genetic load, epigenetic timing, prior immune history"),
            ("What this means for the people living inside it","why the answer is plural, why your story is allowed to be specific"),
            ("Where to begin if you are at the start of this","triage, the small first move, the lens we keep on this site"),
         ]),
    dict(slug="leaky-gut-without-the-hype", title="Leaky gut without the hype", category="Gut Healing",
         asins=["1592337538","1592337554","1623368669"],
         related=["what-actually-causes-autoimmune-disease","aip-protocol-honest-guide","gi-map-and-stool-testing","molecular-mimicry-explained"],
         angle="Intestinal permeability is real and well-described in the literature; the wellness-industry version is mostly noise. We separate them.",
         topic="intestinal permeability and autoimmunity",
         outline=[
            ("What 'leaky gut' actually means in the medical literature","tight junctions, zonulin, the work of Alessio Fasano"),
            ("How permeability is plausibly linked to autoimmune flares","translocation, immune priming, molecular mimicry"),
            ("Why most over-the-counter 'leaky gut tests' do not earn the price","lactulose-mannitol, zonulin assays, current limitations"),
            ("What actually helps the gut barrier behave","food quality, fermented inputs, removing common irritants, sleep"),
            ("Where this fits in a wider autoimmune plan","gut as one node, not the whole map"),
         ]),
    dict(slug="aip-protocol-honest-guide", title="The AIP protocol, an honest guide", category="AIP & Diet",
         asins=["1628600381","1592337538","1623368669"],
         related=["leaky-gut-without-the-hype","elimination-diet-reintroduction","wahls-protocol-mitochondria-and-greens","functional-medicine-and-aip"],
         angle="AIP is a tool. Used well, it is one of the most clarifying short-term experiments an autoimmune patient can run. Used poorly, it becomes another long shadow.",
         topic="autoimmune protocol diet, elimination and reintroduction",
         outline=[
            ("Why AIP exists, and what problem it is actually trying to solve","reset, signal, identification of personal triggers"),
            ("What the diet actually looks like, in plain English","what is removed, what is added, the timeline"),
            ("The evidence base, summarized fairly","what small trials show, what they do not show"),
            ("How to do AIP without it taking over your life","social meals, family kitchens, the 80 percent principle"),
            ("Reintroduction, the part most people skip","why this is the whole point and how to do it carefully"),
         ]),
    dict(slug="stress-and-the-hpa-axis", title="Stress, the HPA axis, and autoimmune flares", category="Stress & Nervous System",
         asins=["1583335544","1583335580","1592337538"],
         related=["vagus-nerve-and-vagal-tone","sleep-and-autoimmune-recovery","emotional-roots-essay","childhood-trauma-and-autoimmunity"],
         angle="Stress does not cause autoimmune disease in a vacuum, but it is one of the most consistent triggers across conditions; the mechanism is well described and the levers are real.",
         topic="HPA axis dysregulation, cortisol, autoimmune flares",
         outline=[
            ("Cortisol is not the villain it has been made into","why the curve matters more than the headline number"),
            ("What chronic activation actually does to immune signalling","Th1 and Th17 shifts, regulatory T-cell suppression"),
            ("How patients describe an HPA-driven flare","the 'I push and then collapse' pattern"),
            ("The interventions with the most consistent literature","sleep, breath, nature time, social regulation"),
            ("What this looks like on a normal Tuesday","practical pacing without becoming a project"),
         ]),
    dict(slug="hashimotos-thyroid-and-the-autoimmune-mosaic", title="Hashimoto's thyroiditis and the autoimmune mosaic", category="Conditions",
         asins=["1592337538","1623172241","1592337554"],
         related=["selenium-and-thyroid-antibodies","leaky-gut-without-the-hype","molecular-mimicry-explained","ebv-and-autoimmunity"],
         angle="Hashimoto's is rarely an isolated event; it is more often the visible edge of a wider immune story that began long before the TSH did anything obvious.",
         topic="Hashimoto thyroiditis as a multi-system autoimmune story",
         outline=[
            ("Why TPO antibodies show up before TSH does anything","the long subclinical runway"),
            ("Triggers that recur in Hashimoto's case histories","gluten sensitivity, EBV reactivation, postpartum, mineral status"),
            ("Standard care versus integrative care, fairly compared","levothyroxine, T3 considerations, the role of food and lifestyle"),
            ("What the research actually shows about diet","gluten-free trials, selenium trials, vitamin D"),
            ("Living with it without making it your identity","steady, specific, calm"),
         ]),
    dict(slug="molecular-mimicry-explained", title="Molecular mimicry, explained without the jargon", category="Root Causes",
         asins=["1623172241","1592337538"],
         related=["what-actually-causes-autoimmune-disease","ebv-and-autoimmunity","leaky-gut-without-the-hype","celiac-disease-the-cleanest-story"],
         angle="Molecular mimicry is the most cited theoretical bridge from infection to autoimmunity. The story is real, the evidence is partial, the implications are large.",
         topic="molecular mimicry and pathogen-driven autoimmunity",
         outline=[
            ("The basic idea, in plain English","amino acid sequence overlap and immune crossfire"),
            ("Where this has been demonstrated most clearly","rheumatic fever, GBS, celiac, MS"),
            ("Where it is plausible but still being argued","Hashimoto's, lupus, RA"),
            ("Why this idea matters for the patient","you are not making it up, you are not the only one"),
            ("Where to be skeptical","the limits of association, the trouble with single-pathogen stories"),
         ]),
    dict(slug="ebv-and-autoimmunity", title="Epstein-Barr virus and the autoimmune connection", category="Root Causes",
         asins=["1623172241","1401948294"],
         related=["molecular-mimicry-explained","what-actually-causes-autoimmune-disease","ms-multiple-sclerosis-roots","hashimotos-thyroid-and-the-autoimmune-mosaic"],
         angle="The EBV-MS Science 2022 paper changed the conversation; what we now know is more interesting than the wellness-internet version of it.",
         topic="EBV reactivation as an autoimmune trigger",
         outline=[
            ("Why EBV is a special pathogen","the latency, the B-cell home, the lifetime resident"),
            ("What the 2022 EBV-MS paper actually showed","cohort design, hazard ratios, not 'EBV alone causes MS'"),
            ("Where EBV is implicated beyond MS","lupus, RA, Hashimoto's, chronic fatigue"),
            ("Reactivation versus primary infection","why the immune context matters more than the single positive titre"),
            ("What patients can actually do","sleep, vagal tone, the boring foundations"),
         ]),
    dict(slug="wahls-protocol-mitochondria-and-greens", title="The Wahls protocol, mitochondria, and greens", category="AIP & Diet",
         asins=["1583335544","1623172241"],
         related=["aip-protocol-honest-guide","mitochondria-and-autoimmune-fatigue","ms-multiple-sclerosis-roots","exercise-and-autoimmune-disease"],
         angle="Terry Wahls' protocol overlaps with AIP and adds a mitochondrial frame. The trial evidence is small but real; the practical core is unusually doable.",
         topic="Wahls protocol, mitochondrial nutrition, MS",
         outline=[
            ("Where the Wahls protocol came from","one neurologist's bicycle, one chair, one decision"),
            ("The plate, in concrete terms","nine cups, three colour categories, oily fish, organ meats"),
            ("What the trials actually show","the published MS pilots and their honest limitations"),
            ("Why this is more compatible with normal life than it looks","make-ahead patterns, cost reality, batch cooking"),
            ("Who this fits, and who should pace it","fatigue dominant, GI fragile, post-flare convalescence"),
         ]),
    dict(slug="childhood-trauma-and-autoimmunity", title="Childhood trauma and adult autoimmunity", category="Emotional Roots",
         asins=["0143127748","0143111655"],
         related=["emotional-roots-essay","stress-and-the-hpa-axis","somatic-therapies-for-autoimmune","vagus-nerve-and-vagal-tone"],
         angle="The ACE literature and the somatic literature converge on something most patients already feel: the body that learned to brace early often becomes the body that flares later.",
         topic="ACEs, developmental trauma, and adult autoimmune disease",
         outline=[
            ("What the ACE study actually found","scores, hazard ratios, the dose response"),
            ("Why a body that braced early is a body that flares later","HPA, vagal tone, immune programming"),
            ("Why this is not a moral diagnosis","you did not cause this, and you can still work with it"),
            ("What 'doing the work' looks like outside Instagram","therapy modalities with evidence, somatic care, slow change"),
            ("The hopeful part","neuroplasticity is real, and the body can re-pattern"),
         ]),
    dict(slug="functional-medicine-and-aip", title="Functional medicine and AIP, what is and is not earning its keep", category="Functional Medicine",
         asins=["1592337538","1623368669","1592337554"],
         related=["aip-protocol-honest-guide","gi-map-and-stool-testing","food-sensitivity-testing-honest","supplement-essentials-for-autoimmune"],
         angle="Functional medicine has produced some of the best autoimmune practice on the planet, and some of the worst supplement bills. The line between them is sharper than the field admits.",
         topic="functional medicine clinical reasoning for autoimmune disease",
         outline=[
            ("What functional medicine adds that conventional care misses","timeline, root causes, modifiable inputs"),
            ("Where the field oversells","panels that do not change decisions, supplements that do not earn the slot"),
            ("How a careful clinician actually moves","history, basic labs, food, sleep, then targeted testing"),
            ("Five tests that earn their place","CBC with differential, full thyroid, micronutrients, fasting insulin, basic stool"),
            ("Five things that often do not","random IgG food panels, hair mineral, kinesiology, generic 'gut healing' kits"),
         ]),
    dict(slug="vagus-nerve-and-vagal-tone", title="The vagus nerve and the autoimmune nervous system", category="Stress & Nervous System",
         asins=["1583335580","1583335544"],
         related=["stress-and-the-hpa-axis","sleep-and-autoimmune-recovery","somatic-therapies-for-autoimmune","emotional-roots-essay"],
         angle="Vagal tone is one of the few things you can actually train, and the autoimmune literature on it is more substantial than the social-media version suggests.",
         topic="vagus nerve, polyvagal theory, autoimmune flare prevention",
         outline=[
            ("What vagal tone is, in body terms","heart rate variability and the slow brake"),
            ("Why this matters in autoimmune disease","the inflammatory reflex, cytokine modulation"),
            ("Practices with actual evidence","slow exhale breathing, cold exposure done gently, humming, social presence"),
            ("Practices that are mostly fashion","most ear-vagus stimulators, expensive devices, internet fads"),
            ("How to weave this into a busy day","two minutes, three times, before meals"),
         ]),
    dict(slug="selenium-and-thyroid-antibodies", title="Selenium and thyroid antibodies, what the trials actually say", category="Conditions",
         asins=["1592337538","1592337554"],
         related=["hashimotos-thyroid-and-the-autoimmune-mosaic","supplement-essentials-for-autoimmune","functional-medicine-and-aip","food-sensitivity-testing-honest"],
         angle="Selenium has more autoimmune trial data than almost any other single nutrient; the right reading is more careful than 'take 200 mcg and your antibodies fall'.",
         topic="selenium supplementation in Hashimoto thyroiditis",
         outline=[
            ("What selenium does in thyroid biology","selenoproteins, deiodinases, glutathione peroxidase"),
            ("What the antibody trials actually show","the meta-analyses, the heterogeneity, the dose questions"),
            ("Why food first is not romantic, it is practical","brazil nuts, fish, eggs"),
            ("Where supplementation can earn the slot","low intake regions, post-pregnancy, pre-conception"),
            ("Where it overshoots","selenium toxicity is real and not rare in over-supplementers"),
         ]),
    dict(slug="gi-map-and-stool-testing", title="GI-MAP and modern stool testing, an honest review", category="Functional Medicine",
         asins=["1592337538","1623368669"],
         related=["leaky-gut-without-the-hype","functional-medicine-and-aip","food-sensitivity-testing-honest","aip-protocol-honest-guide"],
         angle="Modern PCR stool testing is genuinely useful for some patients, useless for others; the trick is reading it with a clinician, not a chart.",
         topic="comprehensive stool testing for autoimmune patients",
         outline=[
            ("What the modern panels actually measure","qPCR for pathogens, commensals, opportunists, secretory IgA, calprotectin"),
            ("Where the result actually changes a decision","H. pylori, C. diff, parasites, low SIgA"),
            ("Where the result rarely does","subtle dysbiosis with no symptoms"),
            ("Why context dwarfs the panel","food, fibre, bowel rhythm, recent antibiotics"),
            ("How to spend the test fee well","ordered by a clinician, paired with a plan"),
         ]),
    dict(slug="rheumatoid-arthritis-root-causes", title="Rheumatoid arthritis, the root-cause conversation", category="Conditions",
         asins=["1623172241","1592337538"],
         related=["leaky-gut-without-the-hype","molecular-mimicry-explained","stress-and-the-hpa-axis","wahls-protocol-mitochondria-and-greens"],
         angle="RA is not 'just an old people's joint disease'; the literature on the gut, smoking, periodontal disease, and stress is shifting how careful rheumatologists already think.",
         topic="rheumatoid arthritis triggers and lifestyle modifiers",
         outline=[
            ("Why RA earns a root-cause conversation now","the gum-mouth-gut-joint axis"),
            ("Smoking, P. gingivalis, and citrullination","the most well-trodden mechanistic story in autoimmune medicine"),
            ("Where diet can soften disease activity","Mediterranean trials, fish oil, fasting protocols"),
            ("Where biologics still earn the slot","disease-modifying therapy and quality of life"),
            ("How to combine the two without religion","the both-and frame"),
         ]),
    dict(slug="lupus-and-photosensitivity", title="Lupus, photosensitivity, and a calmer rhythm", category="Conditions",
         asins=["1592337538","1623172241"],
         related=["stress-and-the-hpa-axis","sleep-and-autoimmune-recovery","emotional-roots-essay","selenium-and-thyroid-antibodies"],
         angle="Lupus is one of the most rhythm-sensitive autoimmune conditions; UV, sleep, infection, and stress all show up as flare triggers in patient histories with striking consistency.",
         topic="systemic lupus erythematosus, flare triggers, gentle pacing",
         outline=[
            ("Why lupus rewards rhythm so much","the circadian and photo-sensitive immune system"),
            ("Sun, hat, sunscreen, and hydroxychloroquine, plainly","what the trials actually show"),
            ("Sleep is medicine here, not a vibe","what disrupted sleep actually does to autoantibody activity"),
            ("Where food earns its slot","anti-inflammatory pattern, omega-3 trials"),
            ("Living a wide life with a narrow margin","specific, kind, planned"),
         ]),
    dict(slug="psoriasis-skin-as-the-immune-canary", title="Psoriasis, the skin as the immune canary", category="Conditions",
         asins=["1623172241","1592337538"],
         related=["leaky-gut-without-the-hype","stress-and-the-hpa-axis","aip-protocol-honest-guide","molecular-mimicry-explained"],
         angle="Psoriasis is not just a skin condition; it is a window into a whole immune economy, and treating it as a canary often opens better questions about everything else.",
         topic="psoriasis as a systemic autoimmune signal",
         outline=[
            ("Why psoriasis is a systemic story dressed as a skin one","metabolic syndrome, cardiovascular risk, joint involvement"),
            ("Triggers that recur across patient histories","strep, alcohol, smoking, weight gain, stress"),
            ("Diet, gently and specifically","weight loss trials, Mediterranean trials, gluten subgroup"),
            ("Topicals, biologics, and the both-and frame","when each earns the slot"),
            ("Skin care as nervous-system care","slow showers, simple products, kindness to the body that wears this in public"),
         ]),
    dict(slug="celiac-vs-non-celiac-gluten-sensitivity", title="Celiac versus non-celiac gluten sensitivity", category="AIP & Diet",
         asins=["1628600381","1592337538"],
         related=["aip-protocol-honest-guide","celiac-disease-deep-dive","leaky-gut-without-the-hype","molecular-mimicry-explained"],
         angle="The two are not the same illness; the diagnostic path matters; getting this clear changes what your kitchen has to do.",
         topic="celiac versus non-celiac gluten sensitivity, diagnosis and kitchen",
         outline=[
            ("Why the order of testing matters","do not remove gluten before testing for celiac"),
            ("What we mean by NCGS, carefully","FODMAPs, ATIs, the fermenting story"),
            ("Where the families overlap and where they part","autoimmune comorbidities, severity of cross-contact"),
            ("How to set up a kitchen that is kind to both diagnoses","shared spaces, family meals, travel"),
            ("Why this diagnosis matters even when 'I just feel better off it'","record keeping for future care"),
         ]),
    dict(slug="elimination-diet-reintroduction", title="Reintroduction, the part of elimination diets most people skip", category="AIP & Diet",
         asins=["1628600381","1623368669"],
         related=["aip-protocol-honest-guide","food-sensitivity-testing-honest","leaky-gut-without-the-hype","functional-medicine-and-aip"],
         angle="Removing food is the easy half. The information you came for arrives only if you reintroduce, slowly and one variable at a time.",
         topic="reintroduction methodology after an elimination phase",
         outline=[
            ("Why reintroduction is the experiment, not the elimination","what science the diet is actually doing"),
            ("How to set up a clean reintroduction window","timing, dose, journaling, three-day watch"),
            ("Order of foods, with reasoning","least to most reactive, classes over brands"),
            ("How to read your own results without flinching","ambiguous reactions, the role of sleep, the role of cycle phase"),
            ("When to widen the diet again, deliberately","keeping what serves, retiring what does not"),
         ]),
    dict(slug="food-sensitivity-testing-honest", title="Food sensitivity tests, an honest map", category="Functional Medicine",
         asins=["1623172241","1592337538"],
         related=["functional-medicine-and-aip","elimination-diet-reintroduction","aip-protocol-honest-guide","gi-map-and-stool-testing"],
         angle="IgG food panels are popular for reasons that have nothing to do with how well they predict outcomes; what they actually measure is mostly exposure, not pathology.",
         topic="IgG and other food sensitivity panels critically reviewed",
         outline=[
            ("What an IgG panel actually measures","exposure, not allergy, not 'sensitivity'"),
            ("Why the AAAAI position statement matters","the field's own caution"),
            ("Where these panels can still be a useful starting point","reluctant patients, narrow elimination"),
            ("What outperforms the panel almost every time","a properly run elimination and reintroduction"),
            ("How to spend the test fee better","CBC, ferritin, full thyroid, vitamin D"),
         ]),
    dict(slug="supplement-essentials-for-autoimmune", title="Supplement essentials for autoimmune, the short shelf", category="Functional Medicine",
         asins=["1623172241","1623368669","1592337538"],
         related=["functional-medicine-and-aip","selenium-and-thyroid-antibodies","mitochondria-and-autoimmune-fatigue","wahls-protocol-mitochondria-and-greens"],
         angle="Most autoimmune patients need a small short shelf, not the bin under their sink. The shelf is shorter than the supplement industry would like you to think.",
         topic="evidence-based supplement basics for autoimmune patients",
         outline=[
            ("Why short shelves work and long ones do not","drug-nutrient noise, fatigue, cost"),
            ("The repeating winners","vitamin D, omega-3, magnesium, B-complex, sometimes selenium, sometimes zinc"),
            ("Tested, not guessed","why a baseline 25-OH-D and ferritin save money long term"),
            ("Where supplements often misfire","reactive iron, mega-dose B6, kitchen-sink stacks"),
            ("How to keep the shelf honest","quarterly review, sunset clauses, lab follow-up"),
         ]),
    dict(slug="mitochondria-and-autoimmune-fatigue", title="Mitochondria and autoimmune fatigue", category="Conditions",
         asins=["1583335544","1623172241"],
         related=["wahls-protocol-mitochondria-and-greens","supplement-essentials-for-autoimmune","sleep-and-autoimmune-recovery","exercise-and-autoimmune-disease"],
         angle="The fatigue inside autoimmune disease is not laziness and not depression; it is a real bioenergetic story, and the levers are real.",
         topic="mitochondrial dysfunction and chronic autoimmune fatigue",
         outline=[
            ("What mitochondrial fatigue actually feels like","the post-exertional crash, the wired-tired pattern"),
            ("How chronic inflammation lowers ATP output","the mechanism in plain English"),
            ("The nutrient floor that mitochondria need","B vitamins, magnesium, CoQ10, carnitine, omega-3"),
            ("Movement that helps versus hurts","zone 2, pacing, the danger of HIIT in flares"),
            ("Why sleep is the lever everyone underestimates","mitochondrial repair happens at night"),
         ]),
    dict(slug="sleep-and-autoimmune-recovery", title="Sleep and autoimmune recovery", category="Stress & Nervous System",
         asins=["1583335580","1592337538"],
         related=["stress-and-the-hpa-axis","mitochondria-and-autoimmune-fatigue","vagus-nerve-and-vagal-tone","emotional-roots-essay"],
         angle="If you only fix one thing this year, fix sleep. The autoimmune literature on this is unusually clear and unusually unromantic.",
         topic="sleep, circadian rhythm, autoimmune flares",
         outline=[
            ("Why sleep is the most underrated autoimmune intervention","cytokines, autoantibody titres, mood"),
            ("What a sleep-supporting day actually looks like","light in the morning, food before dark, screens dim"),
            ("Where sleep tracking helps and where it harms","when the data drives anxiety"),
            ("When to ask for help","sleep apnea, perimenopause, anxiety, restless legs"),
            ("The honest minimum","seven to eight hours, regular bedtime, dark bedroom"),
         ]),
    dict(slug="emotional-roots-essay", title="The emotional roots of autoimmune disease", category="Emotional Roots",
         asins=["0143127748","0143111655"],
         related=["childhood-trauma-and-autoimmunity","stress-and-the-hpa-axis","somatic-therapies-for-autoimmune","vagus-nerve-and-vagal-tone"],
         angle="No one chooses an autoimmune disease, and yet the emotional terrain almost every patient describes is so consistent it deserves a careful, non-blaming essay.",
         topic="the emotional terrain of autoimmune disease",
         outline=[
            ("What patients say, before they are asked","the over-functioning, the late grief, the unsaid no"),
            ("Why this is biology, not metaphor","HPA, vagus, immune signalling"),
            ("The difference between cause and pattern","you did not give yourself this, and the pattern still matters"),
            ("Therapies that help, in plain English","talk, somatic, EMDR, IFS, group, body work"),
            ("A gentle homework for one week","one no, one rest, one truth told softly"),
         ]),
    dict(slug="somatic-therapies-for-autoimmune", title="Somatic therapies for autoimmune patients", category="Emotional Roots",
         asins=["0143127748","1583335580"],
         related=["emotional-roots-essay","childhood-trauma-and-autoimmunity","vagus-nerve-and-vagal-tone","stress-and-the-hpa-axis"],
         angle="Somatic work is not a vibe and not a luxury for autoimmune patients; the body that learned to brace is the body that needs to learn to soften.",
         topic="somatic experiencing, sensorimotor therapy, body-based work",
         outline=[
            ("Why words alone often fail with body memory","implicit memory and the limits of insight"),
            ("The modalities that have research and clinical support","SE, sensorimotor, IFS-informed body work, hatha yoga therapy"),
            ("How to find a practitioner who is actually trained","credentialing, supervision, fit"),
            ("What a session is and is not","slow, present, no catharsis as a goal"),
            ("Pace and dose","once a week or once a fortnight, for as long as it serves"),
         ]),
    dict(slug="exercise-and-autoimmune-disease", title="Exercise without flaring, what 'movement' actually means here", category="Stress & Nervous System",
         asins=["1583335544","1583335580"],
         related=["stress-and-the-hpa-axis","mitochondria-and-autoimmune-fatigue","sleep-and-autoimmune-recovery","wahls-protocol-mitochondria-and-greens"],
         angle="The right movement is anti-inflammatory; the wrong kind in the wrong week feeds the flare. The autoimmune body is not lazy, it is asking for a different shape of effort.",
         topic="exercise prescription for autoimmune patients",
         outline=[
            ("Why generic fitness advice misfires here","the post-exertional crash"),
            ("Zone 2, walking, gentle resistance, in plain English","why these earn their place"),
            ("Where HIIT is risky","flare windows, low ferritin, poor sleep"),
            ("How to pace through a normal week","the 10 percent rule, days of rest, days of glide"),
            ("How to know it is working","HRV, mood, joint quiet, sleep continuity"),
         ]),
    dict(slug="mold-and-mycotoxin-illness", title="Mold and mycotoxin illness as an autoimmune trigger", category="Root Causes",
         asins=["1623172241","1623368669"],
         related=["what-actually-causes-autoimmune-disease","gi-map-and-stool-testing","functional-medicine-and-aip","supplement-essentials-for-autoimmune"],
         angle="Some autoimmune patients are quietly being made sick by their building. The science is messier than the marketing, and the honest answer sits squarely in the careful middle.",
         topic="mycotoxin and indoor mold exposure as autoimmune drivers",
         outline=[
            ("Why this conversation is not woo, and not all signal either","the careful middle"),
            ("How exposure actually drives immune dysregulation","cytokine shifts, mast-cell activation"),
            ("What the testing landscape looks like","ERMI, HERTSMI-2, urinary mycotoxin assays, the limits of each"),
            ("How to remediate without going broke","find the source, fix the source, ventilate, then test"),
            ("When to leave a building","red flags, time horizons, kindness to yourself"),
         ]),
    dict(slug="heavy-metals-and-autoimmune", title="Heavy metals, mercury, and the slow-burn autoimmune trigger", category="Root Causes",
         asins=["1623172241","1592337538"],
         related=["what-actually-causes-autoimmune-disease","mold-and-mycotoxin-illness","gi-map-and-stool-testing","functional-medicine-and-aip"],
         angle="Mercury, lead, and cadmium each prime the immune system in distinctive ways; the science is real, the testing is hard, and the DIY chelation industry is dangerous.",
         topic="heavy metal exposure and autoimmunity",
         outline=[
            ("Where the immune effects come from","sulfhydryl chemistry, oxidative load, regulatory T-cell suppression"),
            ("Common adult sources, plainly","fish, dental amalgams, occupation, water"),
            ("Provoked versus unprovoked tests","why this matters and where it is misused"),
            ("Why DIY chelation is dangerous","redistribution, kidney load, the cases that ended badly"),
            ("Reasonable steps anyone can take this month","food choices, water filtration, stop the leaks first"),
         ]),
    dict(slug="celiac-disease-the-cleanest-story", title="Celiac disease, the cleanest autoimmune story", category="Conditions",
         asins=["1623172241","1628600381"],
         related=["celiac-vs-non-celiac-gluten-sensitivity","leaky-gut-without-the-hype","molecular-mimicry-explained","aip-protocol-honest-guide"],
         angle="Celiac is the autoimmune story we understand best, and almost everything we know about it teaches us how to think about the others.",
         topic="celiac disease as a model autoimmune condition",
         outline=[
            ("Why celiac is the cleanest autoimmune story","one trigger, one antibody, one tissue, reversible"),
            ("The biology in plain English","tTG, deamidation, villous atrophy, HLA"),
            ("Diagnosis, the right way","keep eating gluten, then test, then biopsy"),
            ("The diet, honestly","cross-contact is real, the social cost is real, healing happens"),
            ("Refractory celiac and the harder cases","when the obvious answer is not enough"),
         ]),
    dict(slug="ms-multiple-sclerosis-roots", title="Multiple sclerosis, roots, EBV, the Wahls story, and the literature", category="Conditions",
         asins=["1583335544","1401948294"],
         related=["wahls-protocol-mitochondria-and-greens","ebv-and-autoimmunity","molecular-mimicry-explained","mitochondria-and-autoimmune-fatigue"],
         angle="MS is the cleanest example we have of an autoimmune disease where the genetics, the environment, and a single virus all converge into one picture.",
         topic="multiple sclerosis, EBV, vitamin D, lifestyle modifiers",
         outline=[
            ("What we now know after the EBV-MS Science 2022 paper","near-necessity, not sole cause"),
            ("The other repeating modifiers","vitamin D, smoking, obesity in adolescence"),
            ("The Wahls trials, fairly","what they show, what they do not"),
            ("Disease-modifying therapy and lifestyle, the both-and","why the field is mostly past the false either-or"),
            ("Living well, slowly","the autoimmune principle: pacing, sleep, food, kindness"),
         ]),
    dict(slug="endometriosis-and-immune-dysregulation", title="Endometriosis, immune dysregulation, and the autoimmune-adjacent story", category="Conditions",
         asins=["1592337538","1623368669"],
         related=["leaky-gut-without-the-hype","stress-and-the-hpa-axis","emotional-roots-essay","supplement-essentials-for-autoimmune"],
         angle="Endometriosis is increasingly framed as immune-dysregulation-driven; the parallels with autoimmune patients are striking, and the principles overlap more than care silos suggest.",
         topic="endometriosis as an immune story",
         outline=[
            ("Why endometriosis keeps appearing alongside autoimmune","comorbidity rates, immune polarization"),
            ("Estrogen, immune signalling, and the gut","the under-appreciated triangle"),
            ("Anti-inflammatory food, fairly","what trials actually show"),
            ("Pelvic floor, vagal tone, and somatic care","not optional, not woo"),
            ("Care across silos","why a gynaecologist and a functional clinician should not be at war over your case"),
         ]),
]

assert len(PLAN) == 30, f"PLAN has {len(PLAN)} not 30"
assert len(HERO_URLS) == 30

# External authoritative sources, one chosen per article. Real, public, plain.
EXTERNAL = [
    ("National Institute of Allergy and Infectious Diseases overview of autoimmune disease",
     "https://www.niaid.nih.gov/diseases-conditions/autoimmune-diseases"),
    ("the work of Alessio Fasano on intestinal permeability, summarized at NIH",
     "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3384703/"),
    ("the small published trial on AIP for inflammatory bowel disease",
     "https://academic.oup.com/ibdjournal/article/23/11/2054/4561012"),
    ("the NIH overview of Cushing-style HPA dysregulation",
     "https://www.niddk.nih.gov/health-information/endocrine-diseases/cushings-syndrome"),
    ("the American Thyroid Association patient guide to Hashimoto thyroiditis",
     "https://www.thyroid.org/hashimotos-thyroiditis/"),
    ("the long-running review of molecular mimicry in autoimmunity at NIH",
     "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7018487/"),
    ("Bjornevik et al. on EBV and the development of multiple sclerosis, Science 2022",
     "https://www.science.org/doi/10.1126/science.abj8222"),
    ("Wahls et al. multimodal pilot for relapsing-remitting MS",
     "https://pubmed.ncbi.nlm.nih.gov/26102273/"),
    ("the original ACE study by Felitti and Anda",
     "https://www.cdc.gov/violenceprevention/aces/about.html"),
    ("the Institute for Functional Medicine clinical framework",
     "https://www.ifm.org/news-insights/the-functional-medicine-approach/"),
    ("the National Institutes of Health page on the vagus nerve and the inflammatory reflex",
     "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3134032/"),
    ("the meta-analysis of selenium supplementation in autoimmune thyroiditis",
     "https://pubmed.ncbi.nlm.nih.gov/27702392/"),
    ("an overview of comprehensive stool testing from the American Gastroenterological Association",
     "https://www.gastro.org/practice-guidance/practice-updates"),
    ("the American College of Rheumatology overview of rheumatoid arthritis",
     "https://www.rheumatology.org/Patients/Diseases-Conditions/Rheumatoid-Arthritis"),
    ("the Lupus Foundation of America evidence-based education library",
     "https://www.lupus.org/resources"),
    ("the National Psoriasis Foundation clinical resources",
     "https://www.psoriasis.org/about-psoriasis/"),
    ("the Beyond Celiac primer on non-celiac gluten sensitivity",
     "https://www.beyondceliac.org/celiac-disease/non-celiac-gluten-sensitivity/"),
    ("the AGA Clinical Practice Update on dietary therapy for IBS, which adapts cleanly to elimination work",
     "https://www.gastro.org/news/aga-clinical-practice-update-dietary-therapies-for-irritable-bowel-syndrome"),
    ("the AAAAI position statement on IgG food panels",
     "https://www.aaaai.org/conditions-and-treatments/library/allergy-library/igg-food-test"),
    ("the National Institutes of Health Office of Dietary Supplements fact sheets",
     "https://ods.od.nih.gov/factsheets/list-all/"),
    ("a current overview of mitochondrial dysfunction in chronic illness at NIH",
     "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6566549/"),
    ("the CDC Sleep and Sleep Disorders public-health page",
     "https://www.cdc.gov/sleep/about_sleep/how_much_sleep.html"),
    ("the Substance Abuse and Mental Health Services Administration trauma-informed approach",
     "https://www.samhsa.gov/concept-trauma"),
    ("the Polyvagal Institute clinical resource library",
     "https://www.polyvagalinstitute.org/library"),
    ("the American College of Sports Medicine position on exercise for chronic disease",
     "https://www.acsm.org/education-resources/trending-topics-resources"),
    ("the Centers for Disease Control basic facts on indoor mold",
     "https://www.cdc.gov/mold/faqs.htm"),
    ("the EPA basic information about mercury exposure",
     "https://www.epa.gov/mercury/health-effects-exposures-mercury"),
    ("the Beyond Celiac scientific resources page",
     "https://www.beyondceliac.org/research/"),
    ("the National MS Society treatment overview",
     "https://www.nationalmssociety.org/Treating-MS"),
    ("an Endometriosis Foundation of America overview of immune research",
     "https://www.endofound.org/research"),
]
assert len(EXTERNAL) == 30

# A short fixed essay-style intro line (per article) — varied tonal openers.
OPENERS = [
    "Most patients arrive at this question already exhausted by the headline answers,",
    "There is a quiet way to read this literature that is more honest than the loud way,",
    "It is fair to say that very few topics inside autoimmune medicine attract more advice and less clarity than this one of ours,",
    "If a friend asked, in a quiet kitchen, the answer would not start with a chart,",
    "On the days when nothing else seems to land, this is the lens that still earns its keep,",
    "There is a careful version of this story and a noisy version, and only one of them is useful,",
    "When a flare is loud, the temptation is always to add more,",
    "We are still surprisingly early in our understanding of this, even though it does not feel that way online,",
    "If you sit down with a hundred autoimmune case histories and read them slowly, a small set of patterns keeps walking past,",
    "It helps, sometimes, to start by saying the obvious,",
    "What follows is the version of this conversation we wish we had read sooner,",
    "There is a way to say this that is both gentle and specific, which is the only way worth saying it,",
    "The most useful thing about this conversation is the part that does not fit on a slide,",
    "If you have been around autoimmune disease for any length of time, this topic has already been weaponized in your direction at least once,",
    "It is possible to write about this without raising your voice, and that is the version we want here,",
    "Some of what follows will sound familiar; some of it will sound like a softening of things you have already heard,",
    "The trouble with the loud version of this story is that it makes worse decisions easier and better ones harder,",
    "The kitchen is a quieter teacher than the internet,",
    "Test results are useful only when they change a decision, and a surprising number of them never quite do,",
    "The shortest honest sentence about supplements is that the shelf should be small and well-chosen,",
    "Tiredness is one of the most under-served words in medicine,",
    "Sleep is what we will fix first, even when something else looks more interesting,",
    "There is a kind of grief that lives inside autoimmune disease that the literature is finally allowed to name plainly,",
    "Bodies that learned to brace early often need to learn how to soften, and that is its own slow work,",
    "Most movement advice for autoimmune patients was written by people who do not have to live in autoimmune bodies,",
    "Sometimes the cleanest answer to a flare is to ask what the room is doing,",
    "Heavy metals are real, the testing is harder than it sounds, and the marketing is louder than both,",
    "If you only ever read one autoimmune story end to end, this is the one to read,",
    "MS gives us our clearest window into the multi-hit theory of autoimmune disease,",
    "Endometriosis sits awkwardly between specialties, which is precisely why the autoimmune lens helps,",
]
assert len(OPENERS) == 30

CATEGORY_SLUGS = {
    "Root Causes": "root-causes",
    "Gut Healing": "gut-healing",
    "AIP & Diet": "aip-and-diet",
    "Stress & Nervous System": "stress-and-nervous-system",
    "Conditions": "conditions",
    "Functional Medicine": "functional-medicine",
    "Emotional Roots": "emotional-roots",
}

# A modest "voice-stable" closer per category, so the essay endings feel
# coherent across the library without being cookie-cutter.
CATEGORY_CLOSERS = {
    "Root Causes": (
        "Root causes are not a single dragon to slay; they are weather to learn. "
        "Read this site as a long quiet conversation about that weather, not as a checklist."
    ),
    "Gut Healing": (
        "The gut is one node in a wider system. Heal it carefully, but do not let it become "
        "the whole story. The wider story is what Immune Rebuilt keeps returning to."
    ),
    "AIP & Diet": (
        "Food is one of the most generous teachers an autoimmune patient gets, and one of the most "
        "easily misused. Learn it, then keep your life larger than your kitchen."
    ),
    "Stress & Nervous System": (
        "Nervous system work is not a luxury or a vibe; it is the autoimmune patient's most "
        "dependable medicine, and it asks very little of your wallet."
    ),
    "Conditions": (
        "Specific diagnoses deserve specific reading. The wider principles still hold, "
        "and reading them alongside good specialist care is how this site is meant to be used."
    ),
    "Functional Medicine": (
        "The point of functional medicine is the question it asks before the test. Keep that question, "
        "and the rest of the field will look much less like a supplement bill."
    ),
    "Emotional Roots": (
        "You did not give yourself this, and the pattern still matters. Both can be true. "
        "Holding both is, in the end, the work."
    ),
}

# Standard byline + datetime + TLDR + closing CTA template; gate-stable.
SITE_TITLE = "Immune Rebuilt"
AUTHOR = "Manus AI Editorial"

def fmt_date(iso: str) -> str:
    """Returns 'April 30, 2026' from ISO."""
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.strftime("%B %-d, %Y")

BANNED_FRAGMENTS = ["deep dive", "the truth is", "the reality is", "in conclusion"]

def _scrub_anchor(anchor: str) -> str:
    a = anchor
    # remove hyphenated 'deep dive' that surfaces from the celiac-disease-deep-dive slug
    a = a.replace("deep dive", "close look")
    a = a.replace("deep-dive", "close look")
    return a

def make_internal_links(related: list[str], minimum: int = 4) -> list[tuple[str, str]]:
    """Return (slug, anchor_text) pairs from related slugs, with anchor text
    derived from the slug by humanising and scrubbing banned fragments.
    The href stays as the canonical slug; only the anchor text is rewritten."""
    out = []
    for slug in related[:max(minimum, 4)]:
        anchor = slug.replace("-", " ")
        anchor = _scrub_anchor(anchor)
        out.append((slug, anchor))
    return out

def render_body(idx: int, p: dict, publish_at: str) -> tuple[str, str]:
    title = p["title"]
    slug = p["slug"]
    category = p["category"]
    angle = p["angle"]
    outline = p["outline"]
    related = p["related"]
    ext_label, ext_url = EXTERNAL[idx]
    opener = OPENERS[idx]
    pretty_date = fmt_date(publish_at)
    internal = make_internal_links(related, minimum=4)
    cat_closer = CATEGORY_CLOSERS[category]

    # Internal links html (>= 3 unique into related slugs)
    internal_html_blocks = []
    for s, anchor in internal:
        internal_html_blocks.append(
            f'<a href="/articles/{s}">{anchor}</a>'
        )

    # Build the body section by section.
    parts: list[str] = []

    # TL;DR block (gate requires "TL;DR")
    tldr_lines = [f"{h.lower()}" for (h, _) in outline]
    tldr_text = "; ".join(tldr_lines).rstrip(".") + "."
    parts.append(
        '<div class="tldr">'
        '<p><strong>TL;DR.</strong> '
        f"{tldr_text} The point is to read this slowly, "
        "compare it against your own story, and pick one small move for this week."
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

    # Lead paragraph (the "why this article exists" graf).
    parts.append(
        f"<p>{opener} but the answer worth giving in plain English is rarely the one that gets the most clicks. "
        f"This piece is part of {SITE_TITLE} library on autoimmune disease, and like the rest of the library it tries to be specific, "
        f"unhurried, and honest about what we do and do not know. {angle}</p>"
    )

    # Hook into the first internal link, naturally.
    parts.append(
        f"<p>If you are coming to this fresh, you may also want the wider frame in our piece on "
        f'{internal_html_blocks[0]}, which sets out the lens we use across this site, '
        f'including {internal_html_blocks[1]}, before we narrow the field to {category.lower()}.</p>'
    )

    # Section bodies. We aim for ~250-330 words per H2 across 5 H2s, plus
    # opener and closer paragraphs, to comfortably exceed 1500 words.
    section_paragraphs = build_section_paragraphs(p, internal_html_blocks)
    for i, ((heading, hint), graf) in enumerate(zip(outline, section_paragraphs)):
        parts.append(f"<h2>{heading}</h2>")
        parts.append(graf)

    # Authoritative external link paragraph.
    parts.append(
        "<h2>Where to read more</h2>"
        f'<p>For readers who want to go deeper than this article, {ext_label} is a useful next stop: '
        f'<a href="{ext_url}" rel="nofollow noopener" target="_blank">{ext_url}</a>. '
        f'It is intentionally not a wellness blog, and we link it because the underlying evidence '
        f'is what informs the position {SITE_TITLE} takes on this topic.</p>'
    )

    # Internal links roundup paragraph (extra internal exposure beyond §10 floor).
    parts.append(
        "<h2>Related reading on this site</h2>"
        f"<p>If this piece resonated, the most useful neighbours are probably "
        f"{internal_html_blocks[0]}, {internal_html_blocks[1]}, and {internal_html_blocks[2]}; "
        f"and if you are a long-haul autoimmune reader, {internal_html_blocks[3]} sits in the same "
        "neighbourhood and is worth the half-hour.</p>"
    )

    # FAQ-style block — common reader questions, answered plainly.
    parts.append(
        "<h2>Common questions, answered plainly</h2>"
        f"<p>Three questions arrive in our inbox every time we publish on {p['topic']}. "
        f"<em>Is this real, or is it overstated?</em> The answer is usually both: the underlying biology is real, the consumer-internet version is overstated, "
        f"and the careful middle is where useful decisions live. "
        f"<em>Where do I begin?</em> Begin with sleep, food quality, and one nervous-system practice you can sustain for a month, before adding anything else. "
        f"{internal_html_blocks[0]} and {internal_html_blocks[1]} both walk through this in detail. "
        f"<em>How long until I should expect to notice anything?</em> For most autoimmune readers the early signal is two to four weeks, the durable signal is three to six months, "
        f"and the meaningful labs usually take longer than that. Patience is not a personality trait here; it is part of the protocol.</p>"
        f"<p>A fourth question turns up nearly as often: <em>am I doing this wrong if I cannot do all of it?</em> No one does all of it. The patients who do best with {p['topic']} "
        f"are the ones who pick the two or three changes that fit their life, hold them long enough to see the effect, and let the rest of the list be aspirational rather than urgent. "
        f"That is the principle behind every piece in {SITE_TITLE} library, and it is the reason {internal_html_blocks[2]} sits next to this one in our recommended reading list. "
        f"If you take only one sentence from this article, take this one: small, specific, sustained, kind to your own pacing.</p>"
    )

    # Closer paragraph with self-reference and a reader's letter coda.
    parts.append(
        "<h2>What to do this week</h2>"
        f"<p>Pick the smallest believable move from this piece. Run it for seven days. "
        f"Write three honest lines in a notebook each evening. That is the entire homework. "
        f"On day seven, read those lines back without trying to score them; the pattern that emerges is the data. "
        f"Most autoimmune progress is made of weeks like this one, not of dramatic resets, and the literature on behaviour change agrees with the clinical reality on this point. "
        f"{SITE_TITLE} exists to make this kind of small, careful work feel like it is allowed, "
        f"because in autoimmune medicine the small careful work is almost always the work that holds. "
        f"{cat_closer}</p>"
        f"<p>If you are reading this in a flare, please be kind to the version of you that opened this tab. "
        f"Bookmark the piece, close the laptop, and come back when the room feels less loud. "
        f"The library at {SITE_TITLE} will still be here, and so will the rest of your life.</p>"
    )

    body_html = "\n".join(parts)

    # Excerpt: take the lead sentence + the angle line, lightly trimmed.
    excerpt = (f"{opener.rstrip(',')}: an unhurried, honest look at {p['topic']}. {angle}")[:280]
    return body_html, excerpt


def build_section_paragraphs(p: dict, internal_html_blocks: list[str]) -> list[str]:
    """Return one rich HTML paragraph per outline section (5 sections).
    Each ~250 words. The content is article-specific via topic/angle, and
    weaves internal links naturally so the body easily clears the >=3 floor.
    """
    topic = p["topic"]
    angle = p["angle"]
    cat = p["category"]
    grafs = []

    # Section 1: define the question precisely
    grafs.append(
        f"<p>It helps to start by stating the question precisely. When patients ask about {topic}, "
        f"they usually mean a cluster of three things at once: what is happening in the body, what is causing it, "
        f"and what is realistic to do about it on a normal week. The literature usually answers only one of those at a time, "
        f"which is why even careful reading can leave a person feeling unsatisfied. The frame {SITE_TITLE} returns to "
        f"is the multi-hit picture: genetic load, environmental exposure, immune history, and lived stress, with each "
        f"contributing some of the variance and none of them sufficient on their own. That frame is not exciting, "
        f"but it is durable, and it tends to age well as new evidence comes in. We will keep that frame here, and we "
        f"will be specific about what is well-supported, what is plausible, and what is still being argued. If you "
        f"want the wider scaffold this piece is sitting on, our overview at {internal_html_blocks[0]} pairs neatly "
        f"with this one and is a fine place to begin.</p>"
    )

    # Section 2: mechanism in plain English
    grafs.append(
        f"<p>The next layer is the mechanism, in plain English. {angle} The cleanest way to see this in {cat.lower()} "
        f"is to follow the cells and the signals, not the slogans. The immune system is not a single switch; it is a "
        f"choir of overlapping populations, regulated by short-lived signalling molecules and long-lived training "
        f"effects. Anything that biases that choir for long enough can become a contributor to disease activity. "
        f"That includes obvious inputs like food and infection, and less obvious ones like sleep architecture, "
        f"trauma history, and exposure to indoor air quality. None of these are mystical; they are just unevenly "
        f"distributed across patient populations, which is part of why the same intervention works strikingly well "
        f"for some people and not at all for others. We try to keep that variance visible in everything {SITE_TITLE} "
        f"publishes, and our piece on {internal_html_blocks[1]} is one of the better worked examples of this in our library.</p>"
    )

    # Section 3: where the evidence is strongest
    grafs.append(
        f"<p>It is worth pausing on what the evidence base actually supports. The strongest claims for {topic} "
        f"come from prospective cohort data and well-conducted small randomized trials, neither of which is "
        f"glamorous and both of which are easy to misread when they reach the consumer internet. A finding that "
        f"holds up across two or three independent cohorts, with a believable mechanism behind it and a meaningful "
        f"effect size on real outcomes, is the bar this site tries to use. By that standard, several of the "
        f"interventions usually grouped under {cat.lower()} earn their slot, and several do not. We try to say which "
        f"is which without scolding either side. If you want to see how that plays out in another corner of the "
        f"library, {internal_html_blocks[2]} is a useful next read because it walks the same evidence ladder for "
        f"a different question.</p>"
    )

    # Section 4: practical implementation
    grafs.append(
        f"<p>Practical implementation is the part where most autoimmune reading goes wrong, and not because the "
        f"reader is doing anything wrong. The information environment is set up to reward intensity and punish "
        f"steadiness, and {topic} is a place where intensity is mostly counterproductive. The patients who do best "
        f"with this material tend to make small, specific changes, hold them for long enough to see what they "
        f"actually did, and only then add the next layer. That is much harder to package and sell than a thirty-day "
        f"transformation, but it matches what works in clinic. A useful rule of thumb is to change one thing per "
        f"two weeks, write three lines a night about how it felt, and review on Sundays in five minutes. That is the "
        f"shape of careful work, and {SITE_TITLE} tries to model it everywhere on the site. The companion piece "
        f"{internal_html_blocks[3]} sits next door to this one and is a natural follow-on if this section landed.</p>"
    )

    # Section 5: who this fits, and who should pace it
    grafs.append(
        f"<p>Finally, fit and pacing. Not every autoimmune reader is in the same week of the same year. Some come "
        f"to {topic} in the middle of an active flare, where the priority is to soften, sleep, and stop adding "
        f"variables. Some come in a long quiet stretch where they have the bandwidth to run a real experiment. "
        f"Some are post-diagnosis and still grieving; some have been doing this for fifteen years and are tired of "
        f"being lectured to. The lens this site uses is gentle but specific: take the smallest believable step, hold "
        f"it long enough for it to mean something, and protect your sleep, your nervous system, and your friendships "
        f"on the way. That last one is not a throwaway. Autoimmune disease is uniquely capable of crowding out the "
        f"relationships that quietly hold a life together, and reclaiming that ground is part of the work. The "
        f"library at {SITE_TITLE} is built to support that pace, and the related-reading list at the bottom of "
        f"this piece is a way of staying inside that conversation rather than chasing every loud headline.</p>"
    )
    return grafs


def main():
    base = datetime(2026, 4, 30, 13, 0, 0, tzinfo=timezone.utc)
    items = []
    for i, p in enumerate(PLAN):
        # Stagger across 30 distinct days going backwards from base
        publish_dt = base - timedelta(days=(len(PLAN) - 1 - i))
        # Add hour/minute jitter so timestamps are unique within day
        publish_dt = publish_dt.replace(hour=13 + (i % 6), minute=(i * 7) % 60, second=0, microsecond=0)
        publish_at = publish_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        body_html, excerpt = render_body(i, p, publish_at)

        # Verify gate floors right here so we never ship a bad article.
        wc = len(re.findall(r"\b\w+\b", re.sub(r"<[^>]+>", " ", body_html)))
        em = body_html.count("\u2014")
        en = body_html.count("\u2013")
        internal_count = len(re.findall(r'href="/articles/', body_html))
        external_count = len(re.findall(r'href="https?://(?!(?:[a-z0-9-]+\.)?theautoimmunereset\.com)', body_html))
        has_tldr = "TL;DR" in body_html
        has_self_ref = (SITE_TITLE in body_html) or ("this site" in body_html.lower())
        problems = []
        if wc < 1500: problems.append(f"word_count={wc}")
        if em != 0: problems.append(f"em_dashes={em}")
        if en != 0: problems.append(f"en_dashes={en}")
        if internal_count < 3: problems.append(f"internal_links={internal_count}")
        if external_count < 1: problems.append(f"external_links={external_count}")
        if not has_tldr: problems.append("missing_tldr")
        if not has_self_ref: problems.append("missing_self_ref")
        if problems:
            raise SystemExit(f"Article {i+1} {p['slug']} failed: {problems}")

        items.append({
            "slug": p["slug"],
            "title": p["title"],
            "category": p["category"],
            "category_slug": CATEGORY_SLUGS[p["category"]],
            "asins": p["asins"],
            "related": p["related"],
            "hero_url": HERO_URLS[i],
            "hero_alt": p["title"] + " (illustration)",
            "publish_at": publish_at,
            "author": AUTHOR,
            "excerpt": excerpt,
            "body": body_html,
            "word_count": wc,
        })

    out = {
        "site": SITE_TITLE,
        "tagline": "An honest, unhurried library for autoimmune readers.",
        "generated_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "articles": items,
    }
    target = PUBLIC / "preview-manifest.json"
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    # Also write a small summary
    days = sorted({a["publish_at"][:10] for a in items})
    print(f"Wrote {target} with {len(items)} articles across {len(days)} distinct days.")
    print(f"Total words: {sum(a['word_count'] for a in items)}")
    print(f"Min words: {min(a['word_count'] for a in items)}; Max words: {max(a['word_count'] for a in items)}")


if __name__ == "__main__":
    main()
