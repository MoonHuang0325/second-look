# Release status and checklist

Version: 0.1.0 prototype. Source and reproducible installation archives are prepared locally. This repository does not imply a GitHub remote, published release, approved marketplace listing, or completed user study.

Before publishing a tag:

- Run automated tests, validation, and reproducible builds. Inspect the package contents and source diff for private data.
- Keep the compatibility matrix tied to actual host/version tests. Record untested platforms as such.
- Publish the standard skill ZIP, OpenAI plugin ZIP and SHA256SUMS alongside source. Both packages derive from the same core.
- Run development paired model trials, fix demonstrated problems, freeze the version, then run the holdout set without tuning against it.
- Label releases “prototype” until live host behavior and user efficacy have been assessed. Never turn the 70%/50% pilot goals into marketing claims.
- GitHub creation/push requires the owner's authenticated GitHub destination. Directory submission is separate from GitHub publication. Use an owner-approved account and repository; don't invent a URL.

Deferred: platform history connectors where native access is absent; default scheduling; model-release detection; vector database; external API/backend; team data sharing. Each should follow demonstrated need and preserve the small core.
