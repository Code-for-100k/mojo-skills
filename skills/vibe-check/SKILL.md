---
name: vibe-check
description: Structured idea evaluation before committing to build anything. Use this skill whenever the user brings a new idea, experiment, or project — phrases like "what if we...", "I want to try...", "could we build...", "let's explore...", "have you heard of...", "what about using...", "should we...", or any speculative/exploratory language about a new tool, service, workflow, or project. Also trigger when the user shares a link to a new tool and seems excited about it. The goal is to research first, evaluate honestly, and plan with clear exit points — before any implementation happens.
---

# Vibe Check

When the user brings a new idea, don't jump to "here's how to do it." Run this evaluation process instead. The goal is to figure out if the idea is worth pursuing before investing time building anything.

Scale the depth to the size of the idea — a quick 5-minute pass for small things, a full 15-20 minute evaluation for big ones. But always follow the phases in order.

## Phase 1: Landscape Research

This comes first, always. Before discussing how to do anything, find out what already exists.

Search the web and GitHub thoroughly:
- What tools, projects, or services already do this or something close?
- How mature are they? (GitHub stars, last updated, active community, documentation quality)
- What problems did people run into? (GitHub issues, Reddit threads, blog post warnings)
- Is there a hosted service or existing tool that solves this without building anything?

Present findings in whatever format is clearest for the topic — comparison table, ranked list, or "if you want X, use Y" mapping. Pick the format that helps the user understand their options fastest.

This phase is exploration, not recommendation. Show the landscape before pushing a direction.

The reason this matters: the user's biggest frustration is discovering that a better tool already existed after they've spent hours building something. Catch that early.

## Phase 2: Honest Cost-Benefit

Before any plans or milestones, answer these questions plainly:

- **Is this worth doing?** What's the tangible, concrete benefit — in real terms, not hypotheticals?
- **What does it cost?** Time to set up, money (if any), and ongoing maintenance burden.
- **How does it compare to doing nothing?** Often the right answer is "keep using what you already have" or "just pay for the hosted version." Frame this comparison explicitly.
- **What's the realistic quality?** If building a DIY version of something, be honest about how it compares to the professional/paid alternative.

Style guidance:
- Recommend what you'd do, but flag what you're uncertain about
- Be direct but constructive — "this probably isn't worth the effort, but here's what might work instead"
- Don't sugarcoat and don't oversell
- If the answer is "don't do this," say so clearly and explain why

## Phase 3: Milestone Plan with Exit Gates

Only proceed here if Phase 2 says the idea is worth exploring. Break the project into milestones where each one:

- Has a **clear goal** and rough time estimate
- Ends with a **decision gate** — go, stop, or pivot
- Builds on the previous milestone, so stopping early still leaves value
- Starts with **low-effort validation** — try before you build

At each decision gate, include:
- **Exit pathway**: What does "stop here" look like? What did you still gain by getting this far?
- **What this grows into**: If it goes well, what are the potential future directions? The user thinks in possibilities and wants to see the bigger picture, even when starting small.

Keep milestones high-level. No implementation details, no config files, no terminal commands. The user decides go/no-go first — details come during execution.

## Phase 4: Security Review

Flag every risk in plain, concrete language — not jargon.

- What could go wrong if something is misconfigured? (say "someone could use your server for free" not "this increases your attack surface")
- What's exposed to the internet?
- What credentials or sensitive data are involved?
- Mitigations are REQUIRED STEPS in the plan, not optional add-ons

The user relies on this review as their security layer. They do not see security implications on their own — not "not ahead of time," but at all. If you see a risk, say it. Default to the secure option unless the user explicitly chooses otherwise.

## Principles

These shape how the evaluation is presented:

**Always include:**
- Milestone breakdowns with decision gates
- Honest cost-benefit analysis (including "don't do this")
- Security risks in plain language
- "What could this grow into" — future possibilities

**Avoid early in the evaluation:**
- Implementation details (save for after go/no-go)
- Technical commands, configs, and code snippets
- Architecture diagrams

**Decision format:** Recommend with caveats. "I'd do X because Y, but I'm not sure about Z." The user will push back if they disagree — that's the dynamic that works.

**Use interactive questions:** When there are meaningful choices to make (approach, priority, scope), use structured multiple-choice questions rather than open-ended text. This helps the user think through options without needing to formulate answers from scratch.
