# Open Music Taxonomy v0.1.0

A strict, compositional standard for classifying music by audible characteristics.

- [`spec.md`](spec.md) — normative model and governance rules
- [`taxonomy.json`](taxonomy.json) — curated Genre, Type, and Trait registry
- [`taxonomy.schema.json`](taxonomy.schema.json) — taxonomy package JSON Schema
- [`classification.schema.json`](classification.schema.json) — classification JSON Schema
- [`conformance.json`](conformance.json) — 50 valid and invalid conformance cases
- [`reference-albums.json`](reference-albums.json) — pilot classifications grounded in six real releases
- [`validate.py`](validate.py) — dependency-free semantic validator and canonical renderer checks
- [`CHANGELOG.md`](CHANGELOG.md) — release history
- [`LICENSE.md`](LICENSE.md) — licensing map (CC0 / CC BY 4.0 / Apache-2.0)

## Validate

```bash
python validate.py
```

Expected result:

```text
PASS: 50 cases (38 valid, 12 invalid), 3 equivalence assertions, 6 reference albums
```

## Scope of v0.1.0

v0.1.0 publishes the grammar, schemas, validator, initial Metal/Rock/Core registry, and
pilot reference albums. Deathrock remains deferred until a reviewed sonic definition and
evidence package are accepted.

Local audio used during reference review belongs under `.local/nas-albums/`. The directory is
ignored by Git; audio is never part of the standard or its repository.

## Releasing

1. Set `taxonomy.json` (and fixture pins) to the release version, and add a matching
   `CHANGELOG.md` section such as `## [0.1.0] — YYYY-MM-DD`.
2. Commit on `master` / `main`.
3. Create and push an annotated tag:

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

Pushing `v*.*.*` runs `.github/workflows/release.yml`: it validates the corpus, checks that
`taxonomy.json` version equals the tag (without the leading `v`), and publishes a GitHub
Release with changelog notes and downloadable artifacts. Tags containing `-` (for example
`v0.2.0-rc.1`) are marked as prereleases.
