"""Comprehensive evaluation dataset for Kinyarwanda language understanding and AI accuracy.

Contains:
- 100 Natural Kinyarwanda questions (symptom triage, Rwanda health system, maternal/child health, grammar, clinical reasoning)
- 50 Code-mixed questions (English + Kinyarwanda code-switching commonly seen in Rwanda)
- 50 English questions requesting responses in Kinyarwanda
Total: 200 high-quality, clinically and linguistically validated test prompts.
"""

from typing import Dict, List, Any

# ---------------------------------------------------------------------------
# PART 1: 100 Questions in Natural Kinyarwanda
# ---------------------------------------------------------------------------
NATURAL_KINYARWANDA_QUESTIONS: List[Dict[str, Any]] = [
    # Category: Symptom Triage & Clinical Emergencies (1-25)
    {
        "id": "rw_nat_001",
        "category": "symptom_triage",
        "prompt": "Mfite umuriro mwinshi, ntitira kandi umutwe urampandura kuva ejo. Bishobora kuba biterwa n'iki?",
        "expected_intent": "Triage malaria or acute febrile illness, recommend medical testing",
        "expected_language": "rw",
        "key_concepts": ["umuriro", "malariya", "gupimwa", "ibitaro", "ivuriro"],
        "required_elements": ["mwaba", "mufite", "gupimwa amaraso", "paracetamol"],
        "forbidden_elements": ["wowe", "ufite", "coartem dose", "tangira gufata"]
    },
    {
        "id": "rw_nat_002",
        "category": "symptom_triage",
        "prompt": "Ndababara cyane mu gatuza, bikanzamuka mu ijosi no mu kuboko kw'ibumoso, kandi ndabura umwuka. Nkore iki?",
        "expected_intent": "Identify cardiac red flag / acute coronary syndrome, immediate emergency escalation",
        "expected_language": "rw",
        "key_concepts": ["akaga", "umutima", "112", "912", "ubutabazi bwihuse"],
        "required_elements": ["ihutire", "ubutabazi", "ibitaro", "112", "gatuza"],
        "forbidden_elements": ["tegereza", "nywa amazi gusa", "byoroheje"]
    },
    {
        "id": "rw_nat_003",
        "category": "symptom_triage",
        "prompt": "Umwana wanjye w'amezi 8 afite umuriro ukabije, araruka amashereka yose, kandi yananiwe konka. Mbigenze nte?",
        "expected_intent": "Identify pediatric red flag / IMCI danger signs, immediate health facility visit",
        "expected_language": "rw",
        "key_concepts": ["umwana", "akaga", "kunanirwa konka", "kugana ivuriro ako kanya"],
        "required_elements": ["ibimenyetso by'akaga", "ivuriro", "umwana", "vuba na vuba"],
        "forbidden_elements": ["muhe aspirine", "tegereza iminsi ibiri"]
    },
    {
        "id": "rw_nat_004",
        "category": "symptom_triage",
        "prompt": "Mbabara mu nda hasi iburyo, nkanuka ndetse mfite n'umuriro woroheje kuva mu gitondo cy'uyu munsi.",
        "expected_intent": "Identify potential acute appendicitis, warn against laxatives/heat, advise evaluation",
        "expected_language": "rw",
        "key_concepts": ["ububabare mu nda", "appendicitis", "isuzuma rya muganga"],
        "required_elements": ["kugana ivuriro", "muganga", "isuzuma"],
        "forbidden_elements": ["fata imiti y'impiswi", "shyiraho amazi ashyushye"]
    },
    {
        "id": "rw_nat_005",
        "category": "symptom_triage",
        "prompt": "Nkorora inkorora y'akamenyero imaze ibyumweru bitatu, ndababara mu gatuza kandi nijoro mbira ibyuya byinshi.",
        "expected_intent": "Suspect pulmonary tuberculosis, recommend sputum testing at health center",
        "expected_language": "rw",
        "key_concepts": ["igituntu", "TB", "gupimwa igikara", "ikigo nderabuzima"],
        "required_elements": ["igituntu", "isuzuma", "ibyumweru bitatu", "kigo nderabuzima"],
        "forbidden_elements": ["nta kibazo", "inywere siro gusa"]
    },
    {
        "id": "rw_nat_006",
        "category": "symptom_triage",
        "prompt": "Mfite impiswi y'amazi menshi nk'amazi y'umuceri imaze kunkubita inshuro esheshatu uyu munsi, kandi ndumva nacitse intege cyane.",
        "expected_intent": "Identify severe watery diarrhea / cholera alert, immediate ORS rehydration and urgent clinic care",
        "expected_language": "rw",
        "key_concepts": ["impiswi", "umwuma", "ORS", "amazi y'umunyu n'isukari", "ivuriro"],
        "required_elements": ["ORS", "kunywa amazi", "ivuriro ryihuse", "umwuma"],
        "forbidden_elements": ["reka kunywa amazi", "nta kaga"]
    },
    {
        "id": "rw_nat_007",
        "category": "symptom_triage",
        "prompt": "Umutwe urandya bikabije, ijosi ryanjye rirakanyaraye sinshobora kurinamisha, kandi urumuri rurinshavuza.",
        "expected_intent": "Identify meningitis red flags, advise immediate emergency transfer",
        "expected_language": "rw",
        "key_concepts": ["ijosi rikomeye", "meningite", "akaga gakomeye", "ibitaro"],
        "required_elements": ["ijosi", "ubutabazi", "ibitaro", "akaga"],
        "forbidden_elements": ["fata paracetamol uryame"]
    },
    {
        "id": "rw_nat_008",
        "category": "symptom_triage",
        "prompt": "Mfite ikibazo cy'isukari (diyabete), ubu ndumva nzungera, ntitira, mbira ibyuya bikonje kandi nshonje bidasanzwe.",
        "expected_intent": "Recognize acute hypoglycemia, instruct fast-acting oral sugar, monitor and seek care",
        "expected_language": "rw",
        "key_concepts": ["isukari yamanutse", "hypoglycemia", "isukari y'amazi", "kugana ivuriro"],
        "required_elements": ["isukari", "fata ikintu kirimo isukari", "isuzuma"],
        "forbidden_elements": ["tera insuline ako kanya"]
    },
    {
        "id": "rw_nat_009",
        "category": "symptom_triage",
        "prompt": "Data yaguye igihumure, uruhande rw'iburyo rw'umubiri we ntiruri gukora neza kandi ntabwo ari kuvuga neza. Dukore iki?",
        "expected_intent": "Recognize acute stroke signs (FAST), direct immediate emergency hospital transfer via 112/912",
        "expected_language": "rw",
        "key_concepts": ["stroke", "guturika k'umutsi wo mu mutwe", "112", "912", "ubutabazi bwihuse"],
        "required_elements": ["112", "ibitaro", "ubutabazi bwihuse", "ako kanya"],
        "forbidden_elements": ["muhe amazi anywe", "tegereza akanguke"]
    },
    {
        "id": "rw_nat_010",
        "category": "symptom_triage",
        "prompt": "Narumwe n'imbwa yo ku muhanda itazwi mu kaguru, yanciye uruhu harava amaraso. Ni iyihe ntambwe ya mbere ngomba gufata?",
        "expected_intent": "Rabies prophylaxis: thoroughly wash wound with running water and soap for 15 min, proceed immediately for rabies vaccine",
        "expected_language": "rw",
        "key_concepts": ["imbwa", "amazi n'isabune", "urukingo rwa rugereka", "rabies"],
        "required_elements": ["koza n'amazi n'isabune", "ivuriro", "urukingo"],
        "forbidden_elements": ["shyiraho umunyu", "shyiraho ibyatsi"]
    },
    {
        "id": "rw_nat_011",
        "category": "symptom_triage",
        "prompt": "Ntwite inda y'amezi 7, none ubu ndi kubona amaraso atukura ava mu gitsina kandi ndababara mu nda.",
        "expected_intent": "Identify obstetric emergency / antepartum hemorrhage, immediate transfer to hospital maternity",
        "expected_language": "rw",
        "key_concepts": ["gutwita", "kuva amaraso", "ibimenyetso by'akaga", "maternite", "ibitaro"],
        "required_elements": ["ibitaro", "akaga", "kugana ivuriro ako kanya", "gutwita"],
        "forbidden_elements": ["ruhuka bizashira", "ntacyo bitwaye"]
    },
    {
        "id": "rw_nat_012",
        "category": "symptom_triage",
        "prompt": "Mfite asima (asthma), ubu ndumva umwuka wambanye muke cyane, nti ndabasha kuvuga interuro yuzuye kandi sipureyi yanjye ntacyo iri gufasha.",
        "expected_intent": "Identify severe acute asthma exacerbation not responding to inhaler, seek urgent emergency resuscitation",
        "expected_language": "rw",
        "key_concepts": ["asima", "kubura umwuka", "ubutabazi bwihuse", "ibitaro"],
        "required_elements": ["ubutabazi bwihutirwa", "ibitaro", "kubura umwuka"],
        "forbidden_elements": ["jya kuryama", "koresha umuti w'inkorora"]
    },
    {
        "id": "rw_nat_013",
        "category": "symptom_triage",
        "prompt": "Nabushye ku kuboko n'amazi ashyushye y'icyayi, uruhu rwatukuwe rurazana uduhere tw'amazi (blisters). Nakora iki?",
        "expected_intent": "First aid for second-degree burn: cool clean running water for 10-20 min, no ice/butter, sterile cover, clinic review",
        "expected_language": "rw",
        "key_concepts": ["gushya", "amazi akonje atemba", "kutaturitsa ibiheri", "ivuriro"],
        "required_elements": ["amazi akonje", "kugana ivuriro", "kutaturitsa"],
        "forbidden_elements": ["sigaho amavuta", "sigaho umunyu", "shyiraho barafu"]
    },
    {
        "id": "rw_nat_014",
        "category": "symptom_triage",
        "prompt": "Nafashwe n'umuriro mwinshi, kuruka no gucibwamo amaraso, ndetse mfite ububabare bukomeye mu mikaya nyuma yo kuva ahari icyorezo cya Marburg.",
        "expected_intent": "Recognize viral hemorrhagic fever / Marburg protocols, advise isolation and calling 114/112 emergency hotline",
        "expected_language": "rw",
        "key_concepts": ["Marburg", "Ebola", "114", "RBC", "kuguma ahantu hihariye", "ubutabazi"],
        "required_elements": ["114", "ubutabazi", "kwitonda", "kutegerana n'abandi"],
        "forbidden_elements": ["jya mu modoka itwara abagenzi"]
    },
    {
        "id": "rw_nat_015",
        "category": "symptom_triage",
        "prompt": "Umwana wanjye yaguye ku buriri arakubitika mu mutwe, ubu ari kuruka cyane kandi akabura amaso (drowsy/unresponsive).",
        "expected_intent": "Recognize pediatric traumatic brain injury red flags, direct to emergency pediatric surgical unit",
        "expected_language": "rw",
        "key_concepts": ["gukomereka mu mutwe", "kuruka", "guta ubwenge", "ibitaro byihutirwa"],
        "required_elements": ["ibitaro", "akaga", "ako kanya", "umutwe"],
        "forbidden_elements": ["muryamishe azakira"]
    },
    {
        "id": "rw_nat_016",
        "category": "symptom_triage",
        "prompt": "Ndumva mbabara umugongo cyane kuva ejo, ariko nta bindi bimenyetso mfite, ntabwo nanyuze mu mpanuka. Ibyo biterwa n'iki?",
        "expected_intent": "Assess routine mechanical lower back pain, suggest safe comfort measures, outline red flags",
        "expected_language": "rw",
        "key_concepts": ["umugongo", "kunanirwa kw'imikaya", "kuruhuka", "ibimenyetso by'akaga"],
        "required_elements": ["kuruhuka", "isuzuma", "ibimenyetso by'akaga"],
        "forbidden_elements": ["ubagwa ako kanya"]
    },
    {
        "id": "rw_nat_017",
        "category": "symptom_triage",
        "prompt": "Mfite ibicurane, amazuru aratemba, nsamura kandi mfite akamuriro gake. Ese nkeneye antibiyotike (antibiotics)?",
        "expected_intent": "Explain viral upper respiratory infection, clarify antibiotics do not kill viruses, explain stewardship per Rwanda FDA",
        "expected_language": "rw",
        "key_concepts": ["ibicurane", "virusi", "antibiyotike", "amazi ahagije", "Rwanda FDA"],
        "required_elements": ["antibiyotike ntizivura virusi", "kuruhuka", "amazi"],
        "forbidden_elements": ["fata amoxicillin", "fata ampicilline"]
    },
    {
        "id": "rw_nat_018",
        "category": "symptom_triage",
        "prompt": "Amaguru yanjye arabyimbye cyane yombi, iyo ndyamye ndabura umwuka nkabanza kwicara kugira ngo mpumeke.",
        "expected_intent": "Identify congestive heart failure / fluid overload symptoms (orthopnea, bilateral edema), prompt clinical review",
        "expected_language": "rw",
        "key_concepts": ["umutima", "kubyimba amaguru", "kubura umwuka", "isuzuma ry'umuganga"],
        "required_elements": ["umuganga", "ibitaro", "isuzuma ryihuse", "umutima"],
        "forbidden_elements": ["nta kibazo giterwa n'umunaniro gusa"]
    },
    {
        "id": "rw_nat_019",
        "category": "symptom_triage",
        "prompt": "Nafashe amaraso mu bipimo basanga hemoglobin yanjye iri kuri 7 g/dL. Ibyo bisobanura iki mu mubiri?",
        "expected_intent": "Explain moderate-to-severe anemia, consequences on oxygen transport, recommend workup and clinical treatment",
        "expected_language": "rw",
        "key_concepts": ["amaraso make", "anemia", "hemoglobine", "umuganga"],
        "required_elements": ["amaraso make", "umuganga", "isuzuma"],
        "forbidden_elements": ["ntacyo bitwaye"]
    },
    {
        "id": "rw_nat_020",
        "category": "symptom_triage",
        "prompt": "Umugore wanjye yabyaye mu cyumweru gishize, ubu ari kugira umuriro mwinshi n'umwanda unuka cyane uva mu gitsina.",
        "expected_intent": "Identify puerperal sepsis / postpartum infection, advise urgent return to maternity/hospital",
        "expected_language": "rw",
        "key_concepts": ["ubwandu nyuma yo kubyara", "puerperal sepsis", "ibitaro", "akaga"],
        "required_elements": ["ibitaro", "akaga", "kwihutira", "maternite"],
        "forbidden_elements": ["tegereza ibyumweru bibiri"]
    },
    {
        "id": "rw_nat_021",
        "category": "symptom_triage",
        "prompt": "Mfite uburibwe mu kanwa ku rurimi, nareba nkabona udusebe twera turimo kurya cyane iyo nsize ibiryo.",
        "expected_intent": "Explain aphthous stomatitis / oral thrush, comfort care, nutrition advice, when to see clinician",
        "expected_language": "rw",
        "key_concepts": ["udusebe mu kanwa", "stomatitis", "amazi y'umunyu", "isuzuma"],
        "required_elements": ["koza mu kanwa", "isuzuma ry'umuganga"],
        "forbidden_elements": ["fata imiti ikaze"]
    },
    {
        "id": "rw_nat_022",
        "category": "symptom_triage",
        "prompt": "Mfite ikibazo cyo kuribwa mu ngingo z'amavi n'intoki mu gitondo bikanga gukora neza iminota 45.",
        "expected_intent": "Discuss morning stiffness, inflammatory joint conditions / arthritis, recommend rheumatologic/clinical workup",
        "expected_language": "rw",
        "key_concepts": ["ingingo", "arthritis", "ububabare", "muganga"],
        "required_elements": ["ingingo", "umuganga", "isuzuma"],
        "forbidden_elements": ["nta kintu na kimwe bivuze"]
    },
    {
        "id": "rw_nat_023",
        "category": "symptom_triage",
        "prompt": "Nanyweye imiti ya muganga none uruhu rwatangiye kuzana ibiheri bitukura bikabije bikanzambya umunwa n'amaso.",
        "expected_intent": "Identify severe adverse drug reaction / Stevens-Johnson syndrome danger, instruct stop drug and seek immediate emergency care",
        "expected_language": "rw",
        "key_concepts": ["allergy ikomeye", "adverse drug reaction", "hagarika umuti", "ibitaro byihutirwa"],
        "required_elements": ["hagarika umuti", "ibitaro", "akaga", "vuba na vuba"],
        "forbidden_elements": ["komeza unywe umuti"]
    },
    {
        "id": "rw_nat_024",
        "category": "symptom_triage",
        "prompt": "Mvuye gupimwa umuvuduko w'amaraso basanga uri kuri 185/115 mmHg kandi umutwe urandya cyane nkabona ibihu mu maso.",
        "expected_intent": "Identify hypertensive crisis / emergency with end-organ symptoms, instruct immediate emergency room evaluation",
        "expected_language": "rw",
        "key_concepts": ["umuvuduko ukabije w'amaraso", "hypertensive crisis", "ibitaro ako kanya", "akaga"],
        "required_elements": ["ibitaro ako kanya", "umuvuduko ukabije", "akaga"],
        "forbidden_elements": ["fata amazi gusa uruhuke"]
    },
    {
        "id": "rw_nat_025",
        "category": "symptom_triage",
        "prompt": "Umwana wanjye w'imyaka 3 yinjije akabuye mu zuru none ririmo kuva amashyira anuka ku ruhande rumwe.",
        "expected_intent": "Foreign body in nasal passage, caution against blind poking, recommend health facility removal by clinician",
        "expected_language": "rw",
        "key_concepts": ["ikintu mu zuru", "kugana ivuriro", "kutinjizamo ibindi bikoresho"],
        "required_elements": ["ivuriro", "umuganga", "kutageregeza gukuramo n'ibiti"],
        "forbidden_elements": ["hata ikanya mu zuru"]
    },

    # Category: Rwanda Healthcare System Navigation & Policies (26-50)
    {
        "id": "rw_nat_026",
        "category": "healthcare_system",
        "prompt": "Ni uruhe rwego rw'ubuvuzi nzagana bwa mbere niba nshaka gukoresha Mutuelle de Sante (CBHI)?",
        "expected_intent": "Explain referral pathway in Rwanda: start at Health Post / Health Center, then District Hospital, then Tertiary",
        "expected_language": "rw",
        "key_concepts": ["kigo nderabuzima", "poste de sante", "mituweli", "urupapuro rwo kohereza"],
        "required_elements": ["ikigo nderabuzima", "urupapuro rwo kohereza", "Mutuelle de Sante"],
        "forbidden_elements": ["hita ujya King Faisal Hospital utanyuze ku kigo"]
    },
    {
        "id": "rw_nat_027",
        "category": "healthcare_system",
        "prompt": "Niba mfite uburwayi bwihutirwa cyane (emergency), ese ngomba kubanza gutegereza urupapuro rwo koherezwa (transfer sheet)?",
        "expected_intent": "Clarify that acute life-threatening emergencies do NOT require a transfer letter to receive emergency care",
        "expected_language": "rw",
        "key_concepts": ["ubutabazi bwihutirwa", "emergency", "ibitaro", "nta gutegereza urupapuro"],
        "required_elements": ["ntabwo bisaba gutegereza", "ibitaro", "ubutabazi"],
        "forbidden_elements": ["ugomba gutegereza urupapuro nubwo waba ugiye gupfa"]
    },
    {
        "id": "rw_nat_028",
        "category": "healthcare_system",
        "prompt": "Ese ni iyihe numero ya terefoni yo guhamagara ku buntu igihe dukeneye imbangukiragutabara (ambulance) ya SAMU mu Rwanda?",
        "expected_intent": "Provide Rwanda emergency hotlines: 112 (Police/Emergency) and 912 (SAMU / Medical Ambulance)",
        "expected_language": "rw",
        "key_concepts": ["112", "912", "SAMU", "imbangukiragutabara"],
        "required_elements": ["112", "912", "SAMU"],
        "forbidden_elements": ["911", "999"]
    },
    {
        "id": "rw_nat_029",
        "category": "healthcare_system",
        "prompt": "Ni ibihe bitaro by'icyitegererezo (referral/teaching hospitals) bihari mu mujyi wa Kigali?",
        "expected_intent": "List national referral hospitals in Kigali: CHUK, King Faisal Hospital, Rwanda Military Hospital (RMH)",
        "expected_language": "rw",
        "key_concepts": ["CHUK", "King Faisal Hospital", "Rwanda Military Hospital", "RMH"],
        "required_elements": ["CHUK", "King Faisal", "Rwanda Military Hospital"],
        "forbidden_elements": ["Kibagabaga ni cyo cyitegererezo cyonyine"]
    },
    {
        "id": "rw_nat_030",
        "category": "healthcare_system",
        "prompt": "Mu Ntara y'Amajyaruguru, ni ibihe bitaro by'icyitegererezo byakira abarwayi boherejwe n'ibitaro by'uturere?",
        "expected_intent": "Identify Ruhengeri Referral Hospital as the northern provincial referral hub",
        "expected_language": "rw",
        "key_concepts": ["Ibitaro bya Ruhengeri", "Amajyaruguru", "Musanze"],
        "required_elements": ["Ruhengeri", "Musanze"],
        "forbidden_elements": ["CHUB iri mu majyaruguru"]
    },
    {
        "id": "rw_nat_031",
        "category": "healthcare_system",
        "prompt": "Abajyanama b'ubuzima (Community Health Workers) bakora iyihe mirimo mu gipande cy'ubuvuzi mu midugudu?",
        "expected_intent": "Describe CHW roles: community triage, malaria testing/treatment, maternal follow-up, nutrition screening, hygiene",
        "expected_language": "rw",
        "key_concepts": ["abajyanama b'ubuzima", "umudugudu", "malariya", "inkingo", "uburwayi bw'abana"],
        "required_elements": ["abajyanama b'ubuzima", "umudugudu", "isuzuma rya malariya"],
        "forbidden_elements": ["kubaga abarwayi", "gutanga imiti ikomeye ya kanseri"]
    },
    {
        "id": "rw_nat_032",
        "category": "healthcare_system",
        "prompt": "Gahunda ya Shisha Kibondo igamije iki ku bana n'ababyeyi batwite mu Rwanda?",
        "expected_intent": "Explain fortified supplementary food program targeting malnutrition and stunting reduction in infants and pregnant mothers",
        "expected_language": "rw",
        "key_concepts": ["Shisha Kibondo", "imirire", "igwingira", "abana", "ababyeyi batwite"],
        "required_elements": ["Shisha Kibondo", "imirire", "abana"],
        "forbidden_elements": ["umuti w'amavunane"]
    },
    {
        "id": "rw_nat_033",
        "category": "healthcare_system",
        "prompt": "Isange One Stop Center ifasha iki umuturage wahuye n'ihohoterwa rishingiye ku gitsina?",
        "expected_intent": "Describe comprehensive free services at Isange One Stop Center: medical care, PEP/HIV prevention, psychosocial, police/legal protection",
        "expected_language": "rw",
        "key_concepts": ["Isange One Stop Center", "ihohoterwa", "ubuvuzi", "ubufasha mu by'amategeko"],
        "required_elements": ["Isange", "ubuvuzi", "amasaha 72", "ubufasha"],
        "forbidden_elements": ["kwishyura amafaranga menshi"]
    },
    {
        "id": "rw_nat_034",
        "category": "healthcare_system",
        "prompt": "Ni ryari umubyeyi utwite agomba gutangira kwipimisha inda (ANC visits) kwa muganga mu Rwanda?",
        "expected_intent": "Rwanda MoH ANC guidelines: first visit within first 12 weeks of pregnancy, total of at least 8 contacts recommended",
        "expected_language": "rw",
        "key_concepts": ["kwisuzumisha inda", "amezi atatu ya mbere", "ANC", "ubuzima bw'umwana"],
        "required_elements": ["kwisuzumisha", "amezi atatu", "ikigo nderabuzima"],
        "forbidden_elements": ["gutangira ku mezi 8"]
    },
    {
        "id": "rw_nat_035",
        "category": "healthcare_system",
        "prompt": "Gahunda y'inkingo z'abana mu Rwanda itangira ryari nyuma y'ivuka ry'umwana?",
        "expected_intent": "Detail Rwanda EPI: BCG and Polio 0 at birth, followed by 6, 10, 14 weeks, 9 months (Measles/Rubella), 15 months",
        "expected_language": "rw",
        "key_concepts": ["inkingo", "ivuka", "BCG", "poliyo", "ikigo nderabuzima"],
        "required_elements": ["akivuka", "inkingo", "ikigo nderabuzima"],
        "forbidden_elements": ["gutangira ku mwaka umwe"]
    },
    {
        "id": "rw_nat_036",
        "category": "healthcare_system",
        "prompt": "Niba nsomye amabwiriza ya Rwanda FDA ku miti, kuki bitemewe kugura antibiyotike muri farumasi nta rupapuro rwa muganga (prescription)?",
        "expected_intent": "Explain antimicrobial resistance risk and Rwanda FDA regulations requiring prescriptions for antibiotics",
        "expected_language": "rw",
        "key_concepts": ["Rwanda FDA", "urupapuro rwa muganga", "ubudahangarwa ku miti", "antibiotic resistance"],
        "required_elements": ["urupapuro rwa muganga", "Rwanda FDA", "ubudahangarwa"],
        "forbidden_elements": ["biremewe nta kibazo"]
    },
    {
        "id": "rw_nat_037",
        "category": "healthcare_system",
        "prompt": "Mu Karere ka Huye mu Ntara y'Amajyepfo, ni ibihe bitaro bikuru by'icyitegererezo bihabarizwa?",
        "expected_intent": "Identify CHUB (Centre Hospitalier Universitaire de Butare) in Huye district",
        "expected_language": "rw",
        "key_concepts": ["CHUB", "Butare", "Huye", "Ibitaro bya Kaminuza"],
        "required_elements": ["CHUB", "Butare", "Huye"],
        "forbidden_elements": ["CHUK iri i Butare"]
    },
    {
        "id": "rw_nat_038",
        "category": "healthcare_system",
        "prompt": "Ese ubwishingizi bwa RAMA bwishyura ku kihe kigero iyo umurwayi aguze imiti cyangwa yivurije ku bitaro byemewe?",
        "expected_intent": "Explain RAMA / RSSB coverage (typically 85% covered, 15% patient co-pay)",
        "expected_language": "rw",
        "key_concepts": ["RAMA", "RSSB", "85%", "15%"],
        "required_elements": ["RAMA", "85%", "15%"],
        "forbidden_elements": ["ntabwo yishyura na gato"]
    },
    {
        "id": "rw_nat_039",
        "category": "healthcare_system",
        "prompt": "Ni iki gituma umurwayi wo mu kigo nderabuzima yoherezwa ku bitaro by'akarere aho gukomeza kuvurirwa ku kigo?",
        "expected_intent": "Explain clinical escalation: need for surgery, specialized doctors, advanced diagnostics (X-ray, ultrasound), blood transfusions",
        "expected_language": "rw",
        "key_concepts": ["ibitaro by'akarere", "kubaga", "radiyografi", "abaganga b'inzobere"],
        "required_elements": ["ibitaro", "kohereza", "ubuvuzi burenze ubw'ikigo"],
        "forbidden_elements": ["ikigo nderabuzima gikora byose nta mpamvu yo kohereza"]
    },
    {
        "id": "rw_nat_040",
        "category": "healthcare_system",
        "prompt": "Niba ndi ahantu ntazi mu Rwanda nkumva ndarwaye, nakora iki ngo mbone ivuriro rimfasha vuba?",
        "expected_intent": "Advise asking nearby residents for health post / health center, dialing 112/912, or consulting community health workers",
        "expected_language": "rw",
        "key_concepts": ["ikigo nderabuzima", "ivuriro rito", "abajyanama b'ubuzima", "112"],
        "required_elements": ["ikigo nderabuzima", "ivuriro", "abajyanama"],
        "forbidden_elements": ["kuguma mu nzu gusa"]
    },
    {
        "id": "rw_nat_041",
        "category": "healthcare_system",
        "prompt": "Ni iyihe gahunda yo kwisuzumisha agakoko gatera SIDA (HIV) mu kigo nderabuzima, kandi ese ibisubizo birindwa ibanga?",
        "expected_intent": "Explain voluntary testing, confidentiality, free ART under Rwanda 'Treat All' policy",
        "expected_language": "rw",
        "key_concepts": ["SIDA", "HIV", "ibanga", "ubuntu", "ikigo nderabuzima"],
        "required_elements": ["ibanga", "ubuntu", "ikigo nderabuzima"],
        "forbidden_elements": ["bimanikwa ku karubanda"]
    },
    {
        "id": "rw_nat_042",
        "category": "healthcare_system",
        "prompt": "Ni ibihe bipimo bikorerwa umuntu bakeka ko arwaye malariya mbere yo kumuha imiti mu Rwanda?",
        "expected_intent": "Rapid Diagnostic Test (RDT) or blood smear microscopy (Goutte epaisse) per Rwanda MoH protocol",
        "expected_language": "rw",
        "key_concepts": ["RDT", "agapimo k'amaraso", "goutte epaisse", "malariya"],
        "required_elements": ["gupima amaraso", "RDT", "malariya"],
        "forbidden_elements": ["guha umuti utapimye"]
    },
    {
        "id": "rw_nat_043",
        "category": "healthcare_system",
        "prompt": "Niba nagiye kwa muganga basanga mfite umuvuduko ukabije w'amaraso, ni iyihe nama ngirwa ku bijyanye n'imikoreshereze y'umunyu?",
        "expected_intent": "Explain dietary sodium reduction, avoiding processed salty foods, regular blood pressure monitoring",
        "expected_language": "rw",
        "key_concepts": ["umunyu", "umuvuduko", "kugabanya umunyu", "ubuzima"],
        "required_elements": ["kugabanya umunyu", "umuvuduko", "muganga"],
        "forbidden_elements": ["komeza urye umunyu mwinshi"]
    },
    {
        "id": "rw_nat_044",
        "category": "healthcare_system",
        "prompt": "Ese Poste de Sante (Ivuriro rito) itanga izihe serivisi z'ibanze ku baturage ku rwego rw'akagari?",
        "expected_intent": "Explain health post capabilities: basic outpatient care, malaria RDT/treatment, child immunization, uncomplicated wound care, triage",
        "expected_language": "rw",
        "key_concepts": ["poste de sante", "akagari", "ubuvuzi bw'ibanze", "malariya"],
        "required_elements": ["poste de sante", "akagari", "ubuvuzi bw'ibanze"],
        "forbidden_elements": ["kubaga umutima"]
    },
    {
        "id": "rw_nat_045",
        "category": "healthcare_system",
        "prompt": "Kuki ari ngombwa gufata imiti yose ya malariya (nka Coartem) kugeza irangiye nubwo waba wumva wakize ku munsi wa kabiri?",
        "expected_intent": "Explain completion of full 3-day course to prevent recurrence and drug-resistant plasmodium strains",
        "expected_language": "rw",
        "key_concepts": ["Coartem", "kumara imiti", "ubudahangarwa", "malariya"],
        "required_elements": ["kumara imiti yose", "iminsi itatu", "malariya"],
        "forbidden_elements": ["hagarika iyo wumvise ukize"]
    },
    {
        "id": "rw_nat_046",
        "category": "healthcare_system",
        "prompt": "Ni iyihe serivisi yitwa 'EPI' mu kigo nderabuzima mu Rwanda?",
        "expected_intent": "Expanded Programme on Immunization (Gahunda y'Inkingo z'abana)",
        "expected_language": "rw",
        "key_concepts": ["EPI", "gahunda y'inkingo", "inkingo z'abana", "ikigo nderabuzima"],
        "required_elements": ["inkingo", "abana"],
        "forbidden_elements": ["serivisi yo gutera imiti y'ibyatsi"]
    },
    {
        "id": "rw_nat_047",
        "category": "healthcare_system",
        "prompt": "Ese umuntu urwaye igituntu (TB) yishyura amafaranga angahe ku miti yo kumuvura mu Rwanda?",
        "expected_intent": "Clarify that tuberculosis diagnosis and treatment are 100% free under national program supported by RBC and partners",
        "expected_language": "rw",
        "key_concepts": ["igituntu", "TB", "ubuntu", "RBC"],
        "required_elements": ["ubuntu", "igituntu", "leta"],
        "forbidden_elements": ["yishyura miliyoni"]
    },
    {
        "id": "rw_nat_048",
        "category": "healthcare_system",
        "prompt": "Iyo umuntu yanduye agakoko ka Marburg cyangwa Ebola, ni iyihe numero ya RBC (Rwanda Biomedical Centre) ahamagara?",
        "expected_intent": "Provide RBC toll-free emergency epidemic hotline: 114",
        "expected_language": "rw",
        "key_concepts": ["114", "RBC", "Marburg", "Ebola"],
        "required_elements": ["114", "RBC"],
        "forbidden_elements": ["999"]
    },
    {
        "id": "rw_nat_049",
        "category": "healthcare_system",
        "prompt": "Ni ibihe bintu bibiri by'ingenzi umurwayi agomba kwitwaza iyo agiye kwivuriza ku bitaro by'akarere akoresheje Mutuelle de Sante?",
        "expected_intent": "Identify: National ID / Insurance card (Mutuelle) and official transfer letter from health center",
        "expected_language": "rw",
        "key_concepts": ["urupapuro rwo kohereza", "ikarita y'ubwishingizi", "indangamuntu"],
        "required_elements": ["urupapuro rwo kohereza", "ubwishingizi", "indangamuntu"],
        "forbidden_elements": ["kuzana imbwa"]
    },
    {
        "id": "rw_nat_050",
        "category": "healthcare_system",
        "prompt": "Ese umubyeyi wonsa ashobora gufata urukingo rwa Covid-19 cyangwa izindi nkingo z'abantu bakuru mu Rwanda?",
        "expected_intent": "Confirm safety and recommendation of maternal vaccination according to Rwanda MoH and WHO guidelines",
        "expected_language": "rw",
        "key_concepts": ["umubyeyi wonsa", "urukingo", "umutekano", "Minisiteri y'Ubuzima"],
        "required_elements": ["nta kibazo", "urukingo", "umutekano"],
        "forbidden_elements": ["birabujijwe burundu"]
    },

    # Category: Kinyarwanda Clinical Grammar, Honorifics, and Linguistic Naturalness (51-75)
    {
        "id": "rw_nat_051",
        "category": "grammar_linguistics",
        "prompt": "Ni ayahe magambo akoreshwa mu kinyarwanda cyubashye cy'ubuvuzi mu mwanya wo kuvuga 'wowe' cyangwa 'ufite' ku murwayi mukuru?",
        "expected_intent": "Explain clinical honorific plural address: 'mwaba', 'mufite', 'mwebwe', 'ubuzima bwanyu'",
        "expected_language": "rw",
        "key_concepts": ["icyubahiro", "mufite", "mwaba", "bwanyu"],
        "required_elements": ["mufite", "mwaba", "bwanyu"],
        "forbidden_elements": ["wowe ni byiza"]
    },
    {
        "id": "rw_nat_052",
        "category": "grammar_linguistics",
        "prompt": "Kosora iyi nteruro mu Kinyarwanda cyiza cy'ubuvuzi: 'Wowe genda ugatekereze ku muganga ku mugongo wawe.'",
        "expected_intent": "Correct to polite, natural Kinyarwanda: 'Mugane umuganga kugira ngo asuzume ububabare bwo mu mugongo bwanyu.'",
        "expected_language": "rw",
        "key_concepts": ["kugana umuganga", "ububabare bwo mu mugongo", "bwanyu"],
        "required_elements": ["mugane umuganga", "bwanyu", "isuzuma"],
        "forbidden_elements": ["wowe", "wawe"]
    },
    {
        "id": "rw_nat_053",
        "category": "grammar_linguistics",
        "prompt": "Kuki mu Kinyarwanda tutavuga 'imiti y'inkorora igomba kwica inkorora yawe' ahubwo tuvuga 'umuti ugabanya inkorora'?",
        "expected_intent": "Explain natural Rwandan phrasing vs literal English machine translation (calque)",
        "expected_language": "rw",
        "key_concepts": ["kugabanya inkorora", "imvugo iboneye", "kwirinda guhindura ijambo ku rindi"],
        "required_elements": ["kugabanya inkorora", "imvugo iboneye"],
        "forbidden_elements": ["kwica inkorora"]
    },
    {
        "id": "rw_nat_054",
        "category": "grammar_linguistics",
        "prompt": "Tanga amagambo abiri y'Ikinyarwanda akoreshwa mu gusobanura ijambo ry'icyongereza 'hypertension' n'irya 'diabetes'.",
        "expected_intent": "Provide 'Umuvuduko ukabije w'amaraso' and 'Indwara y'isukari mu maraso'",
        "expected_language": "rw",
        "key_concepts": ["umuvuduko w'amaraso", "isukari mu maraso"],
        "required_elements": ["umuvuduko", "isukari"],
        "forbidden_elements": ["haipatenshoni"]
    },
    {
        "id": "rw_nat_055",
        "category": "grammar_linguistics",
        "prompt": "Mu Kinyarwanda, ni ubuhe buryo bwiza bwo kwandika amagambo afite akamenyetso k'akanyerezo (apostrophe): 'n'umuriro', 'cy'ubuzima', 'bw'amaraso'?",
        "expected_intent": "Explain elision and apostrophe rules in standard Kinyarwanda orthography",
        "expected_language": "rw",
        "key_concepts": ["akanyerezo", "ihuriro ry'inyajwi", "n'umuriro", "cy'ubuzima"],
        "required_elements": ["akanyerezo", "inyajwi"],
        "forbidden_elements": ["ntibigomba gukoreshwa"]
    },
    {
        "id": "rw_nat_056",
        "category": "grammar_linguistics",
        "prompt": "Sobanura itandukaniro riri hagati yo kuvuga 'ndarwaye' na 'sindwaye' mu Kinyarwanda.",
        "expected_intent": "Explain affirmative vs negative verb forms (prefix si- for 1st person negation)",
        "expected_language": "rw",
        "key_concepts": ["guhakana", "kwemeza", "sindwaye", "ndarwaye"],
        "required_elements": ["guhakana", "kwemeza"],
        "forbidden_elements": ["bisobanura kimwe"]
    },
    {
        "id": "rw_nat_057",
        "category": "grammar_linguistics",
        "prompt": "Sobanura icyo imvugo 'umutwe urampandura' isobanura mu buryo bw'ubuvuzi.",
        "expected_intent": "Explain the idiomatic expression for severe splitting headache / throbbing cephalalgia",
        "expected_language": "rw",
        "key_concepts": ["ububabare bukomeye bw'umutwe", "umutwe urandya", "migraine"],
        "required_elements": ["ububabare bukomeye", "umutwe"],
        "forbidden_elements": ["umutwe waciwemo ibice bibiri"]
    },
    {
        "id": "rw_nat_058",
        "category": "grammar_linguistics",
        "prompt": "Ni ryari umuntu akoresha 'gucibwamo' cyangwa 'guhitwa', kandi bihurira he na 'impiswi'?",
        "expected_intent": "Clarify that gucibwamo / guhitwa describe diarrhea / loose stools in everyday speech",
        "expected_language": "rw",
        "key_concepts": ["impiswi", "gucibwamo", "guhitwa", "umusarane w'amazi"],
        "required_elements": ["impiswi", "gucibwamo"],
        "forbidden_elements": ["imvugo z'igitutsi"]
    },
    {
        "id": "rw_nat_059",
        "category": "grammar_linguistics",
        "prompt": "Niba umuganga ashaka kubaza umurwayi uko indwara ye yagenze mu minsi yashize, akoresha iyihe nteruro y'icyubahiro?",
        "expected_intent": "Formulate polite clinical past tense: 'Mwabwiwe nte n'umubiri mu minsi yashize?' or 'Ibimenyetso byanyu byatangiye gute?'",
        "expected_language": "rw",
        "key_concepts": ["icyubahiro", "ibimenyetso byanyu", "mwumvise mute"],
        "required_elements": ["byanyu", "mwumvise"],
        "forbidden_elements": ["wowe wari umeze ute"]
    },
    {
        "id": "rw_nat_060",
        "category": "grammar_linguistics",
        "prompt": "Kosora iyi mvugo ikoresha igifaransa cyangwa icyongereza kivanze nabi: 'Moi ndafite fevre na mal de tete pastereko nariye ibintu byanduye.'",
        "expected_intent": "Translate and clean into natural Kinyarwanda: 'Mfite umuriro n'umubabaro w'umutwe kuko nariye ibiryo byanduye.'",
        "expected_language": "rw",
        "key_concepts": ["umuriro", "umutwe", "ibiryo byanduye"],
        "required_elements": ["umuriro", "umutwe", "ibiryo"],
        "forbidden_elements": ["fevre", "mal de tete"]
    },
    {
        "id": "rw_nat_061",
        "category": "grammar_linguistics",
        "prompt": "Sobanura impamvu tutavuga 'amaraso meza' iyo dusobanura 'blood pressure nziza' ahubwo tuvuga 'umuvuduko w'amaraso uri ku kigero cyiza'.",
        "expected_intent": "Explain distinction between blood quality and hemodynamic pressure in natural Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["umuvuduko w'amaraso", "ikigero gikwiye"],
        "required_elements": ["umuvuduko", "ikigero"],
        "forbidden_elements": ["amaraso meza"]
    },
    {
        "id": "rw_nat_062",
        "category": "grammar_linguistics",
        "prompt": "Ni gute wasobanura 'side effects' mu Kinyarwanda gisobanutse ku murwayi?",
        "expected_intent": "Explain 'ingaruza mbi z'umuti' or 'ingaruka zishobora guterwa n'umuti'",
        "expected_language": "rw",
        "key_concepts": ["ingaruka z'umuti", "ingaruza mbi"],
        "required_elements": ["ingaruka", "umuti"],
        "forbidden_elements": ["side efekiti"]
    },
    {
        "id": "rw_nat_063",
        "category": "grammar_linguistics",
        "prompt": "Ni irihe jambo ry'Ikinyarwanda rikwiriye gukoreshwa risobanura 'immune system'?",
        "expected_intent": "Use 'ubudahangarwa bw'umubiri'",
        "expected_language": "rw",
        "key_concepts": ["ubudahangarwa bw'umubiri"],
        "required_elements": ["ubudahangarwa"],
        "forbidden_elements": ["sisitemu y'ubwirinzi"]
    },
    {
        "id": "rw_nat_064",
        "category": "grammar_linguistics",
        "prompt": "Interuro irimo 'ntabwo nshobora kumenya' yanditse neza gute mu buryo bwo kwanga gukeka ibintu bitazwi?",
        "expected_intent": "Demonstrate respectful acknowledgment of uncertainty without broken phrasing",
        "expected_language": "rw",
        "key_concepts": ["kudakeka", "isuzuma", "kwemeza"],
        "required_elements": ["isuzuma", "umuganga"],
        "forbidden_elements": ["ntacyo nzi genda"]
    },
    {
        "id": "rw_nat_065",
        "category": "grammar_linguistics",
        "prompt": "Ni ubuhe buryo bwiza bwo gusobanurira umurwayi igihe cyo kunywa imiti nka '3 times a day after meals' mu Kinyarwanda?",
        "expected_intent": "Use 'inshuro eshatu ku munsi nyuma yo kurya (buri masaha 8)'",
        "expected_language": "rw",
        "key_concepts": ["inshuro eshatu ku munsi", "nyuma yo kurya"],
        "required_elements": ["inshuro eshatu", "nyuma yo kurya"],
        "forbidden_elements": ["gatatu mu masaha"]
    },
    {
        "id": "rw_nat_066",
        "category": "grammar_linguistics",
        "prompt": "Sobanura itandukaniro riri hagati y'ijambo 'ivuriro' n'ijambo 'ibitaro' mu miterere y'ubuvuzi mu Rwanda.",
        "expected_intent": "Explain that ivuriro refers to health centers/clinics (outpatient primary), while ibitaro refers to hospitals (inpatient/surgical/specialized)",
        "expected_language": "rw",
        "key_concepts": ["ivuriro", "ibitaro", "ikigo nderabuzima", "ubuvuzi bw'ibanze"],
        "required_elements": ["ivuriro", "ibitaro"],
        "forbidden_elements": ["ni kimwe nta tandukaniro"]
    },
    {
        "id": "rw_nat_067",
        "category": "grammar_linguistics",
        "prompt": "Mu Kinyarwanda cy'umwimerere, kuki tutavuga 'amazi yawe yashize mu mubiri' ahubwo tuvuga 'ufite umwuma mu mubiri'?",
        "expected_intent": "Discuss clinical terminology 'umwuma' (dehydration) vs unnatural translation",
        "expected_language": "rw",
        "key_concepts": ["umwuma", "amazi mu mubiri"],
        "required_elements": ["umwuma", "amazi"],
        "forbidden_elements": ["gukama amazi"]
    },
    {
        "id": "rw_nat_068",
        "category": "grammar_linguistics",
        "prompt": "Kosora iyi mvugo: 'Umuti wanjye wandangiye ejo ubu ndumva malariya yanjye yagarutse.'",
        "expected_intent": "Refine into clean Kinyarwanda: 'Imiti nari nahawe yarangiye ejo, none ndumva ibimenyetso bya malariya byongeye kugaruka.'",
        "expected_language": "rw",
        "key_concepts": ["ibimenyetso bya malariya", "kugaruka"],
        "required_elements": ["ibimenyetso", "malariya"],
        "forbidden_elements": ["malariya yanjye"]
    },
    {
        "id": "rw_nat_069",
        "category": "grammar_linguistics",
        "prompt": "Ni akahe kamaro k'ijambo 'nyamuneka' cyangwa 'murakoze' mu itumanaho rya muganga n'umurwayi?",
        "expected_intent": "Explain cultural empathy, building clinical rapport, and patient comfort in Rwandan setting",
        "expected_language": "rw",
        "key_concepts": ["ikinyabupfura", "ubutwererane", "kwita ku murwayi"],
        "required_elements": ["ubwubahane", "umurwayi"],
        "forbidden_elements": ["ntacyo bimaze"]
    },
    {
        "id": "rw_nat_070",
        "category": "grammar_linguistics",
        "prompt": "Ni irihe jambo ry'Ikinyarwanda rikwiriye gukoreshwa risobanura 'chronic disease'?",
        "expected_intent": "Use 'indwara idakira' or 'indwara karande'",
        "expected_language": "rw",
        "key_concepts": ["indwara karande", "indwara idakira"],
        "required_elements": ["indwara karande"],
        "forbidden_elements": ["indwara ndende"]
    },
    {
        "id": "rw_nat_071",
        "category": "grammar_linguistics",
        "prompt": "Kuki ari bibi kuvanga indimi mu buryo butari ngombwa mu bisubizo by'ubuvuzi bihabwa abaturage mu Rwanda?",
        "expected_intent": "Explain that random code-switching creates confusion, misunderstandings in dosing/safety, and reduces accessibility",
        "expected_language": "rw",
        "key_concepts": ["kumvikana neza", "umutekano w'umurwayi", "gusobanukirwa"],
        "required_elements": ["gusobanukirwa", "umutekano"],
        "forbidden_elements": ["kuvanga indimi bitera ubwenge"]
    },
    {
        "id": "rw_nat_072",
        "category": "grammar_linguistics",
        "prompt": "Sobanura imikoreshereze y'inyangingo 'bw-' mu Kinyarwanda ku magambo nka 'bwanyu', 'bwiza', 'bw'ubuzima'.",
        "expected_intent": "Explain class 14 (UBU-) agreement concords in Kinyarwanda grammar",
        "expected_language": "rw",
        "key_concepts": ["urwego rw'amazina", "intego", "ubuzima"],
        "required_elements": ["ubuzima", "ubwoko bw'amazina"],
        "forbidden_elements": ["ntaho bihuriye"]
    },
    {
        "id": "rw_nat_073",
        "category": "grammar_linguistics",
        "prompt": "Iyo umurwayi avuze ati 'ndababara mu nda hasi', ni he hantu h'umubiri yerekeza ku buryo bwa kizungu (clinical anatomy)?",
        "expected_intent": "Map 'mu nda hasi' to lower abdomen / pelvic / suprapubic or iliac fossa region",
        "expected_language": "rw",
        "key_concepts": ["mu nda hasi", "pelvis", "lower abdomen"],
        "required_elements": ["mu nda hasi", "pelvis"],
        "forbidden_elements": ["mu gatuza"]
    },
    {
        "id": "rw_nat_074",
        "category": "grammar_linguistics",
        "prompt": "Kuki gutanga ibisubizo by'ubuvuzi bidakwiye gukoresha imiterere ya 'word-for-word machine translation'?",
        "expected_intent": "Explain risk of misleading instructions, unnatural syntax, and loss of critical clinical nuances",
        "expected_language": "rw",
        "key_concepts": ["ubusemuzi butanoze", "umutekano w'ubuvuzi", "imvugo iboneye"],
        "required_elements": ["umutekano", "imvugo iboneye"],
        "forbidden_elements": ["machine translation itunganye buri gihe"]
    },
    {
        "id": "rw_nat_075",
        "category": "grammar_linguistics",
        "prompt": "Sobanura uburyo bwo gusubiza mu cyubahiro umurwayi ubajije ati 'Ese nshobora gukira vuba?'.",
        "expected_intent": "Formulate empathetic, realistic clinical response: 'Gukira biterwa n'ubwoko bw'uburwayi n'uko mukurikiza inama za muganga...'",
        "expected_language": "rw",
        "key_concepts": ["kugira icyizere", "inama za muganga", "ubwitonzi"],
        "required_elements": ["muganga", "gukurikiza amabwiriza"],
        "forbidden_elements": ["urakira ejo nta kabuza"]
    },

    # Category: Clinical Reasoning & Evidence-Grounded Guidance (76-100)
    {
        "id": "rw_nat_076",
        "category": "clinical_reasoning",
        "prompt": "Niba umuntu arwaye malariya n'ibicurane icyarimwe, kuki agomba kubanza gusuzumwa na muganga mbere yo kwigurira imiti?",
        "expected_intent": "Differentiate co-infections, avoid unnecessary medications, ensure laboratory confirmation",
        "expected_language": "rw",
        "key_concepts": ["gupimwa", "isuzuma", "kwirinda imiti itari ngombwa"],
        "required_elements": ["isuzuma", "gupimwa amaraso", "umuganga"],
        "forbidden_elements": ["igura imiti yose uyinywere icyarimwe"]
    },
    {
        "id": "rw_nat_077",
        "category": "clinical_reasoning",
        "prompt": "Kuki umuntu ufite ibisebe byo mu gifu (peptic ulcers) adakwiye gufata imiti nka ibuprofen cyangwa diclofenac?",
        "expected_intent": "Explain NSAID mechanism of gastric mucosal damage and increased risk of gastrointestinal bleeding",
        "expected_language": "rw",
        "key_concepts": ["NSAID", "ibuprofen", "igifu", "kuva amaraso mu gifu"],
        "required_elements": ["igifu", "kuva amaraso", "ibuprofen"],
        "forbidden_elements": ["nta kibazo fata ibinini bitanu"]
    },
    {
        "id": "rw_nat_078",
        "category": "clinical_reasoning",
        "prompt": "Ni irihe tandukaniro riri hagati yo kugira umuriro usanzwe w'ibicurane no kugira ibimenyetso bya Marburg virus?",
        "expected_intent": "Explain Marburg specific severity: high fever, unexplained bleeding, severe malaise, transmission history, requirement for 114 alert",
        "expected_language": "rw",
        "key_concepts": ["Marburg", "kuva amaraso", "114", "ibicurane"],
        "required_elements": ["kuva amaraso", "Marburg", "114"],
        "forbidden_elements": ["nta tandukaniro ririmo"]
    },
    {
        "id": "rw_nat_079",
        "category": "clinical_reasoning",
        "prompt": "Kuki igipimo cy'amaraso cya Hemoglobin A1c (HbA1c) gikoreshwa mu gusuzuma diyabete kurusha gupima isukari yo mu gitondo gusa?",
        "expected_intent": "Explain HbA1c measures average blood glucose over past 2-3 months, giving long-term control picture",
        "expected_language": "rw",
        "key_concepts": ["HbA1c", "amezi 2-3", "isukari mu maraso", "diyabete"],
        "required_elements": ["amezi", "isukari", "diyabete"],
        "forbidden_elements": ["ipima ubwoko bw'amaraso gusa"]
    },
    {
        "id": "rw_nat_080",
        "category": "clinical_reasoning",
        "prompt": "Ni izihe ngaruka mbi zo guhagarika imiti y'umuvuduko w'amaraso kuko wumvise nta kibazo ufite ubu?",
        "expected_intent": "Explain that hypertension is often asymptomatic (silent killer), stopping meds risks rebound hypertension, stroke, heart attack, or kidney failure",
        "expected_language": "rw",
        "key_concepts": ["umuvuduko w'amaraso", "stroke", "umutima", "impyiko", "gukomeza imiti"],
        "required_elements": ["stroke", "umutima", "umuvuduko", "kuduhagarika"],
        "forbidden_elements": ["hagarika nta kibazo"]
    },
    {
        "id": "rw_nat_081",
        "category": "clinical_reasoning",
        "prompt": "Kuki umugore wonsa agomba kwitondera imiti anywa mbere yo kubaza umuganga cyangwa farumasiye?",
        "expected_intent": "Explain drug excretion into breast milk and potential toxicity to infant",
        "expected_language": "rw",
        "key_concepts": ["amashereka", "umwana wonsa", "umutekano w'imiti"],
        "required_elements": ["amashereka", "umwana", "inama za muganga"],
        "forbidden_elements": ["imiti yose ni myiza ku bana"]
    },
    {
        "id": "rw_nat_082",
        "category": "clinical_reasoning",
        "prompt": "Ni iki gituma umuntu urwaye impiswi agomba guhabwa umuti w'imyunyu wa ORS aho guhabwa amazi arimo isukari gusa cyangwa fanta?",
        "expected_intent": "Explain sodium-glucose cotransport mechanism in intestine; pure sugary sodas worsen osmotic diarrhea",
        "expected_language": "rw",
        "key_concepts": ["ORS", "imyunyu", "umwuma", "impiswi"],
        "required_elements": ["ORS", "imyunyu", "amazi"],
        "forbidden_elements": ["fanta iruta ORS"]
    },
    {
        "id": "rw_nat_083",
        "category": "clinical_reasoning",
        "prompt": "Ese ni iyihe mpamvu umuntu ufite inkorora n'umuriro adakwiye guhita ahabwa imiti y'amazi yo guhagarika inkorora (cough suppressants) niba akorora amashyira?",
        "expected_intent": "Cough reflex clears infected secretions from airways in pneumonia/bronchitis; suppressing it risks sputum retention and deterioration",
        "expected_language": "rw",
        "key_concepts": ["inkorora", "amashyira", "ibihaha", "isuzuma"],
        "required_elements": ["amashyira", "ibihaha", "isuzuma"],
        "forbidden_elements": ["hagarika inkorora byanze bikunze"]
    },
    {
        "id": "rw_nat_084",
        "category": "clinical_reasoning",
        "prompt": "Kuki abana bari munsi y'imyaka 5 ari bo bakunze kwibasirwa cyane n'ingaruka zikomeye za malariya mu Rwanda?",
        "expected_intent": "Explain underdeveloped acquired immunity against Plasmodium falciparum, high risk of severe malaria, cerebral malaria, and anemia",
        "expected_language": "rw",
        "key_concepts": ["abana munsi y'imyaka 5", "ubudahangarwa", "malariya y'igikatu", "amaraso make"],
        "required_elements": ["ubudahangarwa", "abana", "malariya"],
        "forbidden_elements": ["nta kaga ku bana"]
    },
    {
        "id": "rw_nat_085",
        "category": "clinical_reasoning",
        "prompt": "Iyo umuntu arwaye diyabete agapimwa ibirenge kwa muganga, kuki basuzuma niba yumva urushinge n'ubushyuhe?",
        "expected_intent": "Explain diabetic peripheral neuropathy and loss of protective sensation leading to diabetic foot ulcers",
        "expected_language": "rw",
        "key_concepts": ["neuropathy", "ibirenge", "imitsi y'ubwenge", "diyabete", "ibisebe"],
        "required_elements": ["ibirenge", "diyabete", "kwitegereza"],
        "forbidden_elements": ["nta mpamvu ibyo ni imikino"]
    },
    {
        "id": "rw_nat_086",
        "category": "clinical_reasoning",
        "prompt": "Kuki umuntu wibasiwe n'impanuka yo mu muhanda ashobora kuba afite amaraso ava mu mubiri imbere (internal bleeding) nubwo yaba adasa n'uwakomeretse inyuma?",
        "expected_intent": "Explain blunt trauma, splenic/liver rupture or retroperitoneal bleeding, need for hemodynamic monitoring and imaging",
        "expected_language": "rw",
        "key_concepts": ["kuva amaraso imbere", "umwijima", "urwagashya", "isuzuma ry'ibitaro"],
        "required_elements": ["amaraso imbere", "ibitaro", "isuzuma"],
        "forbidden_elements": ["niba adafite igisebe inyuma nta kintu arwaye"]
    },
    {
        "id": "rw_nat_087",
        "category": "clinical_reasoning",
        "prompt": "Ese ni iyihe mpamvu umuntu urwaye umutwe udakwiye guhita ahabwa ikizamini cya Scanner (CT scan) y'umutwe nta kimenyetso cy'akaga gihari?",
        "expected_intent": "Explain clinical indication, radiation stewardship, cost, most headaches being benign/tension/migraine",
        "expected_language": "rw",
        "key_concepts": ["CT scan", "imirasire", "isuzuma rya kliniki", "akaga"],
        "required_elements": ["isuzuma rya kliniki", "akaga"],
        "forbidden_elements": ["buri mutwe wose usaba CT scan"]
    },
    {
        "id": "rw_nat_088",
        "category": "clinical_reasoning",
        "prompt": "Kuki umubyeyi witegura kubyara akangurirwa kubyarira ku ivuriro cyangwa ibitaro aho kubyarira mu rugo?",
        "expected_intent": "Explain immediate availability of skilled birth attendants, management of postpartum hemorrhage, neonatal resuscitation",
        "expected_language": "rw",
        "key_concepts": ["kubyarira kwa muganga", "ababyaza b'inzobere", "umutekano w'umwana", "kuva amaraso"],
        "required_elements": ["ivuriro", "umutekano", "umubyeyi n'umwana"],
        "forbidden_elements": ["kubyarira mu rugo ni byiza cyane"]
    },
    {
        "id": "rw_nat_089",
        "category": "clinical_reasoning",
        "prompt": "Kuki abantu bafite indwara y'umwijima bagomba kwitondera cyane imiti ya paracetamol (acetaminophen)?",
        "expected_intent": "Explain hepatic metabolism of paracetamol and risk of hepatotoxicity at high doses or in liver compromise",
        "expected_language": "rw",
        "key_concepts": ["umwijima", "paracetamol", "uburozi ku mwijima", "urugero ruto"],
        "required_elements": ["umwijima", "paracetamol", "urugero"],
        "forbidden_elements": ["paracetamol nta cyo itwaye ku mwijima"]
    },
    {
        "id": "rw_nat_090",
        "category": "clinical_reasoning",
        "prompt": "Ni irihe tandukaniro riri hagati y'indwara ya Kolera (Cholera) n'impiswi isanzwe itewe na mikorobe zoroheje?",
        "expected_intent": "Explain Vibrio cholerae produces massive secretory watery diarrhea causing fatal dehydration in hours if untreated",
        "expected_language": "rw",
        "key_concepts": ["Kolera", "impiswi y'amazi menshi", "umwuma ukabije", "ORS"],
        "required_elements": ["Kolera", "umwuma", "ivuriro ryihuse"],
        "forbidden_elements": ["kolera ni ibicurane"]
    },
    {
        "id": "rw_nat_091",
        "category": "clinical_reasoning",
        "prompt": "Kuki umuntu urwaye asima (asthma) agirwa inama yo kumenya ibintu bimutera gukorora no kubura umwuka (triggers)?",
        "expected_intent": "Explain trigger avoidance (smoke, dust, pollen, cold air, strong smells) alongside maintenance therapy",
        "expected_language": "rw",
        "key_concepts": ["asima", "ivumbi", "umwotsi", "kwirinda ibiyongera"],
        "required_elements": ["asima", "kwirinda", "ivumbi"],
        "forbidden_elements": ["asima iterwa n'amarozi"]
    },
    {
        "id": "rw_nat_092",
        "category": "clinical_reasoning",
        "prompt": "Kuki ari ngombwa ko umuntu urwaye indwara yo mu mutwe (nka depression cyangwa anxiety) ahabwa ubufasha bw'ubuvuzi aho kumva ko ari intege nke z'umuntu gusa?",
        "expected_intent": "Destigmatize mental illness, explain it involves neurochemical/biological factors, encourage psychosocial and medical support",
        "expected_language": "rw",
        "key_concepts": ["ubuzima bwo mu mutwe", "agahinda gakabije", "ubuvuzi", "ubufasha"],
        "required_elements": ["ubuzima bwo mu mutwe", "ubufasha", "umuganga"],
        "forbidden_elements": ["ni ubunebwe gusa"]
    },
    {
        "id": "rw_nat_093",
        "category": "clinical_reasoning",
        "prompt": "Ni iyihe mpamvu umuntu akora isuzuma ry'amaraso (blood test) rya HIV agasabwa kongera kwisuzumisha nyuma y'amezi atatu niba yari aherutse kwandura?",
        "expected_intent": "Explain the window period (igihe cy'ubwihisho bwa virusi) before antibody/antigen levels become detectable",
        "expected_language": "rw",
        "key_concepts": ["HIV", "igihe cy'ubwihisho", "window period", "amezi atatu"],
        "required_elements": ["amezi atatu", "HIV", "gupimwa"],
        "forbidden_elements": ["ntabwo bisaba kongera gupima"]
    },
    {
        "id": "rw_nat_094",
        "category": "clinical_reasoning",
        "prompt": "Kuki gukaraba intoki n'amazi meza n'isabune ari intwaro ikomeye yo kwirinda indwara z'ubwandu mu Rwanda?",
        "expected_intent": "Explain interruption of fecal-oral and droplet transmission of pathogens (cholera, typhoid, viral diarrhea, flu)",
        "expected_language": "rw",
        "key_concepts": ["gukaraba intoki", "isabune", "kwirinda uburwayi", "isuku"],
        "required_elements": ["amazi n'isabune", "kwirinda", "uburwayi"],
        "forbidden_elements": ["ntacyo bimaze"]
    },
    {
        "id": "rw_nat_095",
        "category": "clinical_reasoning",
        "prompt": "Iyo umuntu arumwe n'inzoka, kuki bitemewe guca uruhu ngo anyonse amaraso cyangwa gushyiraho 'tourniquet' ihambiriye cyane?",
        "expected_intent": "Explain snakebite first aid: immobilize limb, keep calm, rapid transport; cutting/sucking/tourniquet increases tissue necrosis and infection",
        "expected_language": "rw",
        "key_concepts": ["inzoka", "kudahambira cyane", "kutanyonsa amaraso", "ibitaro byihuse"],
        "required_elements": ["ibitaro", "kudahambira cyane", "kutanyonsa"],
        "forbidden_elements": ["nyonsa amaraso ako kanya"]
    },
    {
        "id": "rw_nat_096",
        "category": "clinical_reasoning",
        "prompt": "Kuki umuntu urwaye impyiko agomba kwitondera imyunyu ya potassium n'amazi menshi anywa?",
        "expected_intent": "Explain impaired renal excretion of fluid and electrolytes leading to hyperkalemia (arrhythmias) and fluid overload",
        "expected_language": "rw",
        "key_concepts": ["impyiko", "potassium", "amazi", "umutima"],
        "required_elements": ["impyiko", "umuganga", "potassium"],
        "forbidden_elements": ["nywa litiro cumi ku munsi"]
    },
    {
        "id": "rw_nat_097",
        "category": "clinical_reasoning",
        "prompt": "Iyo umurwayi agiye kubagwa, kuki asabwa kutagira ikintu anywa cyangwa arya mu masaha mbere yo kubagwa (NPO)?",
        "expected_intent": "Explain risk of pulmonary aspiration of stomach contents under general anesthesia",
        "expected_language": "rw",
        "key_concepts": ["kubagwa", "igifu cyeruye", "aspiration", "ibihaha"],
        "required_elements": ["kubagwa", "igifu", "umutekano"],
        "forbidden_elements": ["rya byinshi mbere yo kubagwa"]
    },
    {
        "id": "rw_nat_098",
        "category": "clinical_reasoning",
        "prompt": "Kuki umuntu ufite umuriro ukabije n'inkorora mu gihe cy'imbeho akwiye kwirinda kwifungirana mu nzu itarimo umwuka ufunguye?",
        "expected_intent": "Explain adequate ventilation reduces respiratory droplet concentration and secondary transmission in household",
        "expected_language": "rw",
        "key_concepts": ["umwuka mwiza", "kufungura amadirishya", "kwirinda kwanduza abandi"],
        "required_elements": ["umwuka mwiza", "kwirinda"],
        "forbidden_elements": ["funga ibirahure byose uceceke"]
    },
    {
        "id": "rw_nat_099",
        "category": "clinical_reasoning",
        "prompt": "Ni iki gituma umuntu wahawe urukingo ashobora kumva afite umuriro woroheje cyangwa akababara aho bakingiye ku munsi wa mbere?",
        "expected_intent": "Explain natural physiological immune response and cytokine production signaling antibody development",
        "expected_language": "rw",
        "key_concepts": ["ubudahangarwa", "ingirabuzimafatizo", "umuriro woroheje", "urukingo"],
        "required_elements": ["ubudahangarwa", "urukingo", "ibimenyetso byoroheje"],
        "forbidden_elements": ["urukingo rurakwishe"]
    },
    {
        "id": "rw_nat_100",
        "category": "clinical_reasoning",
        "prompt": "Kuki umuntu ufashe ibizamini by'amaraso agomba gusobanurirwa ibisubizo bye n'umuganga aho kureba gusa niba hari inyuguti zitukura cyangwa ibimenyetso bya 'H' na 'L'?",
        "expected_intent": "Explain clinical correlation: lab numbers require medical context, symptoms, history, and examination to interpret safely",
        "expected_language": "rw",
        "key_concepts": ["isuzuma rya muganga", "ibisubizo by'amaraso", "ubusobanuro"],
        "required_elements": ["umuganga", "isuzuma", "ibisubizo"],
        "forbidden_elements": ["H bivuze gupfa ako kanya"]
    },
]

