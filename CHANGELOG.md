# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
as described in `spec.md` §13.

## [0.8.0] — 2026-08-01

### Added

- **Depressive** Trait (`depressive`) — scoped to `metal` and gated on `required_types:
  ["metal.black"]`, following the `stoner`/`funeral` precedent, so it can only ever qualify Black
  Metal and never renders bare as "Depressive Metal".
- **Breakcore** Type (`electronic.breakcore`) — homes the extreme breakbeat-editing end of
  `Electronic/` (e.g. Igorrr), which no existing Electronic Type described.
- Five conformance cases (C080–C084).
- **Thall** Genre (`thall`) — peer standalone genre to `metalcore` and `deathcore`, homing
  syncopated palm-muted groove–centered artists previously filed under Core subfolders.
- Three conformance cases (C085–C087).

### Notes

- Additive only; no existing classification is affected.
- Thall is driven by the NAS `Core/` library, where several artists fit the thall groove
  vocabulary more precisely than Metalcore or Deathcore alone.
- Depressive / Breakcore driven by auditing the NAS `Metal/Black Metal/` folder, where two artists
  were unclassifiable under v0.7.
- C083–C084 pin a render that **already worked but was never asserted**: "Post-Black Metal" is
  expressible today as two Types, `metal.post` (which carries `join_next: hyphen`) followed by
  `metal.black`. No `post` Trait is needed — the Trait of that name remains deprecated, since a
  bare `post` Trait would collide with the `metal.post` Type on the render "Post-Metal".

## [0.7.0] — 2026-07-28

### Added

- **Screamo** Genre (`screamo`) and **Emocore** Genre (`emocore`) — peer standalone genres to
  `emoviolence`, `hardcore`, and `punk`, homing the Russian-scene screamo and emocore artists
  (`Russian/Screamo/`, formerly `Russian/New Wave Emocore/` → `Russian/Emocore/`).
- Two conformance cases (C078–C079).

### Notes

- Additive only; no existing classification is affected. Both genres are defined by sonic
  characteristics (vocal delivery, dynamics, instrumentation) per §3. "New Wave" (a temporal/scene
  descriptor) is dropped from the folder name in favor of the sonic genre "Emocore".

## [0.6.0] — 2026-07-27

### Added

- **Hip-Hop** Genre (`hiphop`, label "Hip-Hop") with Types `hiphop.boombap` (Boom Bap Hip-Hop),
  `hiphop.gfunk` (G-Funk Hip-Hop), and `hiphop.trap` (Trap Hip-Hop).
- Four conformance cases (C074–C077).

### Notes

- Additive only; no existing classification is affected. Driven by auditing the NAS `Rap/` and
  `Russian/Rap/` folders (~844 files previously unresolvable). The Types are sonic production styles
  only — lyrical/thematic labels (Gangsta, Horrorcore, Mafioso, Conscious) are excluded by §3, so
  the West-Coast artists popularly called "Gangsta Rap" are classified by their sound (G-Funk).
- The `Rap/` folder remains the organizational bucket; the Type is derived from the type subfolder
  underneath, consistent with the Jazz / Electronic / R&B families.

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
