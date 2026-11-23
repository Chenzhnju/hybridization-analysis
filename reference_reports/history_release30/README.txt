These are fresh release verification reports, not reused reports from revision 29.
summary.json and the three stage reports share one run identifier and record the
actual release source/certificate hashes. Timestamps are explicitly UTC.

Running python verify.py creates separate reports/run-... directories; it does
not overwrite these reference results. release_validation.json records the exact
comparison with revision 29 and the additional release regression checks.

The reports certify finite checks supporting Appendix D.1-D.5, conditional on
the analytic premises stated in the manuscript and docs/VERIFICATION_DETAILS.md.
