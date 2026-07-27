# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
as described in `spec.md` §13.

## [0.5.0] — 2026-07-27

### Added

- **R&B** Genre (`rnb`, label "R&B") with Type `rnb.alternative` (Alternative R&B), covering the
  PBR&B / dark / atmospheric strain exemplified by The Weeknd and badXchannels.
- Two conformance cases (C072–C073).

### Notes

- Additive only; no existing classification is affected. Driven by auditing the NAS `R&B/` folder,
  whose two artists (The Weeknd, badXchannels) were previously mislabeled "Electronic". The
  electronic production characteristic of Alternative R&B is intrinsic to that Type's sonic
  definition, so it is not separately tagged via the `electronic` Trait — keeping each artist's
  genre folder-derivable (Type subfolder), consistent with the Jazz / Traditional Pop / Electronic
  families.

## [0.4.0] — 2026-07-27

### Added

- **Electronic** Genre with Types `electronic.house` (House Electronic),
  `electronic.techno` (Techno Electronic), `electronic.idm` (IDM Electronic),
  `electronic.darkwave` (Darkwave Electronic), `electronic.synthpop` (Synthpop Electronic), and
  `electronic.rock` (Rock Electronic, for electronic-rock hybrids).
- Six conformance cases (C066–C071).

### Notes

- The v0.2 `electronic` **Trait** is unchanged and coexists with the new `electronic` **Genre**
  (separate namespaces; distinct renders — Trait "Electronic Metalcore" vs Genre "House
  Electronic"). Driven by organizing the NAS `Electronic/` folder by Type subfolder, matching the
  Jazz/Traditional Pop pattern.

## [0.3.0] — 2026-07-27

### Added

- **Jazz** Genre with Types `jazz.vocal` (Vocal Jazz), `jazz.swing` (Swing Jazz),
  `jazz.bigband` (Big Band Jazz), and `jazz.soul` (Soul Jazz).
- **Traditional Pop** Genre (bare).
- Five conformance cases (C061–C065).

### Notes

- Additive only; no existing classification is affected. Driven by auditing the NAS `Jazz/`
  folder, which conflated real Jazz with Traditional Pop (Sinatra, Crosby, …). The two are now
  separate Genre families, organized by Type subfolder so the classification is folder-derivable.

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
