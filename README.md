# oneshots

A monorepo for one-shot tools. Each subdirectory is a self-contained project built and verified in a single pass: research first, a decision record, code with no runtime dependencies, and a harness that proves the claims.

## Contents

- `caveate/` - a deterministic, offline smishing and scam triage CLI. Paste a suspicious text, get a verdict, the reasons, and the one official channel that matters.

## The prompt behind Caveate

Caveate came out of a single brief. Reproduced below, cleaned up from how it was given and genericized so it no longer points at the local folders of earlier projects:

> Use a research-first process to build something that genuinely makes the world a better place. Do not duplicate acoliver/vellego: the project should be novel, either solving a problem with no established solution or offering a clearly different and better approach. It has to be measurable, and you have to be able to test that it works. Use web search and other tools to gather information. For the name: check that it does not already exist, including a patent-office search; be creative and pick a defensible name that can't get you sued and does not collide in the namespace; make it pronounceable if you can. Consider searching alternative data sources, and draw on research from previous projects without being limited by it. Ship a runnable harness that tests whatever the thing does, and prove it works. If you use subagents, use only ones on the dsflash-mi300x profile, and no other subagents or models.

That brief became the concrete spec recorded in `caveate/research/DECISION.md`:

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
