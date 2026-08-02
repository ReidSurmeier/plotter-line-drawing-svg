# Ignored reference-run custody

## Boundary

The ignored `runs/tumblr-790aa7518ed1` directory is a 290-file local reference
run. It contains 244,531,468 file bytes and is not tracked source. This record
identifies it without committing the run or exposing a machine-specific path.

The whole-tree SHA-256 is
`5d8e06d5681289ee5ca362d34717598905edc1131d83a4705eaacdf3d308d21e`.
It is the SHA-256 of the concatenated `sha256sum` records for every file,
sorted by its `./`-relative path from the run root.

## Inventory

| Relative component | Files | Bytes | Classification |
| --- | ---: | ---: | --- |
| `source_working.png` | 1 | 161,001 | Working source image; publication rights remain unresolved |
| `jax-alpha/` | 44 | 5,148,586 | Alpha Stack input custody and upstream solver evidence |
| `coverage-svg/` | 33 | 22,577,769 | Reproducible Derived SVG and proof output |
| `animation/` | 212 | 216,644,112 | Derived frames, validation output, manifest, and MP4 |

Key Source Fixity and Derived-output checks:

| Artifact | SHA-256 |
| --- | --- |
| `source_working.png` | `3f6cd69eec452e876b6f4cf2c324c733cdbe7269a7a41917c8d463fa614680e9` |
| `jax-alpha/alpha_stack_float32.npz` | `01b7a11dc75b4ffc4dc3c3ca3acb89519d3a632ff1015e4d0e11ce0672c3f632` |
| `jax-alpha/metadata.json` | `0b47f4236a969257c09bf8268dab7d902ae91a32a4ef55b2f16fb2f150decf84` |
| `coverage-svg/master_coverage_svg.svg` | `94e9c8338224b4c299007bb2bc0bdc468eb3ee6040744044478fb9ff799e6af3` |
| `coverage-svg/coverage_svg_metadata.json` | `f69cb5da15f704d6e0d6d63223e1ace7b6489b5c4a4762e2486073198fbf72a2` |
| `animation/tumblr_line_drawing_mark_build.mp4` | `5666eee5f8dcf5113ca52f577534ba6daf3971c8fbe71ef9b0bd329da5aeb603` |
| `animation/animation_manifest.json` | `ff0e32742655ef5c4c7523adada3aed2c0f68855c0c83f3cee06724c1e847f6c` |

The working image depicts a typographic reference test and is not one of the
three portrait, bathroom, or fashion subjects covered by the 2026-08-02 owner
authorization. Keep the run ignored and local; do not treat the MP4 or source
image as publication evidence.

## Reviewed move and rollback map

The run will move with the repository so its relative path remains unchanged.
No external consumer of the run path was found in the reviewed move preflight.
The repository's Git commit, clean tracked state, file count, byte count,
whole-tree digest, and key artifact hashes must match after relocation.

Rollback is the exact inverse repository move, and is allowed only while the
former repository location remains absent. The ignored run must never be
copied into Git, regenerated, or deleted as part of relocation.
