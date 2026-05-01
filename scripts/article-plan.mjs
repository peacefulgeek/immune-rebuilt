// 30-article master plan for Immune Rebuilt.
// 10 already exist in the seed manifest (we'll regenerate them at length to ensure 1500+ words);
// 20 new ones are added across the same categories.

export const PLAN = [
  // === Already-seeded 10, kept (regenerated at length) ===
  { slug: "what-actually-causes-autoimmune-disease", title: "What actually causes autoimmune disease (and what does not)", category: "Root Causes",
    asins: ["1592337538","1623360382"], related: ["leaky-gut-without-the-hype","aip-protocol-honest-guide","stress-and-the-hpa-axis","molecular-mimicry-explained"],
    angle: "Three legs of the stool: genes, gut, trigger. Address the two you can.",
    cover: "Fasano's three-leg model; environmental triggers list; why suppression isn't healing; where to start.",
    hero: "Soft watercolor on warm cream paper: an open-air apothecary table with leaves, herbs, a glass of golden tea, dried chamomile, abstract DNA helix in pale jade." },

  { slug: "leaky-gut-without-the-hype", title: "Leaky gut, without the hype, without the dismissal", category: "Gut Healing",
    asins: ["1465482067","1592337538"], related: ["what-actually-causes-autoimmune-disease","aip-protocol-honest-guide","molecular-mimicry-explained","stress-and-the-hpa-axis"],
    angle: "Zonulin is real; the wellness internet oversold it; here's what the research actually shows.",
    cover: "Tight junctions, zonulin, what loosens them, what closes them; bone broth and the slower repair work.",
    hero: "Watercolor cross-section illustration of intestinal villi with golden tight-junction protein bands, soft sage and warm peach tones, no harsh red, light cream background." },

  { slug: "aip-protocol-honest-guide", title: "An honest guide to the autoimmune protocol (AIP)", category: "AIP & Diet",
    asins: ["1628600381","1628602473"], related: ["leaky-gut-without-the-hype","what-actually-causes-autoimmune-disease","stress-and-the-hpa-axis","functional-medicine-and-aip"],
    angle: "AIP is a 30-90 day diagnostic, not a forever diet. The real value is the reintroduction phase.",
    cover: "Sarah Ballantyne; what's removed; the diagnostic value of reintroduction; common failure modes.",
    hero: "Soft watercolor still-life: a wooden cutting board with a roasted sweet potato, leafy greens, herbs, bone broth in a ceramic mug, all painted in warm cream and sage tones." },

  { slug: "stress-and-the-hpa-axis", title: "The stress no one in the appointment ever asks about", category: "Stress & Nervous System",
    asins: ["0393706095","1583335580"], related: ["childhood-trauma-and-autoimmunity","leaky-gut-without-the-hype","what-actually-causes-autoimmune-disease","vagus-nerve-and-vagal-tone"],
    angle: "Chronic HPA activation is the most underrated driver of autoimmune flares.",
    cover: "Cortisol, Th17 polarization, secretory IgA suppression, sleep fragmentation, ACE study, polyvagal.",
    hero: "Watercolor of a person in soft morning light, hand on chest, eyes closed, by a window with sheer linen curtains, tea cup steaming, warm cream and pale jade palette." },

  { slug: "hashimotos-thyroid-and-the-autoimmune-mosaic", title: "Hashimoto's, the thyroid, and the autoimmune mosaic", category: "Conditions",
    asins: ["0985690437","0985690402"], related: ["aip-protocol-honest-guide","leaky-gut-without-the-hype","ebv-and-autoimmunity","selenium-and-thyroid-antibodies"],
    angle: "Replacing the hormone treats the smoke. Lowering antibodies treats the fire.",
    cover: "TPO and TG antibodies; iodine and selenium; the real Hashimoto's panel; gluten and transglutaminase.",
    hero: "Watercolor illustration of a thyroid butterfly silhouette overlaid on a watercolor wash of warm dawn light, soft golds and sage, no clinical sterility." },

  { slug: "molecular-mimicry-explained", title: "Molecular mimicry: why your immune system mistakes you for something foreign", category: "Root Causes",
    asins: ["1623172241","1592337538"], related: ["ebv-and-autoimmunity","leaky-gut-without-the-hype","what-actually-causes-autoimmune-disease","hashimotos-thyroid-and-the-autoimmune-mosaic"],
    angle: "Shared peptide shapes between pathogens and self-tissue; the cleanest mechanistic story.",
    cover: "Strep + RHD, EBV + MS, gluten + transglutaminase + thyroid; Vojdani's cross-reactivity work.",
    hero: "Watercolor abstract: two interlocking peptide chains in soft amber and forest green, like keys fitting locks, on a warm cream paper background, calming and clear." },

  { slug: "ebv-and-autoimmunity", title: "Epstein-Barr Virus and autoimmunity: the connection that became impossible to ignore", category: "Root Causes",
    asins: ["1401948294"], related: ["molecular-mimicry-explained","stress-and-the-hpa-axis","what-actually-causes-autoimmune-disease","hashimotos-thyroid-and-the-autoimmune-mosaic"],
    angle: "The 2022 Ascherio Science paper made the EBV-MS link nearly inarguable. Implications widening.",
    cover: "EBV biology; reactivation; B-cells; Hashimoto's, lupus, RA, Sjogren's; what to do without an antiviral.",
    hero: "Watercolor of a microscope on an old wood desk surrounded by pressed leaves and a steaming mug, warm afternoon light, gold and forest tones." },

  { slug: "wahls-protocol-mitochondria-and-greens", title: "The Wahls Protocol: mitochondria, greens, and a clinician who got out of her wheelchair", category: "AIP & Diet",
    asins: ["1583335544","1583335214"], related: ["aip-protocol-honest-guide","what-actually-causes-autoimmune-disease","leaky-gut-without-the-hype","mitochondria-and-autoimmune-fatigue"],
    angle: "Nine cups of vegetables a day, around the cofactor needs of mitochondria. The trial evidence followed.",
    cover: "The Wahls food groups; trial data; how it overlaps with AIP; the limits of diet alone.",
    hero: "Watercolor still life of a wooden bowl overflowing with leafy greens, deeply colored vegetables (beets, carrots, blueberries), liver pâté, sardines on a plate, all in soft warm light." },

  { slug: "childhood-trauma-and-autoimmunity", title: "Childhood trauma and autoimmunity: what the ACE studies have been quietly telling us", category: "Emotional Roots",
    asins: ["1476755183","0143127748"], related: ["stress-and-the-hpa-axis","vagus-nerve-and-vagal-tone","emotional-roots-essay","somatic-therapies-for-autoimmune"],
    angle: "Felitti and Anda's ACE study set the dose-response. The body holds the score in the immune system.",
    cover: "ACE mechanism; cortisol calibration in childhood; Nakazawa, Maté, van der Kolk; trauma-informed therapies.",
    hero: "Watercolor of a child's drawing pinned to a sunlit kitchen window, soft amber light, abstract suggestion of being held, no faces visible." },

  { slug: "functional-medicine-and-aip", title: "What a functional-medicine appointment actually looks like (and when it is worth the money)", category: "Functional Medicine",
    asins: ["1623368669","1623172241"], related: ["aip-protocol-honest-guide","stress-and-the-hpa-axis","leaky-gut-without-the-hype","gi-map-and-stool-testing"],
    angle: "The good version is the lab-driven root-cause appointment medicine no longer has time for. The bad is supplement sales.",
    cover: "What a real intake looks like; IFM directory; red flags; the labs that matter; pairing with rheum/endo.",
    hero: "Watercolor of a clinician's wooden desk: lab printouts, a steaming herbal tea, a fountain pen, a small jade plant, warm afternoon light." },

  // === New 20 ===
  { slug: "vagus-nerve-and-vagal-tone", title: "The vagus nerve, vagal tone, and why your exhale is medicine", category: "Stress & Nervous System",
    asins: ["0393706095","0143127748"], related: ["stress-and-the-hpa-axis","childhood-trauma-and-autoimmunity","somatic-therapies-for-autoimmune","sleep-and-autoimmune-recovery"],
    angle: "Polyvagal theory in plain language, with the daily practices that actually move HRV.",
    cover: "Stephen Porges; ventral vagal vs dorsal; HRV; cold-water-on-face; humming; long exhales; daily protocol.",
    hero: "Watercolor of a person breathing slowly by a window with houseplants, sun on shoulders, a small handwritten breath count card on the table." },

  { slug: "selenium-and-thyroid-antibodies", title: "Selenium, the most under-prescribed nutrient in Hashimoto's", category: "Conditions",
    asins: ["0985690437","0985690402"], related: ["hashimotos-thyroid-and-the-autoimmune-mosaic","supplement-essentials-for-autoimmune","aip-protocol-honest-guide","gi-map-and-stool-testing"],
    angle: "Selenium 200mcg/day modestly but consistently lowers TPO antibodies in trials; here's the case.",
    cover: "Selenium biology; trial data; brazil nuts vs supplements; iodine pairing; cautions.",
    hero: "Watercolor of brazil nuts, a small ceramic dish of selenomethionine capsules, dried herbs, all in warm cream and forest tones." },

  { slug: "gi-map-and-stool-testing", title: "GI MAP and stool testing for autoimmune patients: what is worth running and what is hype", category: "Functional Medicine",
    asins: ["1465482067","1592337538"], related: ["leaky-gut-without-the-hype","functional-medicine-and-aip","supplement-essentials-for-autoimmune","food-sensitivity-testing-honest"],
    angle: "Honest tour of comprehensive stool tests, what they find, what they miss, when they're worth $400.",
    cover: "GI MAP, GI Effects, calprotectin, secretory IgA, zonulin, dysbiosis markers; how clinicians use them.",
    hero: "Watercolor still life of a clinician's lab order form, a glass of warm tea, a notebook with anatomical drawings of the gut, soft sage and amber tones." },

  { slug: "rheumatoid-arthritis-root-causes", title: "Rheumatoid arthritis: what triggers the joint attack, and where the gut comes in", category: "Conditions",
    asins: ["1592337538","1628600381"], related: ["leaky-gut-without-the-hype","aip-protocol-honest-guide","what-actually-causes-autoimmune-disease","emotional-roots-essay"],
    angle: "RA's root-cause map: gut bacteria, citrullinated antigens, smoking, periodontitis, stress.",
    cover: "Anti-CCP; Prevotella copri; periodontitis; smoking; AIP for RA; meds + roots together.",
    hero: "Watercolor of two open hands held gently in warm light, painted with restraint and tenderness, no medical imagery, suggesting healing without selling." },

  { slug: "lupus-and-photosensitivity", title: "Lupus, photosensitivity, and the immune system that struggles with daylight", category: "Conditions",
    asins: ["1623368669","1592337538"], related: ["what-actually-causes-autoimmune-disease","leaky-gut-without-the-hype","stress-and-the-hpa-axis","emotional-roots-essay"],
    angle: "Why lupus patients flare in sunlight; the role of NETs, EBV, vitamin D paradox, gut.",
    cover: "Photosensitivity mechanism; NETosis; EBV; vitamin D; stress; pacing; AIP overlap.",
    hero: "Watercolor of a sunhat and linen wrap on a porch chair, dappled afternoon light, ferns, no medical motifs, soft cream and lavender tones." },

  { slug: "psoriasis-skin-as-the-immune-canary", title: "Psoriasis: the skin as the canary for the immune system", category: "Conditions",
    asins: ["1592337538","1628600381"], related: ["leaky-gut-without-the-hype","aip-protocol-honest-guide","gi-map-and-stool-testing","stress-and-the-hpa-axis"],
    angle: "Psoriasis as systemic inflammation visible on skin; gut-skin axis; the IL-17/Th17 story.",
    cover: "Skin barrier; gut-skin axis; alcohol; dysbiosis; AIP for skin; meds + roots together.",
    hero: "Watercolor of a soft hand cream jar, dried calendula petals, a folded linen towel, warm bath light, no clinical or distressing imagery." },

  { slug: "celiac-vs-non-celiac-gluten-sensitivity", title: "Celiac, non-celiac gluten sensitivity, and the autoimmune patient who doesn't know yet", category: "AIP & Diet",
    asins: ["1623172241","1628600381"], related: ["leaky-gut-without-the-hype","molecular-mimicry-explained","aip-protocol-honest-guide","hashimotos-thyroid-and-the-autoimmune-mosaic"],
    angle: "Celiac vs NCGS in plain English; why testing must be done while still eating gluten; cross-reactivity.",
    cover: "tTG-IgA, EMA, biopsy gold standard; NCGS criteria; gluten-thyroid cross-reactivity; reintroduction lessons.",
    hero: "Watercolor of an empty wooden bread basket, fresh greens, a sliced apple, warm linen napkin, sun-soaked and gentle." },

  { slug: "elimination-diet-reintroduction", title: "Reintroduction is where the diagnostic actually lives", category: "AIP & Diet",
    asins: ["1628600381","1628602473"], related: ["aip-protocol-honest-guide","celiac-vs-non-celiac-gluten-sensitivity","food-sensitivity-testing-honest","gi-map-and-stool-testing"],
    angle: "Most people never finish the reintroduction phase; here's how to do it so you actually learn something.",
    cover: "Order of reintroductions; window length; symptom tracking; the trickier ones (eggs, nightshades, nuts).",
    hero: "Watercolor of a small leather notebook on a kitchen counter with one tomato, a roasted egg, almonds in a dish, warm light, gentle composition." },

  { slug: "food-sensitivity-testing-honest", title: "Food-sensitivity blood tests, IgG panels, and what they actually tell you", category: "Functional Medicine",
    asins: ["1623172241","1623368669"], related: ["elimination-diet-reintroduction","gi-map-and-stool-testing","aip-protocol-honest-guide","functional-medicine-and-aip"],
    angle: "IgG food panels are not allergy tests. Here's what the science actually says, and how to use them anyway.",
    cover: "IgG vs IgE; the AAAAI position; Cyrex panels; pattern reading; better than nothing, worse than elimination.",
    hero: "Watercolor of a small lab vial held in warm sunlight, a journal, a fountain pen, dried chamomile sprigs, painted with restraint." },

  { slug: "supplement-essentials-for-autoimmune", title: "The five supplements that earn their place in autoimmune recovery", category: "Functional Medicine",
    asins: ["1623368669","1583335580"], related: ["selenium-and-thyroid-antibodies","leaky-gut-without-the-hype","stress-and-the-hpa-axis","mitochondria-and-autoimmune-fatigue"],
    angle: "Vitamin D, omega-3s, magnesium, selenium, glutamine, in that order — when they help, when they don't.",
    cover: "Each supplement: mechanism; dose ranges; cautions; what to test before; what 'good' looks like.",
    hero: "Watercolor still life of glass jars on a wood shelf with handwritten labels, soft afternoon sun, no garish brand imagery." },

  { slug: "mitochondria-and-autoimmune-fatigue", title: "Mitochondrial fatigue and the autoimmune body that runs out of charge by 2pm", category: "Conditions",
    asins: ["1583335544","1583335214"], related: ["wahls-protocol-mitochondria-and-greens","supplement-essentials-for-autoimmune","stress-and-the-hpa-axis","sleep-and-autoimmune-recovery"],
    angle: "Why autoimmune fatigue is mitochondrial as much as inflammatory, and what nutrient density actually fixes.",
    cover: "ATP biology; B-vitamins, CoQ10, carnitine; the Wahls overlap; pacing; not 'pushing through'.",
    hero: "Watercolor abstract: glowing amber droplets like little suns inside a leaf-shaped vessel, sage and gold tones, calming and warm." },

  { slug: "sleep-and-autoimmune-recovery", title: "Sleep is when the immune system finishes the day's work", category: "Stress & Nervous System",
    asins: ["0143127748","1583335580"], related: ["stress-and-the-hpa-axis","mitochondria-and-autoimmune-fatigue","vagus-nerve-and-vagal-tone","supplement-essentials-for-autoimmune"],
    angle: "Slow-wave sleep is when glymphatic and immune housekeeping happens; fragmenting it is fragmenting the recovery.",
    cover: "Sleep architecture; light hygiene; alcohol cost; cortisol curve; magnesium glycinate; bedroom basics.",
    hero: "Watercolor of a bed with rumpled white linen by a window with first morning light, a book and tea on the nightstand, warm cream and dawn-rose tones." },

  { slug: "emotional-roots-essay", title: "The emotional roots of autoimmunity: not blame, biology", category: "Emotional Roots",
    asins: ["1476755183","0143127748"], related: ["childhood-trauma-and-autoimmunity","stress-and-the-hpa-axis","somatic-therapies-for-autoimmune","vagus-nerve-and-vagal-tone"],
    angle: "What people mean when they talk about 'emotional roots'; why it's not woo; and where the boundary is.",
    cover: "Maté's framework; ACE biology; the spiritual-bypass trap; why this needs trauma therapy not affirmations.",
    hero: "Watercolor of a journal with a pressed flower, candle, hand-thrown ceramic mug, soft golden hour light, painted with patience and care." },

  { slug: "somatic-therapies-for-autoimmune", title: "Somatic therapies for autoimmune patients: EMDR, SE, IFS, trauma-informed yoga", category: "Emotional Roots",
    asins: ["0143127748","0393706095"], related: ["childhood-trauma-and-autoimmunity","emotional-roots-essay","vagus-nerve-and-vagal-tone","stress-and-the-hpa-axis"],
    angle: "The therapies with the best evidence for body-stored trauma, and how to choose between them.",
    cover: "EMDR mechanism; Levine's SE; IFS parts work; trauma-informed yoga; how to find a clinician.",
    hero: "Watercolor of a yoga mat unrolled by a window, a cushion, a small green plant, soft early-morning light, no athletic bravado." },

  { slug: "exercise-and-autoimmune-disease", title: "Exercise without flaring: what 'movement' actually means for autoimmune bodies", category: "Stress & Nervous System",
    asins: ["1583335544","1583335580"], related: ["stress-and-the-hpa-axis","mitochondria-and-autoimmune-fatigue","sleep-and-autoimmune-recovery","wahls-protocol-mitochondria-and-greens"],
    angle: "The right kind of movement is anti-inflammatory; the wrong kind in the wrong week feeds the flare.",
    cover: "Walking, zone 2, gentle resistance, why HIIT is risky in flares, pacing, post-exertional malaise.",
    hero: "Watercolor of a person walking on a forest path with morning light through trees, soft greens and amber, no athletic gear, calm." },

  { slug: "mold-and-mycotoxin-illness", title: "Mold and mycotoxin illness as an autoimmune trigger", category: "Root Causes",
    asins: ["1623172241","1623368669"], related: ["what-actually-causes-autoimmune-disease","gi-map-and-stool-testing","functional-medicine-and-aip","supplement-essentials-for-autoimmune"],
    angle: "Why some autoimmune patients are quietly being made sick by their building, and how to test it.",
    cover: "CIRS basics; ERMI; urinary mycotoxin tests; binders; when to leave the building; controversies.",
    hero: "Watercolor of an old wooden window frame with sunlight pouring in, a green plant on the sill, fresh air motion suggested by curtains, gentle and not alarming." },

  { slug: "heavy-metals-and-autoimmune", title: "Heavy metals, mercury, and the slow-burn autoimmune trigger", category: "Root Causes",
    asins: ["1623172241","1592337538"], related: ["what-actually-causes-autoimmune-disease","mold-and-mycotoxin-illness","gi-map-and-stool-testing","functional-medicine-and-aip"],
    angle: "Mercury, lead, cadmium and how they prime the immune system; the science is real, the testing is hard.",
    cover: "Sources; provoked vs unprovoked tests; safe chelation principles; why DIY chelation is dangerous.",
    hero: "Watercolor abstract of clean rainwater pouring through stone over moss, soft greens and silver light, suggesting careful clearing." },

  { slug: "celiac-disease-deep-dive", title: "Celiac disease, the gold-standard autoimmune story", category: "Conditions",
    asins: ["1623172241","1628600381"], related: ["celiac-vs-non-celiac-gluten-sensitivity","leaky-gut-without-the-hype","molecular-mimicry-explained","aip-protocol-honest-guide"],
    angle: "Celiac is the cleanest autoimmune story we have. What it teaches every other autoimmune patient.",
    cover: "tTG biology; villous atrophy; the dapsone-DH connection; the strict-gluten-free reality; refractory celiac.",
    hero: "Watercolor of a wheat stalk crossed out with a pale ribbon, beside a basket of fresh vegetables and a bowl of buckwheat porridge, warm cream tones." },

  { slug: "ms-multiple-sclerosis-roots", title: "Multiple sclerosis: roots, EBV, the Wahls story, and what the literature shows", category: "Conditions",
    asins: ["1583335544","1401948294"], related: ["wahls-protocol-mitochondria-and-greens","ebv-and-autoimmunity","molecular-mimicry-explained","mitochondria-and-autoimmune-fatigue"],
    angle: "MS as the cleanest example of EBV + genetics + environment converging; the diet evidence; pacing.",
    cover: "EBV-MS Science 2022 paper; vitamin D; smoking; obesity; Wahls trials; gentle hopeful tone.",
    hero: "Watercolor of soft sunlight through autumn leaves on a forest floor, gentle path, no medical motifs, calm." },

  { slug: "endometriosis-and-immune-dysregulation", title: "Endometriosis, immune dysregulation, and the autoimmune-adjacent story", category: "Conditions",
    asins: ["1592337538","1623368669"], related: ["leaky-gut-without-the-hype","stress-and-the-hpa-axis","emotional-roots-essay","supplement-essentials-for-autoimmune"],
    angle: "Endometriosis is increasingly framed as immune-dysregulation-driven; the parallels with autoimmune are striking.",
    cover: "Estrogen, immune polarization, gut microbiome, anti-inflammatory food, somatic care; pacing.",
    hero: "Watercolor of a soft heating pad on a couch, a herbal tea, dried red raspberry leaf, warm rose-and-cream tones, gentle." }
];

// Helper: dates for staggered publish_at — distinct days, oldest -> newest, last 30 days.
export function planDates(count = PLAN.length, baseISO = "2026-04-30T13:00:00.000Z") {
  const base = new Date(baseISO).getTime();
  const dayMs = 24 * 60 * 60 * 1000;
  const out = [];
  // Spread across 30 distinct days going back from base
  for (let i = 0; i < count; i++) {
    const d = new Date(base - (count - 1 - i) * dayMs);
    // Shift the hour slightly so each item has a unique timestamp inside its day
    d.setUTCHours(13 + (i % 6));
    d.setUTCMinutes((i * 7) % 60);
    out.push(d.toISOString());
  }
  return out;
}
