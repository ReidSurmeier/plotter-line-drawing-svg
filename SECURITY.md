# Security policy

## Supported versions

Security fixes are applied to the current `main` branch and, when releases are
published, the latest released version. Older snapshots may not receive fixes.

## Report a vulnerability

Do not open a public issue for a suspected vulnerability or accidentally
committed secret. Use GitHub's
[private vulnerability report](https://github.com/ReidSurmeier/plotter-line-drawing-svg/security/advisories/new)
for this repository.

Include the affected version or commit, reproduction steps, expected impact,
and any suggested mitigation. Remove source images, credentials, private URLs,
and other unrelated personal data from the report.

The maintainer will acknowledge a complete report as soon as practical, assess
its scope, and coordinate disclosure after a fix or mitigation is available.
If private vulnerability reporting is unavailable, open a public issue that
asks for a private contact method without disclosing vulnerability details.

## Dependency and media considerations

This project parses NumPy archives, JSON, SVG, and raster images and invokes
`rsvg-convert` and FFmpeg. Treat files from untrusted sources as untrusted input,
keep system packages current, and run the tools with ordinary user privileges.
Never commit API tokens, private Tailscale URLs, or licensed source images that
you do not have permission to redistribute.
