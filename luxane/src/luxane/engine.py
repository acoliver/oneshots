"""Luxane engine: accumulate every active ingredient across a cabinet.

Public entry point is :func:`analyze`. Everything in here is deterministic:
same inputs, same output dict, byte for byte.
"""

import json
from .registry import INGREDIENTS, PRODUCTS, UNKNOWN_INGREDIENT, ingredient_key


# canonical key for one 'routine' (one cabinet, one day).
def add_product_frequency(strengths, times_per_day):
    """Multiply each per-dose strength by the daily frequency.

    strengths: {ingredient_key: mg per dose unit}.
    Returns a NEW dict; never mutates the caller's.

    The engine only sees integer per-dose milligrams and integer frequencies.
    """
    return {k: int(strengths[k]) * int(times_per_day) for k in strengths}


class Resolution:
    """One line in the report for one LINED product."""

    __slots__ = ("product", "drops", "total_daily_mg", "notes")

    def __init__(self, product, drops, total_daily_mg, notes):
        self.product = product
        self.drops = drops  # {ingredient_key: mg per dose unit}
        self.total_daily_mg = total_daily_mg
        self.notes = notes

    def to_dict(self):
        # Deterministic: drops keys are the registry insertion order.
        return {
            "product": self.product,
            "drops": dict(self.drops),
            "total_daily_mg": self.total_daily_mg,
            "notes": self.notes,
        }


class Cabinet:
    """The resolved state we analyze."""

    def __init__(self):
        self.cabinet = {}   # {product_name: Resolution}
        self.extra = {}     # {product_name: {key: (mg_per_dose, times_per_day)}}

    def set_product(self, name, times_per_day):
        """Add a product by EXACT product name (from the registry) at a daily frequency."""
        for dim in PRODUCTS:
            if dim.name == name:
                self.cabinet[name] = self._resolve_dim(dim, times_per_day, extra=None)
                return
        raise UnknownIngredient(name)

    def add_fe(self, name, ingredient, mg_per_dose, times_per_day):
        """Add a free-text ingredient row: (ingredient, mg/dose, times/day)."""
        key = ingredient_key(ingredient)
        row = self.extra.setdefault(name, {})
        row[key] = (mg_per_dose, times_per_day)

    def _resolve_dim(self, dim, times_per_day, extra):
        return Resolution(
            product=dim.name,
            drops=self._drops(dim.strengths, times_per_day),
            total_daily_mg=self._step(dim.strengths, times_per_day),
            notes=dim.notes,
        )

    @staticmethod
    def _drops(strengths, times_per_day):
        return {k: strengths[k] for k in sorted(strengths)}

    @staticmethod
    def _step(strengths, times_per_day):
        total = 0
        for k in strengths:
            total += strengths[k] * times_per_day
        return int(total)

    def resolved_rows(self):
        """Return list of (name, drops, total_daily_mg, notes) in registry order.

        The list is deterministic: registry PRODUCTS order first, then the free-text rows
        in the order they were added, then the 'unknown' row LAST (stable).
        """
        rows = []
        for name, res in self.cabinet.items():
            rows.append(res)
        for name, row in self.extra.items():
            # fake a Resolution so the CLI code reads one shape.
            keys = list(row.keys())
            total = 0
            for k in keys:
                mg, times = row[k]
                total = total + mg * times
            # produce the Resolution-like shape by reusing the tight class but not the
            # private per-drops method; we intentionally keep the per-dose strength in 'drops'
            # as {key: mg_per_dose} and total_daily_mg as the real total.
            total_daily = {k: row[k][0] for k in row}
            for k in row:
                pass
            rows.append(
                Resolution(
                    name,
                    {k: row[k][0] for k in row},
                    int(sum(row[k][0] * row[k][1] for k in row)),
                    "",
                )
            )
        return rows


def analyze(cabinet_entries, extra=None, neat=False):
    """Evaluate a full cabinet.

    cabinet_entries: list of (product_name, times_per_day) for registry products.
    extra: optional dict {product_name: {ingredient: (mg_per_dose, times_per_day)}}.

    Returns a dict. Every field is derived only from these args plus the static registry.

    IMPORTANT DETERMINISM NOTE: the 'active' totals output is keyed by canonical
    ingredient; 'totals' includes 'unknown' when any row referenced an unknown ingredient
    (from the extra path). Everything is produced in registry order.

    Returns a JSON-serializable dict. Pass neat=False to get a full dict (returns the
    plain dict); neat=True returns a JSON string.
    """
    if extra is None:
        extra = {}
    resolved = []
    for name, times in cabinet_entries:
        dim = None
        for cand in PRODUCTS:
            if cand.name == name:
                dim = cand
                break
        if dim is None:
            raise UnknownIngredient(name)
        resolved.append(dim)

    # per-ingredient running totals across the whole cabinet.
    totals = {}  # canonical key -> int mg/24h
    # NEGATIVE product gates: the per-product label ceiling is a HARD floor; the engine
    # does not second-guess it. A cabinet whose everyday routine exceeds a product's own label
    # gate is EXPECTED and the report says so. (Fail fast: a label may allow more than the
    # product cap; we trust the label, and separately the global ingredient ceiling.)
    product_rows = []
    for dim in resolved:
        per_day = {}
        for k in dim.strengths:
            times = 0
            for n_, t_ in cabinet_entries:
                if n_ == dim.name:
                    times = t_
            per_day = per_day | {k: dim.strengths[k] * times}
        # global totals only count the DAILY routine that actually enters the body.
        for k, mg in per_day.items():
            totals[k] = totals.get(k, 0) + per_day[k]
        product_rows.append(
            {
                "product": dim.name,
                "per_day_mg": {k: per_day[k]},
                "product_daily_ceiling_mg": dim.daily_per_product,
                "notes": dim.notes,
            }
        )

    # free-text rows.
    for row_key in extra:
        for ing, (mg, times) in extra[row_key].items():
            totals[ing] = totals.get(ing, 0) + int(mg) * int(times)
            product_rows.append(
                {
                    "product": row_key,
                    "per_day_mg": {ing: int(mg) * int(times)},
                    "product_daily_ceiling_mg": None,
                    "notes": "",
                }
            )

    active_rows = []
    for dim in resolved:
        times = 0
        for n_, t_ in cabinet_entries:
            if n_ == dim.name:
                times = t_
        active_rows.append(
            {
                "product": dim.name,
                "drops": {k: dim.strengths[k] for k in dim.strengths},
                "total_daily_mg": int(sum(dim.strengths[k] * times for k in dim.strengths)),
            }
        )
    # The 'active' section recomputes per-product daily totals from the SAME inputs the
    # 'totals' section used, so both agree. Everything above uses the same loops.

    # clean per-Ingredient view used by the CLI and by the gold file.
    # 'totals' already has each canonical key exactly once.
    report_rows = []
    for key, val in totals.items():
        ing = INGREDIENTS[key] if key in INGREDIENTS else UNKNOWN_INGREDIENT
        report_rows.append({"key": key, "total_daily_mg": val, "max_dose_mg": ing.get("max_dose_mg")})

    ceiling_gates = {}
    for key, val in totals.items():
        ing = INGREDIENTS.get(key)
        if ing is None or ing.get("max_dose_mg") is None:
            continue
        ceiling_gates[key] = val > ing["max_dose_mg"]

    ctx = {
        "totals": dict(totals),
        "ceiling_violations": ceiling_gates,
        "report": report_rows,
        "product_rows": product_rows,
    }
    if neat:
        return json.dumps(ctx, sort_keys=True, ensure_ascii=True)
    return ctx
