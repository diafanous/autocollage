# Codex Instructions: Physical Connector

Before making physical-connector changes, read:

- docs/superpowers/specs/2026-10-13-physical-connector-design.md

The design spec is the approved source of truth for the project's visitor experience, first-release scope, hardware assumptions, phases, and budget. If a new request conflicts with it, call out the conflict and get a decision before expanding the scope.

## Project objective

Build a reusable tactile controller so a student or professor can shape a live AutoCollage composition projected from the user's laptop. The enclosure's top surface should invite visitors to change and remake the drawing through physical controls. Keep the projected work visually central and make the relationship between each control and its effect understandable.

## First-release boundaries

The first release consists of code, the controller model, and the parts/build information required to construct the controller. It includes:

- Four physical linear faders and five momentary bank buttons for the twenty AutoCollage sliders.
- Wired USB-C-to-USB-C control using USB CDC serial or another documented direct USB serial interface.
- Controller firmware, a versioned generic input protocol, an AutoCollage profile/adapter, and a documented extension path for additional applications.
- Editable CAD source for a standalone controller enclosure, printable STLs sized for the user's A1 mini and P1S, wiring/pin map, assembly instructions, Windows setup, operation, troubleshooting, and a fully priced BOM.
- Reuse of the user's laptop, independently placed Epson 4855 projector, webcam, printers, available woodshop, and white/black PLA or translucent PETG where appropriate. A table/platform is free; the tactile controller is a separate peripheral.

Do not include webcam vision, Bluetooth, a force-sensing pen, interactive canvas-node placement, wireless control, or other Phase 2 features in the first-release code or BOM. Keep any first-release extension seam small and documented. The separate Phase 2 topic branch is physical-connector-phase2-vision-pen.

## Technical requirements

- Recheck the latest stable Windows AutoCollage release, its source layout, and required runtime immediately before implementation. At design approval on 2026-10-13, the latest stable release was v0.1.4 with autocollage-0.1.4.exe; do not treat that as a permanent version.
- Do not assume the released executable has a hardware API. Work from the current source and use an application-owned state interface or supported extension point.
- Do not use screen coordinates, mouse injection, OCR, keyboard shortcuts as fake parameter controls, or fragile UI scraping.
- Keep hardware identities and normalized input values generic. Put AutoCollage parameter names and mapping in the app profile/adapter, not in the firmware.
- Map five banks of four parameters. Preserve normal AutoCollage UI use and define how concurrent edits, disconnect/reconnect, malformed input, and shutdown are handled.
- Use soft takeover/pickup or an equally reliable mechanism so switching banks cannot make a fader snap its parameter to a mismatched physical position.
- Keep the USB connection wired in the first release. Include a replaceable cable and strain relief in the physical design.
- Design a compact, serviceable standalone tabletop controller with tactile, readable labels, comfortable fader travel, rounded user-facing edges, low-voltage USB power, strain relief, and replacement access for the board, buttons, faders, and cable. The controller may sit near the Epson 4855 but must not depend on, attach to, support, cover, or obstruct the projector. Use the free table/platform as needed; no projector mount, enclosure, or integrated support is part of this release.
- Provide the editable source model as well as exported STLs. Document materials, print orientation, assembly clearances, and optional woodshop-built parts. Do not assume purchased wood or filament when the user already has those materials.

## Budget rule

The complete purchase total for the standalone tactile controller, including its enclosure and every required component, must not exceed US$50 after shipping and tax. Use Brooklyn, New York as the delivery location. Amazon is allowed and the user has Prime; count free shipping only for listings that actually qualify for delivery to Brooklyn under Prime, and include the checkout tax for the destination. Count all required switches, faders, board, wire, fasteners, connectors, enclosure materials, and a data-capable USB-C-to-USB-C cable if one cannot be reused. The Epson 4855 projector is already owned and is physically separate from the controller; exclude it from the controller purchase total. A supporting table/platform is free. Also exclude the user's laptop, webcam, printers, filament, and woodshop tools.

Before marking the BOM compliant, verify current prices and calculate the total delivered to Brooklyn, NY, including destination tax and shipping. Amazon Prime listings may be used when Prime delivery is available to the destination. If checkout charges or delivery eligibility cannot be confirmed, mark the BOM estimated/unverified and require a confirmed all-in total of US$50 or less before locking the BOM. If the design exceeds US$50, revise it or show a feasible alternative; never present it as compliant. Do not purchase components or place orders.

## Branch layout

The umbrella branch is physical-connector. Put independent work on these topic branches, each starting from the umbrella branch:

- physical-connector-enclosure — enclosure, control-panel CAD, printed parts, and woodshop interface.
- physical-connector-firmware — controller firmware and generic USB protocol.
- physical-connector-autocollage-adapter — AutoCollage state bridge and profile.
- physical-connector-bom-docs — parts sourcing, budget, wiring, assembly, and user documentation.
- physical-connector-phase2-vision-pen — deferred webcam and Bluetooth force-pen exploration.

Git cannot have physical-connector as both a branch and a parent path for branches named physical-connector/topic. Use the hyphenated names above. Work on the branch matching the change. Do not update, reset, delete, or overwrite a topic branch that predates this work or contains work beyond the approved setup commits. Check that a topic branch name is free before creating it. Do not merge, publish a release, or create a pull request unless the user asks.

## Definition of first-release completion

The first release is ready for build review when a reader can obtain the controller source and quoted parts for US$50 or less delivered to Brooklyn, make the standalone controller enclosure, assemble and wire it, set it up on Windows with the current AutoCollage source, select any bank, control all twenty sliders without jumps, see parameter changes in the projected composition, recover from disconnects, and continue operating the application normally while the Epson 4855 remains a separate display device. Keep Phase 2 visibly deferred.
