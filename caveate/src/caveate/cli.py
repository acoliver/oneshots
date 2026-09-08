"""Caveate CLI: a deterministic, offline smishing/scam triage tool.

Commands:
  caveate check <message.txt|->        print JSON verdict (exit 0 = no SCAM/LIKELY_SCAM)
  caveate explain <message.txt|->      human-readable verdict
  caveate corpus <dir>               run the whole corpus and report agreement
  caveate registry                  dump the brand registry (self-check)
"""

import argparse
import json
import pathlib
import sys

from .engine import analyze, CAUTION, LIKELY_SCAM, SCAM, TIER_ORDER, grade


def _load_input(path):
    if path == "-":
        return sys.stdin.read()
    p = pathlib.Path(path)
    if not p.exists():
        raise SystemExit(f"error: no such file: {path}")
    return p.read_text(encoding="utf-8")


def _print_verdict(v, json_indent=2):
    print(json.dumps(v, indent=json_indent, sort_keys=True))


def cmd_check(args):
    text = _load_input(args.path)
    sender = getattr(args, "sender", None)
    v = analyze(text, sender=sender)
    _print_verdict(v)
    if v["tier"] in (LIKELY_SCAM, SCAM):
        return 1
    return 0


def cmd_explain(args):
    text = _load_input(args.path)
    v = analyze(text, sender=getattr(args, "sender", None))
    print(f"tier: {v['tier']}  (score {v['score']:+.1f})")
    print(f"claimed brand: {v.get('brand_claimed') or 'unidentified'}")
    print("signals:")
    for s in v["signals"]:
        print(f"  [{s['weight']:+.1f}] {s.get('label', s['id'])}")
        print(f"         {s.get('reason', '')}")
    rec = v.get("recommended") or []
    if rec:
        print("official channels (never from the message):")
        for r in rec:
            print(f"  {r['kind']}: {r['value']}")
    sup = v.get("suppressed") or []
    if sup:
        print("contacts found in the message that Caveate does NOT trust:")
        for c in sup:
            print(f"  - {c}")
    if v["tier"] in (LIKELY_SCAM, SCAM):
        raise SystemExit(1)
    return 0


def _norm(entry):
    return json.dumps(entry, sort_keys=True)


def cmd_corpus(args):
    root = pathlib.Path(args.dir)
    gold_path = root / "gold.json"
    if not gold_path.exists():
        raise SystemExit(f"error: no gold.json in {root} (expected one label per .msg file)")
    gold = json.loads(gold_path.read_text(encoding="utf-8"))
    mismatches = []
    rows = []
    total = 0
    for p in sorted(root.glob("*.msg")):
        total += 1
        entry = gold.get(p.name)
        if entry is None:
            mismatches.append({"file": p.name, "problem": "no gold entry"})
            continue
        txt = p.read_text(encoding="utf-8")
        v = analyze(txt, sender=entry.get("sender", ""))
        row = {
            "file": p.name,
            "tier": v["tier"], "score": v["score"],
            "gold": entry,
        }
        rows.append(row)
        if v["tier"] != entry["tier"] or v["score"] != entry["score"]:
            mismatches.append({"file": p.name, "got": [v["tier"], v["score"]],
                              "want": [entry["tier"], entry["score"]]})
    out = {"total": total, "matched": total - len(mismatches), "mismatches": mismatches,
           "rows": rows}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if not mismatches else 1


def cmd_registry(args):
    from .brandregistry import BRANDS
    print(json.dumps({k: {"name": v["name"], "site": v.get("canonical_site"),
                         "phone": v.get("canal_phones", v.get("canonical_phone"))}
                    for k, v in BRANDS.items()}, indent=2))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="caveate", description="deterministic scam/text triage")
    sub = p.add_subparsers(dest="cmd")
    c = sub.add_parser("check", help="verdict JSON")
    c.add_argument("path")
    c.add_argument("--sender")
    c.set_defaults(func=cmd_check)
    e = sub.add_parser("explain", help="human verdict")
    e.add_argument("path")
    e.add_argument("--sender")
    e.set_defaults(func=cmd_explain)
    co = sub.add_parser("corpus", help="corpus agreement")
    co.add_argument("dir")
    co.set_defaults(func=cmd_corpus)
    r = sub.add_parser("registry", help="dump registry")
    r.set_defaults(func=cmd_registry)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not getattr(args, "func", None):
        build_parser().print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
