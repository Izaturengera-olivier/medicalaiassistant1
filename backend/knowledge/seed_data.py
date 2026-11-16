"""Initial content for the knowledge base.

Written into the database by the ``0002`` data migration. After that the
``MedicalKnowledgeSource`` and ``KnowledgeDocument`` tables are the source of
truth, so admins can add, correct or retire material without a code change.
Content is generic public-health guidance only - see AI_SAFETY.md.
"""


DEFAULT_SOURCES = [
    {
        "id": "who",
        "name": "World Health Organization",
        "url": "https://www.who.int",
        "source_type": "WHO",
        "approval_status": "approved",
        "description": "Global health authority providing evidence-based guidelines"
    },
    {
        "id": "moh_rwanda",
        "name": "Rwanda Ministry of Health",
        "url": "https://moh.gov.rw",
        "source_type": "MOH",
        "approval_status": "approved",
        "description": "Official health authority for Rwanda"
    },
    {
        "id": "fda_rwanda",
        "name": "Rwanda Food and Drugs Authority",
        "url": "https://rfd.gov.rw",
        "source_type": "FDA",
        "approval_status": "approved",
        "description": "Regulatory authority for medicines and medical devices"
    },
    {
        "id": "rbc_rwanda",
        "name": "Rwanda Biomedical Centre (RBC)",
        "url": "https://rbc.gov.rw",
        "source_type": "MOH",
        "approval_status": "approved",
        "description": "National operational agency for disease prevention, epidemic response, and specialized care in Rwanda"
    },
    {
        "id": "rssb_rwanda",
        "name": "Rwanda Social Security Board (CBHI / Mutuelle de Sante)",
        "url": "https://rssb.rw",
        "source_type": "MOH",
        "approval_status": "approved",
        "description": "Public manager of community-based health insurance (Mutuelle de Sante) and healthcare benefits in Rwanda"
    },
    {
        "id": "nih",
        "name": "National Institutes of Health / MedlinePlus",
        "url": "https://medlineplus.gov",
        "source_type": "NIH",
        "approval_status": "approved",
        "description": "Authoritative clinical medical research, diagnostic tests, and scan guides"
    },
    {
        "id": "cdc",
        "name": "Centers for Disease Control and Prevention",
        "url": "https://www.cdc.gov",
        "source_type": "CDC",
        "approval_status": "approved",
        "description": "Clinical prevention and disease management protocols"
    },
    {
        "id": "mayoclinic",
        "name": "Mayo Clinic Clinical Reference",
        "url": "https://www.mayoclinic.org",
        "source_type": "LITERATURE",
        "approval_status": "approved",
        "description": "Evidence-based clinical disease guidelines, scanner findings, and diagnostic workup"
    },
    {
        "id": "fleischner_acr",
        "name": "Fleischner Society & ACR Imaging Guidelines",
        "url": "https://www.acr.org",
        "source_type": "LITERATURE",
        "approval_status": "approved",
        "description": "International standard guidelines for pulmonary nodule and diagnostic imaging management"
    },
    {
        "id": "web_search",
        "name": "Approved medical web search",
        "url": "https://tavily.com",
        "source_type": "LITERATURE",
        "approval_status": "approved",
        "description": "Live results restricted to configured medical domains"
    }
]


