# Physical Connector Design

Status: approved first-release design, ready for implementation planning  
Repository: diafanous/autocollage  
Design date: 2026-10-13  
Umbrella branch: physical-connector

## Experience

A student or professor approaches a projected composition that is already moving and changing. A compact enclosure sits between the audience and the laptop, with tactile controls on its top. The projector remains the main display. A visitor can select a group of visual parameters and shift physical sliders to change how the composition looks, then keep making and remaking the drawing as the image responds.

The controls should feel discoverable and inviting. They should communicate that visitors can shape the work, not just start or stop a presentation. The installation should remain usable by the operator through AutoCollage's normal interface.

## Goals

- Build a first-release wired tactile controller for AutoCollage on Windows.
- Let a walk-up visitor adjust all twenty AutoCollage sliders using four physical faders and five section buttons. Each button selects one bank of four parameters.
- Keep parameter changes visible in the projected composition with responsive feedback.
- Make the controller reusable with other applications through replaceable, declarative app profiles and a stable controller-to-host protocol.
- Use the existing laptop, independently placed Epson 4855 projector, USB webcam, A1 mini and P1S printers, white and black PLA, translucent PETG, and available woodshop as existing resources. The tactile controller is a separate peripheral; no projector structure is required. A table/platform is free.
- Keep the delivered purchase cost of the complete standalone tactile controller, including its enclosure and required components, at or below US$50 total, including shipping and tax, for delivery to Brooklyn, NY. Amazon Prime may be used when eligible; include destination checkout tax.

## First-release scope

The first release includes the complete code, model, and required parts information to build and use the tactile controller:

1. Controller firmware for wired USB-C to USB-C operation using USB CDC serial or an equally direct, documented USB serial interface.
2. A host-side AutoCollage adapter integrated with the application or its supported app-side code. It must read/write application parameter state through an application-owned interface.
3. A generic, versioned controller protocol and replaceable app profile format. AutoCollage is the first profile.
4. Editable enclosure and control-panel CAD source plus printable STL files sized for the A1 mini and P1S. Design a standalone tabletop controller that works with the user's woodshop and owned filament. Place the projector separately; projector mounts or integrated structures are outside the first-release controller.
5. A complete parts list with component quantities, exact part/source links, quoted item prices, and the all-in total after shipping and tax.
6. Wiring diagram, pin map, assembly steps, Windows setup instructions, operation guide, and troubleshooting notes.
7. A documented verification procedure for USB connection, all controls, bank switching, parameter feedback, reconnection, and ordinary AutoCollage mouse/keyboard operation.

The current latest stable Windows release was checked on 2026-10-13: AutoCollage v0.1.4, with release asset autocollage-0.1.4.exe. Recheck the latest stable Windows release, source layout, and runtime requirements immediately before implementation. Do not assume the release executable exposes a controller API. The approved direction is to work from the current source and integrate an app-owned bridge rather than automate screen coordinates.

## Interaction and mapping

- Four physical linear faders provide the active bank's four continuous controls.
- Five momentary section buttons select banks 1 through 5. Each bank maps to four of the twenty AutoCollage sliders.
- The active bank and parameter names must be clear to the operator and visitor. Prefer labels and feedback using the enclosure and existing application UI before adding display hardware.
- Bank switching must not snap AutoCollage values to the current physical fader positions. Implement soft takeover/pickup (or an equally reliable documented strategy) so a fader only takes control of its assigned parameter once its position reaches or crosses the parameter's current value.
- Keep normal AutoCollage controls functional. Define behavior for simultaneous physical and on-screen edits, controller disconnect/reconnect, invalid messages, and application shutdown.
- Keep updates stable and smooth. Do not emit noisy serial changes that visibly jitter the image.

## Adaptable architecture

