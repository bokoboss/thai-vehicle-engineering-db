# UI Polish Pass 2 — Visual QA Record

Issue #56 was executed against the accepted Release D baseline.

- Starting baseline: `6776f703e9b181cfda4745503b0d236f642a1929`
- Accepted release: `release_2026_09_d`
- Accepted vehicle count: 41 configurations
- Working branch: `codex/ui-polish-pass2-visual-qa`
- Capture method: Chrome with CSS viewports of 1440×900, 1024×768, and 390×844
- Screenshot policy: captures are local QA artifacts under `artifacts/ui-baseline/` and are not intended for commit

The selected detail record was `th-porsche-911-carrera-gts-992ii-delivered-2025`. The selected compare record set was:

1. `th-toyota-camry-hev-premium-luxury-new-release-2567`
2. `th-porsche-911-carrera-gts-992ii-delivered-2025`
3. `th-ford-ranger-wildtrak-20-biturbo-4x4-nextgen`
4. `th-lamborghini-revuelto-launch-2023-07-25`

The compare URL was `/compare?vehicle_1=th-toyota-camry-hev-premium-luxury-new-release-2567&vehicle_2=th-porsche-911-carrera-gts-992ii-delivered-2025&vehicle_3=th-ford-ranger-wildtrak-20-biturbo-4x4-nextgen&vehicle_4=th-lamborghini-revuelto-launch-2023-07-25&slot_3_q=toyota`.

The populated Design Check state used `available_clear_height_mm=2100`, `available_clear_width_mm=3000`, `lateral_allowance_each_side_mm=0`, `width_envelope=BODY_EXCLUDING_MIRRORS`, `maximum_vehicle_length_mm=5000`, `maximum_turning_value_m=20`, `turning_input_shape=RADIUS`, and `turning_reference=CURB_TO_CURB`. It assessed and displayed all 41 configurations, with PASS 0, FAIL 14, and INDETERMINATE 27.

## Inspection record

Severity is assigned to the observed baseline state. `ACCEPTABLE` means no production change was needed; `NOTICE` means a small production correction was made.