BASE_DOCUMENTS = [
    {
        "id": "doc_1",
        "title": "Headache Management Guidelines",
        "content": "Headaches are common and usually not serious. Most headaches can be treated with rest, hydration, and over-the-counter pain relievers. Seek care urgently if a headache is sudden and severe, follows a head injury, or comes with fever and a stiff neck.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/headache-disorders"
    },
    {
        "id": "doc_2", 
        "title": "Fever Treatment Recommendations",
        "content": "Fever is a common symptom of infection. For adults, rest and hydration are important. Over-the-counter fever reducers can help. Seek medical attention if fever exceeds 103°F (39.4°C), lasts more than 3 days, or comes with confusion, stiff neck, or difficulty breathing.",
        "source_id": "moh_rwanda",
        "url": "https://moh.gov.rw"
    },
    {
        "id": "doc_3",
        "title": "Cough and Cold Symptoms",
        "content": "Most coughs and colds resolve within 1-2 weeks without treatment. Rest, fluids, and over-the-counter medications can help relieve symptoms. Seek medical care if symptoms worsen, if you cough up blood, or if the cough persists beyond 2 weeks.",
        "source_id": "who",
        "url": "https://www.who.int"
    },
    {
        "id": "doc_4",
        "title": "Malaria Signs and When to Seek Care",
        "content": "Malaria is common in Rwanda. Fever with chills, sweating, headache, or body pain may be malaria and needs a test at a health facility the same day. Children under five and pregnant women should be seen urgently. Do not delay treatment when fever with chills occurs.",
        "source_id": "moh_rwanda",
        "url": "https://www.who.int/news-room/fact-sheets/detail/malaria"
    },
    {
        "id": "doc_5",
        "title": "Diarrhea and Dehydration",
        "content": "Most diarrhea improves with rest and fluids. Oral rehydration salts (ORS) replace lost water and salts; zinc is recommended for children. Seek care urgently if there is blood in the stool, no urine for many hours, sunken eyes, drowsiness, or persistent vomiting.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/diarrhoeal-disease"
    },
    {
        "id": "doc_6",
        "title": "High Blood Pressure (Hypertension)",
        "content": "High blood pressure often has no symptoms, so it is found by measuring blood pressure. Reducing salt, staying active, and taking prescribed medicines help control it. Seek emergency care for chest pain, severe headache, blurred vision, or difficulty speaking.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/hypertension"
    },
    {
        "id": "doc_7",
        "title": "Diabetes: Common Signs and Danger Signs",
        "content": "Diabetes can cause thirst, frequent urination, tiredness, and blurred vision. Untreated high blood sugar can lead to confusion, drowsiness, or fruity-smelling breath, which need urgent medical attention. Regular check-ups and prescribed treatment are important.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/diabetes"
    },
    {
        "id": "doc_8",
        "title": "Asthma and Difficulty Breathing",
        "content": "Asthma causes wheezing, cough, and shortness of breath, and is managed with prescribed inhalers. Seek emergency care immediately if you cannot speak full sentences, your lips turn blue, or breathing becomes rapid and difficult despite using your inhaler.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/asthma"
    },
    {
        "id": "doc_9",
        "title": "Skin Rash and Itching",
        "content": "Most rashes improve with gentle skin care and by avoiding scratching. Keep the area clean and dry. Seek care if a rash comes with fever, spreads quickly, blisters, or is accompanied by difficulty breathing or swelling of the face, which may be a severe reaction.",
        "source_id": "moh_rwanda",
        "url": "https://moh.gov.rw"
    },
    {
        "id": "doc_10",
        "title": "Danger Signs in Pregnancy",
        "content": "Pregnant women should go to a health facility immediately for bleeding from the vagina, severe headache, blurred vision, swelling of the face or hands, high fever, or reduced movement of the baby. These danger signs need urgent professional care.",
        "source_id": "moh_rwanda",
        "url": "https://moh.gov.rw"
    },
    {
        "id": "doc_11",
        "title": "Back Pain Assessment and Warning Signs",
        "content": "Back pain may come from muscle strain, joints, or the spine. Gentle movement and avoiding prolonged bed rest may help some uncomplicated pain. Seek urgent care for back pain with weakness or numbness in both legs, loss of bladder or bowel control, fever, or a major injury.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/low-back-pain"
    },
    {
        "id": "doc_12",
        "title": "Abdominal Pain Assessment and Warning Signs",
        "content": "Abdominal pain, also called stomach pain, can have many causes, including digestive illness, infection, or problems involving abdominal organs. Seek urgent care for severe or worsening pain, a rigid abdomen, repeated vomiting, blood in vomit or stool, fainting, or pregnancy with severe pain or bleeding.",
        "source_id": "who",
        "url": "https://www.who.int/health-topics/food-safety"
    },
    {
        "id": "doc_13",
        "title": "Fatigue and Tiredness Assessment",
        "content": "Fatigue or unusual tiredness can be related to poor sleep, stress, infection, anemia, medication effects, or other health conditions. Seek urgent care for severe weakness with confusion, fainting, chest pain, difficulty breathing, or sudden one-sided weakness.",
        "source_id": "who",
        "url": "https://www.who.int/health-topics/anaemia"
    },
    {
        "id": "doc_14",
        "title": "CT Scan and Pulmonary Nodule Management Guidelines",
        "content": "Pulmonary nodules found on chest CT scans require structured risk stratification per Fleischner Society guidelines. Solid nodules under 6 mm in low-risk individuals generally need no routine follow-up. Nodules 6 to 8 mm warrant repeat high-resolution CT at 6 to 12 months. Nodules larger than 8 mm, spiculed borders, upper lobe location, or growing lesions warrant prompt pulmonology review, contrast-enhanced CT, or PET-CT to rule out malignancy.",
        "source_id": "fleischner_acr",
        "url": "https://www.acr.org/Clinical-Resources/Reporting-and-Data-Systems"
    },
    {
        "id": "doc_15",
        "title": "Brain CT and MRI Neuroimaging Interpretation and Red Flags",
        "content": "Neuroimaging with CT or MRI evaluates acute stroke, hemorrhage, trauma, and structural lesions. Acute loss of grey-white matter differentiation or hyperdense vessel signs indicate acute ischemic stroke requiring emergency intervention. Intracranial hemorrhage, midline shift, herniation, or acute hydrocephalus are life-threatening emergencies requiring immediate neurosurgical consultation. Chronic white matter microvascular changes require cardiovascular risk factor control.",
        "source_id": "nih",
        "url": "https://medlineplus.gov/mriscans.html"
    },
    {
        "id": "doc_16",
        "title": "Abdominal and Pelvic CT/Ultrasound Findings and Workup",
        "content": "Abdominal ultrasound and CT scans evaluate organs, vessels, and fluid collections. Hepatic steatosis (fatty liver) shows increased echogenicity or low attenuation and requires metabolic assessment. Simple renal cysts (Bosniak Category I) are benign and require no intervention; complex cysts with thick septa or solid enhancing components (Bosniak III/IV) require urologic oncology evaluation. Gallstones with gallbladder wall thickening >3 mm indicate acute cholecystitis. Appendix diameter >6 mm with fat stranding indicates acute appendicitis needing urgent surgical consult.",
        "source_id": "mayoclinic",
        "url": "https://www.mayoclinic.org/tests-procedures/ct-scan/about/pac-20393675"
    },
    {
        "id": "doc_17",
        "title": "Complete Blood Count (CBC) and Anemia Evaluation Guidelines",
        "content": "Complete blood counts evaluate red cells, white cells, and platelets. Hemoglobin below 12 g/dL in women or 13 g/dL in men indicates anemia. Low MCV (<80 fL) suggests microcytic anemia, most commonly iron deficiency (confirm with ferritin) or thalassemia. Elevated white blood cell count (leukocytosis >11,000/mcL) with neutrophil predominance suggests acute bacterial infection. Platelets under 50,000/mcL increase bleeding risk and require prompt hematology review. Platelets under 20,000/mcL require urgent evaluation.",
        "source_id": "who",
        "url": "https://www.who.int/publications/i/item/9789240018860"
    },
    {
        "id": "doc_18",
        "title": "Comprehensive Metabolic Panel (CMP): Liver and Renal Function",
        "content": "Comprehensive metabolic panels evaluate liver enzymes, kidney filtration, and electrolytes. ALT and AST greater than 3 times the upper limit of normal indicate active hepatocellular injury (viral hepatitis, drug-induced hepatotoxicity, alcohol, or non-alcoholic steatohepatitis). Alkaline phosphatase and bilirubin elevations indicate biliary or cholestatic obstruction. Serum creatinine elevation with eGFR below 60 mL/min/1.73m2 suggests renal impairment. Potassium >5.5 mEq/L (hyperkalemia) or <3.0 mEq/L (hypokalemia) are urgent cardiac arrhythmia risks requiring immediate clinical management.",
        "source_id": "nih",
        "url": "https://medlineplus.gov/lab-tests/comprehensive-metabolic-panel-cmp/"
    },
    {
        "id": "doc_19",
        "title": "Chest X-Ray Findings: Consolidation, Effusion, and Cardiomegaly",
        "content": "Chest radiography is the initial imaging for thoracic symptoms. Focal alveolar consolidation with air bronchograms indicates pneumonia. Blunting of the costophrenic angles signifies pleural effusion. Cardiothoracic ratio exceeding 50% on PA view indicates cardiomegaly, prompting echocardiography for heart failure. Absence of lung markings peripherally with a visible pleural line indicates pneumothorax, requiring urgent decompression if tension physiology is present.",
        "source_id": "cdc",
        "url": "https://www.cdc.gov/pneumonia/index.html"
    },
    {
        "id": "doc_20",
        "title": "Pathology and Biopsy Specimen Evaluation Standards",
        "content": "Histopathology and biopsy reports describe tissue architecture, cytology, and margins. Findings are classified as benign, atypical, dysplastic, or malignant. High-grade dysplasia or invasive carcinoma requires prompt multidisciplinary clinical tumor board review, staging imaging (contrast CT, MRI, or PET), and definitive surgical or oncologic management. Benign lesions should be correlated clinically with symptoms.",
        "source_id": "who",
        "url": "https://www.who.int/teams/noncommunicable-diseases/cancer"
    },
    {
        "id": "doc_21",
        "title": "Ebola and Viral Haemorrhagic Fever: Transmission and Prevention",
        "content": "Ebola is a severe viral haemorrhagic fever spread by direct contact with blood or body fluids of a person who is sick or has died, or with contaminated objects such as needles and linen; it is not carried through the air. Prevention means avoiding contact with body fluids, using protective equipment in care settings, safe burial practices, hand hygiene, and vaccination of contacts and at-risk health workers. Seek urgent care for sudden fever, severe weakness, muscle pain, vomiting or bleeding, especially after contact with a sick person or travel to an outbreak area.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/ebola-and-viral-haemorrhagic-fevers"
    }
]


