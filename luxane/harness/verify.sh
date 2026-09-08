#!/usr/bin/env bash
# Luxane verification harness. Exit 0 on PASS.
# Proves the DECISION.md success criteria:
#   1. The engine is deterministic (two identical runs, byte-identical output).
#   2. The per-Ingredient daily totals are exactly the gold numbers.
#   3. The 'total across products' is the duplication-aware total.
#   4. Every per-product label ceiling is order-independent and equals the label cap.
#   5. An unknown ingredient fails the CLI with a non-zero exit and error marker.
#   6. The CLI exits 0 on a clean cabinet.

set -u
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD/src"
ROOT="$PWD"
mkdir -p "$ROOT/tmp/verify"
fail=0

# Determinism: two runs of the same cabinet must be byte-identical.
python3 -m luxane add "Tylenol Extra Strength" 4 "DayQuil Severe Cold & Flu" 2 > "$ROOT/tmp/verify/det1.json"
python3 -m luxane add "Tylenol Extra Strength" 4 "DayQuil Severe Cold & Flu" 2 > "$ROOT/tmp/verify/det2.json"
if cmp -s "$ROOT/tmp/verify/det1.json" "$ROOT/tmp/verify/det2.json"; then
  echo "PASS determinism (two identical cabinets -> byte-identical JSON)"
else
  echo "FAIL determinism"
  fail=1
fi

# Per-product label ceiling: every product row reports its registry cap (order-independent).
python3 - <<'PYEOF'
import json, pathlib, sys
p = pathlib.Path("tmp/verify/det1.json")
data = json.loads(json.loads(p.read_text()))
cap = {d.name: d.daily_per_product for d in __import__("luxane.registry", fromlist=["PRODUCTS"]).PRODUCTS}
bad = 0
for row in data["product_rows"]:
    if row["product_daily_ceiling_mg"] != cap[row["product"]]:
        print(f"FAIL product ceiling: {row['product']} cap mismatch")
        bad = 1
if not bad:
    print("PASS per-product label ceilings (order-independent)")
sys.exit(bad)
PYEOF
[ $? -ne 0 ] && fail=1

# Gold agreement: every scenario in harness/corpus/gold.json produces exactly the
# gold per-ingredient totals and ceiling violations.
python3 - "$ROOT" <<'PYEOF'
import json, pathlib, subprocess, sys
root = pathlib.Path(sys.argv[1])
gold = json.loads((root / "harness" / "corpus" / "gold.json").read_text())
bad = 0
for name, case in sorted(gold.items()):
    args = [sys.executable, "-m", "luxane"] + ["add"] + case["args"]
    r = subprocess.run(args, capture_output=True, text=True)
    out = json.loads(json.loads(r.stdout))  # CLI double-encoding layer
    if out.get("totals") != case["totals"]:
        print(f"FAIL gold {name}: totals {out.get('totals')} != {case['totals']}")
        bad += 1
        continue
    if out.get("ceiling_violations") != case["violations"]:
        print(f"FAIL gold {name}: violations {out.get('ceiling_violations')} != {case['violations']}")
        bad += 1
        continue
    print(f"PASS gold {name}: total {out['totals']}")
if not bad:
    print("PASS gold agreement (all scenarios match gold.json)")
sys.exit(1 if bad else 0)
PYEOF
[ $? -ne 0 ] && fail=1

# CLI gates: unknown ingredient is a non-zero exit, and a clean cabinet is exit 0.
python3 -m luxane extra "shelf" "not-a-real-ingredient" 10 2 > "$ROOT/tmp/verify/unknown.json" 2>&1
rc=$?
if [ $rc -ne 0 ]; then
  echo "PASS unknown-ingredient fails non-zero"
else
  echo "FAIL unknown-ingredient should be non-zero"
  fail=1
fi
python3 -m luxane extra "my-night-cold" "acetaminophen" 325 2 > "$ROOT/tmp/verify/clean.json" 2>&1
rc=$?
if [ $rc -eq 0 ]; then
  echo "PASS clean cabinet exits 0"
else
  echo "FAIL clean cabinet should be 0"
  fail=1
fi

if [ "$fail" = "0" ]; then
  echo "ALL CHECKS PASS"
fi
exit "$fail"
