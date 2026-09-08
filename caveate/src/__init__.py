"""Caveate: deterministic, offline smishing triage.

Caveate (cue-AY-tee) is a free, offline tool that triages a suspicious
text message, email, or phone call transcript and tells you where it really goes:
the brand's own site and phone number (via a cited registry), never the number
or link inside the suspicious message.

Nothing leaves your machine and the verdict is deterministic: same input,
byte-for-byte same JSON. The engine is a small pure decision table, so every
verdict can be audited by reading the registry.py and engine.py source.

The five signals Caveate can decide:
  1. Sender identity (short code vs random 10-digit vs alpha ID)
  2. Where the link actually goes (canonical vs lookalike)
  3. Whether the ask contradicts the brand's published 'we will never...'
  4. Psychological pressure (urgency, secrecy)
  5. Payment/credential demand (gift cards, crypto, wire, 'safe account')

For research, decisions, and sources see research/DECISION.md.
"""
