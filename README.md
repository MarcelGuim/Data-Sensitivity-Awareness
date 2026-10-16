# Limiting the Blast Radius of Prompt Injection Through Data-Sensitivity Awareness

ECE1776 (Computer Security, Cryptography and Privacy), University of Toronto, Fall 2026. Group 3: Wasilat Ayinla, Khalid Challango, Marcel Guim.

We train an LLM agent to disclose company data according to its sensitivity tier and the requester's authorization, even under prompt injection. We compare an unprotected model, a model with a policy system prompt, and a sensitivity-trained model.

- Project docs: `docs/` (start with `docs/00-project-overview.md`; open questions and decisions in `docs/07-decisions-and-open-questions.md`).
- AI agents: instructions are in `AGENTS.md` (`CLAUDE.md`, `GEMINI.md` and `.github/copilot-instructions.md` point to it).
- When you make a decision, log it in `docs/07` with the date and who decided, so everyone's agents see it.
