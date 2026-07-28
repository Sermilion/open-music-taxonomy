#!/usr/bin/env python3
"""Dependency-free validator for Open Music Taxonomy v0.1 fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def load_json(name: str) -> dict[str, Any]:
    with (ROOT / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def by_id(items: list[dict[str, Any]], kind: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        item_id = item["id"]
        if item_id in result:
            raise ValueError(f"duplicate {kind} id {item_id}")
        result[item_id] = item
    return result


class Validator:
    def __init__(self, taxonomy: dict[str, Any]) -> None:
        self.taxonomy = taxonomy
        self.genres = by_id(taxonomy["genres"], "genre")
        self.types = by_id(taxonomy["types"], "type")
        self.traits = by_id(taxonomy["traits"], "trait")

    def validate_taxonomy(self) -> list[str]:
        errors: list[str] = []
        for type_atom in self.types.values():
            if type_atom["genre"] not in self.genres:
                errors.append(
                    f"type {type_atom['id']} references unknown genre {type_atom['genre']}"
                )

        for trait in self.traits.values():
            for genre_id in trait.get("applicable_genres", []):
                if genre_id not in self.genres:
                    errors.append(f"trait {trait['id']} references unknown genre {genre_id}")
            for type_id in trait.get("required_types", []):
                if type_id not in self.types:
                    errors.append(f"trait {trait['id']} requires unknown type {type_id}")
        return errors

    @staticmethod
    def validate_priorities(
        modifiers: list[dict[str, Any]], kind: str, errors: list[str]
    ) -> None:
        priorities = [item.get("priority") for item in modifiers]
        if any(not isinstance(priority, int) or priority < 1 for priority in priorities):
            errors.append(f"{kind} priorities must be positive integers")
            return
        if len(set(priorities)) != len(priorities):
            errors.append(f"{kind} priorities must be unique")
            return
        if sorted(priorities) != list(range(1, len(priorities) + 1)):
            errors.append(f"{kind} priorities must be contiguous")

    @staticmethod
    def validate_unique_ids(
        modifiers: list[dict[str, Any]], kind: str, errors: list[str]
    ) -> None:
        seen: set[str] = set()
        for item in modifiers:
            item_id = item.get("id")
            if item_id in seen:
                errors.append(f"duplicate {kind} {item_id}")
            seen.add(item_id)

    def validate_classification(self, classification: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        genre_id = classification.get("genre")
        traits = classification.get("traits")
        types = classification.get("types")

        if not isinstance(genre_id, str):
            return ["genre must be one string"]
        if not isinstance(traits, list) or not isinstance(types, list):
            return ["traits and types must be arrays"]

        if genre_id == "unknown":
            if traits or types:
                errors.append("unknown cannot have modifiers")
            return errors

        genre = self.genres.get(genre_id)
        if genre is None:
            errors.append(f"unknown genre {genre_id}")
        elif genre["status"] != "approved":
            errors.append(f"genre {genre_id} is not approved")

        self.validate_unique_ids(traits, "trait", errors)
        self.validate_unique_ids(types, "type", errors)
        self.validate_priorities(traits, "trait", errors)
        self.validate_priorities(types, "type", errors)

        selected_type_ids = {item.get("id") for item in types}
        for item in types:
            type_id = item.get("id")
            type_atom = self.types.get(type_id)
            if type_atom is None:
                errors.append(f"unknown type {type_id}")
                continue
            if type_atom["status"] != "approved":
                errors.append(f"type {type_id} is not approved")
            if type_atom["genre"] != genre_id:
                errors.append(
                    f"type {type_id} belongs to {type_atom['genre']}, not {genre_id}"
                )

        for item in traits:
            trait_id = item.get("id")
            trait = self.traits.get(trait_id)
            if trait is None:
                errors.append(f"unknown trait {trait_id}")
                continue
            if trait["status"] != "approved":
                errors.append(f"trait {trait_id} is not approved")
                continue
            applicable_genres = trait.get("applicable_genres")
            if applicable_genres and genre_id not in applicable_genres:
                errors.append(f"trait {trait_id} is not applicable to {genre_id}")
            required_types = set(trait.get("required_types", []))
            missing_types = sorted(required_types - selected_type_ids)
            if missing_types:
                errors.append(
                    f"trait {trait_id} requires types {', '.join(missing_types)}"
                )
        return errors

    def render(self, classification: dict[str, Any]) -> str:
        genre_id = classification["genre"]
        if genre_id == "unknown":
            return "Unknown"

        tokens: list[tuple[str, str]] = []
        for item in sorted(classification["traits"], key=lambda value: value["priority"]):
            trait = self.traits[item["id"]]
            tokens.append((trait["label"], trait.get("join_next", "space")))
        ordered_types = sorted(
            classification["types"], key=lambda value: value["priority"]
        )
        for index, item in enumerate(ordered_types):
            type_atom = self.types[item["id"]]
            join_next = type_atom.get("join_next", "hyphen" if index < len(ordered_types) - 1 else "space")
            tokens.append((type_atom["label"], join_next))
        tokens.append((self.genres[genre_id]["label"], "space"))

        rendered = tokens[0][0]
        separators = {"space": " ", "hyphen": "-", "concatenate": ""}
        for index in range(1, len(tokens)):
            rendered += separators[tokens[index - 1][1]] + tokens[index][0]
        return rendered

    @staticmethod
    def exact_key(classification: dict[str, Any]) -> tuple[Any, ...]:
        traits = tuple(
            item["id"]
            for item in sorted(classification["traits"], key=lambda value: value["priority"])
        )
        types = tuple(
            item["id"]
            for item in sorted(classification["types"], key=lambda value: value["priority"])
        )
        return classification["genre"], traits, types

    @staticmethod
    def composition_key(classification: dict[str, Any]) -> tuple[Any, ...]:
        traits = frozenset(item["id"] for item in classification["traits"])
        types = frozenset(item["id"] for item in classification["types"])
        return classification["genre"], traits, types


def run() -> int:
    taxonomy = load_json("taxonomy.json")
    corpus = load_json("conformance.json")
    reference_albums = load_json("reference-albums.json")
    validator = Validator(taxonomy)
    failures: list[str] = []

    failures.extend(f"taxonomy: {error}" for error in validator.validate_taxonomy())

    if corpus["taxonomy"]["id"] != taxonomy["id"]:
        failures.append("corpus taxonomy id does not match taxonomy package")
    if corpus["taxonomy"]["version"] != taxonomy["version"]:
        failures.append("corpus taxonomy version does not match taxonomy package")

    cases = corpus["cases"]
    if len(cases) != 87:
        failures.append(f"expected 87 conformance cases, found {len(cases)}")

    case_by_id: dict[str, dict[str, Any]] = {}
    for case in cases:
        case_id = case["id"]
        if case_id in case_by_id:
            failures.append(f"duplicate conformance case id {case_id}")
            continue
        case_by_id[case_id] = case

        errors = validator.validate_classification(case["classification"])
        if not errors and "display" in case:
            rendered = validator.render(case["classification"])
            if rendered != case["display"]:
                errors.append(
                    f"canonical display mismatch: expected {rendered!r}, got {case['display']!r}"
                )

        expected_valid = case["expected"] == "valid"
        if expected_valid and errors:
            failures.append(f"{case_id} expected valid: {'; '.join(errors)}")
        elif not expected_valid and not errors:
            failures.append(f"{case_id} expected invalid but validation passed")
        elif not expected_valid:
            expected_error = case.get("expected_error")
            if expected_error and not any(expected_error in error for error in errors):
                failures.append(
                    f"{case_id} expected error {expected_error!r}, got {'; '.join(errors)}"
                )

    for assertion in corpus["equivalence_assertions"]:
        left = case_by_id[assertion["left"]]["classification"]
        right = case_by_id[assertion["right"]]["classification"]
        exact_equal = validator.exact_key(left) == validator.exact_key(right)
        compositionally_equivalent = (
            validator.composition_key(left) == validator.composition_key(right)
        )
        if exact_equal != assertion["exact_equal"]:
            failures.append(
                f"{assertion['left']}/{assertion['right']} exact equality assertion failed"
            )
        if compositionally_equivalent != assertion["compositionally_equivalent"]:
            failures.append(
                f"{assertion['left']}/{assertion['right']} composition assertion failed"
            )

    if reference_albums["taxonomy"]["id"] != taxonomy["id"]:
        failures.append("reference album taxonomy id does not match taxonomy package")
    if reference_albums["taxonomy"]["version"] != taxonomy["version"]:
        failures.append("reference album taxonomy version does not match taxonomy package")

    album_ids: set[str] = set()
    for album in reference_albums["albums"]:
        album_id = album["id"]
        if album_id in album_ids:
            failures.append(f"duplicate reference album id {album_id}")
            continue
        album_ids.add(album_id)

        if album["review_status"] not in {"accepted", "needs_review"}:
            failures.append(
                f"{album_id} has unsupported review status {album['review_status']!r}"
            )

        errors = validator.validate_classification(album["classification"])
        if errors:
            failures.append(
                f"{album_id} has invalid classification: {'; '.join(errors)}"
            )
            continue

        rendered = validator.render(album["classification"])
        if rendered != album["display"]:
            failures.append(
                f"{album_id} canonical display mismatch: "
                f"expected {rendered!r}, got {album['display']!r}"
            )

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    valid_count = sum(case["expected"] == "valid" for case in cases)
    invalid_count = len(cases) - valid_count
    print(
        f"PASS: {len(cases)} cases "
        f"({valid_count} valid, {invalid_count} invalid), "
        f"{len(corpus['equivalence_assertions'])} equivalence assertions, "
        f"{len(reference_albums['albums'])} reference albums"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
