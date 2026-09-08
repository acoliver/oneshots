# oneshots

A monorepo for one-shot tools. Each subdirectory starts from a single brief: use a research-first process to create something that genuinely makes the world a better place, something measurable, with a runnable harness that proves it works. Each project ships its research, its code with no runtime dependencies, and that harness.

## The brief

The prompt behind the repo, cleaned up from how it was given and genericized so it no longer points at local folders from earlier projects:

> Use a research-first process to create something that genuinely makes the world a better place. Do not duplicate acoliver/vellego: the project should be novel, either solving a problem with no established solution or offering a clearly different and better approach. It has to be measurable, and you have to be able to test that it works. Use web search and other tools to gather information. For the name: check that it does not already exist, including a patent-office search; pick a creative, defensible name that can't get you sued and does not collide in the namespace; make it pronounceable if you can. Consider alternative data sources, and draw on research from previous projects without being limited by it. Ship a runnable harness that tests whatever the thing does, and prove it works. If you use subagents, use only ones on the dsflash-mi300x profile, and no other subagents or models.

"Make the world a better place" is the headline. What keeps a one-shot credible: a name that is checked and defensible, evidence gathered before the build, and a harness anyone can run and watch pass.

## Contents

- `caveate/` - deterministic, offline smishing triage. Paste a suspicious text, get a verdict, the reasons, and the one official channel that matters. See `caveate/README.md` for how to use it.

## Layout

```
oneshots/
  README.md                this file: the brief, and what the repo holds
  caveate/
    README.md             caveate from a user's perspective
    research/DECISION.md  the research and the decisions that design follows
    src/caveate/          engine, CLI, brand registry, extractor
    harness/              verify.sh plus a hand-labeled corpus with a gold file
```
