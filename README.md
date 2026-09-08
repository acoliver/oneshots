# oneshots

A monorepo for one-shot tools. Each subdirectory is a self-contained project built and verified in a single pass: research first, a decision record, code with no runtime dependencies, and a harness that proves the claims.

## Contents

- `caveate/` - a deterministic, offline smishing and scam triage CLI. Paste a suspicious text, get a verdict, the reasons, and the one official channel that matters.

## The prompt behind Caveate

Caveate came out of a single brief:

> Build and verify "Caveate", a deterministic, offline, auditable smishing/scam triage CLI (Python) with a brand registry, signal-based scoring engine, and `check` / `explain` / `corpus` / `registry` subcommands.

A research-first pass (recorded in `caveate/research/DECISION.md`) turned that brief into a concrete requirement set:

- every design decision tied to a cited source
- same input always produces byte-identical output
- no machine learning, no runtime dependencies, no network access
- the verdict never leans on a number or link found inside the message; it routes to a maintained registry of each brand's real channels
- exit codes that let a pipeline fail on a likely scam
- the stated limits: Caveate flags known bad patterns, it never certifies a sender as safe

## Layout

```
oneshots/
  README.md                this file: what the repo is and how caveate was briefed
  caveate/
    README.md             caveate from a user's perspective: what it does, how to run it
    research/DECISION.md  the research and the decisions that design follows
    src/caveate/          engine, CLI, brand registry, extractor
    harness/              verify.sh plus a hand-labeled corpus with a gold file
```

## Why "oneshots" exists

A place to keep small builds that are finished, verified, and worth pointing to. Each one ships with the evidence for what it is rather than a promise.
