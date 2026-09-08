# oneshots

A monorepo for one-shot tools. Each subdirectory starts from a single brief: use a research-first process to create something that genuinely makes the world a better place, something measurable, with a runnable harness that proves it works. Each project ships its research, its code with no runtime dependencies, and that harness.

## The brief

The prompt behind the repo, cleaned up from how it was given and genericized so it no longer points at local folders from earlier projects:

> Use a research-first process to create something that genuinely makes the world a better place. Do not duplicate acoliver/vellego: the project should be novel, either solving a problem with no established solution or offering a clearly different and better approach. It has to be measurable, and you have to be able to test that it works. Use web search and other tools to gather information. For the name: check that it does not already exist, including a patent-office search; pick a creative, defensible name that can't get you sued and does not collide in the namespace; make it pronounceable if you can. Consider alternative data sources, and draw on research from previous projects without being limited by it. Ship a runnable harness that tests whatever the thing does, and prove it works. If you use subagents, use only ones on the dsflash-mi300x profile, and no other subagents or models.

"Make the world a better place" is the headline. What keeps a one-shot credible: a name that is checked and defensible, evidence gathered before the build, and a harness anyone can run and watch pass.

Repos are pulled in as git submodules, so an existing one-shot can be added as a peer without copying its history into this repo.

## Contents

- `caveate/` - deterministic, offline smishing triage. Paste a suspicious text, get a verdict, the reasons, and the one official channel that matters. See `caveate/README.md` for how to use it.
- `vellego/` - deterministic, open-source remediation engine for web accessibility, plus a plain-language readability scorecard. Fixes machine-detectable failure classes in the source with a reviewable diff. See `vellego/README.md` for how to use it.

## Layout

```
oneshots/
  README.md              this file: the brief, and what the repo holds
  caveate/               smishing triage (Python, stdlib only)
    README.md            caveate from a user's perspective
    research/DECISION.md the research and the decisions that design follows
    src/caveate/         engine, CLI, brand registry, extractor
    harness/            verify.sh plus a hand-labeled corpus with a gold file
    tmp/                gitignored verification scratch space
  vellego/              submodule: accessibility remediation engine + readability scorecard
    README.md           what it does and how to run it
    docs/              design and research-round docs
    RESEARCH/          phase1 research outputs
    src/               scanner, remediators, plain-language, diff, CLI
    test/              vitest specs
    harness/           verify.sh plus fixtures (real and plain)
    site/              static landing page
```
