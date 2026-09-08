# Caveate — research-first decision record

Everything in this file was gathered before a line of code was written. Source is provisional (web/exa searches dated 2026-09-07), the numbers are the anchor, and each design choice below is tied to a citation.

## 1. The problem, in numbers

Imposter scams were the most-reported fraud category to the FTC for the fifth year running in 2025, with 1M+ reports and **$3.5B in reported losses** (up from $2.95B in 2024; ~$1B to business impersonators, led by bank impersonators, plus ~$920M to government impersonators). Sources: FTC press release 2026-06-15 (ftc.gov/news-events/news/press-releases/2026/06/ftc-data-show-people-reported-losing-3-point-5-billion-imposter-scams-2025); CNBC 2026-06-26; Forbes Advisor 2026-06-29; FTC "Top Co Complaints" monthly PDFs.

The channel that grew fastest is text. The FTC's own analysis: bogus bank fraud warnings are the most-reported text scam, and the most-impersonated companies are Best Buy/Geek Squad, Amazon, PayPal, with delivery and toll firms (USPS most impersonated overall per Unit 42's global smishing report, with 28,045 USPS-impersonating FQDNs) close behind. Unit 42/Palo Alto Networks, "The Smishing Deluge", 2025-10-23.

The same single piece of advice appears at the end of every one of these advisories, and it is always the same sentence: do not use the number, link, or sender in the message; reach the organization through a channel you already know — the number on the card, the official site typed by hand. Source after source says this: FTC (consumer.ftc.gov/features/how-avoid-imposter-scams; irs.gov/newsroom/ways-to-tell-if-the-irs-is-reaching-out-or-if-its-a-scammer; uspis.gov/news/scam-article/smishing-package-tracking-text-scams; scamverify.ai FAQ; verifydial.com; tuteladigitalis.com/impersonation-index; GeeksforGeeks/Medium rule-based smishing posts). Yet every regulator says this sentence only exists in prose, and a person under pressure has to (a) know which company the message is about, (b) know where the real channel is, and (c) remember to go there instead of acting. That is a cognitive load that software can remove.

Operation Level Up is the strongest evidence that a specific, timely warning during an active scam prevents money loss: the FBI notified 4,323 crypto-fraud victims and estimated $285,639,989 in avoided losses (IC3 2024 Annual Report). A decision aid that points the victim to the official route earlier in the scam is the consumer-side version of that program.

## 2. Market scan — what already exists (and why the lane is still open)

