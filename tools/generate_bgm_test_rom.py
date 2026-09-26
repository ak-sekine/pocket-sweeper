#!/usr/bin/env python3
"""Run the explicit-profile generated-song JSON→UGE→ASM→ROM pipeline."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import analyze_uge  # noqa: E402
import build_sound_test_rom  # noqa: E402
import json_to_huge_asm  # noqa: E402
import json_to_uge  # noqa: E402
from bgm_generator import (  # noqa: E402
    GameBoyConversionInput,
    GenerationInputError,
    generate_logical_composition,
    convert_to_json_v2,
)


def load_profile(path: Path, seed: int) -> dict[str, object]:
    spec = importlib.util.spec_from_file_location("pocket_sweeper_generation_profile", path)
    if spec is None or spec.loader is None:
        raise GenerationInputError(f"cannot load profile: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    factory = getattr(module, "build_profile", None)
    if factory is None:
        raise GenerationInputError(f"{path}: build_profile(seed) is required")
    profile = factory(seed)
    if not isinstance(profile, dict):
        raise GenerationInputError("build_profile must return a dict")
    return profile


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(profile_path: Path, seed: int, output_dir: Path, name: str) -> dict[str, object]:
    profile = load_profile(profile_path, seed)
    result = generate_logical_composition(seed, profile["plan"])
    conversion = GameBoyConversionInput(
        structure=result.structure,
        logical_layers=tuple(profile["logical_layers"](result)),
        allocations=tuple(profile["allocations"]),
        title=profile["title"],
        tempo=profile["tempo"],
        ticks_per_row=profile["ticks_per_row"],
        instrument_by_channel=profile["instrument_by_channel"],
        instruments=tuple(profile["instruments"]),
        absolute_pitch_map=profile["absolute_pitch_map"],
        noise_character_map=profile["noise_character_map"],
    )
    json_data = convert_to_json_v2(conversion)
    json_to_uge.validate_header(json_data)
    uge_data = json_to_uge.build_uge(json_data)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{name}.json"
    uge_path = output_dir / f"{name}.uge"
    asm_path = output_dir / f"{name}.asm"
    rom_path = output_dir / f"{name}.gb"
    json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    uge_path.write_bytes(uge_data)
    report = analyze_uge.read_file(uge_path)
    if report["song_version"]["raw"] != 6 or report["order_alignment"] != "一致":
        raise GenerationInputError("generated UGE failed structural validation")
    asm_path.write_text(json_to_huge_asm.build_asm(json_data, name), encoding="utf-8")
    build_sound_test_rom.build_rom(asm_path, rom_path)
    manifest = {
        "seed": seed,
        "generator_version": result.generator_version,
        "profile": str(profile_path),
        "artifacts": {
            "json": str(json_path), "uge": str(uge_path),
            "asm": str(asm_path), "rom": str(rom_path),
        },
        "sha256": {key: sha256(path) for key, path in {
            "json": json_path, "uge": uge_path, "asm": asm_path, "rom": rom_path,
        }.items()},
        "uge_validation": {
            "song_version": report["song_version"],
            "order_count": report["order_count"],
            "order_alignment": report["order_alignment"],
            "channels": report["channels"],
        },
    }
    manifest_path = output_dir / f"{name}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["artifacts"]["manifest"] = str(manifest_path)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    try:
        manifest = run(args.profile.resolve(), args.seed, args.output_dir.resolve(), args.name)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
