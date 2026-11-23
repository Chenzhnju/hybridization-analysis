# GitHub distribution of version 31.2

23 November 2026. Add the MIT license, CFF software citation, Git attributes and ignore rules, Windows/Ubuntu continuous verification, and publication instructions. Normalize distribution text to LF, identify current and historical manuscript records separately, and refresh the checksums and reference reports. The release-preparation check compares executable source after line-ending normalization and both certificate byte sequences with version 31.2.

# Version 31.2

- Check the CC construction in Eq. (D.3) and the marginal identities in D.6.
- Match all five retained D.3 supports to the D.4 grids. Check the tilt fractions, the averaged inequality in Eq. (D.8), and the rationalization in D.5 against the implemented expressions.
- Share the integer witness calculation between D.1 and both D.3 covers. Report the node, witness and row for failed antialigned inequalities.

# Version 31.1

- The ordinary D.3 covers and the five D.4 covers use the same check for
  complete four-way subdivisions. The antialigned D.3 support uses its
  original fourteen-coordinate binary subdivision.
- For each D.4 parameter box, the verifier evaluates each distinct local
  response norm once and checks every response pair. The interval endpoints
  for all 16,996 row bounds agree with Release 31.
- Certificate parsing checks for duplicate fields and inexact JSON
  numbers. Vector operations check dimensions. A failed ordinary witness
  inequality reports the support, witness, cell, row and exact failing bound.
- Reports use a short temporary filename in the destination directory,
  allowing atomic replacement close to the Windows path length limit.

# Release 31 manuscript companion update

22 November 2026. This edition identifies the source Word file and the SciPost Physics and Physical Review A LaTeX editions. Both formats cite these certificates in Ref. [24].

The document fingerprint and reference reports identify the 21 November 2026 revision to the main text and appendices. Both certificates and the mathematical verification routines match the preceding companion edition.

21 November 2026. The 32-page SciPost Physics draft cites this verifier in Ref. [24].
The manuscript map now identifies the worked support in Appendix D.3 and the
principal row in Table 2 of Appendix D.4. Table 3 gives the auxiliary witnesses.
The report metadata and document fingerprint identify the revised manuscript.
Both certificate files and all mathematical verification routines match the
18 November issue of release 31 byte for byte. The tests in worked_examples.py reproduce both worked examples directly from the released data and code. The notes below record earlier editions.

# Release 31

2026-11-18. Accompanies the 40-page compressed review manuscript.

- Synchronize the restored D.6 classification and Tables 3-4 with the manuscript map.
- Update companion-document names and hashes, current archive reference [28], and
  publication metadata; keep manuscript files outside verifier acceptance inputs.
- Preserve all certificate files and mathematical verification modules byte-for-byte.
- Record a fresh complete verification run and integrity check. Preserve release-30
  reports under reference_reports/history_release30 as historical evidence.
- Abstract and Introduction remain unchanged. The old Supplemental Material pointer
  in the Introduction remains an explicitly unresolved editorial item.

The following release-30 notes describe that historical manuscript, not release 31.

# Release 30

2026-11-17. This release accompanies the four-item shortened manuscript.

- Replace outdated supplement references with current Appendix D.1-D.5 mappings.
- Rename global/local verification modules and place certificates in their own directory.
- Keep one public entry point and place each new run in an independent report directory.
- Give every stage the same run identifier; record failed and skipped stages explicitly.
- Preserve the supplied reference reports when the user reruns verification.
- Add an optional release-integrity check, a Windows launcher, and regression tests
  for failure handling, optimized Python, damaged inputs, and paths containing spaces
  or non-ASCII characters.
- Identify the exact companion Word/PDF versions without making them verifier inputs.

The two certificate files and both exact arithmetic modules are byte-identical
to revision 29. The mathematical helper functions in the preliminary, global,
local, and witness modules are unchanged apart from comments/docstrings.
Acceptance thresholds, cover requirements, witness formulas, and all eighteen
mathematical negative controls are retained. Changes to the stage orchestration
concern paths, current labels, report metadata, and error handling.

The former separate optimal-protocol classification is absent from the manuscript.
Zero-gap identities and strict local inequalities are retained because the current
averaged local bound still uses them. No certificate or condition is removed merely
because an optional application was deleted.

Fresh full runs of revision 29 and this release are compared on all exact
mathematical report values, excluding only version/path/time and explanatory
metadata. See reference_reports/history_release30/release_validation.json for the recorded outcome.
This release makes no runtime speedup claim; the optimization is consistency,
reproducibility, and ease of use.

Provenance: revision 29 already removed repeated matrix-vector and polynomial
operand computations. Its historical reports and old manuscript labels are not
redistributed as the current result; they remain in the preceding archive.
