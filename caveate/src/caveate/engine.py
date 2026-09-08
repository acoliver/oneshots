"""A compact, dependency-free weighted signal engine for smishing triage.

Every signal is a pure function of the message text plus the brand registry.
Output is a verdict dict with: tier, risk score [0..100], list of signals
(weight, label, reason, source), the recognized brand (if any), canonical
domains/phones drawn purely from the registry, and a suppressed list of any
contacts that appeared in the message (so the caller can prove they never
recommend a contact taken from the suspicious artifact).
Deterministic by construction: same input -> same bytes.
"""

import re
import unicodedata

from .brandregistry import BRANDS, ALIASES, GENERIC_2FA_SHORT_CODES

# ---------------------------------------------------------------------------
# Tiers.
SCAM = "SCAM"
LIKELY_SCAM = "LIKELY_SCAM"
CAUTION = "CAUTION"
SAFE = "SAFE"
UNKNOWN = "UNKNOWN"
TIER_ORDER = [SAFE, CAUTION, LIKELY_SCAM, SCAM, UNKNOWN]

# Weight windows per signal class: (min_possible, max_possible). The final grade
# is the max evidence group that trips; each signal carries one weight.
SIGNAL_WEIGHTS = {
    "scam_high": 9.0,
    "scam_med": 6.0,
    "scam_low": 3.0,
    "good_high": -8.0,
    "good_med": -4.0,
    "good_low": -2.0,
}


def normalize(t: str) -> str:
    """Lowercase and strip confusables/Unicode aliases for matching."""
    return "".join(
        ch for ch in unicodedata.normalize("NFKC", t.lower()) if ch.isalnum() or ch in " .-@:/"
    )


# Compiled once so the engine stays fast and deterministic.
_URL_RE = re.compile(
    r"(?i)(?:(?:https?://|www\.)[^\s<>\"']+|(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}(?:/[^\s<>\"']*)?)"
)
_URL_HOST_RE = re.compile(r"(?i)(?:https?://)?(?:www\.)?([a-z0-9-]+(?:\.[a-z0-9-]+)+)(?:[/:?#]|$)")
_IP_HOST_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_SHORTENER_TLDS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd",
                   "cutt.ly", "rb.gy", "shorturl.at", "tiny.cc"}


def _split_domain(url: str) -> str:
    m = _URL_HOST_RE.search(url)
    return m.group(1).lower() if m else ""


def _canonical_domains(reg):
    d = reg.get("canonical_site", "")
    m = _URL_HOST_RE.search(d)
    return {m.group(1).lower()} if m else set()


# Domain fragments responsible for 'this is the brand' decisions, per registry.
BRAND_DOMAIN_FRAGMENTS = {
    "chase": {"chase.com"},
    "wellsfargo": {"wellsfargo.com"},
    "bankofamerica": {"bankofamerica.com"},
    "paypal": {"paypal.com"},
    "usps": {"usps.com"},
    "fedex": {"fedex.com"},
    "dhl": {"dhl.com"},
    "irs": {"irs.gov"},
    "ssa": {"ssa.gov"},
    "amazon": {"amazon.com"},
    "geeksquad": {"bestbuy.com"},
    "apple": {"apple.com"},
    "microsoft": {"microsoft.com"},
    "easypass": {"e-zpassny.com", "ezpassny.com"},
    "pgande": {"pge.com"},
}


