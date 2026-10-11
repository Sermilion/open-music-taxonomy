# Open Music Taxonomy Classification Specification

Version: `0.9.0`

Status: Released

## 1. Purpose

This specification defines a strict, compositional system for classifying music by audible
characteristics. It replaces uncontrolled genre strings with references to a versioned,
maintainer-curated taxonomy.

The system is intentionally opinionated:

- every published classification has one Genre;
- optional ordered Traits and Types add sonic precision;
- every value is an approved taxonomy identity, never an inline string;
- familiar display names are generated from structure and are not metadata identities.

The serialization format is not the standard. JSON is the normative interchange encoding in
v0.1, but the same model may be represented in YAML, a relational database, or another encoding.

## 2. Normative language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY** are to
be interpreted as described by RFC 2119.

## 3. Sonic-only boundary

Genres, Types, and Traits MUST describe audible musical characteristics.

The following are not classification atoms:

- geography or artist origin, such as `Swedish`;
- cultural or linguistic umbrellas, such as `Latin`;
- performer identity, such as `female-fronted`;
- religion, lyrical subject, imagery, marketing, or scene membership.

Applications MAY store those dimensions separately, but they MUST NOT insert them into this
classification grammar.

A geographically or thematically named atom MAY exist only when its normative definition is
sonic. For example, `viking` and `pirate` are Metal-specific sonic Traits in this taxonomy. Artist
location, lyrics, or imagery alone MUST NOT satisfy either Trait.

## 4. Classification grammar

The canonical grammar is:

```text
ordered Traits[0..n] -> ordered Types[0..n] -> Genre[1]
```

Genre is the only required musical atom. `Metal` and `Rock` are therefore complete
classifications. Types and Traits are optional.

Examples:

```text
Metal
Death Metal
Technical Death Metal
Technical Melodic Death-Doom Metal
```

`Death Melodic Technical Metal` is invalid because a Type appears before Traits.

### 4.1 Genre

A Genre is the required head of a classification.

- A classified item MUST reference exactly one approved Genre.
- Multiple Genres are forbidden in v0.1.
- A Genre identity is stable and independent of its display name.

### 4.2 Type

A Type is a substantial sonic form owned by exactly one Genre.

- A classification MAY contain zero or more Types.
- Every selected Type MUST be owned by the selected Genre.
- A Type MUST occur at most once in a classification.
- Multiple Types represent a same-Genre composite, such as `Death-Doom Metal`.
- Type order expresses focus.
- Every selected Type MUST independently satisfy its sonic definition. Mere influence or
  coloration does not qualify as a second Type.

Taxonomy ownership is a strict tree: a Type has exactly one Genre owner. Combinations belong to
classifications, not to multi-parent taxonomy nodes.

### 4.3 Trait

A Trait is an optional sonic qualifier.

- A classification MAY contain zero or more Traits.
- A Trait MUST occur at most once in a classification.
- Trait identity is global, with optional applicability constraints by Genre and required Type.
- Trait order expresses focus.
- v0.1 defines no pairwise Trait incompatibilities.

Unusual Trait combinations are valid unless an individual Trait's applicability constraints reject
the containing classification.

Examples:

- `melodic` and `technical` are broadly reusable Traits;
- `blackened`, `viking`, `pirate`, and `neoclassical` are constrained to Metal;
- `funeral` is constrained to Metal classifications containing the Doom Type;
- `crossover` is constrained to Metal classifications containing the Thrash Type;
- `post` was a global Trait in v0.1; in v0.2 it is deprecated as a Trait and provided as a
  Genre-owned Type (`metal.post`, `rock.post`, `hardcore.post`) that retains the canonical
  hyphen join. See the v0.2.0 migration note in §13.

### 4.4 Priority

Trait and Type priorities are classification-specific.

- Priorities MUST be positive integers.
- Priorities MUST be unique within their own block.
- Priorities MUST be contiguous from `1` through `n`.
- Trait and Type blocks have independent priority sequences.
- Equal-priority ties are forbidden.

Priority is semantic emphasis, not merely serialization order.

## 5. Unknown state

`unknown` is a reserved unresolved state, not a Genre taxonomy node.

- An unresolved classification MUST encode `genre: "unknown"`.
- It MUST contain no Traits and no Types.
- Applications MAY publish unresolved items under an `Unknown` organizational bucket.
- Applications MAY adopt a stricter profile that forbids publication until classification.
- Reclassification replaces `unknown` with an approved Genre.

`Technical Unknown` is invalid.

## 6. Scope and inheritance

Classification ownership is:

- **Album:** MUST own exactly one canonical classification.
- **Release:** MUST inherit its Album classification and MUST NOT own an independent
  classification.
- **Track:** MUST inherit its Album classification unless it declares one complete override.
- **Artist:** MUST NOT own a canonical classification. Artist facets are derived from Albums and
  Tracks.

A Track override replaces the inherited classification as a whole. Partial overrides are forbidden.

## 7. Single canonical classification

An Album or overriding Track MUST have exactly one canonical classification. Primary-plus-alternative
and multiple-equal classification models are forbidden.

