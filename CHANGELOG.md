# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
as described in `spec.md` §13.

## [0.2.0] — 2026-07-27

### Added

- Five new Genres: Hardcore, Punk, Grunge, Nu Metal (`numetal`), and Emoviolence.
- `post` as a Genre-owned Type (`metal.post`, `rock.post`, `hardcore.post`) with a canonical
  hyphen join, expressing Post-Metal, Post-Rock, and Post-Hardcore.
- `electronic` Trait (for example Electronic Metalcore, Electronic Post-Hardcore).
- Optional `join_next` property on Types in `taxonomy.schema.json`, so a Type may define a
  canonical join rule like a Trait already could.
- Ten new conformance cases (C051–C060) covering the new atoms and the deprecated `post` Trait.

### Changed

- The `post` Trait is deprecated (`status: deprecated`; the ID remains resolvable per §13) in
  favor of the `post` Types. `validate.py` now honors a Type's `join_next` when rendering, with
  the prior positional rule as the default.

### Migration

- Re-classify any v0.1 classification using `traits: [post]` to `types: [<genre>.post]` — for
  example Post-Rock moves from `genre: rock, traits: [post]` to `genre: rock, types: [rock.post]`.
  All other v0.1 classifications remain valid without change.

### Notes

- Driven by a read-only audit of a local NAS library (7,290 metadata `.nfo` files), which
  established the usage evidence for the added atoms and surfaced the v0.1 coverage gaps this
  release closes.

## [0.1.0] — 2026-07-24

### Added

- Normative classification specification for Genre, Type, Trait, Unknown, ownership,
  equality, rendering, validation, versioning, profiles, localization, and governance.
- Initial curated taxonomy package with Metal, Rock, Metalcore, and Deathcore Genres,
  Genre-owned Types, and reusable Traits.
- JSON Schemas for taxonomy packages and classifications.
- Executable conformance corpus with 50 valid and invalid cases plus composition
  equivalence assertions.
- Pilot reference-album classifications grounded in six real releases.
- Dependency-free Python validator for taxonomy, conformance, and reference fixtures.

### Notes

- `crossover` is an approved Metal Trait requiring the Thrash Type (Crossover Thrash Metal).
- Deathrock remains deferred pending a reviewed sonic definition and evidence package.
- One reference album (`gojira-from-mars-to-sirius`) is published with
  `review_status: needs_review` to document an open priority dispute.
