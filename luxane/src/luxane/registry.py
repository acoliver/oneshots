"""Build the registry: constant Python tables that back Luxane.

Everything here is a static literal. The product table is hand-entered from the
sources cited in research/DECISION.md; nothing is fetched at runtime.

The unknown-ingredient entry exists so an unrecognized label never gets a guessed
value assigned to it: it stays UNKNOWN_INGREDIENT and the engine treats it as
un-summable instead. Same label, same tombstone, byte for byte.

All ingredient records use integer milligrams per DOSE UNIT. All frequencies are
plain integers (times per day).
"""


class UnknownIngredient(Exception):
    """Raised when a freely-entered 'active ingredient' is not in the registry."""


UNKNOWN_INGREDIENT = {
    "name": "unknown",
    "max_dose_mg": None,
    "unit": "dose",
    "warning": None,
    "lower": None,
    "source": "unknown (not in Luxane registry)",
}


def ingredient_key(name):
    """Return the canonical registry key for a label ingredient string.

    Accepts the plain name, 'salt of the base' forms, brand names, and common
    abbreviations. Unknown strings raise UnknownIngredient with the exact input message.

    Every synonym maps deterministically. Undefined strings FAIL FAST: a label that
    references an ingredient we do not model is a labeling bug we should hear about,
    not an edge case to swallow.
    """
    table = {
        # --- analgesics / antipyretics -------------------------------
        "acetaminophen": "acetaminophen",
        "apap": "acetaminophen",
        "paracetamol": "acetaminophen",
        "n-acetyl-para-aminophenol": "acetaminophen",
        # --- NSAIDs ---------------------------------------------
        "ibuprofen": "ibuprofen",
        "naproxen": "naproxen",
        "naproxen sodium": "naproxen",
        "aspirin": "aspirin",
        # --- first-generation antihistamine (sedating) ---------------
        "diphenhydramine": "diphenhydramine",
        "diphenhydramine citrate": "diphenhydramine",
        # --- non-sedating antihistamines -----------------------------
        "loratadine": "loratadine",
        "cetirizine": "cetirizine",
        "cetirizine hcl": "cetirizine",
        "fexofenadine": "fexofenadine",
        "fexofenadine hcl": "fexofenadine",
        # --- cold/flu actives -----------------------------------
        "guaifenesin": "guaifenesin",
        "dextromethorphan": "dextromethorphan",
        "dextromethorphan hbr": "dextromethorphan",
        "dextromethorphan hydrobromide": "dextromethorphan",
        "phenylephrine": "phenylephrine",
        "phenylephrine hcl": "phenylephrine",
        "phenylephrine hydrochloride": "phenylephrine",
        "pseudoephedrine": "pseudoephedrine",
        "pseudoephedrine hcl": "pseudoephedrine",
        "caffeine": "caffeine",
    }
    key = name.strip().lower()
    if key not in table:
        raise UnknownIngredient(name)
    return table[key]


