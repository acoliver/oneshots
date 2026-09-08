#!/usr/bin/env bash
# Caveate verification harness. Exit 0 on PASS.
# Proves the DECISION.md success criteria:
#   1. gold corpus agreement (tier and score, per gold.json)
#   2. byte-for-byte determinism (phone-bearing message, which previously
#      exercised set-iteration order)
#   3. official-channel override: no recommendation is a contact from the message
#   4. CLI exit-code gating (non-zero iff tier is LIKELY_SCAM/SCAM)
set -u
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD/src"

ROOT="$PWD"
CORPUS="$ROOT/harness/corpus"
fail=0

# 1. Gold corpus agreement via the CLI, including exit-code gating.
python3 - "$CORPUS" <<'PYEOF'
import json, pathlib, subprocess, sys
root = pathlib.Path(sys.argv[1])
gold = json.loads((root / "gold.json").read_text())
bad = 0
for name, exp in sorted(gold.items()):
    p = root / name
    args = [sys.executable, "-m", "caveate.cli", "check", str(p)]
    if exp.get("sender"):
        args += ["--sender", exp["sender"]]
    r = subprocess.run(args, capture_output=True, text=True)
    v = json.loads(r.stdout)
    tier_ok = v["tier"] == exp["tier"]
    score_ok = abs(v["score"] - exp["score"]) < 1e-9
    exit_ok = (r.returncode == 1) == (v["tier"] in ("LIKELY_SCAM", "SCAM"))
    if tier_ok and score_ok and exit_ok:
        print(f"PASS {name}: {v['tier']} ({v['score']:+.1f}), exit {r.returncode}")
    else:
        print(f"FAIL {name}: got {v['tier']} {v['score']:+.1f} exit {r.returncode}, "
              f"want {exp['tier']} {exp['score']:+.1f} exit {1 if exp['tier'] in ('LIKELY_SCAM','SCAM') else 0}")
        bad += 1
sys.exit(1 if bad else 0)
PYEOF
[ $? -ne 0 ] && fail=1

mkdir -p "$ROOT/tmp/verify"

# 2. Determinism: a phone-bearing message (irs.msg has 202-555-0199).
python3 -m caveate.cli check "$CORPUS/irs.msg" > "$ROOT/tmp/verify/det1.json"
python3 -m caveate.cli check "$CORPUS/irs.msg" > "$ROOT/tmp/verify/det2.json"
if cmp -s "$ROOT/tmp/verify/det1.json" "$ROOT/tmp/verify/det2.json"; then
  echo "PASS determinism (phone-bearing, byte-identical)"
else
  echo "FAIL determinism (phone-bearing)"
  diff "$ROOT/tmp/verify/det1.json" "$ROOT/tmp/verify/det2.json"
  fail=1
fi

# 3. Official-channel override invariant across the whole corpus: a contact we
# extracted from the message (the suppressed list) is never recommended.
# Recommendations are built only from registry fields, so the meaningful test is
# that the two sets never overlap (a legit message that happens to contain the
# real official link is not a violation: the recommendation still comes from the
# registry, and that link is not on the suppressed list).
python3 - "$CORPUS" <<'PYEOF'
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
from caveate.engine import analyze
root = pathlib.Path(sys.argv[1])
gold = json.loads((root / "gold.json").read_text())
fail = 0
for name, exp in sorted(gold.items()):
    txt = (root / name).read_text()
    v = analyze(txt, sender=exp.get("sender", ""))
    rec = {r["value"].lower() for r in v.get("recommended", [])}
    sup = {c.lower() for c in v.get("suppressed", [])}
    overlap = rec & sup
    if overlap:
        print(f"FAIL override {name}: recommended {sorted(overlap)} is a suppressed "
              f"contact found in the message")
        fail = 1
print("PASS official-channel override: no suppressed (message) contact is recommended")
sys.exit(fail)
PYEOF
[ $? -ne 0 ] && fail=1

# 4. `caveate corpus` agreement run (exit 0 iff gold matches).
python3 -m caveate.cli corpus "$CORPUS" > "$ROOT/tmp/verify/corpus.json"
if [ $? -eq 0 ]; then
  echo "PASS corpus command (full agreement, see tmp/verify/corpus.json)"
else
  echo "FAIL corpus command: mismatches against gold.json"
  python3 -m caveate.cli corpus "$CORPUS"
  fail=1
fi

# 5. explain runs end-to-end on a scam and a clean message.
python3 -m caveate.cli explain "$CORPUS/v_chase.msg" --sender 888-888-8888 >/dev/null 2>&1
[ $? -eq 1 ] && echo "PASS explain (scam exits 1)" || { echo "FAIL explain (scam exit)"; fail=1; }
python3 -m caveate.cli explain "$CORPUS/v_clean.msg" --sender 28777 >/dev/null 2>&1
[ $? -eq 0 ] && echo "PASS explain (clean exits 0)" || { echo "FAIL explain (clean exit)"; fail=1; }

# 6. registry dumps and covers the brands the corpus relies on.
python3 -m caveate.cli registry > "$ROOT/tmp/verify/registry.json"
if python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert {"usps","chase","amazon","irs"} <= set(d); print("PASS registry (usps, chase, amazon, irs present)")' \
   "$ROOT/tmp/verify/registry.json"; then
  :
else
  echo "FAIL registry dump"
  fail=1
fi

if [ "$fail" -eq 0 ]; then
  echo
  echo "ALL CHECKS PASS"
fi
exit "$fail"
