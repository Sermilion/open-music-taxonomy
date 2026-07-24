# Open Music Taxonomy v0.1 draft

This repository contains the first formal draft of the sonic classification standard.

- [`spec.md`](spec.md) — normative model and governance rules
- [`taxonomy.json`](taxonomy.json) — curated draft Genre, Type, and Trait registry
- [`taxonomy.schema.json`](taxonomy.schema.json) — taxonomy package JSON Schema
- [`classification.schema.json`](classification.schema.json) — classification JSON Schema
- [`conformance.json`](conformance.json) — 50 valid and invalid conformance cases
- [`reference-albums.json`](reference-albums.json) — pilot classifications grounded in six real releases
- [`validate.py`](validate.py) — dependency-free semantic validator and canonical renderer checks

Run the executable corpus:

```bash
python validate.py
```

Expected result:

```text
PASS: 50 cases (37 valid, 13 invalid), 3 equivalence assertions, 6 reference albums
```

Local audio used during reference review belongs under `.local/nas-albums/`. The directory is
ignored by Git; audio is never part of the standard or its repository.

This is a draft, not yet a published standard. In particular, `crossover` remains provisional until
its sonic definition and representative evidence are reviewed.