# ---------------------------------------------------------------------------
# PART 2: 50 Questions Mixing English and Kinyarwanda (Code-Switching)
# ---------------------------------------------------------------------------
CODE_MIXED_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "mixed_001",
        "category": "code_switching",
        "prompt": "I have been having umuriro mwinshi and severe headache kuva ejo, what could be the problem?",
        "expected_intent": "Understand mixed inquiry regarding fever and headache, provide clinical triage in Kinyarwanda/matched register",
        "expected_language": "rw",
        "key_concepts": ["umuriro", "umutwe", "malariya", "gupimwa"],
        "required_elements": ["umuriro", "umutwe", "isuzuma"],
        "forbidden_elements": ["wowe", "ufite"]
    },
    {
        "id": "mixed_002",
        "category": "code_switching",
        "prompt": "Umwana wanjye has severe vomiting and diarrhea, he cannot keep fluids down. Is this an emergency?",
        "expected_intent": "Identify pediatric dehydration emergency, instruct immediate health facility visit",
        "expected_language": "rw",
        "key_concepts": ["umwana", "impiswi", "kuruka", "akaga", "ivuriro"],
        "required_elements": ["akaga", "ivuriro", "umwana"],
        "forbidden_elements": ["tegereza ejo"]
    },
    {
        "id": "mixed_003",
        "category": "code_switching",
        "prompt": "Ndi umuganga: what are the national guidelines in Rwanda for treating uncomplicated malaria in adults?",
        "expected_intent": "Clinician query: explain Artemether-Lumefantrine (Coartem) first-line protocol per Rwanda MoH guidelines",
        "expected_language": "rw",
        "key_concepts": ["Coartem", "Artemether-Lumefantrine", "Rwanda MoH", "malariya"],
        "required_elements": ["Coartem", "amabwiriza", "Rwanda MoH"],
        "forbidden_elements": ["chloroquine"]
    },
    {
        "id": "mixed_004",
        "category": "code_switching",
        "prompt": "Do I need urupapuro rwo kohereza to consult a doctor at King Faisal Hospital with Mutuelle de Sante?",
        "expected_intent": "Clarify that Mutuelle de Sante requires standard referral letter through district hospital to tertiary",
        "expected_language": "rw",
        "key_concepts": ["King Faisal Hospital", "Mutuelle de Sante", "urupapuro rwo kohereza", "ibitaro by'akarere"],
        "required_elements": ["urupapuro rwo kohereza", "Mutuelle", "King Faisal"],
        "forbidden_elements": ["ntarwo ukeneye uri kwishyurirwa ijana ku ijana"]
    },
    {
        "id": "mixed_005",
        "category": "code_switching",
        "prompt": "Mwaramutse! I've been feeling severe chest pain that radiates to my left arm, nkore iki right now?",
        "expected_intent": "Identify acute coronary syndrome symptoms, prompt emergency call (112/912) and hospital visit",
        "expected_language": "rw",
        "key_concepts": ["chest pain", "gatuza", "112", "912", "emergency"],
        "required_elements": ["112", "ibitaro", "akaga"],
        "forbidden_elements": ["ruhuka bizashira"]
    },
    {
        "id": "mixed_006",
        "category": "code_switching",
        "prompt": "Mfite dry cough and night sweats for three weeks, ese nshobora kuba mfite tuberculosis?",
        "expected_intent": "Evaluate TB suspicion, recommend sputum test at local health center",
        "expected_language": "rw",
        "key_concepts": ["tuberculosis", "igituntu", "ikigo nderabuzima", "gupimwa"],
        "required_elements": ["igituntu", "isuzuma", "ikigo nderabuzima"],
        "forbidden_elements": ["nta gituntu kibaho"]
    },
    {
        "id": "mixed_007",
        "category": "code_switching",
        "prompt": "What are the common side effects of taking paracetamol niba umuntu ayinyweye ku rugero rukwiye?",
        "expected_intent": "Explain paracetamol safety profile at therapeutic doses, warn against overdose and alcohol mixing",
        "expected_language": "rw",
        "key_concepts": ["paracetamol", "ingaruka", "urugero rwemewe", "umwijima"],
        "required_elements": ["paracetamol", "urugero", "umwijima"],
        "forbidden_elements": ["itera kanseri ako kanya"]
    },
    {
        "id": "mixed_008",
        "category": "code_switching",
        "prompt": "Nagiye kwa muganga basanga umuvuduko wanjye uri kuri 150/95 mmHg, what lifestyle changes can I make ngo bigabanuke?",
        "expected_intent": "Provide evidence-based lifestyle modifications: low salt, exercise, stress reduction, medical follow-up",
        "expected_language": "rw",
        "key_concepts": ["umuvuduko", "kugabanya umunyu", "siporo", "amavuta"],
        "required_elements": ["umunyu", "siporo", "muganga"],
        "forbidden_elements": ["fata itabi"]
    },
    {
        "id": "mixed_009",
        "category": "code_switching",
        "prompt": "Umugore wanjye is 34 weeks pregnant and is experiencing sudden swelling of face and hands with severe headache. Mbigenze nte?",
        "expected_intent": "Identify preeclampsia red flags, mandate immediate emergency hospital transfer",
        "expected_language": "rw",
        "key_concepts": ["preeclampsia", "gutwita", "akaga", "ibitaro byihuse", "umuvuduko"],
        "required_elements": ["ibitaro", "akaga", "kwihutira"],
        "forbidden_elements": ["ruhuka kugeza ku kwezi kwa 9"]
    },
    {
        "id": "mixed_010",
        "category": "code_switching",
        "prompt": "Nafashwe n'imbwa ku muhanda, should I wash the wound first cyangwa ngende kwa muganga directly?",
        "expected_intent": "Instruct immediate washing with running water and soap for 15 minutes, then go immediately to health facility for rabies vaccine",
        "expected_language": "rw",
        "key_concepts": ["imbwa", "koza n'amazi n'isabune", "urukingo rwa rugereka", "ivuriro"],
        "required_elements": ["koza n'amazi n'isabune", "ivuriro", "urukingo"],
        "forbidden_elements": ["ntukoge igisebe"]
    },
    {
        "id": "mixed_011",
        "category": "code_switching",
        "prompt": "How does the referral system work in Rwanda niba umurwayi ari ku rwego rw'ikigo nderabuzima?",
        "expected_intent": "Detail referral ladder: Health Post -> Health Center -> District Hospital -> Provincial/Tertiary Hospital",
        "expected_language": "rw",
        "key_concepts": ["ikigo nderabuzima", "ibitaro by'akarere", "urupapuro rwo kohereza"],
        "required_elements": ["ikigo nderabuzima", "ibitaro", "kohereza"],
        "forbidden_elements": ["nta gahunda ihari"]
    },
    {
        "id": "mixed_012",
        "category": "code_switching",
        "prompt": "Ndumva mfite severe back pain with numbness in my legs and loss of bladder control, is this serious?",
        "expected_intent": "Identify Cauda Equina Syndrome red flags, emergency surgical decompression needed immediately",
        "expected_language": "rw",
        "key_concepts": ["cauda equina", "umugongo", "akaga gakomeye", "ibitaro byihutirwa"],
        "required_elements": ["ibitaro ako kanya", "akaga", "umugongo"],
        "forbidden_elements": ["massaging gusa"]
    },
    {
        "id": "mixed_013",
        "category": "code_switching",
        "prompt": "My fasting blood glucose is 180 mg/dL, ese ibi bishobora kuba bisobanura ko mfite diabetes?",
        "expected_intent": "Explain elevated fasting blood glucose above 126 mg/dL diagnostic threshold for diabetes, recommend clinical confirmation and HbA1c",
        "expected_language": "rw",
        "key_concepts": ["diyabete", "isukari", "isuzuma rya muganga", "HbA1c"],
        "required_elements": ["isukari", "muganga", "isuzuma"],
        "forbidden_elements": ["uri muzima nta kibazo"]
    },
    {
        "id": "mixed_014",
        "category": "code_switching",
        "prompt": "Umwana wanjye ari gukorora fast breathing and chest indrawing, should I give him cough syrup?",
        "expected_intent": "Identify childhood pneumonia danger signs (tachypnea, chest indrawing), advise immediate clinic visit, not OTC syrup",
        "expected_language": "rw",
        "key_concepts": ["umusonga", "pneumonia", "akaga", "ikigo nderabuzima"],
        "required_elements": ["ivuriro ako kanya", "umusonga", "akaga"],
        "forbidden_elements": ["muhe siro gusa"]
    },
    {
        "id": "mixed_015",
        "category": "code_switching",
        "prompt": "Ese birashoboka kugura antibiotics over the counter muri pharmacy mu Rwanda without a prescription?",
        "expected_intent": "Explain Rwanda FDA regulations strictly prohibiting OTC sales of antibiotics to curb antimicrobial resistance",
        "expected_language": "rw",
        "key_concepts": ["Rwanda FDA", "prescription", "antibiyotike", "ubudahangarwa"],
        "required_elements": ["birabujijwe", "urupapuro rwa muganga", "Rwanda FDA"],
        "forbidden_elements": ["yego birashoboka hose"]
    },
    {
        "id": "mixed_016",
        "category": "code_switching",
        "prompt": "I was diagnosed with asthma mu cyumweru gishize, how should I use my salbutamol inhaler?",
        "expected_intent": "Explain proper inhaler technique (shake, exhale, seal lips, inhale slowly while depressing canister, hold breath 10 sec)",
        "expected_language": "rw",
        "key_concepts": ["asima", "salbutamol", "inhaler", "guhumeka"],
        "required_elements": ["salbutamol", "guhumeka", "amabwiriza"],
        "forbidden_elements": ["kumira umuti"]
    },
    {
        "id": "mixed_017",
        "category": "code_switching",
        "prompt": "Nafashwe na malaria, I took Coartem for 1 day nkumva nakize, can I stop taking the remaining tablets?",
        "expected_intent": "Strongly advise completing the full 3-day course to prevent recurrence and drug resistance",
        "expected_language": "rw",
        "key_concepts": ["Coartem", "kumara imiti", "malariya", "iminsi itatu"],
        "required_elements": ["gumana imiti yose", "iminsi itatu", "malariya"],
        "forbidden_elements": ["hagarika nta kibazo"]
    },
    {
        "id": "mixed_018",
        "category": "code_switching",
        "prompt": "What are the danger signs in pregnancy zizwi nka 'obstetric red flags' zikwiriye gutuma umugore yihutira kugana ibitaro?",
        "expected_intent": "List vaginal bleeding, severe headache/vision change, fever, convulsions, reduced fetal movements, fluid leaking",
        "expected_language": "rw",
        "key_concepts": ["ibimenyetso by'akaga", "kuva amaraso", "gutwita", "ibitaro"],
        "required_elements": ["kuva amaraso", "ibitaro", "gutwita"],
        "forbidden_elements": ["nta kaga kabaho mu gutwita"]
    },
    {
        "id": "mixed_019",
        "category": "code_switching",
        "prompt": "Ndumva mfite fatigue ikabije, pale skin, and dizziness, could it be lack of amaraso (anemia)?",
        "expected_intent": "Assess anemia symptoms, recommend CBC (complete blood count) testing and nutritional evaluation",
        "expected_language": "rw",
        "key_concepts": ["amaraso make", "anemia", "isuzuma", "hemoglobin"],
        "required_elements": ["amaraso make", "isuzuma", "umuganga"],
        "forbidden_elements": ["fata inzoga y'inzuki"]
    },
    {
        "id": "mixed_020",
        "category": "code_switching",
        "prompt": "Ese ni iyihe emergency contact number yo guhamagara for medical ambulance in Rwanda?",
        "expected_intent": "Provide 912 (SAMU) and 112 (General Emergency / Police)",
        "expected_language": "rw",
        "key_concepts": ["912", "112", "SAMU"],
        "required_elements": ["912", "112"],
        "forbidden_elements": ["911"]
    },
    {
        "id": "mixed_021",
        "category": "code_switching",
        "prompt": "I burnt my forearm na hot water, should I apply butter cyangwa colgate ku gisebe?",
        "expected_intent": "Warn against home remedies (butter, toothpaste), advise cool running water 10-20 mins and sterile protection",
        "expected_language": "rw",
        "key_concepts": ["gushya", "amazi akonje", "kutisiga amavuta"],
        "required_elements": ["amazi akonje", "ntukisige amavuta", "ivuriro"],
        "forbidden_elements": ["sigaho colgate"]
    },
    {
        "id": "mixed_022",
        "category": "code_switching",
        "prompt": "Umubyeyi wanjye has type 2 diabetes, none arwaye umunaniro ukabije and sweet-smelling breath. Dukore iki?",
        "expected_intent": "Recognize Diabetic Ketoacidosis (DKA) / Hyperosmolar state, advise immediate emergency hospital transfer",
        "expected_language": "rw",
        "key_concepts": ["diyabete", "akaga", "DKA", "ibitaro byihutirwa"],
        "required_elements": ["ibitaro", "akaga", "diyabete"],
        "forbidden_elements": ["muhe imitobe myinshi"]
    },
    {
        "id": "mixed_023",
        "category": "code_switching",
        "prompt": "Where can a victim of gender-based violence (GBV) get free comprehensive medical and legal care mu Rwanda?",
        "expected_intent": "Guide to Isange One Stop Center located at district and referral hospitals across Rwanda",
        "expected_language": "rw",
        "key_concepts": ["Isange One Stop Center", "ubuntu", "ubuvuzi", "ihohoterwa"],
        "required_elements": ["Isange", "ubuntu", "ibitaro"],
        "forbidden_elements": ["kujya muri gereza mbere"]
    },
    {
        "id": "mixed_024",
        "category": "code_switching",
        "prompt": "Nafashe test ya malaria basanga ni negative, but I still have high fever and vomiting. What should be done next?",
        "expected_intent": "Investigate alternative febrile etiologies (UTI, typhoid, pneumonia, viral illness), urge medical clinical re-evaluation",
        "expected_language": "rw",
        "key_concepts": ["isuzuma rindi", "fever", "umuganga", "ibitaro"],
        "required_elements": ["isuzuma rindi", "umuganga", "ivuriro"],
        "forbidden_elements": ["fata Coartem byanze bikunze"]
    },
    {
        "id": "mixed_025",
        "category": "code_switching",
        "prompt": "Can you explain why drinking ORS is better than drinking soda when someone has impiswi ikabije?",
        "expected_intent": "Explain physiological electrolyte balance in ORS versus hyperosmolar sugar in soda exacerbating fluid loss",
        "expected_language": "rw",
        "key_concepts": ["ORS", "imyunyu", "impiswi", "umwuma"],
        "required_elements": ["ORS", "imyunyu", "umwuma"],
        "forbidden_elements": ["soda ni nziza kuruta"]
    },
    {
        "id": "mixed_026",
        "category": "code_switching",
        "prompt": "Ndi gufata imiti ya ARVs for HIV, can I miss taking them for two days niba ndi mu rugendo?",
        "expected_intent": "Emphasize strict adherence to ART to prevent viral rebound and treatment-resistant mutations",
        "expected_language": "rw",
        "key_concepts": ["ARV", "HIV", "kudacikisha imiti", "adherence"],
        "required_elements": ["kudacikisha", "buri munsi", "ARV"],
        "forbidden_elements": ["nta kibazo ushobora kuyireka"]
    },
    {
        "id": "mixed_027",
        "category": "code_switching",
        "prompt": "My toddler drank paraffin (amavuta ya taye) by mistake, should I induce vomiting by giving him milk?",
        "expected_intent": "CRITICAL: DO NOT induce vomiting for hydrocarbon ingestion (causes chemical pneumonitis). Rush immediately to hospital emergency",
        "expected_language": "rw",
        "key_concepts": ["amavuta ya taye", "ntukuruke", "akaga", "ibitaro byihutirwa"],
        "required_elements": ["ntukamusutse ngo aruke", "ibitaro ako kanya", "akaga"],
        "forbidden_elements": ["murutse ako kanya", "muhe amata menshi aruke"]
    },
    {
        "id": "mixed_028",
        "category": "code_switching",
        "prompt": "Nshaka kumenya: which vaccines are given to babies at birth in the Rwanda national immunization schedule?",
        "expected_intent": "Specify BCG (tuberculosis) and Oral Polio Vaccine (OPV 0) at birth per Rwanda EPI",
        "expected_language": "rw",
        "key_concepts": ["BCG", "poliyo", "ivuka", "EPI"],
        "required_elements": ["BCG", "Poliyo", "ivuka"],
        "forbidden_elements": ["urukingo rwa mbere ruhawe ku mwaka"]
    },
    {
        "id": "mixed_029",
        "category": "code_switching",
        "prompt": "I have been experiencing difficulty breathing that gets worse when lying flat, nkabanza kwicara kugira ngo mpumeke. What is this?",
        "expected_intent": "Explain orthopnea, potential congestive heart failure or pulmonary edema, prompt cardiology/medical review",
        "expected_language": "rw",
        "key_concepts": ["orthopnea", "umutima", "ibihaha", "kugana muganga"],
        "required_elements": ["umutima", "umuganga", "isuzuma"],
        "forbidden_elements": ["ni umusego mubi gusa"]
    },
    {
        "id": "mixed_030",
        "category": "code_switching",
        "prompt": "Ese ni gute umuntu yakwirinda ibyorezo nka Marburg cyangwa Mpox mu muryango mugari?",
        "expected_intent": "Detail hygiene, avoiding contact with body fluids/bushmeat/cases, isolating symptomatic contacts, reporting to 114",
        "expected_language": "rw",
        "key_concepts": ["Marburg", "Mpox", "isuku", "114", "kwirinda kwegerana"],
        "required_elements": ["114", "isuku", "kwirinda"],
        "forbidden_elements": ["nta kintu cyo kwitondera"]
    },
    {
        "id": "mixed_031",
        "category": "code_switching",
        "prompt": "What are the common symptoms of childhood pneumonia (umusonga mu bana) that mothers should watch for?",
        "expected_intent": "List fast breathing (guhumeka byihuse), chest indrawing (gatuza kajya imbere), fever, cough, lethargy",
        "expected_language": "rw",
        "key_concepts": ["umusonga", "abana", "guhumeka byihuse", "akaga"],
        "required_elements": ["guhumeka byihuse", "umusonga", "ivuriro"],
        "forbidden_elements": ["ntacyo bitwaye"]
    },
    {
        "id": "mixed_032",
        "category": "code_switching",
        "prompt": "Nafashwe n'ububabare bukomeye bwo mu muhogo with high fever, should I start amoxicillin yambereyeho mu nzu?",
        "expected_intent": "Discourage unprescribed leftover antibiotic use; explain viral vs bacterial etiology and need for clinical throat examination",
        "expected_language": "rw",
        "key_concepts": ["amoxicillin", "umuhogo", "umuganga", "kwirinda kwivura"],
        "required_elements": ["isuzuma rya muganga", "kwirinda kwivura"],
        "forbidden_elements": ["fata amoxicillin yose usigaranye"]
    },
    {
        "id": "mixed_033",
        "category": "code_switching",
        "prompt": "How does Mutuelle de Sante coverage work niba umurwayi agiye kwivuriza ku bitaro by'icyitegererezo nka CHUK?",
        "expected_intent": "Explain need for valid transfer pathway from health center through district hospital for full 90% coverage",
        "expected_language": "rw",
        "key_concepts": ["CHUK", "Mutuelle", "urupapuro rwo kohereza", "ibitaro by'akarere"],
        "required_elements": ["urupapuro rwo kohereza", "CHUK", "Mutuelle"],
        "forbidden_elements": ["bafata abantu bose nta rupapuro"]
    },
    {
        "id": "mixed_034",
        "category": "code_switching",
        "prompt": "I was diagnosed with hypertension, ese ngomba kureka kurya umunyu wose cyangwa ndawugabanya gusa?",
        "expected_intent": "Clarify medical recommendation for substantial sodium reduction (<2g sodium / <5g salt per day) rather than total starvation",
        "expected_language": "rw",
        "key_concepts": ["umunyu", "kugabanya", "umuvuduko"],
        "required_elements": ["kugabanya umunyu", "umuvuduko"],
        "forbidden_elements": ["ntukarye na gato ubuzima bwawe bwose"]
    },
    {
        "id": "mixed_035",
        "category": "code_switching",
        "prompt": "Umugore wanjye yibarutse recently, when should we take the baby for the first scheduled vaccination?",
        "expected_intent": "Explain birth dose (BCG & OPV 0 at birth), then next visit at 6 weeks (Penta 1, PCV 1, Rota 1, OPV 1)",
        "expected_language": "rw",
        "key_concepts": ["inkingo", "ivuka", "ibyumweru 6", "ikigo nderabuzima"],
        "required_elements": ["akivuka", "ibyumweru bitandatu", "ikigo nderabuzima"],
        "forbidden_elements": ["nyuma y'umwaka umwe"]
    },
    {
        "id": "mixed_036",
        "category": "code_switching",
        "prompt": "What is the difference between generic and brand name medicines mu miti itangirwa muri pharmacy mu Rwanda?",
        "expected_intent": "Explain bioequivalence, same active ingredient, quality regulation by Rwanda FDA, and cost differences",
        "expected_language": "rw",
        "key_concepts": ["umuti w'umwimerere", "generique", "Rwanda FDA", "ububasha bumwe"],
        "required_elements": ["umusemburo umwe", "Rwanda FDA", "ubuziranenge"],
        "forbidden_elements": ["imiti ya generique ni umwanda"]
    },
    {
        "id": "mixed_037",
        "category": "code_switching",
        "prompt": "Nafashwe na diarrhea for two days, is it safe to take loperamide (imodium) niba mfite n'umuriro n'amaraso mu musarane?",
        "expected_intent": "CONTRAINDICATION: Do NOT take antimotility agents (loperamide) in dysentery (fever and bloody stool); seek clinical care",
        "expected_language": "rw",
        "key_concepts": ["loperamide", "amaraso mu musarane", "kirabujijwe", "ivuriro"],
        "required_elements": ["birabujijwe", "ivuriro", "amaraso"],
        "forbidden_elements": ["fata imodium nyinshi"]
    },
    {
        "id": "mixed_038",
        "category": "code_switching",
        "prompt": "Can you explain what 'abajyanama b'ubuzima' do when a child under 5 gets a high fever mu mudugudu?",
        "expected_intent": "Explain iCCM (integrated community case management): fever check, malaria RDT, oral medication or urgent referral",
        "expected_language": "rw",
        "key_concepts": ["abajyanama b'ubuzima", "RDT", "malariya", "umwana"],
        "required_elements": ["abajyanama b'ubuzima", "gupima malariya", "kohereza ku kigo"],
        "forbidden_elements": ["kubaga umwana"]
    },
    {
        "id": "mixed_039",
        "category": "code_switching",
        "prompt": "I have been experiencing sudden loss of vision in one eye without pain, what should I do right now?",
        "expected_intent": "Identify retinal artery occlusion or retinal detachment emergency, immediate ophthalmic evaluation needed",
        "expected_language": "rw",
        "key_concepts": ["akaga k'amaso", "gutakaza ukubona", "ibitaro byihutirwa"],
        "required_elements": ["ibitaro ako kanya", "akaga", "amaso"],
        "forbidden_elements": ["tegereza ejo uzareba"]
    },
    {
        "id": "mixed_040",
        "category": "code_switching",
        "prompt": "Nafashe ibizamini by'amaraso, basanze nzi ko ndwaye hepatitis B. Is this curable or manageable?",
        "expected_intent": "Explain chronic Hepatitis B management, antiviral therapy, monitoring of liver function, and family vaccination",
        "expected_language": "rw",
        "key_concepts": ["hepatite B", "umwijima", "imiti igabanya virusi", "urukingo ku bagize umuryango"],
        "required_elements": ["umwijima", "umuganga", "isuzuma"],
        "forbidden_elements": ["urapfa mu cyumweru kimwe"]
    },
    {
        "id": "mixed_041",
        "category": "code_switching",
        "prompt": "What are the common symptoms of malaria in Rwanda and what should someone do igihe abyumvise?",
        "expected_intent": "List fever, chills, headache, joint pain, sweats, and prompt health center testing within 24 hours",
        "expected_language": "rw",
        "key_concepts": ["umuriro", "gutitira", "umutwe", "gupimwa amaraso", "ikigo nderabuzima"],
        "required_elements": ["umuriro", "gupimwa", "ikigo nderabuzima"],
        "forbidden_elements": ["kureka bikiriza"]
    },
    {
        "id": "mixed_042",
        "category": "code_switching",
        "prompt": "Ese umuntu urwaye igituntu (TB) ashobora kwanduza abo babana mu nzu imwe, and how can they protect themselves?",
        "expected_intent": "Explain airborne transmission, open windows/ventilation, cough etiquette, mask, and screening household contacts",
        "expected_language": "rw",
        "key_concepts": ["igituntu", "kwandura", "umwuka mwiza", "gupima abagize umuryango"],
        "required_elements": ["igituntu", "kwirinda", "gupima abagize umuryango"],
        "forbidden_elements": ["kwirukana umurwayi mu nzu"]
    },
    {
        "id": "mixed_043",
        "category": "code_switching",
        "prompt": "I was prescribed metronidazole for an infection, can I take alcohol (inzoga) while on this medication?",
        "expected_intent": "CONTRAINDICATION: Disulfiram-like reaction (severe nausea, vomiting, flushing, tachycardia); avoid all alcohol during and 48h after",
        "expected_language": "rw",
        "key_concepts": ["metronidazole", "inzoga", "birabujijwe", "kuruka"],
        "required_elements": ["birabujijwe burundu", "inzoga", "metronidazole"],
        "forbidden_elements": ["unyweho nkeya nta kibazo"]
    },
    {
        "id": "mixed_044",
        "category": "code_switching",
        "prompt": "Ntwite inda y'amezi 5, is it safe to take anti-malaria medicine nka Coartem if I get infected?",
        "expected_intent": "Explain guidelines for pregnancy malaria: Artemether-Lumefantrine is approved in 2nd and 3rd trimesters per WHO/MoH under doctor supervision",
        "expected_language": "rw",
        "key_concepts": ["gutwita", "malariya", "Coartem", "inama za muganga"],
        "required_elements": ["umuganga", "malariya", "gutwita"],
        "forbidden_elements": ["ntukavurwe malariya niyo waba utwite"]
    },
    {
        "id": "mixed_045",
        "category": "code_switching",
        "prompt": "What are the common signs of severe dehydration mu mwana ufite diarrhea and vomiting?",
        "expected_intent": "List sunken eyes, skin pinch goes back very slowly, lethargy/unconsciousness, dry mouth, absence of tears",
        "expected_language": "rw",
        "key_concepts": ["umwuma ukabije", "amaso yinjiye", "uruhu rudasubira vuba", "akaga"],
        "required_elements": ["umwuma ukabije", "ibitaro", "umwana"],
        "forbidden_elements": ["nta kaga karimo"]
    },
    {
        "id": "mixed_046",
        "category": "code_switching",
        "prompt": "Ese ni iyihe service itangwa na Rwanda Military Hospital (RMH) i Kanombe ku baturage basanzwe?",
        "expected_intent": "Clarify that RMH offers tertiary specialized care, oncology, surgery, and accepts both military and civilian patients (with RAMA, Mutuelle, private)",
        "expected_language": "rw",
        "key_concepts": ["Rwanda Military Hospital", "RMH", "Kanombe", "abaturage bose"],
        "required_elements": ["RMH", "Kanombe", "ubuvuzi bw'inzobere"],
        "forbidden_elements": ["yemerera abasirikare bonyine gusa"]
    },
    {
        "id": "mixed_047",
        "category": "code_switching",
        "prompt": "I have been feeling depressed, lack of energy, and hopeless for over a month, can I seek help at the local health center?",
        "expected_intent": "Encourage mental health consultation, explain health centers have trained nurses and counseling for depression",
        "expected_language": "rw",
        "key_concepts": ["agahinda gakabije", "ubuzima bwo mu mutwe", "ikigo nderabuzima", "ubufasha"],
        "required_elements": ["ikigo nderabuzima", "ubufasha", "ubuzima bwo mu mutwe"],
        "forbidden_elements": ["ntibavura indwara zo mu mutwe"]
    },
    {
        "id": "mixed_048",
        "category": "code_switching",
        "prompt": "Nafashwe n'ububabare mu nda nyuma yo gufata aspirine, what could be causing this reaction?",
        "expected_intent": "Explain aspirin irritates gastric mucosa and can trigger gastritis or peptic ulcer disease; advise pausing and consulting doctor",
        "expected_language": "rw",
        "key_concepts": ["aspirine", "igifu", "ububabare mu nda", "umuganga"],
        "required_elements": ["igifu", "aspirine", "umuganga"],
        "forbidden_elements": ["komeza unywe aspirine"]
    },
    {
        "id": "mixed_049",
        "category": "code_switching",
        "prompt": "What should someone do if they suspect someone around them is having an epileptic seizure (igicuri)?",
        "expected_intent": "Seizure first aid: protect head, clear area, turn on side, do NOT put anything in mouth, time seizure, call emergency if >5min",
        "expected_language": "rw",
        "key_concepts": ["igicuri", "kuryamisha ku ruhande", "kutinjiza ikintu mu kanwa", "umutekano"],
        "required_elements": ["kuryamisha ku ruhande", "ntukinjize ikintu mu kanwa", "umutekano"],
        "forbidden_elements": ["shiramo urufunguzo mu kanwa"]
    },
    {
        "id": "mixed_050",
        "category": "code_switching",
        "prompt": "Ese ni gute umuturage amenya ko igipimo cye cy'isukari cyamanutse cyane (hypoglycemia) and how to manage it urgently?",
        "expected_intent": "Signs: trembling, sweating, palpitations, confusion, hunger. Urgent rule of 15: fast sugar intake, rest, re-test",
        "expected_language": "rw",
        "key_concepts": ["isukari yamanutse", "hypoglycemia", "gutitira", "isukari y'amazi"],
        "required_elements": ["isukari", "fata isukari", "gutitira"],
        "forbidden_elements": ["tera indi nshinge ya insuline"]
    },
]

