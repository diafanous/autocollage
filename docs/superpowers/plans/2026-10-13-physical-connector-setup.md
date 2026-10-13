# Physical Connector Project Setup Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task after the user approves the plan. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Add clear Codex instructions and an approved design spec to `diafanous/autocollage`, then create topic branches based on `physical-connector`.

**Architecture:** Keep this setup pass documentation-only. The root `AGENTS.md` directs future Codex work to the design spec; GitHub topic branches separate the enclosure, firmware, AutoCollage adapter, BOM/documentation, and deferred Phase 2 work.

**Tech Stack:** Markdown documents and GitHub branches; no software dependencies or product code in this setup pass.

**Spec:** `docs/superpowers/specs/2026-10-13-physical-connector-design.md`

## Global Constraints

- Target the GitHub project currently named diafanous/morphaic (formerly diafanous/autocollage); use physical-connector as the umbrella branch based on main.
- The latest Windows release at design time is v0.1.4; future implementation must recheck the latest stable Windows release.
- Keep all first-release required controller purchases, enclosure materials, shipping, tax, wiring, and a USB-C cable if needed at or below US$50 delivered to Brooklyn, NY. Amazon Prime may be used when the listing qualifies for delivery there; include checkout tax. The Epson 4855 is used separately and is not part of the controller build. The free table/platform may support the controller.
- First release is a wired USB-C-to-USB-C controller with replaceable app profiles; do not depend on screen coordinates.
- The physical-controller design call remains four linear faders banked across the twenty AutoCollage sliders and five momentary section buttons. The controller is a standalone peripheral that can sit separately from the user's Epson 4855; no projector support or integrated structure is required. The controller and enclosure must cost US$50 or less delivered to Brooklyn, NY, including shipping and tax; use Prime-eligible Amazon delivery when helpful.
- Phase 2 camera and Bluetooth force-pen work is future scope only.
- Do not modify the ChatGPT project's synced `sources/` files; make changes only in the specified GitHub repository.

## Review Focus

- BOM price must include every required standalone controller/enclosure item and remain at or below US$50 after shipping and tax to Brooklyn, NY; Amazon Prime is allowed when eligible. The projector is separate and the table/platform is free.
- Windows version compatibility can change; Task 1 requires rechecking the latest stable release before implementation.
- UI-coordinate automation would make the controller fragile; Task 1 prohibits it and requires a direct app-owned integration.
- Webcam and Bluetooth pen work could leak into the first release; Task 1 makes the phase boundary explicit.
- Keep the controller mechanically separate from the Epson projector; no projector-specific fit or support structure is needed.
- Git does not allow `physical-connector` alongside `physical-connector/<topic>`; Task 2 uses hyphenated topic branch names and verifies each ref.

---

### Task 1: Add the design spec and Codex instructions

**Files:**
- Create: `docs/superpowers/specs/2026-10-13-physical-connector-design.md`
- Create: `AGENTS.md`

**Interfaces:**
- Consumes: the user-approved design for the projected AutoCollage experience, hardware, budget, reuse goal, phases, and branch layout.
- Produces: a design spec recording intent, goals, non-goals, constraints, approved calls, and remaining builder choices; a root Codex instruction file that points to and operationalizes the spec.

- [x] **Step 1: Write the design spec** with the first-release deliverables, current release baseline, available equipment, US$50-or-less Brooklyn-delivered controller budget and standalone form factor, USB serial architecture, physical-control assumptions, adaptable app profiles, branch names, and Phase 2 boundary.
- [x] **Step 2: Write root `AGENTS.md`** instructing Codex to read the spec, recheck the latest Windows release, keep the first release scoped, source and price every required component, avoid coordinate-based automation, and document/verify the standalone controller build.
- [x] **Step 3: Fetch both files from `physical-connector`** and confirm they exist as UTF-8 text and preserve every global constraint above.

No software tests are applicable to Markdown-only changes; verify the saved file contents directly.

### Task 2: Create the scoped topic branches

**Files:**
- No file changes; create GitHub branch refs only.

**Interfaces:**
- Consumes: the updated head of `physical-connector` after Task 1.
- Produces: five topic branches that start at the umbrella branch and can evolve independently.

- [x] **Step 1: Check for existing topic refs** before creation; never move or overwrite an existing ref.
- [x] **Step 2: Create missing branches from `physical-connector`:** `physical-connector-enclosure`, `physical-connector-firmware`, `physical-connector-autocollage-adapter`, `physical-connector-bom-docs`, and `physical-connector-phase2-vision-pen`.
- [x] **Step 3: Fetch the branch refs** and confirm all five exist; report the parent and topic branch links without creating a pull request or merging anything.
