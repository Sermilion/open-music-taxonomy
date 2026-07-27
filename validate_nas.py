#!/usr/bin/env python3
"""Validate a real NAS music library against Open Music Taxonomy v0.2.

Scans ``/mnt/nas-music/{Metal,Core,Alternative,Rock}`` (configurable),
reads every ``album.nfo`` and ``artist.nfo`` (Kodi/Emby-style XML),
and checks each against the taxonomy by mapping both the NFO ``<genre>``
free text AND the on-disk subgenre folder to a structured classification
via the taxonomy's own ``Validator.render()`` (brute-force render match).

Reports:
  * conformance  — does the genre render to a valid taxonomy classification?
  * coverage     — which on-disk subgenres the taxonomy v0.2 cannot express?
  * drift        — albums whose NFO genre disagrees with their folder.
  * hygiene      — empty genres, parse errors, scene-release junk .nfo files.

Read-only. Never writes to the NAS. Output report is local (.local/).
"""
from __future__ import annotations

import argparse
import glob
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from itertools import combinations, permutations
from pathlib import Path
from typing import Any

from validate import Validator, load_json  # reuse the taxonomy validator

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / ".local" / "nas-full-report.md"

DEFAULT_ROOT = "/mnt/nas-music"
DEFAULT_SCOPES = ["Metal", "Core", "Alternative", "Rock", "Jazz", "Traditional Pop", "Electronic", "R&B"]
SCOPE_GENRES = {
    "metal", "metalcore", "deathcore", "rock",
    "hardcore", "punk", "grunge", "numetal", "emoviolence",
    "jazz", "traditionalpop", "electronic", "rnb",
}
METADATA_NFOS = {"album.nfo", "artist.nfo"}

# Abbreviations / casing variants the render index won't catch on its own.
GENRE_ALIASES = {
    "alt rock": "alt. rock",
}


def normalize(text: str) -> str:
    text = text.strip().lower()
    text = GENRE_ALIASES.get(text, text)
    return " ".join(text.split())


def build_render_index(validator: Validator) -> dict[str, dict[str, Any]]:
    """Map lowercased canonical render -> one representative classification.

    Enumerates per approved scope genre: one type with 0-2 traits (all priority
    orderings). Small taxonomy, so cheap; gives an exact render-faithful reverse
    lookup from free text (folder name or NFO <genre>) -> classification.
    """
    index: dict[str, dict[str, Any]] = {}

    def prefer(existing: dict | None, candidate: dict[str, Any]) -> dict[str, Any]:
        # Prefer fewer traits, then alphabetical, for stable representation.
        if existing is None:
            return candidate
        key = lambda c: (len(c["traits"]), [t["id"] for t in c["traits"]],
                         [t["id"] for t in c["types"]])
        return min(existing, candidate, key=key)

    for genre_id, genre in validator.genres.items():
        if genre_id not in SCOPE_GENRES or genre.get("status") != "approved":
            continue
        types = [ty for ty in validator.taxonomy["types"]
                 if ty["genre"] == genre_id and ty.get("status") == "approved"]
        traits = [tr for tr in validator.taxonomy["traits"]
                  if tr.get("status") == "approved"
                  and (not tr.get("applicable_genres")
                       or genre_id in tr["applicable_genres"])]
        # Bare genre (no type): metalcore/deathcore/rock/metal have no sub-types
        # and are valid classifications on their own.
        bare = {"genre": genre_id, "traits": [], "types": []}
        index[validator.render(bare).lower()] = prefer(
            index.get(validator.render(bare).lower()), bare)
        # Trait(s) on a bare genre (no type): "Folk Metal", "Post-Metal",
        # "Symphonic Metal" — valid classifications my first index omitted.
        for tr in traits:
            cls = {"genre": genre_id, "traits": [{"id": tr["id"], "priority": 1}],
                   "types": []}
            key = validator.render(cls).lower()
            index[key] = prefer(index.get(key), cls)
        for a, b in combinations(traits, 2):
            for first, second in permutations((a, b), 2):
                cls = {"genre": genre_id,
                       "traits": [{"id": first["id"], "priority": 1},
                                  {"id": second["id"], "priority": 2}],
                       "types": []}
                key = validator.render(cls).lower()
                index[key] = prefer(index.get(key), cls)
        for ty in types:
            base_types = [{"id": ty["id"], "priority": 1}]
            cls0 = {"genre": genre_id, "traits": [], "types": base_types}
            index[validator.render(cls0).lower()] = prefer(
                index.get(validator.render(cls0).lower()), cls0)
            for tr in traits:
                cls1 = {"genre": genre_id,
                        "traits": [{"id": tr["id"], "priority": 1}],
                        "types": base_types}
                key = validator.render(cls1).lower()
                index[key] = prefer(index.get(key), cls1)
            for a, b in combinations(traits, 2):
                for first, second in permutations((a, b), 2):
                    cls2 = {"genre": genre_id,
                            "traits": [{"id": first["id"], "priority": 1},
                                       {"id": second["id"], "priority": 2}],
                            "types": base_types}
                    key = validator.render(cls2).lower()
                    index[key] = prefer(index.get(key), cls2)

    # Short type-label folders: a folder named "Techno" must resolve to the same
    # classification as the full render "Techno Electronic", mirroring tidalwatch's
    # label-alias resolver. Only unambiguous labels qualify (a single render, and
    # not itself a display string), so "Rock"/"Gothic" are excluded. Without this,
    # short type-label subfolders (Electronic/House, R&B/Alternative, …) are
    # falsely reported as taxonomy coverage gaps.
    renders_seen = set(index.keys())
    label_renders: dict[str, set[str]] = {}
    for genre_id, genre in validator.genres.items():
        if genre_id not in SCOPE_GENRES or genre.get("status") != "approved":
            continue
        for ty in validator.taxonomy["types"]:
            if ty["genre"] != genre_id or ty.get("status") != "approved":
                continue
            r = validator.render({"genre": genre_id, "traits": [],
                                  "types": [{"id": ty["id"], "priority": 1}]}).lower()
            label_renders.setdefault(ty["label"], set()).add(r)
    for label, rs in label_renders.items():
        if len(rs) == 1 and label.lower() not in renders_seen:
            render_lc = next(iter(rs))
            if render_lc in index:
                index[label.lower()] = index[render_lc]
    return index