Nuance is represented through ordered Traits and Types, not alternative genre strings.

## 8. Equality and filtering

The standard defines two comparisons.

### 8.1 Exact equality

Two classifications are exactly equal when all of the following match:

- Genre identity;
- ordered Trait identities;
- ordered Type identities.

### 8.2 Compositional equivalence

Two classifications are compositionally equivalent when they share:

- Genre identity;
- the same set of Trait identities, ignoring priority;
- the same set of Type identities, ignoring priority.

`Technical Melodic Death Metal` and `Melodic Technical Death Metal` are compositionally equivalent
but not exactly equal.

Facet filtering uses identity membership by default. Filtering by `melodic` therefore matches every
classification containing that Trait, regardless of Type, Genre, or Trait priority. Applications MAY
offer exact-order and priority-specific filters.

## 9. Hybrids and influences

v0.1 defines neither a Hybrid field nor an Influence field.

- Multiple Types express same-Genre combinations.
- An approved sonic Trait may express an audible characteristic historically derived from another
  style.
- Exactly one Genre remains canonical.

For example:

```text
traits: [blackened]
types: [death]
genre: metal
```

This is Blackened Death Metal. It is Death Metal with the Blackened Trait; it is not Black Metal and
does not match the Black Type.

## 10. Identities, labels, and rendering

Taxonomy IDs are metadata identities. Display labels are presentation.

- IDs MUST be stable within the taxonomy's lifetime.
- Renaming a display label MUST NOT change its ID.
- Classification MUST NOT be inferred by splitting or parsing a display name.
- Canonical rendering sorts Traits and Types by priority, then emits
  `Traits -> Types -> Genre`.
- The default token separator is one space.
- Adjacent Types MUST be joined with a hyphen, making composites explicit:
  `Death-Doom Metal`, not `Death Doom Metal`.
- A taxonomy atom — Trait or Type — MAY define a canonical join rule, such as the hyphen in
  `Post-Rock` (the `rock.post` Type) or `Post-Metal` (the `metal.post` Type).

Canonical spellings are normative. `Death Rock` and `Deathrock` are not automatically equivalent.
Deathrock is deferred from v0.1 and no approved Rock atom is created merely because the word exists.

## 11. Taxonomy applicability

The taxonomy package declares:

- Genres;
- Genre-owned Types;
- globally identified Traits;
- Trait applicability constraints;
- canonical English labels and join rules;
- lifecycle status and replacement IDs.

A Trait with no applicability constraints MAY be used with every approved Genre. Constraints are
deny-by-validation: using a Trait outside its declared Genres or without its required Types is
invalid.

## 12. Validation

A conforming validator MUST reject:

- unknown or unapproved IDs;
- more or less than one Genre;
- Types owned by another Genre;
- Traits outside their applicability constraints;
- duplicate Trait or Type IDs;
- duplicate, missing, zero, negative, or non-contiguous priorities;
- modifiers attached to `unknown`;
- partial Track overrides;
- non-sonic values inserted as classification atoms.

Imported text MAY produce suggestions or resolve through curated aliases. It MUST NOT create
taxonomy atoms. Invalid or ambiguous imports SHOULD remain in a review queue unless the application
explicitly publishes the reserved Unknown state.

## 13. Versioning and migration

Taxonomy packages use semantic versioning. Metadata MUST pin an exact taxonomy version.

- **Patch:** documentation or localization corrections without semantic or validation changes.
- **Minor:** additive approved atoms, aliases, translations, or deprecations.
- **Major:** reparenting, changed meaning, grammar changes, or rules that invalidate previously valid
  classifications.

IDs MUST NOT be silently renamed or deleted. Deprecated IDs remain resolvable and SHOULD identify an
explicit replacement. Applications MUST preview and explicitly execute taxonomy migrations; they
MUST NOT silently reinterpret libraries against the latest release.

Schema version and taxonomy version are independent.

### v0.2.0 migration

The `post` Trait is deprecated and replaced by Genre-owned `post` Types (`metal.post`,
`rock.post`, `hardcore.post`). Classifications using `traits: [post]` MUST be migrated to
`types: [<genre>.post]`; for example, v0.1 Post-Rock (`genre: rock, traits: [post]`) becomes
`genre: rock, types: [rock.post]`. The deprecated `post` Trait ID remains resolvable; it is no
longer approved for new classifications. v0.2.0 is otherwise additive (new Genres Hardcore,
Punk, Grunge, Nu Metal, and Emoviolence; the `electronic` Trait), so non-`post` v0.1
classifications remain valid without change.

### v0.3.0

Additive only: the **Jazz** Genre (Types `jazz.vocal`, `jazz.swing`, `jazz.bigband`,
`jazz.soul`) and the **Traditional Pop** Genre are added. No existing classification is affected.

### v0.4.0

Additive only: the **Electronic** Genre (Types `electronic.house`, `electronic.techno`,
`electronic.idm`, `electronic.darkwave`, `electronic.synthpop`, `electronic.rock`) is added.
The pre-existing `electronic` **Trait** is unchanged and coexists with the new Genre (distinct
namespaces, distinct renders — e.g. Trait "Electronic Metalcore" vs Genre "House Electronic").

