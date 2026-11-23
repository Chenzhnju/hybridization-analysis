# Publishing the verification package

The repository root is the directory containing `verify.py`, `README.md`, and `certificates/`. The GitHub repository is [hybridization-analysis](https://github.com/Chenzhnju/hybridization-analysis).

1. Create a local Git repository from this directory, stage the files including `.github/`, `.gitignore`, and `.gitattributes`, and review the initial commit. GitHub Desktop can publish the repository under the chosen account and visibility.
2. Once the repository exists, add its actual URL as `repository-code` in `CITATION.cff`. Fill `date-released` with the actual release date when publishing. Use the identifier issued by the archive service when adding `doi`.
3. After staging the intended release files, run `python tools/update_manifest.py` to refresh `SHA256SUMS`. Review and stage the resulting manifest.
4. Run the four commands shown below and check that the GitHub Actions jobs pass. The supplied reference reports record local checks. Workflow runs on GitHub provide the platform-matrix results.
5. Create the first public release with tag `v31.2` at the verified commit. Attach the corresponding ZIP and copy the release-note text below. Download the attached ZIP, extract it, and run the same four commands.
6. For a citable archive, connect the public repository to Zenodo before creating the GitHub release. Use the issued version DOI in the manuscript's software reference. The software version is 31.2 and the certificate release is 31.

```console
python verify.py --check-integrity
python verify.py
python -m unittest discover -v
python worked_examples.py
```

The maintainer command `tools/update_manifest.py` uses Git's tracked-file list and each file's current bytes. Stage new files and removals before running it. Include the refreshed manifest in the same commit as the changes. Generated reports and caches are ignored by Git. If verification source or certificates change, run the complete checks, copy the matching summary and three stage reports into `reference_reports/`, update `release_validation.json`, and then regenerate the manifest. Use a new tag for each subsequent release.

Suggested release text follows.

> Exact verification software for Appendix D of *Hybrid correlation generation with finite shared randomness* by Zihan Chen, Shengjun Wu, and Zeng-Bing Chen.
>
> Version 31.2 uses the Release 31 certificates. The verification checks 49 support orbits, 2,744 global leaves, 467 local leaves, and 16,996 local row bounds, and rejects 18 invalid controls. The package includes 23 regression tests and two worked examples.
>
> This distribution includes an MIT license, software citation metadata, fixed LF line endings, Git ignore rules, refreshed checksums and reference reports, and a GitHub Actions workflow for Windows and Ubuntu. Python 3.8 or later is required. The verifier uses the Python standard library.

Repository URLs and DOIs can be added after they have been assigned. The existing manuscript reference can retain its connection to the Release 31 certificates while specifying software version 31.2 and the archived version DOI.

Official instructions cover repository publishing, release creation, software citations, and DOI archiving. [GitHub Desktop](https://docs.github.com/en/desktop/adding-and-cloning-repositories/adding-an-existing-project-to-github-using-github-desktop), [GitHub releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository), [CITATION.cff](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files), [Zenodo integration](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content).
