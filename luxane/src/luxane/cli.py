"""Luxane CLI.

Commands:

    luxane add  PRODUCT TIMES_PER_DAY [PRODUCT TIMES_PER_DAY ...]
        one or more already-in-registry products at a daily frequency, one cabinet.

    luxane extra PRODUCT INGREDIENT MG_PER_DOSE TIMES_PER_DAY
        a free-text row: (product-name, ingredient label, mg-per-dose, times-per-day).
        INGREDIENT may be a brand or generic label the registry maps.

    luxane ceiling [FREELY-INGREDIENT]

Standard report is deterministic (sort_keys=True), and any active row that
raises UnknownIngredient exits non-zero.
"""

import argparse
import json
import sys

from .engine import analyze
from .registry import (
    INGREDIENTS,
    PRODUCTS,
    UNKNOWN_INGREDIENT,
    UnknownIngredient,
    ingredient_key,
)


def make_parser():
    p = argparse.ArgumentParser(prog="luxane", description="Lexane total-daily-dose report.")
    sub = p.add_subparsers(dest="cmd", required=True)

    add = sub.add_parser("add", help="add already-registry products at a daily frequency.")
    add.add_argument("pairs", nargs="+", help="PRODUCT TIMES_PER_DAY PRODUCT TIMES_PER_DAY ...")
    add.add_argument("--ingredient", help="(cosmetic) validates an ingredient label; ignored for the add form.")

    ex = sub.add_parser("extra", help="one free-text row.")
    ex.add_argument("product", help="display name you call it.")
    ex.add_argument("ingredient", help="next label string (brand or generic).")
    ex.add_argument("mg_per_dose", type=int)
    ex.add_argument("times_per_day", type=int)

    ce = sub.add_parser("ceiling", help="print the registry ceiling table.")
    ce.add_argument("ingredient", nargs="?", help="optional free-text ingredient to inspect.")
    return p


def _resolve(binary_name, argv):
    parser = make_parser()
    args = parser.parse_args(argv)

    if args.cmd == "add":
        if len(args.pairs) % 2 != 0:
            parser.error("add requires PRODUCT TIMES_PER_DAY pairs")
        pairs = []
        for i in range(0, len(args.pairs), 2):
            pairs.append((args.pairs[i], int(args.pairs[i + 1])))
        return analyze(pairs, extra=None, neat=True)

    if args.cmd == "extra":
        key = ingredient_key(args.ingredient)
        if key not in INGREDIENTS:
            raise UnknownIngredient(args.ingredient)
        return json.dumps(analyze([], extra={args.product: {key: (args.mg_per_dose, args.times_per_day)}}, neat=True))

    if args.cmd == "ceiling":
        if args.ingredient:
            key = ingredient_key(args.ingredient)
            if key not in INGREDIENTS:
                raise UnknownIngredient(args.ingredient)
        return json.dumps(analyze([], extra=None, neat=True))

    parser.error(f"unknown command {args.cmd}")
    return json.dumps({"error": "unreachable"}, sort_keys=True, ensure_ascii=True)


def _json(obj):
    import json as _json
    return _json.dumps(obj, sort_keys=True, ensure_ascii=True)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        print(_json(_resolve("luxane", argv)))
    except UnknownIngredient as e:
        print(json.dumps({"error": "unknown-ingredient", "detail": str(e)}, sort_keys=True, ensure_ascii=True))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