def subgenre_of(path: str, root: str) -> str | None:
    """First directory component under the scope root: <root>/<Scope>/<SUBGENRE>/..."""
    try:
        rel = os.path.relpath(path, root)
    except ValueError:
        return None
    parts = rel.split(os.sep)
    # parts[0]=Scope, parts[1]=subgenre, ...
    return parts[1] if len(parts) > 1 else None


def audit(validator: Validator, root: str, scopes: list[str]) -> dict[str, Any]:
    index = build_render_index(validator)
    stats: dict[str, Any] = {
        "per_scope": {},
        "per_subgenre": defaultdict(lambda: Counter()),
        "unmapped_subgenres": Counter(),
        "unmapped_nfo_genres": Counter(),
        "drift_samples": [],
        "empty_genre": [],
        "parse_errors": [],
        "junk_nfos": [],
        "totals": Counter(),
    }

    for scope in scopes:
        scope_dir = os.path.join(root, scope)
        nfos = sorted(glob.glob(os.path.join(scope_dir, "**", "*.nfo"), recursive=True))
        s = stats["per_scope"].setdefault(scope, Counter())
        s["nfo_files"] = len(nfos)
        stats["totals"]["nfo_files"] += len(nfos)

        for nfo in nfos:
            base = os.path.basename(nfo)
            if base not in METADATA_NFOS:
                stats["junk_nfos"].append(os.path.relpath(nfo, root))
                s["junk"] += 1
                stats["totals"]["junk"] += 1
                continue
            s["metadata"] += 1
            stats["totals"]["metadata"] += 1

            try:
                xml = ET.parse(nfo).getroot()
            except ET.ParseError as exc:
                stats["parse_errors"].append((os.path.relpath(nfo, root), str(exc)))
                s["parse_error"] += 1
                stats["totals"]["parse_error"] += 1
                continue

            genre_raw = xml.findtext("genre") or ""
            sub = subgenre_of(nfo, root)
            sub_norm = normalize(sub) if sub else ""
            nfo_norm = normalize(genre_raw)

            sub_cls = index.get(sub_norm)
            nfo_cls = index.get(nfo_norm)

            # Subgenre accounting.
            if sub:
                bucket = stats["per_subgenre"][f"{scope}/{sub}"]
                bucket["total"] += 1
                if sub_cls:
                    bucket["mapped_render"] = validator.render(sub_cls)
                else:
                    stats["unmapped_subgenres"][f"{scope}/{sub}"] += 1
                    bucket["unmapped"] += 1

            # NFO genre accounting.
            if not genre_raw.strip():
                stats["empty_genre"].append(os.path.relpath(nfo, root))
                s["empty_genre"] += 1
                stats["totals"]["empty_genre"] += 1
            elif nfo_cls:
                s["nfo_conformant"] += 1
                stats["totals"]["nfo_conformant"] += 1
            else:
                stats["unmapped_nfo_genres"][genre_raw.strip()] += 1
                s["nfo_unmapped"] += 1
                stats["totals"]["nfo_unmapped"] += 1

            # Drift: both mapped but disagree.
            if sub_cls and nfo_cls:
                if validator.render(sub_cls).lower() != validator.render(nfo_cls).lower():
                    if len(stats["drift_samples"]) < 200:
                        stats["drift_samples"].append({
                            "path": os.path.relpath(nfo, root),
                            "folder": sub,
                            "nfo_genre": genre_raw.strip(),
                            "folder_render": validator.render(sub_cls),
                            "nfo_render": validator.render(nfo_cls),
                        })
                    s["drift"] += 1
                    stats["totals"]["drift"] += 1
    return stats


