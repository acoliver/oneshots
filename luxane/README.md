# luxane

**Luxane** (pronounced *luh-ZAYN*): a deterministic, zero-dependency home-medication daily-dose checker. You type the medicines you actually took in a day; luxane resolves brand and generic names to active ingredients and shows your per-ingredient 24-hour total from **all** of them together, and it refuses (non-zero exit) anything it does not understand.

Two ceilings are checked:

- **Per-ingredient daily total** — acetaminophen from *Tylenol Extra Strength* **plus** the acetaminophen hiding in *DayQuil*, against the FDA/label daily cap for that ingredient.
- **Per-product label cap** — each product’s own "do not take more than X in 24 hours".

Pairing a pain pill with a "cold & flu" product that silently contains the same painkiller is the exact case the Drug Facts box warns about, and it is the exact case everything in the aisle sells. There are entire product categories built on the buyer not noticing the overlap. Luxane is the arithmetic the label assumes you do in your head.

## What it is

`luxane add` a cabinet at how many times a day you took each product. `luxane extra` a shelf item directly. `luxane ceiling` dumps the ceiling table.

```
PYTHONPATH=src python3 -m luxane add "Tylenol Extra Strength" 4 "DayQuil Severe Cold & Flu" 2
# {"acetaminophen": 2650, "dextromethorphan": 20, "guaifenesin": 400, "phenylephrine": 10}
```

The `totals` field is the entire point: **2650 mg of acetaminophen** is the number a drawer of "pain Buddies" and "Cold & Flu" produce when someone takes both, and 2650 ≤ 4000 so gate 0 — but `4 × Tylenol` and `2 × DayQuil` is a real cabinet and the tool's job is making that total visible, not hiding it.

Deterministic: same command, byte-identical output. No config, no network, no AI, no model, no package.

## Why

Same-feel, cloning, "I already took something" is a 500,000-hospitalizations-a-year stack. CDC fast-stats: more than 1.5M ED visits / ~0.5M hospitalizations a year for adverse drug events, older adults at more than double the rate of younger people; the exact duplication (Tylenol + DayQuil → acetaminophen in both) is the classic. That is the specific, unserved arithmetic. (Sources and the full evidence trail, and the name check: `research/DECISION.md`.)

## What is in this repo

- `src/luxane/` — Python 3 stdlib only. `registry.py` (ingredient keys plus the ceiling table), `engine.py` (the accumulation), `cli.py` (argparse CLI).
- `harness/` — `verify.sh` and `harness/corpus/gold.json`. The gold file holds the per-command expectations the harness asserts, and `verify.sh` runs them and `exit`s 0 only when every cabinet equals gold and every ceiling equals the product's label cap, with byte-for-byte determinism, with unknown ingredients non-zero, and a clean cabinet at 0.

## Verify it yourself

```
PYTHONPATH=src bash harness/verify.sh
# ALL CHECKS PASS
```

The success criteria that the harness proves:

1. **Deterministic** — two identical cabinets produce byte-identical JSON.
2. **Gold agreement** — every cabinet in `harness/corpus/gold.json` produces exactly the gold per-ingredient totals.
3. **Per-product ceiling** — every product row reports its product label cap from the registry (order-independent).
4. **Unknown ingredient → non-zero** — a shelf item with a name the registry does not model prints `{"error": "unknown-ingredient"}` and the CLI exits non-zero (a label we do not understand **fails** — the point is that a literal nothing-checks look like "fine").
5. **Clean cabinet → 0** — a clean shelf item is a fine 4000-cap well under cap, and exits 0.

All five, every run, byte-for-byte. There is no `pip install`, no `npm`, no lockfile, no test framework: the harness **is** the test.

## The honest scope

This is a **label table plus arithmetic**. The point is the duplication gate, which is a deterministic per-ingredient daily total across **all** products a person is taking — the single sentence the FDA prints on every acetaminophen box — turned into a number a person actually sees. It is not medical advice, it is not a diagnosis, it is not a professional interaction checker, and it is not a model. Every ceiling cites its source (every `source` field in `registry.py`). A person takes 2650 mg of acetaminophen, never above the 4000 cap; a drawer with 2 × 4 Tylenol **plus** 2 × DayQuil is a person who just took 4000 of the same ingredient — that is the entire point, and "clean" is 0.