### v0.5.0

Additive only: the **R&B** Genre (Type `rnb.alternative`) is added. No existing classification is
affected. The electronic production characteristic of much Alternative R&B is intrinsic to that
Type's sonic definition and is therefore not separately modeled as the `electronic` Trait on these
classifications.

### v0.6.0

Additive only: the **Hip-Hop** Genre (Types `hiphop.boombap`, `hiphop.gfunk`, `hiphop.trap`) is
added. No existing classification is affected. The Types are strictly sonic production styles;
lyrical or thematic labels current in popular use (Gangsta, Horrorcore, Mafioso, Conscious) are
not classification atoms under §3, so the West-Coast artists historically called "Gangsta Rap" are
classified here by their sound (the G-Funk Type).

### v0.7.0

Additive only: the **Screamo** and **Emocore** Genres are added (peer standalone genres to
`emoviolence`, `hardcore`, and `punk`). No existing classification is affected. Both are modeled
by their sonic characteristics (vocal delivery, dynamics, instrumentation) per §3.

### v0.8.0

Additive only: the **Thall** Genre, the **Depressive** Trait (Metal, requiring the Black Type),
and the **Breakcore** Type (`electronic.breakcore`) are added. No existing classification is
affected.

### v0.9.0

Additive in the validation sense: previously valid classifications stay valid. The release splits
progressive and djent music that library practice had been filing under Metalcore.

- **Djent** (`djent`) is a new Genre. On a library that follows this taxonomy it lives at
  `Core/Djent`, beside Metalcore, Deathcore, and Thall. It is modern, down-tuned, syncopated
  progressive metalcore, including instrumental music in that vocabulary.
- **Progressive Metal** already exists. It is the `progressive` Trait on Metal with no Type
  (`genre: metal`, `traits: [progressive]`), canonical render `Progressive Metal`, library folder
  `Metal/Progressive Metal`. v0.9.0 refines that Trait's definition so this classification covers
  classic and modern prog metal, including instrumental prog, and states its boundaries with
  Djent, Thall, and Metalcore. The same Trait still qualifies other foundations
  (`Progressive Death Metal`, `Progressive Rock`, `Progressive Metalcore`). No second Progressive
  Metal atom is added.
- **Instrumental** is not a Genre or a Trait. Absence of vocals does not determine classification.
  Instrumental djent stays Djent. Instrumental prog metal is Progressive Metal.
- Thall stays the Genre `thall`. Boundaries among Thall, Djent, Progressive Metal, and Metalcore
  are sonic and are stated on those atoms.

## 14. Application profiles

The base standard requires only Genre and permits Unknown. Applications MAY declare a named,
versioned stricter profile, for example:

- requiring one or more Types;
- forbidding published Unknown classifications;
- requiring human confirmation of automatic suggestions.

A profile MAY reject base-valid metadata. It MUST NOT make base-invalid metadata conforming.

## 15. Localization

v0.1 defines normative English labels and rendering.

- IDs and priority are language-neutral.
- Optional locale packs MAY provide translated labels and rendering templates.
- Missing translations fall back to normative English.
- User display overrides are application-local and MUST NOT alter metadata identities.

Full grammatical localization is designed for but not required by v0.1.

## 16. Governance

The taxonomy begins with maintainer-led governance.

Contributions MUST provide:

- proposed ID, kind, label, and placement or applicability;
- a sonic definition;
- representative recordings;
- evidence of established usage;
- aliases and conflicts with existing atoms;
- renderer requirements, if any.

The maintainer approves, requests revision, defers, or rejects with a written rationale. Rejected or
deferred proposals MAY be resubmitted with new evidence.

An atom MUST NOT be approved from lyrical themes, geography, artist identity, or spelling alone.

## 17. Licensing

Licensing for this repository is:

- taxonomy data: CC0 1.0;
- specification prose: CC BY 4.0;
- validators and reference implementations: Apache License 2.0.

See [`LICENSE.md`](LICENSE.md) and the texts under [`licenses/`](licenses/). Contributions are
accepted under the license that already applies to the files being changed.

## 18. Normative JSON example

```json
{
  "schema": "open-music-taxonomy/classification/0.1",
  "taxonomy": {
    "id": "open-music-taxonomy",
    "version": "0.9.0"
  },
  "scope": "album",
  "genre": "metal",
  "traits": [
    {"id": "technical", "priority": 1},
    {"id": "melodic", "priority": 2}
  ],
  "types": [
    {"id": "metal.death", "priority": 1},
    {"id": "metal.doom", "priority": 2}
  ]
}
```

Its canonical English rendering is:

```text
Technical Melodic Death-Doom Metal
```

## 19. Deferred questions

The following are intentionally not standardized by v0.1:

- automatic audio classification algorithms and confidence scoring;
- non-sonic metadata dimensions;
- cross-Genre relations;
- pairwise Trait incompatibilities;
- full multilingual morphology;
- Deathrock.
