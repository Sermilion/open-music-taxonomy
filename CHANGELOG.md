# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
as described in `spec.md` §13.

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