def write_report(stats: dict[str, Any], root: str) -> Path:
    t = stats["totals"]
    lines: list[str] = []
    lines.append("# NAS Library Validation Report (full)")
    lines.append("")
    lines.append(f"Source: `{root}/{{Metal,Core,Alternative,Rock}}`  ·  "
                 "Open Music Taxonomy v0.2  ·  read-only audit.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- `.nfo` files found: **{t['nfo_files']}**")
    lines.append(f"- Metadata NFOs scanned (album.nfo + artist.nfo): **{t['metadata']}**")
    lines.append(f"- Scene-release / junk `.nfo` skipped: **{t['junk']}**")
    lines.append(f"- Parse errors: **{t['parse_error']}**")
    lines.append(f"- NFO `<genre>` conformant (renders to a taxonomy atom): **{t['nfo_conformant']}**")
    lines.append(f"- NFO `<genre>` unmapped (taxonomy gap): **{t['nfo_unmapped']}**")
    lines.append(f"- Empty `<genre>`: **{t['empty_genre']}**")
    lines.append(f"- Folder ↔ NFO drift: **{t['drift']}**")
    lines.append("")

    lines.append("## Per scope")
    lines.append("")
    lines.append("| Scope | metadata | conformant | unmapped | empty | drift | parse-err | junk |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for scope, c in stats["per_scope"].items():
        lines.append(f"| {scope} | {c['metadata']} | {c['nfo_conformant']} | "
                     f"{c['nfo_unmapped']} | {c['empty_genre']} | {c['drift']} | "
                     f"{c['parse_error']} | {c['junk']} |")
    lines.append("")

    if stats["unmapped_subgenres"]:
        lines.append("## Taxonomy coverage gaps — subgenres v0.2 cannot express")
        lines.append("")
        lines.append("These on-disk subgenre folders have no matching taxonomy classification.")
        lines.append("")
        lines.append("| Subgenre folder | albums |")
        lines.append("|---|---|")
        for sub, n in stats["unmapped_subgenres"].most_common():
            lines.append(f"| `{sub}` | {n} |")
        lines.append("")

    if stats["unmapped_nfo_genres"]:
        lines.append("## Unmapped NFO `<genre>` values")
        lines.append("")
        lines.append("| NFO `<genre>` | count |")
        lines.append("|---|---|")
        for g, n in stats["unmapped_nfo_genres"].most_common(40):
            lines.append(f"| {g} | {n} |")
        lines.append("")

    if stats["drift_samples"]:
        lines.append("## Folder ↔ NFO drift (sample, first 200)")
        lines.append("")
        lines.append("| Album path | folder | NFO genre | folder→ | NFO→ |")
        lines.append("|---|---|---|---|---|")
        for d in stats["drift_samples"]:
            lines.append(f"| `{d['path']}` | {d['folder']} | {d['nfo_genre']} "
                         f"| {d['folder_render']} | {d['nfo_render']} |")
        lines.append("")

    if stats["empty_genre"]:
        lines.append(f"## Empty `<genre>` ({len(stats['empty_genre'])})")
        lines.append("")
        for p in stats["empty_genre"][:100]:
            lines.append(f"- `{p}`")
        if len(stats["empty_genre"]) > 100:
            lines.append(f"- …and {len(stats['empty_genre']) - 100} more")
        lines.append("")

    if stats["parse_errors"]:
        lines.append(f"## Parse errors ({len(stats['parse_errors'])})")
        lines.append("")
        for p, err in stats["parse_errors"][:50]:
            lines.append(f"- `{p}` — {err}")
        lines.append("")

    if stats["junk_nfos"]:
        lines.append(f"## Scene-release / non-metadata `.nfo` skipped ({len(stats['junk_nfos'])})")
        lines.append("")
        lines.append("_These are piracy-scene release notes, not Kodi/Emby metadata._")
        lines.append("")
        for p in stats["junk_nfos"][:40]:
            lines.append(f"- `{p}`")
        lines.append("")

    lines.append("## Scope note")
    lines.append("")
    lines.append("Conformance here is **structural**: a tag must render to a valid "
                 "taxonomy `genre + type + traits` classification. It does **not** "
                 "judge whether a label is musically correct — the NFO's own "
                 "`<genre>` and the folder placement are trusted. `Rock/` has no "
                 "`.nfo` files at all and is reported as 0 metadata.")
    lines.append("")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    return REPORT


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--scopes", nargs="*", default=DEFAULT_SCOPES)
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        print(f"root not found: {args.root}", file=sys.stderr)
        return 2

    validator = Validator(load_json("taxonomy.json"))
    stats = audit(validator, args.root, args.scopes)
    path = write_report(stats, args.root)
    t = stats["totals"]
    pct = (t["nfo_conformant"] / t["metadata"] * 100) if t["metadata"] else 0
    print(f"Scanned {t['metadata']} metadata NFOs "
          f"({t['nfo_files']} total .nfo, {t['junk']} junk skipped).")
    print(f"Conformant: {t['nfo_conformant']} ({pct:.1f}%)  "
          f"Unmapped: {t['nfo_unmapped']}  Empty: {t['empty_genre']}  "
          f"Drift: {t['drift']}  Parse-err: {t['parse_error']}")
    print(f"Unmappable subgenre folders: {len(stats['unmapped_subgenres'])}")
    print(f"Report: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