Separate hardware input, the USB protocol, generic parameter mapping, and app-specific behavior. The physical controls should report control identities and normalized values; they should not hard-code AutoCollage variable names into firmware. A profile should define bank labels and map each fader slot to an app parameter. The AutoCollage adapter owns the mapping from profile parameters to the actual app state. Document how a future app can add a profile/adapter while reusing the controller, enclosure, and build.

Use a direct app-side bridge or supported extension point. Do not use mouse movement, screen coordinates, OCR, keyboard shortcuts masquerading as parameter control, or fragile UI scraping as the controller integration.

## Cost and sourcing rule

The complete standalone controller must cost US$50 or less delivered to Brooklyn, NY. Include every newly required purchased controller component and enclosure material, shipping, and tax. Amazon may be used; assume the user has Prime, but count free shipping only for listings that are actually Prime-eligible for delivery to Brooklyn. Include the destination's checkout tax. Include a USB-C-to-USB-C data cable if the user cannot reuse one. The Epson 4855 projector is already owned and is used separately; the free table/platform is not part of the purchase total. The existing laptop, webcam, printers, filament, and woodshop may also be treated as already-owned resources; do not add their purchase cost.

Before declaring the BOM compliant, obtain a current quote for every required purchased controller item and calculate the delivered total for Brooklyn, NY. If listing eligibility, shipping, or tax cannot be confirmed, leave the BOM explicitly estimated/unverified and require a confirmed all-in total of US$50 or less before locking component choices. Do not hide shipping, tax, small hardware, cable, or enclosure materials outside the total. If the total exceeds US$50, revise the design or present a compliant alternative; never describe an over-budget design as meeting the limit.

## Physical design and materials

Build a compact, durable, serviceable standalone tabletop controller. It can be placed beside the Epson 4855, but it must remain mechanically independent: it must not sit on, attach to, support, cover, or require a custom bay for the projector. The free table/platform can support the controller. Keep the projector's separate projection path and ventilation unobstructed.

Provide comfortable fader travel and buttons identifiable by touch. Use simple printed parts where they improve repeatability, with optional woodshop-built parts. Provide CAD source, print orientation, material choice, and access for replacing switches, faders, and the controller board.

## Explicit non-goals for first release

- Webcam tracking, computer vision, pen/stylus input, force sensing, Bluetooth, or any wireless connection.
- Replacing or modifying the projector, laptop, webcam, printers, or woodshop.
- Purchasing parts or placing orders on the user's behalf.
- Adding controls for features beyond the AutoCollage slider bank unless necessary for clear operation and within the cost cap.
- Building a polished production enclosure or claiming classroom safety certification.

## Phase 2: vision pen

Phase 2 may explore the existing USB webcam and a Bluetooth pen with a force sensor at its tip. Its goal is to estimate where the tip touches the projected canvas by combining video and force data, then add nodes interactively while the physical controller continues to change selected parameters.

Keep this work on its own branch, physical-connector-phase2-vision-pen. In the first release, include only a short architecture note or stable extension seam if it does not add hardware, cost, or scope. Do not add a camera pipeline, Bluetooth dependency, pen hardware, calibration UI, or node-placement feature to the first-release implementation.

## Acceptance criteria

The first release is ready for a build review when:

- The complete firmware, host adapter/profile, editable CAD, printable model, wiring/build documentation, and priced BOM are present.
- Four faders and five bank buttons can address all twenty AutoCollage sliders.
- Switching banks does not cause unintended jumps; normal GUI edits remain usable.
- The protocol and profile boundary make an additional application profile feasible without changing enclosure mechanics or firmware identities.
- Windows setup is based on the latest stable AutoCollage Windows release and verified runtime requirements.
- The quoted delivered total for the complete standalone controller, including all required purchased parts/materials, shipping, and tax to Brooklyn, NY, is US$50 or less; otherwise the design is not marked budget-compliant.
- The controller works as a separate peripheral and does not require a mount, support, or enclosure for the Epson 4855.
- Phase 2 remains deferred and separately scoped.