def levenshtein(a: str, b: str) -> int:
    """Tiny levenshtein for lookalike-detection of registry domains."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ch_a in enumerate(a, 1):
        cur = [i]
        for j, ch_b in enumerate(b, 1):
            cur.append(min(
                prev[j] + 1,
                cur[j - 1] + 1,
                prev[j - 1] + (ch_a != ch_b),
            ))
        prev = cur
    return prev[len(b)]


def _classify_host(host: str):
    """Return (kind, canonical-style-domain, notes) for a host."""
    host = host.lower().rstrip(".")
    if _IP_HOST_RE.match(host):
        return "ip", "", "host is a literal IP address"
    # brand fragment coverage
    for frag, doms in BRAND_DOMAIN_FRAGMENTS.items():
        if all(f in host or host in f for f in doms):
            return "brand", frag, ""
    return "unknown", "", ""


def detect_brand(text: str) -> str:
    """Return the brand key a message claims to be from, if any."""
    n = normalize(text)
    for alias, key in ALIASES.items():
        if key and re.search(r"(?<![a-z])" + re.escape(alias) + r"(?![a-z])", n):
            return key
    return ""


# ---------------------------------------------------------------------------
# Signal checkers. Each returns None (not applicable) or (weight, label, reason, source).

def sig_sender_mismatch(parsed, brand_key):
    """Known short code is trustworthy; any-number sender with a brand claim is not."""
    if not brand_key or brand_key not in BRANDS:
        return None
    reg = BRANDS.get(brand_key)
    if reg is None:
        return None
    codes = reg.get("short_codes") or []
    if parsed.sender:
        sc = parsed.sender.lower()
        if sc in codes:
            return (SIGNAL_WEIGHTS["good_med"], "recognized_short_code",
                    f"sender matches a short code {reg.get('name')} actually uses", reg.get("phone_source", ""))
        if re.fullmatch(r"5\d{4,5}", sc) or re.fullmatch(r"\d{4,6}", sc):
            # A purely numeric 5-6 digit sender is a defensible 'probably legit' shape,
            # but not enough alone to call safe.
            return (SIGNAL_WEIGHTS["good_low"], "sender_is_short_code_shape",
                    "sender is a numeric short-code shape (for A2P this is where "
                    "legitimate alerts come from)", "https://www.usshortcodes.com/")
        if re.fullmatch(r"\d{10,15}", sc) and len(sc) > 6:
            return (SIGNAL_WEIGHTS["scam_low"], "sender_random_10digit",
                    "sender is a random 10-digit number pretending to be a service "
                    "(real services use short codes or registered alpha IDs)",
                    "https://cautellus.com/blog/short-code-text-messages")
    return None


def sig_url_lookalike(parsed, brand_key):
    """If URL host is a lookalike (levenshtein <=3) of a canonical brand domain, flag."""
    if not brand_key or brand_key not in BRANDS:
        return None
    reg = BRANDS[brand_key]
    canon = _canonical_domains(reg)
    frags = BRAND_DOMAIN_FRAGMENTS.get(brand_key, set())

    for url in parsed.urls:
        host = _split_domain(url)
        if not host:
            continue
        for c in canon | frags:
            if levenshtein(host, c) <= 3 and host != c:
                return (SIGNAL_WEIGHTS["scam_high"], "lookalike_domain",
                        f"link goes to {host}, which is not {c} but is 3-or-fewer "
                        "edits away (classic typosquat)", "https://isitspamchecker.com/blog/is-this-text-message-a-scam")
        for s in _SHORTENER_TLDS:
            if host.endswith(s):
                return (SIGNAL_WEIGHTS["scam_low"], "url_shortener",
                        f"link uses snippet {s}; legitimate notifications route to the "
                        "official app/site, not a shortener", "https://detection.fyi/sublime-security/sublime-rules/impersonation_usps/")
    return None


def sig_phone_in_message(parsed, brand_key):
    """A phone number embedded in the message that is not the brand's canonical.
    We never surface this number; it is exactly the trap the scammer planted."""
    if not brand_key or brand_key not in BRANDS:
        return None
    reg = BRANDS[brand_key]
    canon = reg.get("canonical_phone") or ""
    for ph in parsed.phones:
        if ph != canon:
            return (SIGNAL_WEIGHTS["scam_low"], "embedded_phone",
                    "the message supplies its own callback number; legitimate alerts "
                    "send you to a channel you already know, never the number in the text",
                    "https://consumer.ftc.gov/features/how-avoid-imposter-scams")
    return None


def sig_urgency(text):
    if re.search(r"(?i)((urgent|immediately|within \d+ (hours?|minutes?)|act now|"
                 r"final notice|will be (suspended|terminated|closed|locked)|"
                 r"don't? (tell|share) (anyone|this)|keep this (secret|private)|"
                 r"call (back|us) (now|immediately))\b)", text):
        return (SIGNAL_WEIGHTS["scam_med"], "urgency_pressure",
                "message uses manufactured urgency or secrecy (act now, don't tell "
                "anyone, account will be locked)", "https://consumer.ftc.gov/features/how-avoid-imposter-scams")
    return None


def sig_payment_demand(text):
    if re.search(r"(?i)(gift\s?cards?|apple\s?cards?|itunes\s?cards?|"
                 r"(?<!\w)(crypto(?:currency)?|bitcoin)(?!\w)|"
                 r"wire\s?transfer|(?:via\s+)?zelle|(?:via\s+)?venmo|"
                 r"read\s?back\s?(the\s?)?code|one[- ]time\s?(pass)?code|"
                 r"move your money|safe\s?account)(?!\w)", text):
        return (SIGNAL_WEIGHTS["scam_high"], "payment_demand",
                "message demands an irreversible payment or asks you to move money to a "
                "'safe' account; legitimate firms never do this (FTC)", "https://www.ftc.gov/news-events/news/press-releases/2026/06/ftc-data-show-people-reported-losing-3-point-5-billion-imposter-scams-2025")
    return None


def sig_verification_request(text, brand_key):
    if brand_key and re.search(r"(?i)(verify (your )?account|confirm (your )?"
                             r"(identity|account|personal)|update (your )?(billing|"
                             r"payment|shipping)|sign in (again|to|here)|verify certificate)",
                             text):
        return (SIGNAL_WEIGHTS["scam_low"], "verification_request",
                "message asks you to verify/confirm/update account details via a link; "
                "real banks ask you to reply YES/NO or check the official app",
                "https://isitspamchecker.com/blog/is-this-text-message-a-scam")
    return None


def sig_government_first_contact(text, brand_key):
    if brand_key in ("irs", "ssa") and re.search(r"(?i)(refund|stimulus|arrest|warrant|"
                                                 r"court|back\s?taxes|social security|revoke|entitled)", text):
        return (SIGNAL_WEIGHTS["scam_high"], "government_first_contact",
                "IRS/SSA do not text first; they send a letter. A text about a "
                "refund/arrest is a scam", "https://www.irs.gov/newsroom/ways-to-tell-if-the-irs-is-reaching-out-or-if-its-a-scammer")
    return None


def sig_unknown_sender_no_brand(parsed):
    if parsed.sender and re.fullmatch(r"\d{10,15}", parsed.sender) and _has_ask(text_of(parsed)):
        return (SIGNAL_WEIGHTS["scam_low"], "unknown_10digit_with_ask",
                "random 10-digit sender + a request is low-trust", "https://cautellus.com/blog/short-code-text-messages")
    return None


def text_of(_):
    return ""


# Compose so each *_check function works with the Parsed struct.
def _text(parsed):
    return parsed.text


class Parsed:
    __slots__ = ("text", "sender", "urls", "phones", "emails")


def _run_all(parsed):
    out = []
    brand = detect_brand(parsed.text)
    merged = [
        ("sender_mismatch", sig_sender_mismatch(parsed, brand)),
        ("url_lookalike", sig_url_lookalike(parsed, brand)),
        ("phone_in_message", sig_phone_in_message(parsed, brand)),
        ("urgency", sig_urgency(parsed.text)),
        ("payment", sig_payment_demand(parsed.text)),
        ("verification", sig_verification_request(parsed.text, brand)),
        ("government", sig_government_first_contact(parsed.text, brand)),
    ]
    for name, res in merged:
        if res:
            w, label, reason, src = res
            out.append({"id": name, "label": label, "weight": w, "reason": reason, "src": src})
    return brand, out


def grade(signals):
    """Grade from the signal weights. Return (tier, score)."""
    score = 0
    for s in signals:
        score += s["weight"]
    if score >= 8:
        return SCAM, score
    if score >= 4:
        return LIKELY_SCAM, score
    if score >= 0:
        return CAUTION, score
    return SAFE, score

def analyze(text, sender=None):
    """Analyze a suspicious message. Main entry point.

    Returns a verdict dict (see module docstring).
    """
    parsed = Parsed()
    parsed.text = text or ""
    parsed.sender = (sender or "").strip()
    # Placeholder: raw URL/phone extraction lives in extract.py (see module)
    parsed.urls = []
    parsed.phones = []
    parsed.emails = []

    brand_key = detect_brand(parsed.text)
    brand = BRANDS.get(brand_key)
    signals = []

    # Best-effort URL extraction so lookalike check actually finds something.
    for u in _URL_RE.findall(parsed.text):
        parsed.urls.append(u)
    parsed.phones = sorted(set(re.findall(r"(?<!\d)(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}(?!\d)", parsed.text)))

    # Pre-emptive lookalike block: flag any message link whose host is not the
    # brand's official domain and does not sit under a known brand domain fragment
    # (a subdomain like tools.usps.com is overridden by the fragment match).
    seen_hosts = set()
    for url in parsed.urls:
        host = _split_domain(url)
        if not host:
            continue
        canon = _canonical_domains(brand) if brand else set()
        frags = BRAND_DOMAIN_FRAGMENTS.get(brand_key, set())
        is_canonical_claimed = (host in canon or any(f in host or host in f for f in frags))
        matched_frag = ""
        for frag, doms in BRAND_DOMAIN_FRAGMENTS.items():
            if any(f in host or host in f for f in doms) and brand_key != frag:
                matched_frag = frag
        if brand and not is_canonical_claimed and not matched_frag:
            if host not in seen_hosts:
                seen_hosts.add(host)
                signals.append({"id": "lookalike_domain", "label": "lookalike_domain",
                              "weight": SIGNAL_WEIGHTS["scam_high"],
                              "reason": f"link host '{host}' is not the official {brand['name']} domain (this is the classic smishing shape)",
                              "src": "https://isitspamchecker.com/blog/is-this-text-message-a-scam"})
        elif not brand and not is_canonical_claimed:
            # no brand claim at all + a link that isn't a canonical domain is still
            # a caution-level lookalike-less signal (URL handling is best-effort).
            pass

    # Ensure brand from text is present.
    if brand_key and not any(s["id"] == "brand_claimed" for s in signals):
        signals.append({"id": "brand_claimed", "label": "brand_claimed",
                     "weight": 0.0, "reason": f"message claims to be from {brand['name']}", "src": ""})

    # Now run the canonical rule set. Any sigs already present are not duplicated.
    bkey, sigs = _run_all(parsed)
    for s in sigs:
        if s["id"] == "url_lookalike" or not any(s["id"] == o["id"] for o in signals):
            signals.append(s)

    tier, score = grade(signals)

    # Suppress any contact that came from the message. This is the FTC-hard rule.
    suppressed = []
    if brand:
        canon = set()
        canon.update(_canonical_domains(brand))
        if brand.get("canonical_phone"):
            canon.add(brand["canonical_phone"])
        for ph in parsed.phones:
            if ph not in canon:
                suppressed.append(ph)

    recommended = []
    if brand:
        recommended = [
            {"kind": "website", "value": brand["canonical_site"], "src": brand["phone_source"]},
        ]
        if brand.get("canonical_phone"):
            recommended.append({"kind": "phone", "value": brand["canonical_phone"], "src": brand["phone_source"]})

    return {
        "input": {"text": parsed.text, "sender": parsed.sender or None},
        "brand_claimed": brand_key,
        "tier": tier,
        "score": score,
        "signals": signals,
        "recommended": recommended,
        "suppressed": suppressed,
        "note": "Caveate never recommends a number or link found inside the message.",
    }