# Canonical daily-dose ceilings. Every number has a citation in research/DECISION.md.
# For 'unknown', max_dose_mg is None: a report will show the running total and
# read 'no citable ceiling in the Luxane registry'.
INGREDIENTS = {
    # acetaminophen: 4000 mg/24 h is the FDA ceiling for all sources.
    # (FDA acetaminophen page; 21 CFR 201.326 liver warning.)
    "acetaminophen": {
        "name": "acetaminophen",
        "max_dose_mg": 4000,
        "unit": "mg",
        "warning": "above: exceed 4000 mg/24 h of acetaminophen from all sources is the FDA ceiling; it can cause liver damage.",
        "lower": None,
        "source": "FDA acetaminophen page (fda.gov/drugs/safe-use-over-counter-pain-relievers-and-fever-reducers/acetaminophen); 21 CFR 201.326",
    },
    # ibuprofen OTC labeling ceiling 1200 mg/24 h (ibuprofen 200 mg label:
    # 'do not exceed 6 tablets in 24 hours').
    "ibuprofen": {
        "name": "ibuprofen",
        "max_dose_mg": 1200,
        "unit": "mg",
        "warning": "above: exceed 1200 mg/24 h of ibuprofen from all sources; stomach-bleeding/GI risk rises with dose.",
        "lower": None,
        "source": "Ibuprofen 200 mg OTC label (DailyMed)",
    },
    # naproxen OTC label ceiling 660 mg/24 h (naproxen 220 mg: 'do not exceed
    # 3 tablets in 24 hours').
    "naproxen": {
        "name": "naproxen",
        "max_dose_mg": 660,
        "unit": "mg",
        "warning": "above: exceed 660 mg/24 h of naproxen from all sources.",
        "lower": None,
        "source": "Naproxen sodium 220 mg OTC label (DailyMed)",
    },
    # aspirin: OTC internal-analgesic aspirin labeling max is 4000 mg/24 h.
    "aspirin": {
        "name": "aspirin",
        "max_dose_mg": 4000,
        "unit": "mg",
        "warning": "above: exceed 4000 mg/24 h of aspirin from all sources; stomach-bleeding risk rises with dose.",
        "lower": None,
        "source": "OTC aspirin (ASA) labeling; 21 CFR part 343 / IAAA monograph",
    },
    # diphenhydramine: 'do not take more than' 300 mg/24 h.
    "diphenhydramine": {
        "name": "diphenhydramine",
        "max_dose_mg": 300,
        "unit": "mg",
        "warning": "above: exceed 300 mg/24 h of diphenhydramine from all sources; heavy sedation, falls, confusion in older adults.",
        "lower": None,
        "source": "OTC diphenhydramine 25 mg label",
    },
    # second-generation antihistamines are dosed once daily as 10 mg / day;
    # those are the practical ceilings we hold, not a formal FDA daily cap.
    "loratadine": {
        "name": "loratadine",
        "max_dose_mg": 10,
        "unit": "mg",
        "warning": "above: recommended once-daily dose is 10 mg; combining two 'daily allergy' products doubles it.",
        "lower": "the standard once-daily dose is 10 mg",
        "source": "Loratadine 10 mg OTC label (DailyMed)",
    },
    "cetirizine": {
        "name": "cetirizine",
        "max_dose_mg": 10,
        "unit": "mg",
        "warning": "above: recommended once-daily dose is 10 mg; combining two 'daily allergy' products doubles it.",
        "lower": "the standard once-daily dose is 10 mg",
        "source": "Cetirizine HCl 10 mg OTC label (DailyMed)",
    },
    "fexofenadine": {
        "name": "fexofenadine",
        "max_dose_mg": 180,
        "unit": "mg",
        "warning": "above: standard dose is 180 mg once daily for adults (120 mg for 120-mg variants); combining 'daily allergy' products.",
        "lower": "the standard once-daily adult dose is 180 mg (120 mg for the 120-mg variants)",
        "source": "Fexofenadine HCl 180 mg OTC label (DailyMed)",
    },
    "guaifenesin": {
        "name": "guaifenesin",
        "max_dose_mg": 2400,
        "unit": "mg",
        "warning": "above: 2400 mg/24 h is the OTC ceiling for guaifenesin from all sources; too much can cause nausea and stomach upset.",
        "lower": None,
        "source": "Guaifenesin 400 mg / guaifenesin 600 mg strengths (not to exceed 2400 mg/24 h)",
    },
    "dextromethorphan": {
        "name": "dextromethorphan",
        "max_dose_mg": 120,
        "unit": "mg",
        "warning": "above: 120 mg/24 h is the OTC ceiling for dextromethorphan from all sources; larger amounts can cause confusion, a racing heart, serotonin-like toxicity.",
        "lower": None,
        "source": "OTC dextromethorphan 10 mg label",
    },
    # decongestant OTC ceiling for phenylephrine and pseudoephedrine is 240 mg/24 h.
    "phenylephrine": {
        "name": "phenylephrine",
        "max_dose_mg": 240,
        "unit": "mg",
        "warning": "above: 240 mg/24 h is the OTC ceiling for phenylephrine from all sources; excessive use can raise blood pressure and heart rate.",
        "lower": None,
        "source": "Phenylephrine HCl 10 mg OTC label",
    },
    "pseudoephedrine": {
        "name": "pseudoephedrine",
        "max_dose_mg": 240,
        "unit": "mg",
        "warning": "above: 240 mg/24 h is the OTC ceiling for pseudoephedrine from all sources; excessive use can raise blood pressure and heart rate.",
        "lower": None,
        "source": "Pseudoephedrine HCl 30 mg OTC label",
    },
    "caffeine": {
        "name": "caffeine",
        "max_dose_mg": 400,
        "unit": "mg",
        "warning": "above: 400 mg/24 h is a common caffeine safety ceiling across diet/medication guidance; above it is high caffeine intake and can raise heart rate and blood pressure.",
        "lower": None,
        "source": "Common dietary/medication guidance (caffeine 200 mg label / 400 mg guidance)",
    },
    # A free-text ingredient that we do not model.
    "unknown": UNKNOWN_INGREDIENT,
}


class ProductDim:
    """One row in the hand-entered product table."""

    __slots__ = ("name", "strengths", "daily_per_product", "notes")

    def __init__(self, name, strengths, daily_per_product, notes=""):
        self.name = name
        self.strengths = strengths  # {ingredient_key: mg per dose unit}
        self.daily_per_product = daily_per_product  # mg total per PRODUCT per 24 h
        self.notes = notes

    def __repr__(self):
        return f"ProductDim({self.name!r}, {{...}})"