# Each passage below was read from the published page listed as its URL on
# 2026-10-23 and is kept to what that page states. Treatment detail and dosages
# are deliberately left out: AI_SAFETY.md forbids the model from prescribing, and
# a professional decides treatment.
PATIENT_GUIDANCE_DOCUMENTS = [
    {
        "id": "doc_22",
        "title": "Tuberculosis: Symptoms and When to Seek Care",
        "content": "Tuberculosis (TB) spreads through the air when a person with TB coughs, sneezes or spits, and it is preventable and curable. Symptoms to watch for are a prolonged cough (sometimes with blood), chest pain, weakness, fatigue, weight loss, fever and night sweats. Anyone with these symptoms should seek medical attention, because finding and treating cases early also stops spread in the community. Drug-resistant TB remains a public health crisis, so treatment must be taken exactly as a clinician prescribes it.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/tuberculosis"
    },
    {
        "id": "doc_23",
        "title": "HIV: Transmission, Testing and When to Seek Care",
        "content": "HIV is passed through body fluids including blood, breast milk, semen and vaginal secretions, and from a mother to a child during pregnancy and delivery. Everyday contact does not transmit HIV. A person on sustained treatment with an undetectable viral load will not transmit HIV to sexual partners. Rapid tests give same-day results but a positive needs confirmation by trained staff; someone who tested negative after a recent high-risk exposure can test again after 28 days, and everyone should be retested before being enrolled in treatment and care. Babies under 18 months need virological testing as early as birth or at 6 weeks. Ask a clinician about PrEP or PEP after a risky exposure.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids"
    },
    {
        "id": "doc_24",
        "title": "Cholera: Watery Diarrhoea, Dehydration and Urgent Rehydration",
        "content": "Cholera is a severe diarrhoeal disease that can be fatal within hours if not treated. Illness usually starts 12 hours to 5 days after swallowing the bacteria, and many infected people have no symptoms. When symptoms appear they include severe diarrhoea and vomiting, leg cramps, exhaustion, thirst, sunken eyes and tight skin from fluid loss. Most people recover if given oral rehydration solution (ORS) quickly; severe cases need urgent care. Spread is through contaminated food and water, so prevention is safe water, sanitation and handwashing with soap and clean water, plus cholera vaccination in outbreaks.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/cholera"
    },
    {
        "id": "doc_25",
        "title": "Measles: Rash, Fever and Serious Complications",
        "content": "Measles is a highly contagious airborne disease that can cause severe complications and death. Symptoms usually begin 7 to 14 days after exposure with fever, runny nose, cough, red watery eyes and white spots in the mouth; the rash appears 3 to 5 days after the first symptoms, starting on the face and upper neck and spreading downward over about three days. Complications include blindness, encephalitis, severe diarrhoea with dehydration, ear infections and pneumonia. Measles in pregnancy can cause miscarriage, premature delivery and low birth weight. Vaccination with two doses is the most effective prevention.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/measles"
    },
    {
        "id": "doc_26",
        "title": "Childhood Pneumonia: Fast Breathing and Chest Indrawing",
        "content": "Pneumonia is the leading infectious killer of children under five and can be caused by viruses, bacteria and fungi. The key signs to look for are fast breathing, or the lower chest wall pulling in when the child breathes in. Wheezing can occur with viral pneumonia. Danger signs in a sick child are being unable to feed or drink, unconsciousness, low body temperature and convulsions. Immunization against Hib, pneumococcus, measles and whooping cough is the most effective prevention, together with exclusive breastfeeding, clean cooking smoke and ventilation. Pneumonia needs antibiotic treatment decided by a clinician, and hospitalization is recommended only for severe cases.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/pneumonia"
    },
    {
        "id": "doc_27",
        "title": "Anaemia: Tiredness, Pallor and Breathlessness",
        "content": "Anaemia mainly affects young children, pregnant and postpartum women, and menstruating girls and women, and the greatest burden is in low- and lower-middle-income countries. Common signs are tiredness, dizziness or light-headedness, cold hands and feet, headache, and shortness of breath especially on exertion. More advanced signs are pale mucous membranes in the mouth or nose, pale skin and nail beds, rapid breathing and heartbeat, dizziness on standing, and bruising easily. Causes include nutrient deficiencies, poor absorption, infections such as malaria and TB, chronic disease, heavy periods, blood loss in pregnancy and childbirth, and inherited red cell disorders; iron shortage is the most common nutritional cause. Eating iron-, folate-, vitamin B12- and vitamin A-rich foods helps, and supplements should only be taken when a qualified health-care provider recommends them.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/anaemia"
    },
    {
        "id": "doc_28",
        "title": "Depression: Recognizing It and Getting Help",
        "content": "Depression is a common mental disorder affecting about 5.2% of adults worldwide, and more women than men are affected. Symptoms are depressed mood (sad, irritable or empty), loss of pleasure or interest, poor concentration, excessive guilt or low self-worth, hopelessness, thoughts about dying or suicide, disrupted sleep, changes in appetite or weight, and very low energy, lasting most of the day, nearly every day, for at least two weeks. Depression can lead to suicide, and there is effective treatment for mild, moderate and severe depression. Psychological treatments such as behavioural activation, cognitive behavioural therapy, interpersonal psychotherapy and problem-solving therapy are the first treatments, and may be combined with antidepressant medicines in moderate and severe depression. Talking to someone you trust, keeping active and seeking help from a health-care provider all help; if there is any risk of self-harm, contact emergency services or a crisis line immediately.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/depression"
    },
    {
        "id": "doc_29",
        "title": "Stroke: Sudden Weakness, Speech Change and Facial Droop",
        "content": "Stroke is a health emergency: a suspected stroke must be treated as one, with immediate scanning and hospital care, because specialist admission significantly lowers the chance of death. Warning signs that appear suddenly are dizziness or loss of coordination, loss of vision, facial droop, weakness in one or both arms, and slurred or strange speech. Most strokes are driven by modifiable risks including high blood pressure, air pollution, tobacco, poor diet and inactivity. Recovery is better when rehabilitation starts promptly once the person is stable, including physical exercises, daily skills training, communication therapy, mental health support and cognitive rehabilitation.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/stroke"
    },
    {
        "id": "doc_30",
        "title": "Meningitis: Fever With Stiff Neck Is an Emergency",
        "content": "Meningitis is a devastating disease that can be deadly, and many organisms including bacteria can cause it. The main signs are fever, neck stiffness, and confusion or altered mental status; in infants the presentation is often poor feeding or irritability. When it progresses to sepsis, warning signs are cold hands and feet, rapid breathing, falling blood pressure and a non-blanching skin rash. Meningitis is a medical emergency, and anyone with these signs should seek immediate care at a hospital or health centre. Vaccination provides long-lasting protection.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/meningitis"
    },
    {
        "id": "doc_31",
        "title": "Sickle Cell Disease: Pain Crises and Danger Signs",
        "content": "Sickle-cell disease is a serious inherited blood disorder caused by a mutation in the HBB gene, with about 515 000 affected births each year, mainly in sub-Saharan Africa. Features include pain crises (sudden severe pain from blocked blood flow), anaemia from rapid breakdown of sickle cells causing fatigue, weakness and shortness of breath, swelling of the hands and feet known as dactylitis, frequent infections from spleen damage, delayed growth, and vision problems. Other complications are stroke, infection, kidney failure and pregnancy-related risks. Care includes regular check-ups with a provider experienced in sickle-cell disease, vaccinations against pneumococcal and meningococcal infection, a balanced diet and adequate hydration, genetic counselling, and an emergency plan for crises during pregnancy.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/sickle-cell-disease"
    },
    {
        "id": "doc_32",
        "title": "Rabies: Wash an Animal Bite and Go Immediately",
        "content": "Rabies causes tens of thousands of deaths every year, mostly from dog bites, and once neurological signs appear it is fatal in 100% of cases. Deaths are still preventable because immediate care after exposure works. The virus enters through broken skin or mucous membranes via saliva, usually from bites, scratches or direct contact with mucosa; bats cause most cases in the Western Hemisphere and routine casual contact does not spread it. First aid is extensive wound washing with water and soap for at least 15 minutes as soon as possible after the exposure, then seeking medical attention immediately after any suspected dog or wild animal incident so a clinician can decide on post-exposure prophylaxis.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/rabies"
    },
    {
        "id": "doc_33",
        "title": "Burns: Cool Running Water, No Ice or Pastes",
        "content": "Around 163 000 people died in 2023 from exposure to fire, heat and hot substances, and many burns happen at home and at work, with children particularly at risk of scalds. First aid is to cool a thermal burn promptly with cool running water for approximately 20 minutes and to remove rings, watches and other tight items early, covering the wound with a clean protective material. Do not apply ice, oils, butter or toothpaste, and do not pull off clothing stuck to the wound; chemical burns are irrigated with abundant water. Medical care is needed for deep, large, electrical or chemical burns, burns of the face, hands, feet or genitals, and any possible inhalation injury. Severe burns cause prolonged treatment, scarring and lasting disability.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/burns"
    },
    {
        "id": "doc_34",
        "title": "Epilepsy: Recurrent Unprovoked Seizures Are Treatable",
        "content": "Epilepsy affects about 50 million people worldwide, and nearly 80% live in lower-resource countries where treatment gaps are largest. Epilepsy is defined as having two or more unprovoked seizures. Seizures range from brief lapses of attention or muscle twitches to intense convulsions, and may occur from annually to daily depending on the person. Up to 70% of people living with epilepsy could become seizure free with appropriate use of antiseizure medicines, which can be delivered through basic health networks; dose changes are considered after two seizure-free years, and surgery remains an option for drug-resistant cases. Recurrent seizures also raise the risk of physical injury and of anxiety or depression, and premature mortality is roughly tripled, so uncontrolled seizures need professional review.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/epilepsy"
    },
    {
        "id": "doc_35",
        "title": "Kidney Disease: Silent Until Late, Found by Simple Tests",
        "content": "Kidney disease includes acute kidney injury (AKI) and chronic kidney disease (CKD), and around 674 million people worldwide have CKD, most in low- and middle-income countries. It is often asymptomatic until late stages, which is why regular testing matters for people at risk; simple serum creatinine and urine albumin tests used in primary health care can detect CKD. Later symptoms are fatigue, breathlessness, generalized itchiness, leg swelling, muscle cramps, nausea or vomiting. Chronic causes include diabetes, hypertension, cardiovascular disease, glomerulonephritis, some genetic conditions, certain drugs and toxins, and infections. AKI follows sepsis, major surgery, trauma, complications of pregnancy, nephrotoxic medications and volume depletion. The most severe form, kidney failure, requires dialysis or transplantation.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/kidney-disease"
    },
    {
        "id": "doc_36",
        "title": "Pregnancy Danger Signs and Skilled Care",
        "content": "Over 700 women died every day in 2023 from preventable causes related to pregnancy and childbirth, a maternal death almost every two minutes, and just over 90% of these deaths occurred in low- and lower-middle-income countries. The main causes are severe bleeding (mostly bleeding after childbirth), infections (usually after childbirth), high blood pressure during pregnancy (pre-eclampsia and eclampsia), complications from delivery, and unsafe abortion. Care by skilled health professionals before, during and after childbirth can save the lives of women and newborns, and all births should be attended by skilled professionals who can detect early signs of infection and manage raised blood pressure before convulsions (eclampsia) start. Access to contraception and safe services also prevents deaths from unintended pregnancy and unsafe abortion.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/maternal-mortality"
    },
    {
        "id": "doc_37",
        "title": "COPD: Breathlessness, Chronic Cough and Flare-Ups",
        "content": "Chronic obstructive pulmonary disease (COPD) is the third leading cause of death worldwide, and nearly 90% of COPD deaths in people under 70 occur in low- and middle-income countries. The most common symptoms are difficulty breathing, a chronic cough that is sometimes with phlegm, and feeling tired. Symptoms can get worse quickly, which are called flare-ups; these usually last a few days and often require additional medicine. Main risks are tobacco smoking (active and passive), occupational dusts, fumes or chemicals, household air pollution from biomass fuel or coal, early life events such as poor growth in the womb, prematurity and frequent severe respiratory infections in childhood, childhood asthma, and the rare alpha-1 antitrypsin deficiency. COPD is not curable but improves with not smoking, avoiding air pollution and vaccination; bronchodilator inhalers are the most important treatment, given by a clinician.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/chronic-obstructive-pulmonary-disease-(copd)"
    },
    {
        "id": "doc_38",
        "title": "Preterm Birth: Prevention and Newborn Care",
        "content": "An estimated 13.4 million babies were born preterm in 2020, with rates from 4 to 16% across countries, and preterm birth complications are the leading cause of death among children under five; three-quarters of these deaths could be prevented with current cost-effective interventions. Antenatal prevention includes counselling on healthy diet and optimal nutrition and on tobacco and substance use, fetal measurements including early ultrasound, and a minimum of eight contacts with health professionals throughout pregnancy. Where early birth is expected, care may include antenatal steroids and tocolytic treatments to delay labour, and antibiotics for preterm prelabour rupture of membranes (PPROM). After birth, kangaroo mother care immediately, early initiation of breastfeeding, and support such as CPAP and caffeine for respiratory distress are used, and mothers and newborns should remain together from birth.",
        "source_id": "who",
        "url": "https://www.who.int/news-room/fact-sheets/detail/preterm-birth"
    },
    {
        "id": "doc_39",
        "title": "Where Care Happens in Rwanda: Referral Hospitals, District Hospitals and Health Centres",
        "content": "Rwanda organises public care in levels, so a sick person is not expected to reach the biggest hospital straight away. A health post and community health workers handle the simplest problems; a health centre, ivuriro in Kinyarwanda, covers a sector and gives routine outpatient care, antenatal care, immunisation and normal delivery; a district hospital covers a district and has inpatient beds, an operating theatre and a laboratory; and a referral hospital or teaching hospital takes the difficult cases sent up from district hospitals, with specialists and advanced imaging. The government public facility register lists these referral and teaching hospitals: University Teaching Hospital of Kigali (CHUK) in Nyarugenge, Kigali; the Butare teaching hospital (CHUB) in Huye; Ngoma referral hospital in Kibungo; Ruhengeri referral hospital in Musanze; Kabgayi referral hospital in Muhanga; Kibuye referral hospital in Karongi; the Kigali mental health referral centre in Kinyinya, Gasabo; Inkuru Nziza orthopaedic specialised hospital in Gikondo, Kicukiro; Huye Isange rehabilitation centre in Huye; and HNP Caraës in Butare. A district hospital is usually the closest place with beds and a surgical team, which is why Rubavu district hospital, Gisenyi district hospital, Kabutare district hospital and Ruhengeri hospital are the right first stop for a serious problem that is not an immediate emergency. For an emergency, go to the nearest hospital at any level rather than waiting for a referral letter, and carry any document or medicine list you already have.",
        "source_id": "moh_rwanda",
        "url": "https://www.mmi.gov.rw/partners/public-health-facilities/referrals-and-teaching-hospitals"
    },
    {
        "id": "doc_40",
        "title": "Emergency Health Helplines and Urgent Care in Rwanda",
        "content": "In Rwanda, acute emergencies and life-threatening conditions require immediate action. Call SAMU (Service d'Aide Medicale Urgente) at 112 or 912 for emergency ambulance transport. The Rwanda National Police emergency number is 112. For infectious disease emergencies, epidemic outbreaks, or urgent health advice, call the Rwanda Biomedical Centre (RBC) toll-free hotline at 114. For domestic violence, child abuse, and gender-based violence medical and psychosocial care, call Isange One Stop Centre at 3029 or go to the nearest Isange centre located in district hospitals across the country. In a medical emergency, go immediately to the closest hospital or health facility without waiting for transfer paperwork or referral letters; emergency stabilization is prioritized across all public health facilities in Rwanda.",
        "source_id": "moh_rwanda",
        "url": "https://moh.gov.rw"
    },
    {
        "id": "doc_41",
        "title": "What to Do When Feeling Unwell in an Unfamiliar Area in Rwanda",
        "content": "If you feel sick in an area or district of Rwanda you do not know, follow these practical steps. First, assess your symptoms: if you have red flag warning signs (such as chest pain, severe difficulty breathing, sudden severe bleeding, persistent vomiting, severe headache with stiff neck, or loss of consciousness), go immediately to the nearest hospital or call 112 or 912 for SAMU ambulance. For non-emergency symptoms (such as mild fever, cough, stomach upset, or minor pain), ask local residents for the nearest Health Centre (ivuriro in Kinyarwanda) or Health Post (poste de sante) in that sector or cell. Health centres provide outpatient consultations, malaria testing, rapid blood tests, and basic treatment. Always carry your National ID (Indangamuntu), your health insurance card or Mutuelle de Sante (CBHI) details, and any medication you take. If you have Mutuelle de Sante, public health centres will attend to you, and transfer you to the district hospital if advanced care is required.",
        "source_id": "moh_rwanda",
        "url": "https://moh.gov.rw"
    },
    {
        "id": "doc_42",
        "title": "Rwanda National Malaria Guidelines: Testing, Coartem Treatment and Prevention",
        "content": "Malaria is a major public health priority in Rwanda managed under the Rwanda Biomedical Centre (RBC) National Malaria Control Program. Fever, chills, sweating, muscle aches, and headache are typical signs. Rwanda national guidelines require mandatory diagnostic confirmation using a Rapid Diagnostic Test (RDT) or microscopy before taking anti-malarial medication. First-line treatment for confirmed uncomplicated Plasmodium falciparum malaria is oral Artemether-Lumefantrine (Coartem), taken with food or milk over three days. For severe or complicated malaria (such as cerebral malaria, severe anaemia, or vomiting everything), intravenous artesunate administered at a health centre or hospital is required. Prevention strategies in Rwanda include sleeping under long-lasting insecticidal nets (LLINs / inzitiramibu), indoor residual spraying (IRS) in high-risk districts, eliminating standing water, and seeking early testing on the same day fever begins, especially for pregnant women and children under five.",
        "source_id": "rbc_rwanda",
        "url": "https://rbc.gov.rw"
    },
    {
        "id": "doc_43",
        "title": "Rwanda Maternal, Newborn and Child Health: ANC Contacts, Delivery and Nutrition",
        "content": "Rwanda prioritizes maternal and child survival through structured care from pregnancy to childhood. Pregnant women should complete at least 8 Antenatal Care (ANC / CPN) visits at their local health centre starting in the first trimester. ANC includes ultrasound scans, blood pressure monitoring to detect pre-eclampsia early, tetanus vaccination, screening for anaemia and HIV, and iron-folic acid supplementation. Delivery should always take place at a health facility attended by skilled midwives or doctors. Danger signs during pregnancy requiring immediate hospital care are vaginal bleeding, severe headache with vision changes, swollen face and hands, high fever, or reduced baby movements. For child health, community health workers (Abajyanama b'ubuzima) and health centres monitor infant growth and provide the Shisha Kibondo supplementary nutrition program for vulnerable pregnant/lactating mothers and children under two to prevent malnutrition and stunting.",
        "source_id": "moh_rwanda",
        "url": "https://moh.gov.rw"
    },
    {
        "id": "doc_44",
        "title": "Rwanda National Guidelines: Tuberculosis (TB) and HIV Care (Treat All, TLD)",
        "content": "Rwanda provides free, comprehensive diagnosis and treatment for Tuberculosis (TB) and HIV at all public health facilities under RBC programs. Tuberculosis is diagnosed using rapid GeneXpert MTB/RIF testing and managed with a standard 6-month Directly Observed Therapy (DOTS) regimen; any cough lasting more than two weeks, night sweats, unexplained weight loss, or chest pain warrants TB testing. For HIV, Rwanda implements the Treat All policy: anyone testing positive on rapid HIV tests begins antiretroviral therapy (ART) promptly, typically with the first-line fixed-dose combination of Tenofovir, Lamivudine, and Dolutegravir (TLD). Regular viral load testing ensures viral suppression, which prevents disease progression and eliminates transmission. Prevention of mother-to-child transmission (PMTCT), Pre-Exposure Prophylaxis (PrEP), and emergency Post-Exposure Prophylaxis (PEP within 72 hours) are widely accessible.",
        "source_id": "rbc_rwanda",
        "url": "https://rbc.gov.rw"
    },
    {
        "id": "doc_45",
        "title": "Epidemic Preparedness in Rwanda: Marburg Virus, Mpox and Cholera Protocols",
        "content": "Rwanda maintains strict epidemic surveillance and infection prevention protocols under the Ministry of Health and RBC. Marburg Virus Disease (MVD) and Ebola are viral haemorrhagic fevers characterized by sudden high fever, severe headache, muscle aches, extreme fatigue, vomiting, diarrhea, and in severe stages, unexplained bleeding. Transmission occurs through direct contact with blood, body fluids, or contaminated items from infected persons. In any suspected outbreak or case, avoid contact, practice frequent hand hygiene, isolate immediately, and notify the Ministry of Health and RBC immediately via toll-free number 114. Cholera is prevented by drinking boiled or treated water, using latrines, and thorough handwashing; severe watery diarrhea requires immediate Oral Rehydration Salts (ORS) and urgent transfer to a health facility. Rwanda deploys rapid response teams, mobile laboratories, and dedicated treatment centers during epidemics.",
        "source_id": "rbc_rwanda",
        "url": "https://rbc.gov.rw"
    },
    {
        "id": "doc_46",
        "title": "Rwanda FDA Guidelines: Medicine Safety, Prescriptions and Antibiotic Stewardship",
        "content": "The Rwanda Food and Drugs Authority (Rwanda FDA) regulates pharmaceuticals, medical devices, and food safety across Rwanda. Medicines are divided into Over-The-Counter (OTC) drugs for mild self-limiting symptoms and Prescription-Only Medicines (POM) requiring a licensed clinician's prescription. In Rwanda, dispensing antibiotics without a valid medical prescription is strictly prohibited by law to prevent antimicrobial resistance (AMR). Patients must only buy medicines from licensed pharmacies (farumasi) or accredited health facility dispensaries, inspect packaging for tamper seals and expiry dates, and complete the full prescribed course. Never share medicines with others. Adverse drug reactions or substandard medications should be reported to the pharmacist, physician, or Rwanda FDA pharmacovigilance portal (toll-free 8444 or www.rfd.gov.rw).",
        "source_id": "fda_rwanda",
        "url": "https://rfd.gov.rw"
    },
    {
        "id": "doc_47",
        "title": "National Immunization Schedule and Preventable Diseases in Rwanda",
        "content": "Rwanda's Expanded Programme on Immunization (EPI / Gahunda y'Inkingo) provides free vaccines protecting against life-threatening childhood illnesses. At birth: BCG (tuberculosis) and Oral Polio Vaccine (OPV-0). At 6, 10, and 14 weeks: Pentavalent vaccine (Diphtheria, Tetanus, Pertussis, Hepatitis B, Haemophilus influenzae type b), Pneumococcal conjugate vaccine (PCV), Rotavirus vaccine, and Inactivated Polio Vaccine (IPV). At 9 months: Measles-Rubella 1 (MR-1) and Vitamin A. At 15 months: Measles-Rubella 2 (MR-2). Rwanda also conducts nationwide Human Papillomavirus (HPV) vaccination for girls aged 12 years in schools, achieving over 95% coverage to eliminate cervical cancer. Vaccines are delivered through health centres and community outreach, maintaining high immunity across the country.",
        "source_id": "rbc_rwanda",
        "url": "https://rbc.gov.rw"
    },
    {
        "id": "doc_48",
        "title": "Health Insurance in Rwanda: Mutuelle de Sante (CBHI), RAMA and Care Referrals",
        "content": "Over 90% of Rwandans are covered by health insurance, primarily Community-Based Health Insurance (CBHI / Mutuelle de Sante) managed by the Rwanda Social Security Board (RSSB), alongside RAMA (civil servants and private employees) and MMI (military). Under Mutuelle de Sante, patients receive care according to Rwanda's established referral system: first visit a Health Post or Sector Health Centre (Ivuriro); if specialist or surgical care is needed, the doctor issues a formal transfer (urusobane) to the District Hospital, which in turn can refer to a National Referral Hospital (such as CHUK, CHUB, RMH, King Faisal Hospital, or Ndera). Under Mutuelle, patient co-payments are minimal at health centres and 10% of hospital invoices. For life-threatening emergencies, any public hospital provides emergency care immediately without requiring prior transfer forms.",
        "source_id": "rssb_rwanda",
        "url": "https://rssb.rw"
    },
]


DEFAULT_DOCUMENTS = BASE_DOCUMENTS + PATIENT_GUIDANCE_DOCUMENTS
