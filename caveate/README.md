# Caveate

Paste a suspicious text message. Caveate tells you what it looks like, why, and gives you the one official channel you should actually use. It runs entirely on your machine: no network, no models, nothing to install beyond Python 3.

## The problem

Imposter scams were the most-reported fraud category to the FTC for the fifth year running in 2025: over 1 million reports and $3.5 billion in losses. The fastest-growing channel is text. The most reported text scams are fake bank fraud warnings, and the most impersonated company is USPS (over 28,000 USPS-impersonating web domains found by Palo Alto Networks in 2025).

Every advisory about these scams ends with the same sentence: do not call the number in the message, do not click the link in the message, reach the organization through a channel you already know. Caveate automates exactly that advice. It recognizes which brand a message claims to be from, checks the message against the patterns those brands and the FTC say real services never use, and outputs the real site and phone number for the impersonated brand, each with a source link. See `research/DECISION.md` for the full record and citations.

## What it does

Given a message (and optionally the sender number or short code), Caveate returns:

- a verdict tier and a numeric score
- the signals that fired, each with a weight, an explanation, and a source
- the brand the message claims to be from
- the official website and phone number for that brand, drawn only from the bundled registry
- every phone number found inside the message, listed separately as contacts Caveate will not trust

Tiers:

| Tier | Score | Meaning |
| --- | --- | --- |
| SCAM | >= 8 | strong scam evidence, exit code 1 |
| LIKELY_SCAM | >= 4 | credible scam evidence, exit code 1 |
| CAUTION | >= 0 | no strong signal either way, exit code 0 |
| SAFE | < 0 | a known-good signal (for example the brand's real short code) outweighed everything, exit code 0 |

Caveate never claims a message is safe in an absolute sense. "SAFE" means "no known scam signal, and one thing checked out." A brand-new attack that uses none of the known patterns will land in CAUTION, which is the accurate result.

## Quick start

Python 3.9+ with no third-party packages. From the `caveate/` directory:

```
export PYTHONPATH="$PWD/src"
python3 -m caveate.cli check /path/to/message.txt --sender 888-888-8888
```

Paste from stdin with a dash for the path:

```
cat suspicious.txt | python3 -m caveate.cli check -
```

### check

Machine-readable JSON verdict. Exit code is 1 when the tier is LIKELY_SCAM or SCAM, else 0.

```
$ python3 -m caveate.cli check harness/corpus/v_chase.msg --sender 888-888-8888
{
  "brand_claimed": "chase",
  "score": 15.0,
  "tier": "SCAM",
  "signals": [ ... ],
  "recommended": [
    {"value": "https://www.chase.com", "kind": "website", ...},
    {"value": "1-800-935-9935", "kind": "phone", ...}
  ],
  "suppressed": []
}
```

### explain

The same verdict in prose. It prints each signal with its reason and the official channels, then exits 1 for a likely scam.

```
$ python3 -m caveate.cli explain harness/corpus/v_chase.msg --sender 888-888-8888
tier: SCAM  (score +15.0)
claimed brand: chase
signals:
  [+9.0] lookalike_domain
         link host 'chase-secure-alert.xyz' is not the official Chase domain (this is the classic smishing shape)
  [+0.0] brand_claimed
         message claims to be from Chase
  [+6.0] urgency_pressure
         message uses manufactured urgency or secrecy (act now, don't tell anyone, account will be locked)
official channels (never from the message):
  website: https://www.chase.com
  phone: 1-800-935-9935
```

### registry

Dumps the brand registry so you can audit every channel and source for yourself.

### corpus

Checks every hand-labeled message in a corpus directory against a `gold.json` file and reports agreement. The bundled corpus lives at `harness/corpus/`.

```
python3 -m caveate.cli corpus harness/corpus
```

## How the scoring works

Signals are pure functions of the message text and the registry. The score is the sum of signal weights, and the tier comes from the score. The weights:

| Signal | Weight |
| --- | --- |
| lookalike domain (host is a few edits from the brand's real domain) | +9.0 |
| payment or credential demand (gift cards, crypto, Zelle, "safe account") | +9.0 |
| government impersonator (IRS/SSA, which never text first) | +9.0 |
| manufactured urgency ("act now", "account will be locked", "don't tell anyone") | +6.0 |
| verification request ("verify your account") | +3.0 |
| random 10-digit sender claiming to be a service | +3.0 |
| phone number embedded in the message | +3.0 |
| sender is a short-code shape | -2.0 |
| sender matches a short code the brand actually uses | -4.0 |
| brand claimed | 0.0 (context only) |

Example: a message is a +9 lookalike and a +6 urgency. Score 15, SCAM. A USPS message from short code 28777 with no other signals scores -4, SAFE.

The one rule the scoring never breaks: a phone number or link found inside the message is always added to the suppressed list and never appears in the recommended channels. Recommended channels come only from the registry, and the harness asserts this.

## The registry

`src/caveate/brandregistry.py` holds the entry per brand: real website, real phone number, the short codes and sender IDs the brand actually uses, and the behaviors the brand or the FTC says it would never do. Each row carries a source link. Brands covered include Chase, Wells Fargo, Bank of America, PayPal, USPS, FedEx, DHL, Amazon, Apple, Microsoft, Best Buy / Geek Squad, E-ZPass, PG&E, IRS, and SSA. "USPS", "chase", "amazon" and the other bare-name aliases all resolve so a normal message gets the right brand.

## Determinism and privacy

The same input always produces byte-identical JSON, including messages that contain phone numbers (extraction results are sorted before use). The harness runs the same message twice and compares bytes. Nothing is random, nothing is a model, nothing leaves your machine, and there is no telemetry.

## Verifying

`harness/verify.sh` proves the guarantees on every run:

```
bash harness/verify.sh
```

It checks gold agreement on the 12-message corpus (tier and score), byte-for-byte determinism on a phone-bearing message, the suppressed-versus-recommended invariant, exit-code gating, and the `explain`, `corpus`, and `registry` subcommands.

## Limits

- English and US-centric: the registry, the 7726 / reportfraud.ftc.gov defaults, and the patterns are built for US messages. A UK or non-English set is future work.
- The corpus is 12 hand-labeled messages. It represents the common legit and illegit shapes, not a random sample. Precision against an independent public dataset (UCI SMS, Mendeley smishing, and so on) is the next step before any accuracy claim.
- Novel rewording evades a rule engine. A scam in fresh idiom with no payment keywords and no link lands in CAUTION, not SCAM.
- Lookalike detection uses edit distance against the real domains. It is not yet punycode or homoglyph aware.

These limits are the trade for being auditable, offline, and deterministic. The right question for Caveate is not "did it catch everything" but "did it stop me from calling the number in the message."