- **LLM-paste checkers** (bewary.app, scamchecker.app, gacs.app, aiscamchecker.com, isitspamchecker.com, scamverify.ai): paste or screenshot, AI returns a risk verdict. All are black boxes by design: they give a score, occasionally a "why" panel, and then the generic advice again. None ship an auditable, hand-maintained, cited registry of each brand's real sender IDs, real short codes, and real official channels, and none let a user check "this is what the brand says it would never ask for" against the actual text. They also send the message to a server. Verification 2026-09-07: confirmed dozens of these; none expose a deterministic rule set or a per-brand cited policy table.
- **Call/sms blockers and call-screeners** (SafeHaven app, Kova, lilyServes, SilverGuard, ScamLight, veriCall, Trustline, scam-sentinel): they protect the *next* call/text by filtering or interrupting it. They are the right tool for an installed phone; they are not a tool you can paste a text into and get "here is the real number (from the bank's page, linked)". They are also all dependent on ML/ASR/cloud or fine-tuned on-device models; none claim a per-brand canonical-contact directory that a user can audit.
- **Generic suggestion iframes** (validatethis.org): a checklist of "8 things to check" with no per-brand data.
- **Sender-ID registries** (ACMA Australia, ComReg Ireland, OFCA Hong Kong, CEPT, MEF UK, US Short Code Registry/usshortcodes.com, incogni's compiled list): these are the right databases but they are fragmented, split across five regulators, some behind a search portal, and aimed at senders and operators, not at a panicked consumer with a phone. No open, machine-readable, per-brand canonical-contact directory exists that a user (or program) can query offline. This is the exact gap we fill, with citations per row.

Novelty claim (to be kept honest in the README): the *deterministic per-brand canonical-contact directory with cited policies*, combined with a paste-your-text smishing analyzer whose verdicts are auditable rules rather than a model — the consumer side of the sender-ID registry story. No existing product combines a cited brand directory, sender-ID/short-code matching, lookalike-domain detection, and the "official channel override" decision — in a package with zero runtime dependencies and byte-for-byte determinism.

## 3. The five signals a machine can decide (and each is testable)

1. **Sender identity.** Is the sender a known short code, a known alpha sender ID, a random 10-digit number, or an international/numeric sender that a real bank/delivery firm would not use? (cite: incogni short-code list, Chase's own SMS terms page listing its codes, US Short Code Registry, CEPT/ComReg/ACMA registration rules — all show real businesses use short codes / registered alpha IDs.)
2. **Where the link goes.** Canonical + lookalike: destination host vs. the brand's canonical domains; suspicious TLDs (.xyz/.top/.click/.zip), URL shorteners, IP-address hosts, punycode/homoglyph. (cite: isitspamchecker "legitimate vs scam URL" pairs; unit42 FQDN typosquatting; detection.fyi USPS impersonation rule showing lookalike domains and shorteners are the concrete attack hundle.)
3. **What the text asks.** Overlap with the brand's documented "we will never ask" policy (no bank asks for your OTP; no courier asks for a reshipping fee except DHL's specific customs nuance; IRS/SSA/CBP do not text you first at all). (cite: ireland ComReg Registry Q&A "Does a consumer need to register"; tuteladigitalis impersonation index aggregating 28 orgs' own never-statements; IRS/USPS official pages.)
4. **Urgency/psychological pressure.** Secrecy ("don't tell anyone"), threats ("warrant", "arrest"), manufactured deadlines, "act now". (cite: FTC How to Avoid Imposter Scams; Scam checker glossaries; classic smishing corpus taxonomy.)
5. **Payment or credential demand.** Gift cards, crypto, wire, "read back the code", "move your money to a safe account" — the FTC's stated red line for bank scams. (cite: FTC 2025 statements: "legitimate will never tell you to move money to protect it"; IC3 crypto investment fraud $7.2B.)

The engine is a pure decision table: signals accumulate weighted evidence, tiers are SCAM / LIKELY_SCAM / CAUTION / SAFE / UNKNOWN, and the output always ends with at least one button's worth of canonical action: the exact official site and phone for the brand *contained in the message*, or "no brand identified" + the default advice (report to 7726 / reportfraud.ftc.gov).

## 4. Why it is honestly better, and what it will never claim

- Deterministic: same input, byte-identical verdict JSON, double-run test in the harness.
- Auditable: every verdict lists the signals, each signal has a cited source; no weights are hidden.
- Private by default: the analysis is a local function; nothing leaves the machine. (All competing paste-checkers upload to a server by design.)
- Canonical override: it never tells you to trust the message's own contact; every recommendation routes to a separately sourced official channel, which is the FTC's own instruction.
- It will never claim to catch every scam, will not run a deepfake/LLM classifier, and will not say a sender is "safe" — only "no known scam signals" with the specific remaining checks.

## 5. Measurable success criteria (the harness proves these)

1. On the labeled corpus the verdicts match the gold file exactly (recall/agreement = 100% on the corpus; this is a rule engine, not a model).
2. Determinism: two runs of the same input produce byte-identical JSON (asserted by the harness).
3. Each canonical-routing recommendation, when the corpus message is routed to the brand in the message, goes only to a canonical domain or phone drawn from the registry, never to a contact taken from the message (invariant asserted by a counter-test where the message's own contact is included and must always be suppressed).
4. Exit codes gate CI: `caveate check` exits non-zero above CAUTION so a pipeline can fail on LIKELY_SCAM/SCAM.

No time estimates are made in this record; the effort step is bounded by the implementation task that follows.
