# Releasing

GeoDebug releases are tag-driven.

1. Ensure CI is green on `main`.
2. Confirm `CHANGELOG.md` contains the release entry.
3. Confirm `src/geodebug/version.py` contains the release version.
4. Create and push a matching `vX.Y.Z` tag.
5. The release workflow verifies the tag/version match, builds sdist and wheel,
   runs `twine check`, and creates the GitHub Release with both artifacts.

PyPI publication is intentionally not automated in 0.1.0. Configure trusted
publishing and add a separate publish job before enabling registry publication.
