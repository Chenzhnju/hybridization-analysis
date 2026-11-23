# Exact verification for hybrid correlation generation

Verification software for Appendix D of *Hybrid correlation generation with finite shared randomness* by Zihan Chen, Shengjun Wu, and Zeng-Bing Chen.

Software version **31.2** uses the two **Release 31** certificates cited in manuscript Ref. [24]. This GitHub distribution was prepared on 23 November 2026. The manuscript supplies the analytic reductions, averaging, integration, and classification arguments connecting the finite checks to the theorems.

Use Python 3.8 or later with assertions enabled. The verifier and its tests use the Python standard library. From the directory containing `verify.py`, run

```console
python verify.py --check-integrity
python verify.py
python -m unittest discover -v
python worked_examples.py
```

On Windows, `RUN_WINDOWS.cmd` runs the complete verification. A successful verification prints `PASS_EXACT_VERIFICATION` and exits with code 0. The integrity command checks the distributed file hashes. The test command runs 23 regression tests, and the worked examples finish with `PASS_WORKED_EXAMPLES`.

Every verification run creates a separate directory under `reports/`. `reports/latest.json` points to its summary, and the three stage reports share the summary's run identifier. Use `python verify.py --output-dir PATH` to choose another report directory. The supplied `reference_reports/` records a completed run for this distribution.

| Manuscript location | Implementation | Checks |
| --- | --- | --- |
| D.1 and D.2 | `verify_prerequisites.py`, `grid_witness.py` | Three-label CC construction, missing-quadrant witness and small-cost cutoff |
| D.3, Lemma D.1 | `verify_global.py`, `certificates/global.json` | Support classification, complete covers and localization |
| D.4–D.6, Lemma D.2 | `verify_local.py`, `local_rows.py`, `certificates/local.json` | Local row bounds, exceptional weights, scalar estimates and marginal identities |

The complete run checks 49 support orbits, 2,744 global leaves, 467 local leaves, and 16,996 local row bounds. It also rejects 18 deliberately invalid controls. Acceptance checks use integer arithmetic, exact fractions, and outward-rounded intervals.

The worked examples reproduce the support {0,3,12} in D.3 and the principal-row substitution for the (f,e) witness in D.4. The implementation is connected to the manuscript in [MANUSCRIPT_MAP.md](docs/MANUSCRIPT_MAP.md). The arithmetic and cover checks are described in [VERIFICATION_DETAILS.md](docs/VERIFICATION_DETAILS.md).

The current SciPost and PRA manuscript fingerprints, PDF page counts, and source-archive hashes are recorded in [DOCUMENT_VERSIONS.json](docs/DOCUMENT_VERSIONS.json). Earlier Word metadata and release-30 reports are explicitly marked as historical records.

All distributed text uses UTF-8 and LF line endings. `.gitattributes` preserves these bytes through Git checkout, including on Windows. `.gitignore` excludes generated reports and Python caches. The GitHub Actions workflow is configured to run integrity checks, complete verification, tests, and worked examples on Windows and Ubuntu with Python 3.8, 3.12, and 3.14.

Please cite this software and the accompanying manuscript when using the results. The software authors, title, and version are provided in [CITATION.cff](CITATION.cff). Publication steps, release-note text, and instructions for adding the final repository address and DOI are in [RELEASING.md](docs/RELEASING.md).

Released under the [MIT License](LICENSE). Copyright © 2026 Zihan Chen, Shengjun Wu, and Zeng-Bing Chen.