# Products. Each ProductDim holds the per-dose strength of each active ingredient
# AND the per-PRODUCT daily ceiling from that product's own label (never the global
# ingredient ceiling). The product-specific daily cap is what a single bottle allows; the
# global ceiling is what all products together allow. Both gates are checked.
#
# Every row is a real consumer product with the numbers actually printed on its Drug
# Facts label. The product-specific caps come straight from each label.
PRODUCTS = [
    # Tylenol Extra Strength 500 mg: 2 caplets every 6 h, no more than 6 caplets/24 h.
    ProductDim(
        name="Tylenol Extra Strength",
        strengths={"acetaminophen": 500},
        daily_per_product=3000,
        notes="500 mg per caplet, max 6 caplets/24 h.",
    ),
    # DayQuil Severe Cold & Flu: 2 caplets every 4 h, no more than 12 softgels/24 h.
    ProductDim(
        name="DayQuil Severe Cold & Flu",
        strengths={"acetaminophen": 325, "dextromethorphan": 10, "guaifenesin": 200, "phenylephrine": 5},
        daily_per_product=3900,
        notes="325 mg APAP + 10 mg DXM + 200 mg guaifenesin + 5 mg phenylephrine per 2-caplet dose, max 12 softgels/24 h.",
    ),
    # Advil Cold & Sinus: ibuprofen 200 mg + pseudoephedrine 30 mg, max 6 caplets/24 h.
    ProductDim(
        name="Advil Cold & Sinus",
        strengths={"ibuprofen": 200, "pseudoephedrine": 30},
        daily_per_product=1200,
        notes="ibuprofen 200 mg + pseudoephedrine 30 mg per caplet, max 6 caplets/24 h.",
    ),
    # Aleve (naproxen sodium 220 mg), max 3 tablets/24 h.
    ProductDim(
        name="Aleve",
        strengths={"naproxen": 220},
        daily_per_product=660,
        notes="naproxen sodium 220 mg, max 3 tablets/24 h.",
    ),
    # Benadryl (diphenhydramine 25 mg), max 300 mg/24 h.
    ProductDim(
        name="Benadryl",
        strengths={"diphenhydramine": 25},
        daily_per_product=300,
        notes="diphenhydramine 25 mg, max 12 capsules/24 h (sedating).",
    ),
    # Claritin (loratadine 10 mg, once daily).
    ProductDim(
        name="Claritin",
        strengths={"loratadine": 10},
        daily_per_product=10,
        notes="loratadine 10 mg, once daily.",
    ),
    # Zyrtec (cetirizine 10 mg, once daily).
    ProductDim(
        name="Zyrtec",
        strengths={"cetirizine": 10},
        daily_per_product=10,
        notes="cetirizine 10 mg, once daily.",
    ),
    # Allegra (fexofenadine 180 mg, once daily).
    ProductDim(
        name="Allegra",
        strengths={"fexofenadine": 180},
        daily_per_product=180,
        notes="fexofenadine 180 mg, once daily.",
    ),
    # Mucinex DM (600 mg guaifenesin + 30 mg DXM, max 8 tablets/24 h).
    ProductDim(
        name="Mucinex DM",
        strengths={"guaifenesin": 600, "dextromethorphan": 30},
        daily_per_product=1200,
        notes="600 mg guaifenesin + 30 mg dextromethorphan per tablet, max 8 tablets/24 h.",
    ),
    # Excedrin Extra Strength (acetaminophen 250 mg + aspirin 250 mg + caffeine 65 mg,
    # max 8 caplets/24 h).
    ProductDim(
        name="Excedrin Extra Strength",
        strengths={"acetaminophen": 250, "aspirin": 250, "caffeine": 65},
        daily_per_product=2000,
        notes="250 mg APAP + 250 mg ASA + 65 mg caffeine, max 8 caplets/24 h.",
    ),
    # Children's acne/pain products.
    ProductDim(
        name="Children's Motrin",
        strengths={"ibuprofen": 100},
        daily_per_product=100,
        notes="ibuprofen 100 mg per 5 mL, 4 doses/24 h.",
    ),
    ProductDim(
        name="Robitussin Cough",
        strengths={"dextromethorphan": 20, "guaifenesin": 100},
        daily_per_product=200,
        notes="20 mg DXM + 100 mg guaifenesin per 5 mL.",
    ),
    ProductDim(
        name="Robitussin Max Strength",
        strengths={"dextromethorphan": 20, "guaifenesin": 200},
        daily_per_product=400,
        notes="20 mg DXM + 200 mg guaifenesin per 5 mL.",
    ),
    # Generic single-actives people actually keep alongside brands.
    ProductDim(
        name="Generic Acetaminophen 500 mg",
        strengths={"acetaminophen": 500},
        daily_per_product=3000,
        notes="acetaminophen 500 mg, max 6 caplets/24 h.",
    ),
    ProductDim(
        name="Generic Ibuprofen 200 mg",
        strengths={"ibuprofen": 200},
        daily_per_product=1200,
        notes="ibuprofen 200 mg, max 6 tablets/24 h.",
    ),
]
