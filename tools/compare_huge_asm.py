#!/usr/bin/env python3
"""Compare hUGEDriver ASM while ignoring generator-specific label spelling."""
import argparse
import re
from pathlib import Path

LABEL = re.compile(r"^(?P<label>[A-Za-z_][A-Za-z0-9_]*)(?:::|:)(?P<rest>.*)$")
PREFIX_HINT = re.compile(r"^(?P<prefix>.+)_(?:P\d+|duty_instruments|wave_instruments|noise_instruments|routines|waves|it(?:Square|Wave|Noise)inst\d+|_hUGE_Routine_\d+)$")
STATUS_EQUAL = "一致"
STATUS_SPELLING = "表記上の差異"
STATUS_EXTENSION = "hUGETracker標準Exportに存在しない独自拡張"
STATUS_MISMATCH = "再生動作に影響する不一致"
STATUS_UNCOMPARABLE = "比較不能"

def sections(path):
    result, current, lines = {}, None, []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        match = LABEL.match(line)
        if match:
            if current is not None:
                result[current] = lines
            current, lines = match.group("label"), ([match.group("rest").strip()] if match.group("rest").strip() else [])
        elif current is not None:
            lines.append(line)
    if current is not None:
        result[current] = lines
    return result

def clean(lines):
    return [re.sub(r"^[A-Za-z_][A-Za-z0-9_]*:\s*", "", re.sub(r";.*$", "", x).strip()) for x in lines
            if x.strip() and not x.lstrip().startswith(";")]

def semantic_lines(lines):
    result = []
    for line in clean(lines):
        match = re.fullmatch(r"ds\s+(\d+)", line, re.I)
        result.extend(["db 0"] * int(match.group(1)) if match else [line])
    return result

def detect_prefix(labels):
    candidates = []
    for label in labels:
        match = PREFIX_HINT.match(label)
        if match:
            candidates.append(match.group("prefix") + "_")
    return max(candidates, key=len, default="")

def canonical(label, prefix):
    label = label[len(prefix):] if prefix and label.startswith(prefix) else label
    match = re.fullmatch(r"_+(?:end_)?hUGE_Routine_(\d+)", label)
    return "__hUGE_Routine_" + match.group(1) if match else label

def canonical_sections(raw, prefix):
    result = {}
    for label, lines in raw.items():
        result.setdefault(canonical(label, prefix), []).extend(lines)
    return result

def bytes_from(lines):
    values = []
    for line in clean(lines):
        match = re.match(r"(?P<width>db|dw)\s+(.+)$", line, re.I)
        if not match:
            continue
        for token in re.split(r"\s*,\s*", match.group(2)):
            token = token.split()[0]
            try:
                value = int(token.replace("$", "0x"), 0)
                values.extend(([value & 0xff] if match.group("width").lower() == "db"
                                else [value & 0xff, (value >> 8) & 0xff]))
            except ValueError:
                pass
    return values

def comparable(left, right, category):
    a, b = semantic_lines(left), semantic_lines(right)
    if category in {"descriptor", "OrderMatrix"}:
        symbol = r"[A-Za-z0-9_]+_((?:order(?:_cnt|[1-4])?|P\d+|duty_instruments|wave_instruments|noise_instruments|routines|waves))\b"
        a = [re.sub(symbol, r"\1", x) for x in a]
        b = [re.sub(symbol, r"\1", x) for x in b]
    if category == "descriptor" and len(a) == len(b) + 1:
        a = [x for x in a if "loop_metadata" not in x]  # Version 2 extension.
    if category == "pattern":
        return a == b
    if category == "wave table":
        # Export ASM commonly emits only the banks referenced by instruments;
        # compare the common prefix and let the caller report omitted banks.
        left_bytes, right_bytes = bytes_from(a), bytes_from(b)
        return left_bytes[:len(right_bytes)] == right_bytes
    if category == "instrument":
        return bytes_from(a) == bytes_from(b)
    if category == "routine":
        return [x.lower() for x in a if not LABEL.match(x)] == [x.lower() for x in b if not LABEL.match(x)]
    return a == b

def category(label):
    if re.fullmatch(r"P\d+", label): return "pattern"
    if label in {"duty_instruments", "wave_instruments", "noise_instruments"}: return label.replace("_", " ").title() + " bank"
    if re.fullmatch(r"it(?:Square|Wave|Noise)inst\d+", label): return "instrument"
    if label in {"routines"} or re.fullmatch(r"__hUGE_Routine_\d+", label): return "routine"
    if label == "waves" or re.match(r"wave\d", label): return "wave table"
    if label.startswith("order") or label == "order_cnt": return "OrderMatrix"
    if label in {"song_descriptor", "descriptor"}: return "descriptor"
    if label.endswith("loop_metadata"): return "loop metadata"
    return "other"

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("generated"); parser.add_argument("export")
    parser.add_argument("--prefix", help="generated ASM label prefix to remove")
    args = parser.parse_args(argv)
    gen_raw, exp_raw = sections(args.generated), sections(args.export)
    prefix = args.prefix if args.prefix is not None else detect_prefix(gen_raw)
    generated = canonical_sections(gen_raw, prefix)
    exported = canonical_sections(exp_raw, "")
    for table in (generated, exported):
        if "song_descriptor" in table:
            table["descriptor"] = table.pop("song_descriptor")
        for n in range(16):
            end = "__end_hUGE_Routine_" + str(n)
            key = "__hUGE_Routine_" + str(n)
            if end in table:
                table.setdefault(key, []).extend(table.pop(end))
    descriptor_candidates = [k for k in generated if k not in {"descriptor", "loop_metadata"}
                             and k.startswith("bgm_")]
    if "descriptor" not in generated and descriptor_candidates:
        generated["descriptor"] = generated.pop(descriptor_candidates[0])
    # hUGETracker may put the table in wave0: db ... instead of waves: db ... .
    if "waves" in generated and "waves" in exported:
        exported["waves"] = exported["waves"] + sum((v for k, v in exported.items()
                                                        if re.fullmatch(r"wave\d+", k)), [])
    labels = sorted(set(generated) | set(exported))
    labels = [label for label in labels if not (re.fullmatch(r"wave\d+", label) and "waves" in generated)]
    for label in labels:
        kind = category(label)
        left, right = generated.get(label), exported.get(label)
        if kind == "loop metadata" and left is not None and right is None:
            status = STATUS_EXTENSION
        elif left is None or right is None:
            status = STATUS_UNCOMPARABLE
        elif comparable(left, right, kind):
            original_gen = next((x for x in gen_raw if canonical(x, prefix) == label), label)
            original_exp = next((x for x in exp_raw if x == label), label)
            status = STATUS_SPELLING if original_gen != original_exp else STATUS_EQUAL
        elif kind == "other":
            status = STATUS_UNCOMPARABLE
        else:
            status = STATUS_MISMATCH
        print(f"{status}\t{kind}\t{label}\tgenerated={len(clean(left or []))} export={len(clean(right or []))}")

if __name__ == "__main__":
    main()
