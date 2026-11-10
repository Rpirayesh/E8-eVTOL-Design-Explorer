E8 eVTOL Design Explorer — Offline Student Edition 1.1

GET STARTED
1. Extract this ZIP (Windows: right-click > Extract All; Mac: double-click ZIP).
2. Double-click E8_eVTOL_Explorer_Offline.html.
3. If prompted, open the file in Chrome, Edge, Firefox or Safari.

No account, sign-in, internet, installation, server, Python or other software is required beyond a modern web browser with JavaScript enabled. Open the downloaded file in a browser, rather than an email or learning-platform preview. The file runs directly from your computer, including from a USB drive.

USING THE EXPLORER
- Choose Winged or Wingless and change the speed or aircraft inputs.
- Expand the input groups for wing, rotor, battery and mission assumptions.
- Select Power or Range above the graph; click the graph to set speed.
- Open Model & equations to inspect the equations, assumptions and citations.
- Open Validation to inspect analytical checks and five independent benchmarks.
- Use Export study to save a CSV of inputs, both configurations and the speed sweep. Submit that CSV with your explanation if your instructor requests it.
- Use Reset to restore the illustrative starting assumptions.

Inputs are saved only in your browser when local-file storage is supported. If your browser blocks local storage, calculations still work; export your results before closing. Browser storage behavior may differ when the HTML file is moved or renamed. Each student has a separate local copy. This file contains no cloud sync, login, analytics or external dependencies. Its security policy blocks network connections. Reference URLs are displayed as text and are not opened automatically.

SHARING
Send this ZIP through your normal class distribution method. Students can use it offline after downloading and extracting it. The hosted private explorer is separate; this package does not change its access or make it public.

MODEL SCOPE
Two occupants and eight equal, non-overlapping tilting rotors. The optional wing adds mass and aerodynamic drag. Cruise is steady, level and in still air. Battery energy is pack-level; range deducts hover and a user-entered transition/climb allowance and retains the chosen reserve. Motor, battery-power, energy and advance-ratio screens can withhold range. These are concept-level estimates, not flight-performance or airworthiness approval. All starting values are illustrative assumptions, not measured properties of a particular aircraft.

VALIDATION
Edition 1.1 passed 20,245 independent numerical operating-point checks, 3,061 exact-range mission checks, 600 separate exact/inside/outside trip regressions, 339 invalid-input checks, and 19 offline software test groups comprising 2,212 simulated UI operations. Its nine embedded reference checks and five stored numerical cases pass. These verify the implementation under its stated assumptions, not real-aircraft performance. See AUDIT_REPORT.md for the test methods and browser-verification limits.

AUDIT REVISION 1.1
- Fixed floating-point roundoff at an exactly exhausted cruise-energy budget: a numerically zero mission margin no longer becomes a false energy shortfall.
- Kept CSV export visible at tablet/narrow-window widths and added its accessible name.
- Blocked export while an invalid numeric edit remains highlighted; correct that input or use Reset before exporting.
- Labeled range as energy-based, strengthened the model-domain explanation, and added rotor blade-loading diagnostics without inventing a universal pass threshold.
- Added an embedded exact-range mission-boundary regression check.
- Lift, power, range equations, input defaults and the five numerical reference cases are unchanged.

See AUDIT_REPORT.md and VALIDATION_EXAMPLES.json for the independent review, tested examples and limits of validation. The offline package does not change access to the separate private hosted version.