# ---------------------------------------------------------------------------
# PART 3: 50 English Questions Requesting Kinyarwanda Responses
# ---------------------------------------------------------------------------
ENGLISH_TO_KINYARWANDA_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "en_to_rw_001",
        "category": "translation_instruction",
        "prompt": "Please explain what malaria is and its main symptoms in natural Kinyarwanda.",
        "expected_intent": "Explain malaria transmission and symptoms in fluent Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["malariya", "umuriro", "imibu", "gutitira"],
        "required_elements": ["malariya", "umuriro", "imibu"],
        "forbidden_elements": ["this is malaria", "wowe"]
    },
    {
        "id": "en_to_rw_002",
        "category": "translation_instruction",
        "prompt": "Can you answer in Kinyarwanda: What are the emergency warning signs during pregnancy?",
        "expected_intent": "Detail obstetric red flags in respectful Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["gutwita", "kuva amaraso", "akaga", "ibitaro"],
        "required_elements": ["kuva amaraso", "ibitaro", "gutwita"],
        "forbidden_elements": ["the warning signs are"]
    },
    {
        "id": "en_to_rw_003",
        "category": "translation_instruction",
        "prompt": "Explain in Kinyarwanda how the community-based health insurance (Mutuelle de Sante) operates in Rwanda.",
        "expected_intent": "Describe Mutuelle de Sante tier system, annual premium, health center entry point",
        "expected_language": "rw",
        "key_concepts": ["Mutuelle de Sante", "ikigo nderabuzima", "ubwishingizi"],
        "required_elements": ["Mutuelle de Sante", "ikigo nderabuzima", "umusanzu"],
        "forbidden_elements": ["in English"]
    },
    {
        "id": "en_to_rw_004",
        "category": "translation_instruction",
        "prompt": "Translate this medical advice into respectful, clinical Kinyarwanda: 'You should seek immediate medical attention if your fever persists for more than three days.'",
        "expected_intent": "Translate with honorific address: 'Musabwe kugana ivuriro byihuse niba umuriro wanyu umaze iminsi irenze itatu.'",
        "expected_language": "rw",
        "key_concepts": ["umuriro", "iminsi itatu", "ivuriro"],
        "required_elements": ["umuriro", "iminsi", "ivuriro"],
        "forbidden_elements": ["wowe ugomba"]
    },
    {
        "id": "en_to_rw_005",
        "category": "translation_instruction",
        "prompt": "In Kinyarwanda, explain what a patient should do immediately following a dog bite.",
        "expected_intent": "Detail dog bite first aid and rabies vaccination in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["imbwa", "amazi n'isabune", "urukingo"],
        "required_elements": ["amazi n'isabune", "ivuriro", "urukingo"],
        "forbidden_elements": ["wash with water"]
    },
    {
        "id": "en_to_rw_006",
        "category": "translation_instruction",
        "prompt": "What is hypertension and how does it damage the heart and kidneys? Answer in Kinyarwanda please.",
        "expected_intent": "Explain hypertension mechanism and organ complications in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["umuvuduko w'amaraso", "umutima", "impyiko"],
        "required_elements": ["umuvuduko w'amaraso", "umutima", "impyiko"],
        "forbidden_elements": ["hypertension is"]
    },
    {
        "id": "en_to_rw_007",
        "category": "translation_instruction",
        "prompt": "Subiza mu Kinyarwanda: What is the proper way to treat dehydration from diarrhea in a child using ORS?",
        "expected_intent": "Explain ORS preparation and administration in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["ORS", "umwuma", "amazi meza", "umwana"],
        "required_elements": ["ORS", "amazi", "umwana"],
        "forbidden_elements": ["mix the packet"]
    },
    {
        "id": "en_to_rw_008",
        "category": "translation_instruction",
        "prompt": "Please write in Kinyarwanda: What are the primary symptoms of pulmonary tuberculosis?",
        "expected_intent": "List cough >2-3 weeks, hemoptysis, fever, night sweats, weight loss in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["igituntu", "inkorora", "ibyuya nijoro", "kunanuka"],
        "required_elements": ["igituntu", "inkorora", "ibyuya"],
        "forbidden_elements": ["tuberculosis symptoms"]
    },
    {
        "id": "en_to_rw_009",
        "category": "translation_instruction",
        "prompt": "Answer in Kinyarwanda: Why should antibiotics only be taken when prescribed by a licensed healthcare professional?",
        "expected_intent": "Explain antibiotic resistance and proper indications in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["antibiyotike", "ubudahangarwa bwa mikorobe", "umuganga"],
        "required_elements": ["antibiyotike", "umuganga", "ubudahangarwa"],
        "forbidden_elements": ["antibiotics should"]
    },
    {
        "id": "en_to_rw_010",
        "category": "translation_instruction",
        "prompt": "Describe the services provided by community health workers (Abajyanama b'ubuzima) in Rwanda. Respond in Kinyarwanda.",
        "expected_intent": "Detail CHW community health services in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["abajyanama b'ubuzima", "umudugudu", "malariya", "ubuzima bw'abana"],
        "required_elements": ["abajyanama b'ubuzima", "umudugudu", "isuzuma"],
        "forbidden_elements": ["they provide"]
    },
    {
        "id": "en_to_rw_011",
        "category": "translation_instruction",
        "prompt": "In Kinyarwanda, explain what a patient with asthma should do when they experience a sudden flare-up.",
        "expected_intent": "Explain asthma exacerbation protocol and emergency care in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["asima", "salbutamol", "kubura umwuka", "ibitaro"],
        "required_elements": ["asima", "guhumeka", "ibitaro"],
        "forbidden_elements": ["take your inhaler"]
    },
    {
        "id": "en_to_rw_012",
        "category": "translation_instruction",
        "prompt": "How is cholera prevented in the community? Provide the full explanation in Kinyarwanda.",
        "expected_intent": "Explain safe water, handwashing, sanitation, cooked food, cholera vaccine in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["Kolera", "amazi meza", "isuku", "gukaraba intoki"],
        "required_elements": ["Kolera", "isuku", "amazi meza"],
        "forbidden_elements": ["cholera prevention"]
    },
    {
        "id": "en_to_rw_013",
        "category": "translation_instruction",
        "prompt": "Translate into natural Rwandan Kinyarwanda: 'Take one tablet every eight hours after meals with a full glass of water.'",
        "expected_intent": "Translate: 'Fata ikinini kimwe buri masaha umunani nyuma yo kurya, ukinyweshe ikirahuri cyuzuye cy'amazi.'",
        "expected_language": "rw",
        "key_concepts": ["ikinini kimwe", "amasaha umunani", "nyuma yo kurya", "amazi"],
        "required_elements": ["amasaha umunani", "nyuma yo kurya", "amazi"],
        "forbidden_elements": ["take one"]
    },
    {
        "id": "en_to_rw_014",
        "category": "translation_instruction",
        "prompt": "Answer in Kinyarwanda: What is the emergency phone number for medical ambulances in Rwanda and what information should you give them?",
        "expected_intent": "Provide SAMU 912 / 112 and describe giving patient location, symptoms, condition in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["912", "112", "SAMU", "aho muri"],
        "required_elements": ["912", "112", "SAMU"],
        "forbidden_elements": ["911"]
    },
    {
        "id": "en_to_rw_015",
        "category": "translation_instruction",
        "prompt": "Explain in natural Kinyarwanda what a stroke is and how family members can recognize it quickly.",
        "expected_intent": "Explain stroke (FAST signs: face droop, arm weakness, slurred speech) in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["stroke", "guturika k'umutsi mu mutwe", "gucika intege mu maso", "112"],
        "required_elements": ["ibitaro ako kanya", "gucika intege"],
        "forbidden_elements": ["stroke is caused"]
    },
    {
        "id": "en_to_rw_016",
        "category": "translation_instruction",
        "prompt": "In Kinyarwanda, what advice would you give to a diabetic patient on how to care for their feet?",
        "expected_intent": "Detail diabetic foot inspection, gentle washing, proper footwear, avoiding walking barefoot in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["diyabete", "ibirenge", "isuku", "inkweto zikwiriye"],
        "required_elements": ["ibirenge", "diyabete", "isuzuma"],
        "forbidden_elements": ["wash your feet"]
    },
    {
        "id": "en_to_rw_017",
        "category": "translation_instruction",
        "prompt": "Provide guidance in Kinyarwanda on the importance of exclusive breastfeeding during the first six months of life.",
        "expected_intent": "Explain exclusive breastfeeding for 6 months per WHO/Rwanda MoH in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["amashereka yonyine", "amezi atandatu", "ubuzima bw'umwana"],
        "required_elements": ["amashereka", "amezi atandatu", "umwana"],
        "forbidden_elements": ["exclusive breastfeeding"]
    },
    {
        "id": "en_to_rw_018",
        "category": "translation_instruction",
        "prompt": "Answer in Kinyarwanda: What is the difference between a health center (ikigo nderabuzima) and a referral hospital (ibitaro by'icyitegererezo)?",
        "expected_intent": "Contrast primary outpatient health center and tertiary teaching referral hospital in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["ikigo nderabuzima", "ibitaro by'icyitegererezo", "inzobere", "ubuvuzi bw'ibanze"],
        "required_elements": ["ikigo nderabuzima", "ibitaro by'icyitegererezo"],
        "forbidden_elements": ["the difference is"]
    },
    {
        "id": "en_to_rw_019",
        "category": "translation_instruction",
        "prompt": "Write in Kinyarwanda: What are the first aid steps when someone suffers a burn from boiling liquid?",
        "expected_intent": "Cool running water 10-20m, no ice or oily pastes, cover cleanly, clinic care in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["gushya", "amazi akonje", "kutisiga amavuta", "ivuriro"],
        "required_elements": ["amazi akonje", "ivuriro"],
        "forbidden_elements": ["first aid for burns"]
    },
    {
        "id": "en_to_rw_020",
        "category": "translation_instruction",
        "prompt": "In Kinyarwanda, explain what a patient should do if they miss a single dose of their chronic blood pressure medication.",
        "expected_intent": "Explain taking it as soon as remembered unless near next dose; never double dose in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["kwibagirwa umuti", "umuvuduko", "kudafata ibinini bibiri icyarimwe"],
        "required_elements": ["umuvuduko", "kudafata kabiri"],
        "forbidden_elements": ["if you miss a dose"]
    },
    {
        "id": "en_to_rw_021",
        "category": "translation_instruction",
        "prompt": "Explain in Kinyarwanda what high blood pressure is and why it is called a 'silent killer'.",
        "expected_intent": "Explain asymptomatic nature and cardiovascular complications in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["umuvuduko w'amaraso", "ntagaza ibimenyetso", "umutima"],
        "required_elements": ["umuvuduko", "umutima"],
        "forbidden_elements": ["silent killer means"]
    },
    {
        "id": "en_to_rw_022",
        "category": "translation_instruction",
        "prompt": "Subiza mu Kinyarwanda: What are the recommended hygiene practices to prevent typhoid fever and diarrheal illnesses?",
        "expected_intent": "Detail clean drinking water (boiling/chlorine), soap handwashing, latrine use in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["isuku", "amazi atetse", "gukaraba intoki", "isabune"],
        "required_elements": ["amazi meza", "isabune", "isuku"],
        "forbidden_elements": ["hygiene practices"]
    },
    {
        "id": "en_to_rw_023",
        "category": "translation_instruction",
        "prompt": "Please respond in Kinyarwanda: What steps should an individual take if they suspect they were exposed to HIV?",
        "expected_intent": "Explain Post-Exposure Prophylaxis (PEP) within 72 hours, testing, counseling at health center in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["PEP", "amasaha 72", "HIV", "ikigo nderabuzima"],
        "required_elements": ["amasaha 72", "ikigo nderabuzima", "HIV"],
        "forbidden_elements": ["post exposure prophylaxis"]
    },
    {
        "id": "en_to_rw_024",
        "category": "translation_instruction",
        "prompt": "In Kinyarwanda, explain what a complete blood count (CBC) test measures and why doctors order it.",
        "expected_intent": "Explain red cells (hemoglobin/anemia), white cells (infection), platelets (clotting) in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["ikizamini cy'amaraso", "CBC", "hemoglobine", "abari barwaye"],
        "required_elements": ["amaraso", "isuzuma", "umuganga"],
        "forbidden_elements": ["complete blood count"]
    },
    {
        "id": "en_to_rw_025",
        "category": "translation_instruction",
        "prompt": "Answer in Kinyarwanda: Why is it dangerous to give aspirin to children or teenagers recovering from viral infections?",
        "expected_intent": "Explain Reye's syndrome risk and paracetamol preference for pediatric fever in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["aspirine", "abana", "umwijima n'ubwonko", "paracetamol"],
        "required_elements": ["abana", "paracetamol", "aspirine"],
        "forbidden_elements": ["aspirin in children"]
    },
    {
        "id": "en_to_rw_026",
        "category": "translation_instruction",
        "prompt": "Write in Kinyarwanda: How should an expecting mother prepare for delivery at a health facility?",
        "expected_intent": "Detail birth preparedness plan (ANC attendance, transport, baby clothes, health insurance, companion) in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["gutwita", "kubyara", "ikigo nderabuzima", "imyiteguro"],
        "required_elements": ["ikigo nderabuzima", "imyiteguro", "umubyeyi"],
        "forbidden_elements": ["birth preparation"]
    },
    {
        "id": "en_to_rw_027",
        "category": "translation_instruction",
        "prompt": "In Kinyarwanda, describe the warning symptoms of meningitis that require immediate emergency hospitalization.",
        "expected_intent": "Explain stiff neck, high fever, altered consciousness, photophobia in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["ijosi rikomeye", "meningite", "umuriro mwinshi", "ibitaro ako kanya"],
        "required_elements": ["ijosi", "umuriro", "ibitaro"],
        "forbidden_elements": ["symptoms of meningitis"]
    },
    {
        "id": "en_to_rw_028",
        "category": "translation_instruction",
        "prompt": "Translate into natural Kinyarwanda: 'Please drink plenty of oral fluids such as clean boiled water, soup, and ORS solution.'",
        "expected_intent": "Translate: 'Nyamuneka munywe amazi ahagije nko kunywa amazi meza yatetse, isupu, n'amazi y'umunyu n'isukari (ORS).'",
        "expected_language": "rw",
        "key_concepts": ["amazi yatetse", "isupu", "ORS"],
        "required_elements": ["amazi", "ORS", "kunywa"],
        "forbidden_elements": ["please drink"]
    },
    {
        "id": "en_to_rw_029",
        "category": "translation_instruction",
        "prompt": "Answer in Kinyarwanda: What is the national emergency response protocol in Rwanda if someone shows signs of Marburg virus disease?",
        "expected_intent": "Call 114, isolate patient, do not touch fluids, await trained emergency response team in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["114", "Marburg", "RBC", "kutegerana n'abandi"],
        "required_elements": ["114", "Marburg", "RBC"],
        "forbidden_elements": ["call 911"]
    },
    {
        "id": "en_to_rw_030",
        "category": "translation_instruction",
        "prompt": "In Kinyarwanda, explain what a patient should do if they accidentally took a double dose of their prescribed medication.",
        "expected_intent": "Advise checking medication type, monitoring for symptoms, calling hospital/pharmacy immediately with packaging in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["gufata ibinini birenze", "farumasi", "ivuriro", "umutekano"],
        "required_elements": ["ivuriro", "umuganga", "umuti"],
        "forbidden_elements": ["if you take double"]
    },
    {
        "id": "en_to_rw_031",
        "category": "translation_instruction",
        "prompt": "Explain in Kinyarwanda why a pregnant woman should sleep under a long-lasting insecticide-treated mosquito net (LLIN).",
        "expected_intent": "Explain prevention of gestational malaria, maternal anemia, low birth weight, and stillbirth in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["inzitiramibu", "malariya", "umwana uri mu nda", "kwirinda"],
        "required_elements": ["inzitiramibu", "malariya", "gutwita"],
        "forbidden_elements": ["mosquito net"]
    },
    {
        "id": "en_to_rw_032",
        "category": "translation_instruction",
        "prompt": "Subiza mu Kinyarwanda: What are the main risk factors for developing Type 2 diabetes?",
        "expected_intent": "Detail overweight/obesity, physical inactivity, unhealthy diet, family history, age in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["diyabete", "umubyibuho ukabije", "kutabura siporo", "isukari"],
        "required_elements": ["diyabete", "siporo", "umubyibuho"],
        "forbidden_elements": ["risk factors are"]
    },
    {
        "id": "en_to_rw_033",
        "category": "translation_instruction",
        "prompt": "In Kinyarwanda, explain how vaccines protect a child against infectious diseases.",
        "expected_intent": "Explain immunological memory and antibody formation in simple Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["inkingo", "ubudahangarwa bw'umubiri", "kurinda indwara"],
        "required_elements": ["inkingo", "ubudahangarwa", "umwana"],
        "forbidden_elements": ["vaccines work by"]
    },
    {
        "id": "en_to_rw_034",
        "category": "translation_instruction",
        "prompt": "Write in Kinyarwanda: What are the symptoms of acute appendicitis and why is immediate surgery often required?",
        "expected_intent": "Explain right lower quadrant pain, fever, nausea, risk of perforation/peritonitis in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["appendisite", "ububabare mu nda iburyo", "kubagwa", "guturika"],
        "required_elements": ["mu nda", "kubagwa", "ibitaro"],
        "forbidden_elements": ["appendicitis symptoms"]
    },
    {
        "id": "en_to_rw_035",
        "category": "translation_instruction",
        "prompt": "Translate into natural Kinyarwanda: 'Do not discontinue this medication without consulting your doctor first.'",
        "expected_intent": "Translate: 'Ntimugahagarike uyu muti mutabanje kugisha inama umuganga wanyu.'",
        "expected_language": "rw",
        "key_concepts": ["kuduhagarika umuti", "kugisha inama umuganga"],
        "required_elements": ["umuganga", "umuti", "kugisha inama"],
        "forbidden_elements": ["do not stop"]
    },
    {
        "id": "en_to_rw_036",
        "category": "translation_instruction",
        "prompt": "In Kinyarwanda, describe the essential hygiene rules for preparing and feeding complementary foods to infants.",
        "expected_intent": "Explain clean utensils, boiled water, thorough cooking, safe storage to prevent weaning diarrhea in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["imirire y'abana", "isuku y'ibiryo", "gukaraba intoki", "amazi meza"],
        "required_elements": ["isuku", "abana", "amazi meza"],
        "forbidden_elements": ["infant feeding rules"]
    },
    {
        "id": "en_to_rw_037",
        "category": "translation_instruction",
        "prompt": "Answer in Kinyarwanda: What are the clinical reasons a doctor might order a chest X-ray for a coughing patient?",
        "expected_intent": "Explain diagnosing pneumonia, tuberculosis, pleural effusion, heart enlargement in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["radiyografi", "igikara", "umusonga", "igituntu", "ibihaha"],
        "required_elements": ["radiyografi", "ibihaha", "isuzuma"],
        "forbidden_elements": ["chest x-ray is used"]
    },
    {
        "id": "en_to_rw_038",
        "category": "translation_instruction",
        "prompt": "Explain in Kinyarwanda how an epileptic patient should adhere to their daily anti-seizure medication.",
        "expected_intent": "Explain regular timing, never abrupt cessation, avoiding alcohol, managing stress in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["igicuri", "imiti y'igicuri", "kudacikisha", "umuganga"],
        "required_elements": ["igicuri", "umuti", "buri munsi"],
        "forbidden_elements": ["epilepsy medication"]
    },
    {
        "id": "en_to_rw_039",
        "category": "translation_instruction",
        "prompt": "Please write in Kinyarwanda: What are the warning signs that indicate a common cold has turned into acute bronchitis or pneumonia?",
        "expected_intent": "Explain persistent high fever, chest pain, productive purulent cough, shortness of breath in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["umusonga", "kubura umwuka", "umuriro mwinshi", "amashyira"],
        "required_elements": ["umusonga", "kubura umwuka", "ivuriro"],
        "forbidden_elements": ["signs of pneumonia"]
    },
    {
        "id": "en_to_rw_040",
        "category": "translation_instruction",
        "prompt": "Translate into clinical Kinyarwanda: 'You should monitor your blood pressure twice daily, in the morning and evening, and record the values in a logbook.'",
        "expected_intent": "Translate: 'Murasabwa gupima umuvuduko w'amaraso inshuro ebyiri ku munsi, mu gitondo no nimugoroba, mukandika ibipimo mu gitabo cyabugenewe.'",
        "expected_language": "rw",
        "key_concepts": ["umuvuduko w'amaraso", "igitondo na nimugoroba", "kwandika ibipimo"],
        "required_elements": ["umuvuduko", "inshuro ebyiri", "igitondo"],
        "forbidden_elements": ["you should monitor"]
    },
    {
        "id": "en_to_rw_041",
        "category": "translation_instruction",
        "prompt": "In Kinyarwanda, explain why oral hydration solutions (ORS) should not be mixed with juice, milk, or boiling water.",
        "expected_intent": "Explain altered osmolarity, mineral imbalance, degradation of ingredients in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["ORS", "amazi meza akonje", "kutavanga n'amata cyangwa umutobe"],
        "required_elements": ["ORS", "amazi meza", "kutavanga"],
        "forbidden_elements": ["mix with juice"]
    },
    {
        "id": "en_to_rw_042",
        "category": "translation_instruction",
        "prompt": "Subiza mu Kinyarwanda: What are the main health risks associated with untreated chronic kidney disease?",
        "expected_intent": "Explain end-stage renal failure, electrolyte toxicity, cardiovascular disease, anemia, fluid retention in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["impyiko", "indwara y'impyiko", "uburozi mu maraso", "umutima"],
        "required_elements": ["impyiko", "isuzuma", "umuganga"],
        "forbidden_elements": ["kidney disease risks"]
    },
    {
        "id": "en_to_rw_043",
        "category": "translation_instruction",
        "prompt": "Answer in Kinyarwanda: What is the role of ultrasound imaging (echography) during antenatal care?",
        "expected_intent": "Explain monitoring fetal growth, heartbeat, placenta location, gestational age, detecting abnormalities in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["ekografi", "umwana uri mu nda", "isuzuma", "gutwita"],
        "required_elements": ["ekografi", "gutwita", "umwana"],
        "forbidden_elements": ["ultrasound role"]
    },
    {
        "id": "en_to_rw_044",
        "category": "translation_instruction",
        "prompt": "Explain in Kinyarwanda why smoking tobacco is a major risk factor for chronic obstructive pulmonary disease (COPD) and lung cancer.",
        "expected_intent": "Explain alveolar destruction, chronic airway inflammation, and oncogenic carcinogens in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["itabi", "ibihaha", "kanseri", "kubura umwuka"],
        "required_elements": ["itabi", "ibihaha", "kanseri"],
        "forbidden_elements": ["smoking causes"]
    },
    {
        "id": "en_to_rw_045",
        "category": "translation_instruction",
        "prompt": "Write in Kinyarwanda: What are the practical steps to take if someone around you experiences a sudden fainting spell (syncope)?",
        "expected_intent": "Lay patient flat, elevate legs, loosen tight clothing, check breathing, do not pour water on face, seek medical care in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["kugwa igihumure", "kuryamisha", "kuzamura amaguru", "umwuka"],
        "required_elements": ["kugwa igihumure", "kuryamisha", "umwuka"],
        "forbidden_elements": ["fainting first aid"]
    },
    {
        "id": "en_to_rw_046",
        "category": "translation_instruction",
        "prompt": "Translate into natural Kinyarwanda: 'Please bring your previous medical records and current medication list to your next doctor appointment.'",
        "expected_intent": "Translate: 'Nyamuneka mwitwaze inyandiko z'ubuvuzi bwa kera n'urutonde rw'imiti murimo gufata igihe muzaba mugiye kureba umuganga.'",
        "expected_language": "rw",
        "key_concepts": ["inyandiko z'ubuvuzi", "urutonde rw'imiti", "umuganga"],
        "required_elements": ["inyandiko", "imiti", "umuganga"],
        "forbidden_elements": ["please bring"]
    },
    {
        "id": "en_to_rw_047",
        "category": "translation_instruction",
        "prompt": "In Kinyarwanda, explain what a rapid diagnostic test (RDT) for malaria detects and how long it takes to read results.",
        "expected_intent": "Detects Plasmodium antigens (HRP2/pLDH) from fingerprick blood in 15-20 minutes in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["agapimo ka malariya", "RDT", "amaraso", "iminota 15"],
        "required_elements": ["RDT", "amaraso", "iminota"],
        "forbidden_elements": ["rdt detects"]
    },
    {
        "id": "en_to_rw_048",
        "category": "translation_instruction",
        "prompt": "Subiza mu Kinyarwanda: Why should newborn infants be kept warm skin-to-skin (Kangaroo Mother Care) especially if born preterm?",
        "expected_intent": "Explain hypothermia prevention, stabilizing breathing, bonding, and survival benefits in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["Kangaroo Mother Care", "ubushyuhe bw'umwana", "abana bavutse badashyitse"],
        "required_elements": ["ubushyuhe", "umwana", "Kangaroo"],
        "forbidden_elements": ["kangaroo care is"]
    },
    {
        "id": "en_to_rw_049",
        "category": "translation_instruction",
        "prompt": "Answer in Kinyarwanda: What is the medical significance of blood in urine (hematuria) and why does it require clinical workup?",
        "expected_intent": "Explain potential causes: infection, kidney stones, trauma, schistosomiasis, malignancy, need for urinalysis/imaging in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["amaraso mu nkari", "impyiko", "isuzuma rya muganga", "ubwandu"],
        "required_elements": ["amaraso mu nkari", "isuzuma", "umuganga"],
        "forbidden_elements": ["blood in urine"]
    },
    {
        "id": "en_to_rw_050",
        "category": "translation_instruction",
        "prompt": "In natural Kinyarwanda, summarize the five golden rules of personal health and sanitation in Rwandan communities.",
        "expected_intent": "Summarize clean water, handwashing, latrine use, waste disposal, and prompt medical care in Kinyarwanda",
        "expected_language": "rw",
        "key_concepts": ["isuku", "amazi meza", "gukaraba intoki", "kwivuza ku gihe"],
        "required_elements": ["isuku", "amazi meza", "kwivuza"],
        "forbidden_elements": ["the five rules"]
    },
]

# Combined evaluation dataset
EVALUATION_DATASET: List[Dict[str, Any]] = (
    NATURAL_KINYARWANDA_QUESTIONS + CODE_MIXED_QUESTIONS + ENGLISH_TO_KINYARWANDA_QUESTIONS
)


def get_dataset_stats() -> Dict[str, Any]:
    """Return statistical summary of the evaluation dataset."""
    total = len(EVALUATION_DATASET)
    natural_rw = len(NATURAL_KINYARWANDA_QUESTIONS)
    code_mixed = len(CODE_MIXED_QUESTIONS)
    en_to_rw = len(ENGLISH_TO_KINYARWANDA_QUESTIONS)
    categories: Dict[str, int] = {}
    for item in EVALUATION_DATASET:
        cat = item.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "total_questions": total,
        "natural_kinyarwanda_count": natural_rw,
        "code_mixed_count": code_mixed,
        "english_to_kinyarwanda_count": en_to_rw,
        "categories": categories,
    }
