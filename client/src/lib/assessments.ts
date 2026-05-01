/**
 * Eleven self-screen instruments most relevant to autoimmune patients.
 * Adapted from the public, widely-cited research instruments. None of these
 * replace clinical evaluation. Each one returns a numeric score, a band, and
 * a short next-step paragraph plus 2-3 internal article links.
 *
 * Source notes are inlined per assessment with the original author and a link
 * to the canonical reference. We keep adaptations minimal and conservative.
 */
export type Choice = { label: string; value: number };
export type Question = { id: string; text: string; choices: Choice[] };
export type Band = { min: number; max: number; label: string; copy: string; readNext: string[] };

export type Assessment = {
  slug: string;
  title: string;
  short: string;
  authorAttribution: string;
  source: string;
  about: string;
  questions: Question[];
  bands: Band[];
};

const yesNo: Choice[] = [
  { label: "Not at all", value: 0 },
  { label: "A little", value: 1 },
  { label: "Often", value: 2 },
  { label: "Very often", value: 3 },
];

const phqChoices: Choice[] = [
  { label: "Not at all", value: 0 },
  { label: "Several days", value: 1 },
  { label: "More than half the days", value: 2 },
  { label: "Nearly every day", value: 3 },
];

export const ASSESSMENTS: Assessment[] = [
  {
    slug: "phq-9-mood",
    title: "PHQ-9 — Mood and depression screen",
    short: "Nine-item self-rating used in primary care to gauge depressive symptoms over the last two weeks.",
    authorAttribution: "Kroenke, Spitzer & Williams (2001), public domain",
    source: "https://www.phqscreeners.com/",
    about: "Autoimmune patients carry above-average rates of depression. This is the most widely validated brief screen used in primary care. It is not a diagnosis. A high score means a conversation with a clinician is wise.",
    questions: [
      { id: "1", text: "Little interest or pleasure in doing things", choices: phqChoices },
      { id: "2", text: "Feeling down, depressed, or hopeless", choices: phqChoices },
      { id: "3", text: "Trouble falling or staying asleep, or sleeping too much", choices: phqChoices },
      { id: "4", text: "Feeling tired or having little energy", choices: phqChoices },
      { id: "5", text: "Poor appetite or overeating", choices: phqChoices },
      { id: "6", text: "Feeling bad about yourself or that you have let yourself or your family down", choices: phqChoices },
      { id: "7", text: "Trouble concentrating on things, such as reading the newspaper or watching television", choices: phqChoices },
      { id: "8", text: "Moving or speaking so slowly that other people could have noticed, or the opposite, being so fidgety or restless", choices: phqChoices },
      { id: "9", text: "Thoughts that you would be better off dead or of hurting yourself in some way", choices: phqChoices },
    ],
    bands: [
      { min: 0, max: 4, label: "Minimal", copy: "Symptoms are not in the clinical range right now. The score still earns its keep as a baseline you can revisit during a flare or a stressful month.", readNext: ["the-emotional-roots-of-autoimmune-disease", "trauma-and-the-immune-system", "stress-the-hpa-axis-and-flare-risk"] },
      { min: 5, max: 9, label: "Mild", copy: "A mild range. Sleep, light, movement, and a steady kitchen often move this needle. If the score persists for more than a couple of weeks, talk to a clinician you trust.", readNext: ["sleep-as-the-quietest-anti-inflammatory", "stress-the-hpa-axis-and-flare-risk", "the-emotional-roots-of-autoimmune-disease"] },
      { min: 10, max: 14, label: "Moderate", copy: "A moderate range. This is the range where most clinical guidelines recommend a formal evaluation. Bring this score to a primary care visit.", readNext: ["the-emotional-roots-of-autoimmune-disease", "trauma-and-the-immune-system", "somatic-practices-for-the-nervous-system"] },
      { min: 15, max: 19, label: "Moderately severe", copy: "A moderately severe range. Please reach out to a clinician within the week. If question 9 is anything above zero, please call 988 (US) or your local crisis line now.", readNext: ["trauma-and-the-immune-system", "the-emotional-roots-of-autoimmune-disease", "somatic-practices-for-the-nervous-system"] },
      { min: 20, max: 27, label: "Severe", copy: "A severe range. Please reach out to a clinician now. If you are having thoughts of self-harm, call 988 (US) or your local crisis line right now.", readNext: ["the-emotional-roots-of-autoimmune-disease", "trauma-and-the-immune-system", "somatic-practices-for-the-nervous-system"] },
    ],
  },
  {
    slug: "gad-7-anxiety",
    title: "GAD-7 — Anxiety screen",
    short: "Seven-item self-rating, the standard brief measure of generalized anxiety symptoms.",
    authorAttribution: "Spitzer, Kroenke, Williams & Lowe (2006), public domain",
    source: "https://www.phqscreeners.com/select-screener",
    about: "Anxiety and autoimmune flares often track each other through HPA-axis activation. This score is a starting line for a conversation, not a label.",
    questions: [
      { id: "1", text: "Feeling nervous, anxious, or on edge", choices: phqChoices },
      { id: "2", text: "Not being able to stop or control worrying", choices: phqChoices },
      { id: "3", text: "Worrying too much about different things", choices: phqChoices },
      { id: "4", text: "Trouble relaxing", choices: phqChoices },
      { id: "5", text: "Being so restless that it is hard to sit still", choices: phqChoices },
      { id: "6", text: "Becoming easily annoyed or irritable", choices: phqChoices },
      { id: "7", text: "Feeling afraid as if something awful might happen", choices: phqChoices },
    ],
    bands: [
      { min: 0, max: 4, label: "Minimal", copy: "Below the clinical screen threshold. Keep an eye on it during flares.", readNext: ["stress-the-hpa-axis-and-flare-risk", "vagus-nerve-and-the-anti-inflammatory-reflex", "sleep-as-the-quietest-anti-inflammatory"] },
      { min: 5, max: 9, label: "Mild", copy: "A mild range. Vagal-tone work, breathwork, and consistent sleep are the lowest-risk first steps.", readNext: ["vagus-nerve-and-the-anti-inflammatory-reflex", "stress-the-hpa-axis-and-flare-risk", "somatic-practices-for-the-nervous-system"] },
      { min: 10, max: 14, label: "Moderate", copy: "A moderate range. This is the threshold at which formal evaluation is usually recommended.", readNext: ["the-emotional-roots-of-autoimmune-disease", "vagus-nerve-and-the-anti-inflammatory-reflex", "trauma-and-the-immune-system"] },
      { min: 15, max: 21, label: "Severe", copy: "A severe range. Please reach out to a clinician this week.", readNext: ["the-emotional-roots-of-autoimmune-disease", "trauma-and-the-immune-system", "somatic-practices-for-the-nervous-system"] },
    ],
  },
  {
    slug: "iss-symptom-severity",
    title: "Inflammatory Symptom Snapshot",
    short: "A ten-item self-snapshot of the symptoms most often reported by autoimmune patients in the four weeks before a flare.",
    authorAttribution: "Adapted by Immune Rebuilt from the literature on autoimmune symptom reporting",
    source: "https://immunerebuilt.com/articles/what-actually-causes-autoimmune-disease",
    about: "This is not a validated instrument; it is a structured way to take your own pulse before a clinic visit so the conversation is more useful.",
    questions: [
      { id: "1", text: "Joint pain or stiffness lasting more than 30 minutes after waking", choices: yesNo },
      { id: "2", text: "Skin rash, hives, or unexplained itching", choices: yesNo },
      { id: "3", text: "Brain fog, word-finding trouble, or unusual fatigue after meals", choices: yesNo },
      { id: "4", text: "GI symptoms: bloating, loose stools, or new food sensitivities", choices: yesNo },
      { id: "5", text: "Hair shedding above what you consider normal", choices: yesNo },
      { id: "6", text: "Cold hands and feet, Raynaud-style colour changes", choices: yesNo },
      { id: "7", text: "Sleep that does not refresh, even at 7-8 hours", choices: yesNo },
      { id: "8", text: "Mouth ulcers, dry eyes, or dry mouth", choices: yesNo },
      { id: "9", text: "Brief low-grade fevers without obvious infection", choices: yesNo },
      { id: "10", text: "Feeling worse the day after light exercise", choices: yesNo },
    ],
    bands: [
      { min: 0, max: 6, label: "Quiet", copy: "Symptoms are quiet right now. A monthly snapshot is a good idea so trends become visible early.", readNext: ["what-actually-causes-autoimmune-disease", "leaky-gut-without-the-hype", "supplement-essentials-for-autoimmune"] },
      { min: 7, max: 14, label: "Murmuring", copy: "Symptoms are murmuring. Often the first lever is sleep, then food, then nervous system. Then re-check in two weeks.", readNext: ["aip-protocol-honest-guide", "stress-the-hpa-axis-and-flare-risk", "leaky-gut-without-the-hype"] },
      { min: 15, max: 22, label: "Loud", copy: "Symptoms are loud. Bring this snapshot to a clinician in the next two weeks. Avoid overhauling everything at once.", readNext: ["aip-protocol-honest-guide", "molecular-mimicry-explained", "functional-medicine-and-aip"] },
      { min: 23, max: 30, label: "Flare", copy: "This pattern fits a flare. Anchor the basics: sleep, fluid, gentle food, walking, breath. Get a clinician evaluation this week.", readNext: ["aip-protocol-honest-guide", "supplement-essentials-for-autoimmune", "functional-medicine-and-aip"] },
    ],
  },
  {
    slug: "epworth-sleepiness",
    title: "Epworth Sleepiness Scale",
    short: "Eight-item measure of daytime sleepiness, widely used in sleep medicine.",
    authorAttribution: "Murray Johns, MD (1991)",
    source: "https://epworthsleepinessscale.com/",
    about: "Daytime sleepiness is one of the most overlooked drivers of autoimmune fatigue. A high score is a sign to investigate sleep architecture, not just sleep duration.",
    questions: [
      { id: "1", text: "Sitting and reading", choices: [{label:"No chance",value:0},{label:"Slight chance",value:1},{label:"Moderate chance",value:2},{label:"High chance",value:3}] },
      { id: "2", text: "Watching television", choices: [{label:"No chance",value:0},{label:"Slight chance",value:1},{label:"Moderate chance",value:2},{label:"High chance",value:3}] },
      { id: "3", text: "Sitting inactive in a public place", choices: [{label:"No chance",value:0},{label:"Slight chance",value:1},{label:"Moderate chance",value:2},{label:"High chance",value:3}] },
      { id: "4", text: "As a passenger in a car for an hour without a break", choices: [{label:"No chance",value:0},{label:"Slight chance",value:1},{label:"Moderate chance",value:2},{label:"High chance",value:3}] },
      { id: "5", text: "Lying down to rest in the afternoon when circumstances permit", choices: [{label:"No chance",value:0},{label:"Slight chance",value:1},{label:"Moderate chance",value:2},{label:"High chance",value:3}] },
      { id: "6", text: "Sitting and talking to someone", choices: [{label:"No chance",value:0},{label:"Slight chance",value:1},{label:"Moderate chance",value:2},{label:"High chance",value:3}] },
      { id: "7", text: "Sitting quietly after lunch without alcohol", choices: [{label:"No chance",value:0},{label:"Slight chance",value:1},{label:"Moderate chance",value:2},{label:"High chance",value:3}] },
      { id: "8", text: "In a car, while stopped for a few minutes in traffic", choices: [{label:"No chance",value:0},{label:"Slight chance",value:1},{label:"Moderate chance",value:2},{label:"High chance",value:3}] },
    ],
    bands: [
      { min: 0, max: 7, label: "Normal", copy: "Within the normal range. Keep your sleep window consistent.", readNext: ["sleep-as-the-quietest-anti-inflammatory", "mitochondria-and-autoimmune-fatigue", "supplement-essentials-for-autoimmune"] },
      { min: 8, max: 9, label: "Average", copy: "Average. Worth tracking if your fatigue feels worse than the score suggests.", readNext: ["sleep-as-the-quietest-anti-inflammatory", "mitochondria-and-autoimmune-fatigue", "stress-the-hpa-axis-and-flare-risk"] },
      { min: 10, max: 15, label: "Excessive", copy: "Excessive daytime sleepiness. Ask your clinician about a sleep study, especially if you snore, wake unrefreshed, or have a partner who notices breathing pauses.", readNext: ["sleep-as-the-quietest-anti-inflammatory", "mitochondria-and-autoimmune-fatigue", "the-emotional-roots-of-autoimmune-disease"] },
      { min: 16, max: 24, label: "Pathological", copy: "Pathological range. A formal sleep evaluation is strongly indicated.", readNext: ["sleep-as-the-quietest-anti-inflammatory", "mitochondria-and-autoimmune-fatigue", "stress-the-hpa-axis-and-flare-risk"] },
    ],
  },
  {
    slug: "fss-fatigue",
    title: "Fatigue Severity Scale (FSS)",
    short: "Nine-item rating of fatigue impact on daily life, widely used in MS, lupus, and Sjogren's research.",
    authorAttribution: "Krupp et al., Archives of Neurology (1989)",
    source: "https://www.healthywomen.org/sites/default/files/Fatigue%20Severity%20Scale.pdf",
    about: "FSS measures how much fatigue interferes with your function, not how often you feel tired. A higher score is more disabling fatigue.",
    questions: Array.from({length:9},(_,i)=>({
      id: String(i+1),
      text: [
        "My motivation is lower when I am fatigued",
        "Exercise brings on my fatigue",
        "I am easily fatigued",
        "Fatigue interferes with my physical functioning",
        "Fatigue causes frequent problems for me",
        "My fatigue prevents sustained physical functioning",
        "Fatigue interferes with carrying out certain duties and responsibilities",
        "Fatigue is among my three most disabling symptoms",
        "Fatigue interferes with my work, family, or social life",
      ][i],
      choices: [
        { label: "Strongly disagree", value: 1 },
        { label: "Disagree", value: 2 },
        { label: "Slightly disagree", value: 3 },
        { label: "Neutral", value: 4 },
        { label: "Slightly agree", value: 5 },
        { label: "Agree", value: 6 },
        { label: "Strongly agree", value: 7 },
      ],
    })),
    bands: [
      { min: 9, max: 35, label: "Low impact", copy: "Fatigue is not heavily limiting your function right now. Keep tracking it across the cycle of a flare.", readNext: ["mitochondria-and-autoimmune-fatigue", "sleep-as-the-quietest-anti-inflammatory", "supplement-essentials-for-autoimmune"] },
      { min: 36, max: 53, label: "Moderate impact", copy: "Moderate impact on function. This is the range where many autoimmune patients sit. The single best lever is usually sleep architecture.", readNext: ["mitochondria-and-autoimmune-fatigue", "sleep-as-the-quietest-anti-inflammatory", "wahls-protocol-mitochondria-and-greens"] },
      { min: 54, max: 63, label: "High impact", copy: "High-impact fatigue. Ask a clinician about iron, ferritin, B12, vitamin D, and a sleep study before adding any supplements.", readNext: ["mitochondria-and-autoimmune-fatigue", "wahls-protocol-mitochondria-and-greens", "supplement-essentials-for-autoimmune"] },
    ],
  },
  {
    slug: "ace-childhood",
    title: "Adverse Childhood Experiences (ACE)",
    short: "Ten-item history that strongly predicts adult inflammatory and autoimmune risk.",
    authorAttribution: "Felitti & Anda, Kaiser-CDC ACE Study (1998)",
    source: "https://www.cdc.gov/violenceprevention/aces/",
    about: "ACE is not a diagnosis. It is a window into the kind of early-life stress load that biases the immune system toward dysregulation. Knowing your number changes how you treat your own nervous system.",
    questions: Array.from({length:10},(_,i)=>({
      id: String(i+1),
      text: [
        "Did a parent or other adult often swear at, insult, put you down, or humiliate you?",
        "Did a parent or other adult often push, grab, slap, or throw something at you, or hit you so hard you had marks?",
        "Did an adult ever touch or fondle you, or have you touch their body in a sexual way, or attempt or have any kind of sexual contact with you?",
        "Did you often feel that no one in your family loved you or thought you were important?",
        "Did you often feel that you did not have enough to eat, had to wear dirty clothes, or had no one to protect you?",
        "Were your parents ever separated or divorced?",
        "Was your mother or stepmother often pushed, grabbed, slapped, or had something thrown at her, or hit?",
        "Did you live with anyone who was a problem drinker or an alcoholic, or who used street drugs?",
        "Was a household member depressed or mentally ill, or did a household member attempt suicide?",
        "Did a household member go to prison?",
      ][i],
      choices: [{label:"No",value:0},{label:"Yes",value:1}],
    })),
    bands: [
      { min: 0, max: 0, label: "0", copy: "Zero ACEs. Your early window was protective. The rest of the work still matters.", readNext: ["trauma-and-the-immune-system", "the-emotional-roots-of-autoimmune-disease", "stress-the-hpa-axis-and-flare-risk"] },
      { min: 1, max: 3, label: "1-3", copy: "1-3 ACEs. Common. Worth a slow, kind read of the trauma-immune literature, paired with a nervous-system practice that fits your life.", readNext: ["trauma-and-the-immune-system", "the-emotional-roots-of-autoimmune-disease", "somatic-practices-for-the-nervous-system"] },
      { min: 4, max: 10, label: "4+", copy: "4 or more ACEs. The literature on adult inflammatory disease is unambiguous here. Trauma-informed care is not optional, it is the high-leverage move.", readNext: ["trauma-and-the-immune-system", "the-emotional-roots-of-autoimmune-disease", "somatic-practices-for-the-nervous-system"] },
    ],
  },
  {
    slug: "leaky-gut-self-screen",
    title: "Leaky Gut Self-Screen",
    short: "A pragmatic 12-item self-screen we built around the symptoms most often described by patients with intestinal permeability findings on testing.",
    authorAttribution: "Adapted by Immune Rebuilt from Fasano et al. (zonulin/intestinal permeability literature)",
    source: "https://immunerebuilt.com/articles/leaky-gut-without-the-hype",
    about: "This is a pattern-recognition tool, not a lab test. It is meant to help you decide whether the rest of our leaky-gut writing is relevant to you.",
    questions: [
      { id: "1", text: "Bloating within an hour of eating, several days a week", choices: yesNo },
      { id: "2", text: "Two or more new food sensitivities in the last twelve months", choices: yesNo },
      { id: "3", text: "Loose stools or constipation more than three days a week", choices: yesNo },
      { id: "4", text: "An autoimmune diagnosis, even if quiet right now", choices: yesNo },
      { id: "5", text: "Skin: eczema, hives, or unexplained rashes", choices: yesNo },
      { id: "6", text: "Brain fog or post-meal fatigue", choices: yesNo },
      { id: "7", text: "Joint pain that comes and goes", choices: yesNo },
      { id: "8", text: "History of long antibiotic courses or many courses", choices: yesNo },
      { id: "9", text: "Heavy NSAID use (ibuprofen, naproxen) for pain", choices: yesNo },
      { id: "10", text: "A high-stress year recently", choices: yesNo },
      { id: "11", text: "Heartburn or reflux requiring acid blockers", choices: yesNo },
      { id: "12", text: "Mood swings tied to specific foods", choices: yesNo },
    ],
    bands: [
      { min: 0, max: 8, label: "Quiet", copy: "Quiet pattern. Permeability work is unlikely to be your highest-leverage lever right now.", readNext: ["leaky-gut-without-the-hype", "what-actually-causes-autoimmune-disease", "aip-protocol-honest-guide"] },
      { min: 9, max: 20, label: "Active", copy: "An active pattern. The leaky-gut writing in our library is worth reading, in the order linked below.", readNext: ["leaky-gut-without-the-hype", "aip-protocol-honest-guide", "reintroducing-foods-after-aip"] },
      { min: 21, max: 36, label: "Loud", copy: "A loud pattern. A clinician who can run zonulin or a comprehensive stool panel is the next move.", readNext: ["leaky-gut-without-the-hype", "gi-map-and-stool-testing", "functional-medicine-and-aip"] },
    ],
  },
  {
    slug: "thyroid-self-screen",
    title: "Thyroid / Hashimoto's Self-Screen",
    short: "A pragmatic screen of the symptoms most associated with hypothyroid and Hashimoto's presentations.",
    authorAttribution: "Adapted by Immune Rebuilt from the AACE clinical guidelines",
    source: "https://immunerebuilt.com/articles/hashimotos-step-by-step",
    about: "This is a starting place, not a diagnosis. The conversation worth having with a clinician is TSH + free T4 + free T3 + TPO and TgAb antibodies, not TSH alone.",
    questions: [
      { id: "1", text: "Cold intolerance, especially in the hands and feet", choices: yesNo },
      { id: "2", text: "Hair shedding or loss of the outer third of the eyebrows", choices: yesNo },
      { id: "3", text: "Constipation or sluggish digestion", choices: yesNo },
      { id: "4", text: "Weight gain unrelated to food intake", choices: yesNo },
      { id: "5", text: "Brain fog, slow thinking, low motivation", choices: yesNo },
      { id: "6", text: "Persistent fatigue not explained by sleep", choices: yesNo },
      { id: "7", text: "Dry skin, brittle nails", choices: yesNo },
      { id: "8", text: "Mood low, mildly depressed", choices: yesNo },
      { id: "9", text: "Heavy menstrual cycles or fertility difficulty", choices: yesNo },
      { id: "10", text: "Family history of thyroid disease or autoimmune disease", choices: yesNo },
    ],
    bands: [
      { min: 0, max: 6, label: "Low pattern", copy: "Low pattern. A baseline TSH at your next physical is reasonable.", readNext: ["hashimotos-step-by-step", "selenium-iodine-and-hashimotos", "what-actually-causes-autoimmune-disease"] },
      { min: 7, max: 14, label: "Suggestive", copy: "Suggestive pattern. Ask for the full panel: TSH, free T4, free T3, TPO, TgAb. Not just TSH.", readNext: ["hashimotos-step-by-step", "selenium-iodine-and-hashimotos", "molecular-mimicry-explained"] },
      { min: 15, max: 30, label: "Strong pattern", copy: "Strong pattern. The full panel is overdue.", readNext: ["hashimotos-step-by-step", "selenium-iodine-and-hashimotos", "functional-medicine-and-aip"] },
    ],
  },
  {
    slug: "stress-load",
    title: "Allostatic Load Snapshot",
    short: "Twelve markers, three lifestyle, three biological, three relational, three trauma-history, that together estimate cumulative stress load.",
    authorAttribution: "Adapted by Immune Rebuilt from McEwen's allostatic load framework",
    source: "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4561403/",
    about: "Allostatic load is the wear-and-tear cost of chronic stress on the body. This snapshot is qualitative and is meant for self-tracking.",
    questions: [
      { id: "1", text: "Sleep is consistently under 7 hours", choices: yesNo },
      { id: "2", text: "Two or more alcoholic drinks most days", choices: yesNo },
      { id: "3", text: "No regular movement for at least 30 min, four days a week", choices: yesNo },
      { id: "4", text: "Resting heart rate above 80 (if known)", choices: yesNo },
      { id: "5", text: "Blood pressure consistently above 130/85", choices: yesNo },
      { id: "6", text: "Waist circumference rising over the past year", choices: yesNo },
      { id: "7", text: "A primary relationship that drains rather than restores", choices: yesNo },
      { id: "8", text: "Caregiving responsibilities that exceed your capacity", choices: yesNo },
      { id: "9", text: "Few people you can call at 11 pm if needed", choices: yesNo },
      { id: "10", text: "Childhood trauma not yet processed in any therapy", choices: yesNo },
      { id: "11", text: "Adult trauma in the last three years", choices: yesNo },
      { id: "12", text: "A persistent feeling of bracing or being keyed up", choices: yesNo },
    ],
    bands: [
      { min: 0, max: 8, label: "Light load", copy: "A light load. Maintenance is the work.", readNext: ["stress-the-hpa-axis-and-flare-risk", "vagus-nerve-and-the-anti-inflammatory-reflex", "sleep-as-the-quietest-anti-inflammatory"] },
      { min: 9, max: 18, label: "Moderate load", copy: "Moderate load. Identify the one or two markers most under your control and work on those for the next ninety days.", readNext: ["stress-the-hpa-axis-and-flare-risk", "the-emotional-roots-of-autoimmune-disease", "vagus-nerve-and-the-anti-inflammatory-reflex"] },
      { min: 19, max: 36, label: "Heavy load", copy: "Heavy load. This pattern is one of the strongest predictors of inflammatory flare risk we have. The trauma-informed nervous-system work is high leverage here.", readNext: ["trauma-and-the-immune-system", "the-emotional-roots-of-autoimmune-disease", "somatic-practices-for-the-nervous-system"] },
    ],
  },
  {
    slug: "fodmap-pattern",
    title: "Food Reaction Pattern Snapshot",
    short: "A short snapshot used to decide whether a structured elimination is worth your time.",
    authorAttribution: "Adapted by Immune Rebuilt from Monash FODMAP and AIP elimination practice",
    source: "https://immunerebuilt.com/articles/aip-protocol-honest-guide",
    about: "Elimination protocols are powerful but costly in time and social energy. This snapshot helps you decide whether the cost is justified.",
    questions: [
      { id: "1", text: "Bloating that comes and goes, more than two days a week", choices: yesNo },
      { id: "2", text: "Brain fog or fatigue within two hours of certain meals", choices: yesNo },
      { id: "3", text: "Joint or skin flares that you suspect a food triggers", choices: yesNo },
      { id: "4", text: "An autoimmune diagnosis with active symptoms", choices: yesNo },
      { id: "5", text: "Tried random elimination diets without a clear plan", choices: yesNo },
      { id: "6", text: "Willing to commit four to six weeks to a structured plan", choices: yesNo },
      { id: "7", text: "Have time and a kitchen that supports cooking from scratch", choices: yesNo },
      { id: "8", text: "Have a clinician or coach to consult", choices: yesNo },
    ],
    bands: [
      { min: 0, max: 4, label: "Low value", copy: "An elimination protocol is unlikely to repay the investment right now. Track symptoms for another four weeks first.", readNext: ["aip-protocol-honest-guide", "leaky-gut-without-the-hype", "reintroducing-foods-after-aip"] },
      { min: 5, max: 10, label: "Worth considering", copy: "An elimination is worth considering if you have the bandwidth. Read the AIP guide and the reintroduction guide together before you start.", readNext: ["aip-protocol-honest-guide", "reintroducing-foods-after-aip", "celiac-vs-non-celiac-gluten-sensitivity"] },
      { min: 11, max: 16, label: "High value", copy: "High likely value. A 30-day AIP with a planned reintroduction is one of the most informative experiments an autoimmune patient can run.", readNext: ["aip-protocol-honest-guide", "reintroducing-foods-after-aip", "wahls-protocol-mitochondria-and-greens"] },
    ],
  },
  {
    slug: "mold-exposure",
    title: "Mold and Indoor Environment Screen",
    short: "Eight indoor-environment questions that, taken together, identify patients whose flares may be tied to a building.",
    authorAttribution: "Adapted by Immune Rebuilt from CIRS clinical case-definition reviews",
    source: "https://immunerebuilt.com/articles/mold-and-mycotoxin-illness",
    about: "This screen does not diagnose mold illness. It identifies whether a careful indoor-environment review is worth doing before the next round of testing.",
    questions: [
      { id: "1", text: "Visible mold or persistent musty smell at home or work", choices: yesNo },
      { id: "2", text: "A water leak or flood in the building in the last five years", choices: yesNo },
      { id: "3", text: "Symptoms improve when you spend a week away from home", choices: yesNo },
      { id: "4", text: "Symptoms worsen on humid days or in damp spaces", choices: yesNo },
      { id: "5", text: "Multiple unexplained symptom systems active at once", choices: yesNo },
      { id: "6", text: "Other people in the household feel sick too", choices: yesNo },
      { id: "7", text: "Standard autoimmune workups have been unrevealing", choices: yesNo },
      { id: "8", text: "Sensitivity to perfumes, smoke, or low-level chemical smells", choices: yesNo },
    ],
    bands: [
      { min: 0, max: 4, label: "Low likelihood", copy: "Low likelihood that the building is a primary driver. Other levers are more likely to repay attention.", readNext: ["mold-and-mycotoxin-illness", "what-actually-causes-autoimmune-disease", "functional-medicine-and-aip"] },
      { min: 5, max: 9, label: "Worth investigating", copy: "Worth investigating. Start with a careful walkthrough and an honest moisture inspection.", readNext: ["mold-and-mycotoxin-illness", "gi-map-and-stool-testing", "functional-medicine-and-aip"] },
      { min: 10, max: 16, label: "High likelihood", copy: "A high-likelihood pattern. Air quality and a clinician familiar with mold-related illness should be on your short list.", readNext: ["mold-and-mycotoxin-illness", "what-actually-causes-autoimmune-disease", "functional-medicine-and-aip"] },
    ],
  },
];

export function scoreAssessment(a: Assessment, answers: Record<string, number>): { score: number; band: Band | null } {
  const score = Object.values(answers).reduce((sum, v) => sum + (Number.isFinite(v) ? v : 0), 0);
  const band = a.bands.find((b) => score >= b.min && score <= b.max) ?? null;
  return { score, band };
}
