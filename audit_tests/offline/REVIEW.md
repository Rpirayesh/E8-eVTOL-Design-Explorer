# Independent software/offline review

Reviewed the exact original delivered HTML and final revised v1.1 file without editing either.

## Findings and fixes

- Original: medium-severity responsive issue hid the only CSV export button between 621 and 820 CSS px. The revised CSS removes that hide rule and adds an explicit accessible export label. Regression check passed.
- Original: low-severity ambiguity allowed CSV export while a numeric field displayed an invalid pending edit; the model and CSV correctly retained the last valid state and displayed a notice. Revised behavior blocks export until the highlighted input is corrected. Both browser and deterministic regressions passed.
- No additional calculation/display/CSV inconsistency was found. Physics accuracy is covered by the separate numerical and physics reviews, not established by this software review.

## Deterministic coverage

Original: 17 groups passed, 2,207 simulated UI operations.
Final revised: 19 groups passed, 2,212 simulated UI operations. Includes 1,000 mixed repeated edits/resets, 56 min/max field edits, 168 invalid-edit cases, 10 storage scenarios, configuration/chart/view controls, chart click conversion, and 40 locally generated CSV exports with both configurations and each 101-point sweep checked against current model state. All simulated network API calls remained zero; script, styles and benchmark fixtures are inline and the security policy blocks connections. Storage denial/corrupt state cases continued calculating successfully.

## Browser verification and limits

The exact revised HTML was served via the supported managed preview and tested in the browser at http://127.0.0.1:4173/. Speed, configuration, range controls, all 9 embedded checks, all 5 independent reference cases, invalid-input export blocking, corrected-input CSV download and reset all worked. The 621–820 CSS px fix was checked statically; a separate rendered 700 px screenshot was not available.

Fresh direct file:// testing could not be completed in this environment. Native Chromium launched, but native input failed because its AT-SPI provider was unavailable. The cloud browser permits only http/https and rejected file protocol; no security workaround was attempted. Offline structure was instead tested deterministically with network APIs unavailable and with both localStorage read/write access denied. No claim of fresh file:// or cross-browser testing is made.