| Page / state | Viewport | Route, query, or UI state | Observation | Severity | Action | Retained capture |
| --- | --- | --- | --- | --- | --- | --- |
| Vehicles / default | 1440×900 | `/vehicles` | Shell, navigation, filter card, table hierarchy, and row density read cleanly. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/vehicles-default-1440x900.png` |
| Vehicles / default | 1024×768 | `/vehicles` | Header and filter controls wrap without page-level overflow; catalog scroll affordance is clear. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/vehicles-default-1024x768.png` |
| Vehicles / default | 390×844 | `/vehicles` | Mobile navigation and filter stack are usable. The wide catalog remains an intentional inner horizontal-scroll region; document/body width stayed 390px. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/vehicles-default-390x844.png` |
| Vehicles / filtered | 1440×900 | `/vehicles?manufacturer=Toyota` | Seven exact Toyota configurations render with the same table rhythm and readable filter state. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/vehicles-filtered-toyota-1440x900.png` |
| Vehicles / zero | 390×844 | `/vehicles?q=no-such-configuration` | Empty result copy, reset action, and surrounding table container remain readable. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/vehicles-zero-390x844.png` |
| Vehicle detail / normal | 1440×900 | Porsche detail route | Identity, readiness, engineering summary, and evidence-aware sections have clear hierarchy and no visible clipping. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/detail-porsche-normal-1440x900.png` |
| Vehicle detail / normal | 1024×768 | Porsche detail route | Readiness table and dense engineering content remain legible at the tablet breakpoint. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/detail-porsche-normal-1024x768.png` |
| Vehicle detail / normal | 390×844 | Porsche detail route | Fixed `760px` readiness table caused use-case labels and blocker controls to clip inside the mobile table viewport. | NOTICE | Made the readiness table fluid on mobile and assigned explicit columns (`36% / 30% / 34%`) with safe wrapping. | Before: `artifacts/ui-baseline/pass2-before/detail-porsche-normal-390x844.png`; after: `artifacts/ui-baseline/pass2-after/detail-porsche-normal-390x844.png` |
| Vehicle detail / expanded evidence | 1440×900 | First Body dimensions evidence disclosure expanded | Evidence metadata, source observation, and provenance hierarchy are readable in the desktop table. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/detail-porsche-evidence-expanded-1440x900.png` |
| Vehicle detail / expanded evidence | 390×844 | First Body dimensions evidence disclosure expanded | The evidence body had a `360px` minimum width while its mobile table cell was about `235px`, extending beyond the cell. | NOTICE | Removed the mobile minimum/max-width constraint and set the evidence body to the available cell width; the engineering table's intentional horizontal scroll remains. | Before: `artifacts/ui-baseline/pass2-before/detail-porsche-evidence-expanded-390x844-fresh.png`; after: `artifacts/ui-baseline/pass2-after/detail-porsche-evidence-expanded-390x844.png` |
| Compare / empty | 1440×900 | `/compare` | Empty state explains the workflow and the four-slot form is balanced. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/compare-empty-1440x900.png` |
| Compare / partial selection | 1024×768 | `/compare` with two selected vehicles | Selected and unselected slots, labels, and actions retain a clear progression. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/compare-partial-1024x768.png` |
| Compare / four slots + advanced filter | 1440×900 | Four selected vehicles; `slot_3_q=toyota`; Vehicle 3 advanced filter expanded | Four cards remain balanced and the advanced candidate list is discoverable without disrupting the form. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/compare-four-top-1440x900.png` |
| Compare / matrix | 1440×900 | Same four-slot query; comparison matrix visible | Matrix headers, sticky first column, and horizontal-scroll hint work at desktop. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/compare-four-matrix-1440x900.png` |
| Compare / mobile form | 390×844 | Same four-slot query; advanced filter state | Slot cards stack cleanly and do not create page-level horizontal overflow. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/compare-four-top-390x844.png` |
| Compare / mobile matrix | 390×844 | Same four-slot query; matrix horizontally scrolled | Sticky parameter column and inner horizontal scroll preserve context in the dense matrix. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/compare-four-matrix-scrolled-390x844.png` |
| Design Check / empty | 1440×900 | `/design-check` | Screening boundary explanation, grouped form controls, and empty-state guidance read clearly. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/design-check-empty-1440x900.png` |
| Design Check / empty | 390×844 | `/design-check` | Form controls stack within the viewport and the submission boundary remains understandable. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/design-check-empty-390x844.png` |
| Design Check / populated results | 1440×900 | Populated query documented above | Summary counts and PASS / FAIL / INDETERMINATE result states are visually distinct and readable. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/design-check-results-1440x900.png` |
| Design Check / results matrix | 1440×900 | Same populated query; results matrix horizontally scrolled | Wide matrix uses an inner scroll region with sticky vehicle context; blockers remain reachable. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/design-check-results-matrix-scrolled-1440x900.png` |
| Design Check / populated results | 1024×768 | Same populated query | Result summary and the top of the matrix remain legible at the tablet breakpoint. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/design-check-results-top-1024x768.png` |
| Design Check / populated results | 390×844 | Same populated query | Counts stack, result summary remains readable, and no page-level overflow occurs. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/design-check-results-summary-390x844-final.png` |
| Design Check / mobile matrix | 390×844 | Same populated query; results matrix horizontally scrolled | Sticky vehicle column and horizontal-scroll behavior work in the dense results matrix. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/design-check-results-matrix-scrolled-390x844.png` |
| Issues / default | 1440×900 | `/issues` | Work-queue hierarchy, severity badges, and dense issue table are readable. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/issues-default-1440x900.png` |
| Issues / filtered | 1024×768 | `/issues?kind=READINESS` | Filter selection and readiness issue rows remain clear at the tablet breakpoint. | ACCEPTABLE | No change | `artifacts/ui-baseline/pass2-before/issues-readiness-1024x768.png` |
| Issues / zero | 390×844 | `/issues?kind=NO_SUCH_KIND` | Empty-state explanatory line was clipped by the table's fixed wide minimum, even though the page itself did not overflow. | NOTICE | Constrained the empty-state content to the mobile viewport while preserving wide-table scrolling for non-empty issue rows. | Before: `artifacts/ui-baseline/pass2-before/issues-zero-390x844.png`; after: `artifacts/ui-baseline/pass2-after/issues-zero-390x844.png` |
| Keyboard focus | 390×844 | Issues zero state; Tab from document start | Skip-link and brand navigation focus use a visible 3px gold outline with 2px offset. | ACCEPTABLE | No change | Focus verified live; no separate capture retained |

## Findings by severity

| Severity | Count | Finding |
| --- | ---: | --- |
| BLOCKER | 0 | No state prevented the intended workflow or hid a required control. |
| NOTICE | 3 | Mobile readiness table clipping; mobile expanded-evidence cell overflow; mobile issues zero-state copy clipping. All three were corrected with scoped CSS. |
| ACCEPTABLE | Remaining inspected states | Desktop/tablet hierarchy, intentional wide-table scrolling, compare workflow, Design Check result states, empty states, and focus treatment required no change. |

## Production change boundary

Only `app/web/static/styles.css` changed in production. The patch is limited to the `max-width: 680px` rules for readiness table sizing, evidence-body sizing, and issue-table empty-state width. No templates, routes, data, release manifests, calculations, domain rules, or semantics were changed. The QA record is the only other repository file added.

The wide catalog, compare matrix, engineering-value tables, Design Check results matrix, and non-empty issues table intentionally retain inner horizontal scrolling. At the tested 390px viewport, the document and body stayed at 390px wide; the scroll containers—not the page—held the wide content.

## Verification

- Release D runtime smoke: `/api/vehicles` reported `count=41` and 41 items; `/vehicles`, `/compare`, `/design-check`, and `/issues` returned HTTP 200.
- Focused test: `tests/integration/test_web_readability.py` — 11 passed.
- Full test suite: `python -m pytest` — 192 passed, 1 existing `StarletteDeprecationWarning`.
- Remaining imperfection: wide engineering and result tables still require horizontal scrolling on narrow screens by design; no blocker or unverified semantic change was introduced.
