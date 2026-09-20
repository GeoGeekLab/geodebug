# Releasing

GeoDebug releases are tag-driven and publish to both GitHub Releases and PyPI.

## One-time PyPI setup

GeoDebug uses PyPI Trusted Publishing through GitHub Actions. No long-lived PyPI API token is stored in GitHub.

In the PyPI publisher configuration for the `geodebug` project, configure:

- Owner: `GeoGeekLab`
- Repository: `geodebug`
- Workflow: `release.yml`
- Environment: `pypi`

For the first publication, use a pending trusted publisher if the PyPI project does not exist yet.

## Release process

1. Ensure CI is green on `main`.
2. Confirm `CHANGELOG.md` contains the release entry.
3. Confirm `src/geodebug/version.py` contains the release version.
4. Create and push a matching `vX.Y.Z` tag.
5. The release workflow verifies the tag/version match.
6. The workflow builds the sdist and wheel and runs `twine check`.
7. The workflow creates the GitHub Release with both distribution artifacts.
8. A separate job publishes the exact same distributions to PyPI using OIDC trusted publishing.

The publish job is intentionally isolated behind the GitHub `pypi` environment and receives only the `id-token: write` permission required for trusted publishing.
