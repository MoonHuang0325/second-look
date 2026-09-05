# Working on Second Look

Canonical runtime: `skills/second-look/`. Keep host-specific behavior in references/adapters, not vendor requirements in the core.

Run `python3 -m unittest discover -s tests -v`, `python3 tools/validate.py`, and `python3 tools/build.py` from the repository root. Runtime code must remain Python 3.9+ standard-library-only.

Use synthetic development cases for iteration. Don't load holdout expectations into the model under evaluation. Once holdout cases guide a change, disclose that contamination for the experiment.

Private histories, ledgers and evaluation outputs belong outside this public repository. Package only the explicit build allowlist. Generated archives are under ignored `dist/`.

Never describe unit tests, fixture demos, prepared evaluation packets, or a successful installer as proof of real-user efficacy or live cross-platform compatibility. Update the compatibility matrix with precisely observed results.

Keep public content useful to users and open-source contributors. Owner-only launch plans, outreach drafts, growth research and operating metrics belong outside this repository and all public release assets.
