/**
 * Apothecary: 50 carefully chosen items across supplements, herbs, and TCM.
 * All Amazon links use tag=spankyspinola-20.
 *
 * Affiliate disclosure: Immune Rebuilt is a participant in the Amazon Services
 * LLC Associates Program. As an Amazon Associate we earn from qualifying
 * purchases. This earns us a small commission at no extra cost to you.
 */
export type Family = "Supplement" | "Herb" | "TCM" | "Adaptogen" | "Topical";
export type Item = {
  asin: string;
  title: string;
  brand: string;
  family: Family;
  category: string; // e.g., "Gut barrier", "Mitochondria", "Vagal tone"
  whyHere: string; // one sentence on why we list it
  bestFor: string; // who tends to benefit
  warning?: string; // honest caveat
  internalSlug?: string; // article that goes deeper
};

const T = "spankyspinola-20";
export const amazonUrl = (asin: string) => `https://www.amazon.com/dp/${asin}?tag=${T}`;

export const APOTHECARY: Item[] = [
  // --- GUT BARRIER (8) ---
  { asin: "B00E9M4XEE", title: "L-Glutamine powder, unflavored", brand: "Pure Encapsulations", family: "Supplement", category: "Gut barrier", whyHere: "The most studied amino acid for enterocyte fuel and tight-junction support.", bestFor: "Active leaky-gut symptoms", internalSlug: "leaky-gut-without-the-hype" },
  { asin: "B0013OXKHC", title: "Slippery elm bark powder", brand: "Starwest Botanicals", family: "Herb", category: "Gut barrier", whyHere: "A demulcent mucilage that coats irritated mucosa.", bestFor: "Reflux, IBS-style discomfort", internalSlug: "leaky-gut-without-the-hype" },
  { asin: "B000Z960OG", title: "DGL deglycyrrhizinated licorice chewable", brand: "Enzymatic Therapy", family: "Herb", category: "Gut barrier", whyHere: "Soothes gastric mucosa without raising blood pressure.", bestFor: "Reflux, gastritis", warning: "Avoid full-glycyrrhizin licorice if you have hypertension.", internalSlug: "leaky-gut-without-the-hype" },
  { asin: "B000Z90QBG", title: "Marshmallow root capsules", brand: "Nature's Way", family: "Herb", category: "Gut barrier", whyHere: "Demulcent, gentle, complements slippery elm.", bestFor: "Dry-mouth, dry-throat, irritated gut" },
  { asin: "B07MD8VQ57", title: "Aloe vera inner-leaf juice, decolorized", brand: "Lily of the Desert", family: "Herb", category: "Gut barrier", whyHere: "Decolorized aloe avoids the laxative anthraquinones.", bestFor: "Inflamed gut lining", warning: "Do not use whole-leaf aloe long term." },
  { asin: "B00CQ7TX4A", title: "Zinc carnosine 75 mg", brand: "PepZin GI / Doctor's Best", family: "Supplement", category: "Gut barrier", whyHere: "The form with the strongest mucosal-healing evidence.", bestFor: "Gastric ulcer history, NSAID gut", internalSlug: "leaky-gut-without-the-hype" },
  { asin: "B0013OXBMS", title: "Saccharomyces boulardii capsules", brand: "Jarrow Formulas", family: "Supplement", category: "Gut barrier", whyHere: "A non-colonizing yeast that supports the gut lining and limits opportunistic species.", bestFor: "Post-antibiotic, traveler's diarrhea history" },
  { asin: "B07F7CRQ22", title: "Bone broth protein, unflavored", brand: "Ancient Nutrition", family: "Supplement", category: "Gut barrier", whyHere: "Concentrated collagen and amino acids for connective tissue and gut lining.", bestFor: "AIP and post-AIP rebuild" },

  // --- MITOCHONDRIA / FATIGUE (7) ---
  { asin: "B003B3OM7G", title: "Ubiquinol CoQ10 100 mg", brand: "Jarrow Formulas", family: "Supplement", category: "Mitochondria", whyHere: "Reduced form, better absorbed than ubiquinone in older adults.", bestFor: "Fatigue, statin users, mitochondrial-load conditions", internalSlug: "mitochondria-and-autoimmune-fatigue" },
  { asin: "B00F6TZJ48", title: "Acetyl-L-carnitine 500 mg", brand: "Jarrow Formulas", family: "Supplement", category: "Mitochondria", whyHere: "Carrier of fatty acids into mitochondria; the acetyl form crosses the blood-brain barrier.", bestFor: "Brain fog, neuropathy, fatigue", warning: "Avoid in untreated hypothyroidism without a clinician." },
  { asin: "B00B79G42S", title: "PQQ 20 mg", brand: "Doctor's Best", family: "Supplement", category: "Mitochondria", whyHere: "Promotes mitochondrial biogenesis in human trials.", bestFor: "Stubborn fatigue", internalSlug: "mitochondria-and-autoimmune-fatigue" },
  { asin: "B00H8YQDG4", title: "Magnesium glycinate 400 mg", brand: "Doctor's Best", family: "Supplement", category: "Mitochondria", whyHere: "The most consistently tolerated form for sleep and ATP cofactor needs.", bestFor: "Sleep, muscle tension, almost everyone", internalSlug: "supplement-essentials-for-autoimmune" },
  { asin: "B00U7HBC8G", title: "Methylated B-complex", brand: "Pure Encapsulations B-Complex Plus", family: "Supplement", category: "Mitochondria", whyHere: "Active forms (methylfolate, methylcobalamin, P-5-P) for known MTHFR variants.", bestFor: "Suspected methylation issues" },
  { asin: "B00CBAFRH6", title: "D-ribose powder", brand: "NOW Foods", family: "Supplement", category: "Mitochondria", whyHere: "Pentose sugar used in ATP regeneration; helpful in chronic fatigue and fibromyalgia.", bestFor: "Post-exertional malaise" },
  { asin: "B000I4FMP8", title: "Alpha-lipoic acid 600 mg", brand: "Doctor's Best", family: "Supplement", category: "Mitochondria", whyHere: "Recycles glutathione, supports nerve health.", bestFor: "Diabetic-style neuropathy, oxidative load" },

  // --- THYROID / SELENIUM (4) ---
  { asin: "B0019LRY8A", title: "Selenium L-selenomethionine 200 mcg", brand: "Pure Encapsulations", family: "Supplement", category: "Thyroid", whyHere: "Two trials show TPO antibody reduction in Hashimoto's at this dose.", bestFor: "Confirmed Hashimoto's", warning: "Ceiling 400 mcg/day; selenium toxicity is real.", internalSlug: "selenium-iodine-and-hashimotos" },
  { asin: "B003L17QO6", title: "Liquid iodine, low dose", brand: "Pure Encapsulations", family: "Supplement", category: "Thyroid", whyHere: "Useful only when intake is genuinely low; risky in autoimmune thyroiditis if dose is high.", bestFor: "Vegan diets, low-salt diets", warning: "Do not exceed 150 mcg/day in Hashimoto's without a clinician." },
  { asin: "B0013OXC1S", title: "Ashwagandha KSM-66 600 mg", brand: "Sports Research", family: "Adaptogen", category: "Thyroid", whyHere: "Small trials show modest TSH and T3 improvement in subclinical hypothyroid.", bestFor: "Stress-driven thyroid dysregulation", warning: "Caution in hyperthyroid presentations." },
  { asin: "B07MQF2X6P", title: "Tyrosine 500 mg", brand: "NOW Foods", family: "Supplement", category: "Thyroid", whyHere: "A precursor amino acid for thyroid hormone synthesis.", bestFor: "Hypothyroid presentations after a blood-test conversation" },

  // --- VITAMIN D / IMMUNE BASELINE (5) ---
  { asin: "B003L1IRGI", title: "Vitamin D3 5000 IU + K2 MK-7", brand: "Sports Research", family: "Supplement", category: "Immune baseline", whyHere: "K2 directs calcium to bone away from arteries; 5000 IU is the most-studied autoimmune dose.", bestFor: "Confirmed low 25-OH-D, autoimmune diagnosis", warning: "Test before dosing; ceiling 10,000 IU/day except under clinician.", internalSlug: "supplement-essentials-for-autoimmune" },
  { asin: "B07GJTPKWY", title: "Cod liver oil, fermented unflavored", brand: "Rosita", family: "Supplement", category: "Immune baseline", whyHere: "Whole-food vitamin A and D in their natural ratio.", bestFor: "Old-school immune support, dry skin" },
  { asin: "B00CQ7VGNM", title: "Omega-3 EPA/DHA, triglyceride form", brand: "Nordic Naturals Ultimate Omega", family: "Supplement", category: "Immune baseline", whyHere: "TG-form is better absorbed than ethyl ester; resolution of inflammation literature.", bestFor: "Almost everyone with autoimmune disease" },
  { asin: "B07PLP9MPB", title: "Curcumin phytosome (Meriva) 500 mg", brand: "Thorne", family: "Supplement", category: "Immune baseline", whyHere: "Phytosome form is 30x more bioavailable than ordinary curcumin.", bestFor: "Joint inflammation, RA presentations", internalSlug: "rheumatoid-arthritis-real-talk" },
  { asin: "B00JEKYNZA", title: "Quercetin 500 mg", brand: "Thorne", family: "Supplement", category: "Immune baseline", whyHere: "Mast-cell stabilizer with histamine-modulating effects.", bestFor: "Itching, hives, IgE-flavored autoimmune presentations", internalSlug: "igg-food-sensitivity-tests-honestly" },

  // --- HERBS / ADAPTOGENS (8) ---
  { asin: "B07FSR3YV2", title: "Reishi mushroom extract 1000 mg", brand: "Real Mushrooms", family: "TCM", category: "Adaptogen", whyHere: "TCM 'shen tonic'; modulates Th1/Th2 balance in cell-line studies.", bestFor: "Chronic stress, sleep, Th2-dominant presentations" },
  { asin: "B07FYCB1ND", title: "Cordyceps militaris extract", brand: "Real Mushrooms", family: "TCM", category: "Adaptogen", whyHere: "Energy and stamina support, modest evidence for VO2max.", bestFor: "Fatigue, athletic recovery" },
  { asin: "B00U2DXDWU", title: "Rhodiola rosea standardized 500 mg", brand: "Gaia Herbs", family: "Adaptogen", category: "Adaptogen", whyHere: "Best-studied adaptogen for stress-related fatigue.", bestFor: "HPA dysregulation, low motivation", warning: "Stimulating; take in the morning." },
  { asin: "B00HC4M1RM", title: "Holy basil (tulsi) 600 mg", brand: "Banyan Botanicals", family: "Herb", category: "Adaptogen", whyHere: "Ayurvedic adaptogen with cortisol-modulating evidence.", bestFor: "Anxiety, blood-sugar swings" },
  { asin: "B07T8FW4KG", title: "Mucuna pruriens (L-DOPA) 600 mg", brand: "Gaia Herbs", family: "Herb", category: "Adaptogen", whyHere: "Natural L-DOPA precursor used in Ayurveda for mood and motivation.", bestFor: "Low motivation paired with chronic stress" },
  { asin: "B07GC3M2QM", title: "Triphala powder", brand: "Banyan Botanicals", family: "Herb", category: "Digestion", whyHere: "Three-fruit Ayurvedic digestive tonic; gentle and well-tolerated.", bestFor: "Sluggish digestion" },
  { asin: "B00OVO5TZU", title: "Berberine 500 mg", brand: "Thorne", family: "Herb", category: "Microbiome", whyHere: "Antimicrobial action against opportunistic gut species; insulin-sensitizer.", bestFor: "Suspected SIBO, dysbiosis, insulin resistance", warning: "Avoid in pregnancy; can drop blood sugar.", internalSlug: "gi-map-and-stool-testing" },
  { asin: "B07J6S96SX", title: "Astragalus root 1000 mg", brand: "Nature's Answer", family: "TCM", category: "Adaptogen", whyHere: "TCM 'wei qi' tonic; supports Th1 immunity.", bestFor: "Frequent infections, post-viral fatigue" },

  // --- VAGAL / SLEEP / NERVOUS SYSTEM (6) ---
  { asin: "B00H2T4G5K", title: "Magnesium glycinate evening dose", brand: "Klean Athlete", family: "Supplement", category: "Nervous system", whyHere: "Glycine + magnesium = parasympathetic priming for sleep.", bestFor: "Sleep, anxiety", internalSlug: "vagus-nerve-and-the-anti-inflammatory-reflex" },
  { asin: "B00W5DZJN6", title: "L-theanine 200 mg", brand: "Suntheanine / NOW", family: "Supplement", category: "Nervous system", whyHere: "Increases alpha-wave EEG activity, gentle anxiolysis without sedation.", bestFor: "Daytime stress, anxious presentations" },
  { asin: "B07K2ZGN2C", title: "Melatonin 0.3 mg, low-dose", brand: "Life Extension", family: "Supplement", category: "Nervous system", whyHere: "Low physiologic dose; high-dose melatonin is rarely better and often worse.", bestFor: "Jet lag, intermittent sleep", warning: "Avoid in autoimmune thyroid without a clinician.", internalSlug: "sleep-as-the-quietest-anti-inflammatory" },
  { asin: "B00U2DXEDU", title: "Apigenin 50 mg", brand: "Double Wood", family: "Supplement", category: "Nervous system", whyHere: "Chamomile-derived; mild GABAergic action.", bestFor: "Sleep onset" },
  { asin: "B0013OXEPM", title: "Passionflower extract", brand: "Gaia Herbs", family: "Herb", category: "Nervous system", whyHere: "Modulates GABA, evidence for situational anxiety.", bestFor: "Racing-mind insomnia" },
  { asin: "B07V47CHPP", title: "Hawthorn berry capsules", brand: "Gaia Herbs", family: "Herb", category: "Nervous system", whyHere: "Cardiovascular tonic with mild parasympathetic effect.", bestFor: "Resting-heart-rate driven by stress" },

  // --- TOPICAL / DETOX (6) ---
  { asin: "B00ESCBCQU", title: "Magnesium chloride flakes for foot soaks", brand: "Ancient Minerals", family: "Topical", category: "Nervous system", whyHere: "Transdermal magnesium for evening parasympathetic priming.", bestFor: "Sleep, sore muscles" },
  { asin: "B07LFVVJLT", title: "Castor oil cold-pressed in glass", brand: "Heritage Store", family: "Topical", category: "Liver / lymph", whyHere: "Castor packs are an old-school lymph and gallbladder tool.", bestFor: "Right-upper-quadrant fullness, lymphatic stagnation" },
  { asin: "B07TGZHQHP", title: "Bentonite clay (food grade)", brand: "Redmond", family: "Supplement", category: "Detox", whyHere: "Binds bile and certain mycotoxins in the gut.", bestFor: "Suspected mold exposure", warning: "Avoid within 2 hours of medications.", internalSlug: "mold-and-mycotoxin-illness" },
  { asin: "B0013OQGDC", title: "Activated charcoal capsules", brand: "Bulk Supplements", family: "Supplement", category: "Detox", whyHere: "Acute binder for occasional GI distress; not a daily tool.", bestFor: "Food poisoning, occasional bloat", warning: "Will bind medications too." },
  { asin: "B00F1F4G46", title: "N-acetyl cysteine 600 mg", brand: "Jarrow Formulas", family: "Supplement", category: "Detox", whyHere: "Glutathione precursor; supports phase II liver detox.", bestFor: "Oxidative stress, mucus, mold-related presentations" },
  { asin: "B005GHBC52", title: "Milk thistle 175 mg silymarin", brand: "Nature's Way", family: "Herb", category: "Detox", whyHere: "Hepatoprotective in NAFLD and chemical-load contexts.", bestFor: "Sluggish liver presentations" },

  // --- WOMEN / HORMONES (3) ---
  { asin: "B07VL3JBZK", title: "Vitex (chasteberry) 400 mg", brand: "Gaia Herbs", family: "Herb", category: "Hormones", whyHere: "Pituitary-acting herb for luteal-phase support.", bestFor: "PMS, perimenopause cycle irregularity", internalSlug: "perimenopause-and-autoimmune-flares" },
  { asin: "B07KRYSG2R", title: "DIM 200 mg", brand: "Smoky Mountain Naturals", family: "Supplement", category: "Hormones", whyHere: "Indole-3-carbinol metabolite; supports estrogen detoxification.", bestFor: "Estrogen-dominant presentations" },
  { asin: "B07J9YL9SP", title: "Maca root 1000 mg", brand: "Healths Harmony", family: "Adaptogen", category: "Hormones", whyHere: "Andean adaptogen; gentle support for libido and vitality.", bestFor: "Perimenopause, libido" },

  // --- MEN / BLOOD SUGAR (3) ---
  { asin: "B0013HQH52", title: "Saw palmetto 320 mg", brand: "Doctor's Best", family: "Herb", category: "Men's", whyHere: "Standardized extract for prostate health.", bestFor: "Older men with urinary symptoms", internalSlug: "men-autoimmune-and-the-stories-we-skip" },
  { asin: "B07WRH2ZPF", title: "Inositol 2000 mg", brand: "Designs for Health", family: "Supplement", category: "Blood sugar", whyHere: "Insulin-sensitizing in PCOS and metabolic-syndrome contexts.", bestFor: "Insulin resistance" },
  { asin: "B07BTFPJYR", title: "Chromium picolinate 200 mcg", brand: "Pure Encapsulations", family: "Supplement", category: "Blood sugar", whyHere: "Modest evidence for fasting glucose support.", bestFor: "Borderline metabolic markers" },
];

export const FAMILIES: Family[] = ["Supplement", "Herb", "TCM", "Adaptogen", "Topical"];
export const CATEGORIES = Array.from(new Set(APOTHECARY.map((i) => i.category))).sort();
