# Development and validation

Python 3.9+; standard library only for the shipped helpers. Use the full source checkout:

```sh
python3 -m unittest discover -s tests -v
python3 tools/validate.py
python3 tools/build.py
```

The same canonical `skills/second-look` becomes the standard skill ZIP and the OpenAI plugin package. Assets are allowlisted. Public demos are synthetic; never add personal corpus or ledger data to source or releases.

The original 24 synthetic behavioral cases remain separated into 16 development and 8 holdout cases. [Evaluation protocol](../evals/README.md). The new demonstration pack is a development/showcase exercise, not an independent benchmark. [Observed trials](../evals/observations/README.md).

The two first-use additions that need meaningful regression coverage are demo extraction (no personal reads or overwrite) and explicit upgrades (backup, rollback and private ledger preservation). Structural checks and green CI do not prove live host routing, native account history access or usefulness.
