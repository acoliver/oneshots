# Luxane — research-first decision record

Everything here was gathered before the engine was written. The source facts are the anchor, and each design choice below is tied to one. This is the source that cites the number.

## 1. The problem, in numbers

**Over 1.5M people a year visit a US emergency department for an adverse drug event and almost 500,000 are hospitalized; older adults (65+) make more than 600,000 of those ED visits each year, more than twice the younger-adult rate.** The leading causes of ED visits for ADEs are anticoagulants (about one in five), diabetes agents, and antibiotics. (CDC Medication Safety "FastStats" / NEISS-CADES, `cdc.gov/medication-safety/data-research/facts-stats/index.html`, as of 2025.)

The exact "two different products, same active ingredient, one 24-hour total" is the hole the Drug Facts box assumes the reader does in their head. The same single sentence appears on every box — "do not use with any other drug containing acetaminophen" (21 CFR 201.326) — and it is a per-bottle sentence. The cross-product 24-hour total is the number a person actually takes from **all** of them together.

## 2. The gap

**The whole-cabinet per-ingredient daily total does not exist in the market.** Existing home-medication software is inventory (mojApteczka, Pharmory, okliki), scanned-cabinet reminders (WellbieRx, SnapRx), name-list / confused-name (ISMP "List of Confused Drug Names", ISMP 2023-10), and the pharmacist's duplicate-therapy pair rules (PEPID) — each a pair or a list. None sum the per-ingredient daily total across different products, and none are byte-for-byte deterministic. A same-ingredient daily total for a person's whole shelf, with a per-row `source`, in a zero-dependency CLI, with a runnable harness, is the gap.

**The exact human-cost number:** a person who takes Tylenol Extra Strength 500 mg × 4 + DayQuil Severe Cold & Flu × 2 → 2650 mg of acetaminophen, from two different bottles, seen as one total.

## 3. The design, tied to the §1 numbers

1. **Duplication-aware per-ingredient daily total** — a single `times_per_day` per product → per-ingredient **sum** across every product in the cabinet, summed into one number, against the cap. (The §1 numbers are the human-cost.)
2. **Deterministic** — no time, no date, no random, no sort (registry order → byte-identical). Determinism is the promise and the harness proves it, byte for byte.
3. **Unknown → non-zero** — a shelf item the registry does not model exits non-zero (a label we do not model is a label we fail on) rather than guessing.
4. **Per-product label cap** — each product's own "do not take more than X in 24 hours" is checked as a per-bottle cap, alongside the global per-ingredient ceiling.

## 4. The market, honestly bounded (with a citation per row)

| Existing | What it is | Does it sum the whole-cabinet daily total? |
|---|---|---|
| mojApteczka / Pharmory / okliki | medicine inventory / scanned-cabinet / reminders | No — inventory, not a daily total |
| PEPID | pharmacist's duplicate-therapy pair rules | No — a pair, not a total |
| SnapRx / WellbieRx | scanned-cabinet interaction checkers | No — a pair, not a total |
| ISMP / FDA tall-man list | confused-name list | No — a list |
| Pill reminder apps | single-med reminders | No — one at a time |

## 5. Ceilings in `registry.py` — with an exact source per row

| Ingredient | Ceiling | Source |
|---|---|---|
| acetaminophen | 4000 mg/24h | FDA acetaminophen page; liver-warning 21 CFR 201.326 |
| ibuprofen | 1200 mg/24h | ibuprofen 200 mg "do not exceed 6 tablets/24 h" (DailyMed) |
| naproxen | 660 mg/24h | naproxen sodium 220 mg "do not exceed 3 tablets/24 h" (DailyMed) |
| aspirin | 4000 mg/24h | aspirin 325 mg IAAA monograph / 21 CFR part 343 |
| diphenhydramine | 300 mg/24h | diphenhydramine 25 mg "not to exceed 300/24 h" |
| loratadine | 10 mg | loratadine 10 mg "once daily" |
| cetirizine | 10 mg | cetirizine 10 mg "once daily" |
| fexofenadine | 180 mg | fexofenadine 180 mg "once daily" |
| guaifenesin | 2400 mg/24h | guaifenesin 400/600 mg "not to exceed 2400/24 h" |
| dextromethorphan | 120 mg/24h | dextromethorphan 10/20 mg "not to exceed 120/24 h" |
| phenylephrine | 240 mg/24h | phenylephrine HCl 10 mg "not to exceed 240/24 h" |
| pseudoephedrine | 240 mg/24h | pseudoephedrine HCl 30 mg "not to exceed 240/24 h" |
| caffeine | 400 mg | common dietary/medication guidance (caffeine 65 mg label / 400 mg daily) |
| unknown | (none — fail) | unknown (not in Luxane registry) |

## 6. Why this is not the same as a pharmacist's tool

The pharmacist's "duplicate therapy" screen looks at the drug you are about to buy against other drugs a patient is on — a live, per-pair, per-basket check. Luxane looks at what a person will actually take of a **single** ingredient from all their products in a day, deterministically, offline, from a hand-curated table. Different data, different output, different stakes: this one runs anywhere, byte-for-byte, and its tables are auditable.

## 7. The name (checked, defensible)

**Luxane** is a coined nonsense mark: pronounceable, not a dictionary word, no drug, no ingredient, no brand, no package, no `pip`/`npm`/GitHub namespace collision found in a web + USPTO/patent + package search. It is not a generic descriptive phrase, so it does not read as a functional claim; it names the tool, and the tool's behavior is the honest claim.

## 8. The honest scope

This is a label table plus arithmetic. It is not medical advice, not a diagnosis, not an interaction checker, and not a model. Its single job: show the per-ingredient 24-hour total across the whole cabinet, deterministically, and fail loudly on anything it does not model. Every ceiling cites its source in `registry.py`.
