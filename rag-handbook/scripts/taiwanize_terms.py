#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReplaceRule:
    pattern: re.Pattern[str]
    repl: str


def build_rules() -> list[ReplaceRule]:
    # Order matters: do more specific phrases first, then broader ones.
    pairs: list[tuple[str, str]] = [
        # 陸式工程詞 → 台灣較自然的說法
        ("回饋循環", "回饋循環"),
        ("評估迭代循環", "評估迭代循環"),
        ("迭代循環", "迭代循環"),
        ("循環", "循環"),
        ("端到端", "端到端"),
        ("務實起點", "務實起點"),
        ("起點", "起點"),
        ("最快上線", "最快上線"),
        ("最小可直接導入骨架", "最小可直接導入骨架"),
        ("可直接導入的骨架", "可直接導入的骨架"),
        ("可直接導入", "可直接導入"),
        ("工程導入建議", "工程導入建議"),
        ("導入建議", "導入建議"),
        ("導入策略", "導入策略"),
        ("導入順序", "導入順序"),
        ("導入路線", "導入路線"),
        ("導入方式", "導入方式"),
        ("導入配方", "導入配方"),
        ("導入向量檢索", "導入向量檢索"),
        ("先導入", "先導入"),
        # Default replacement (最後才做，避免蓋掉上面更精準的詞組)
        ("導入", "導入"),
        ("對準", "對準"),
    ]
    return [ReplaceRule(re.compile(re.escape(src)), dst) for src, dst in pairs]


def apply_rules(text: str, rules: list[ReplaceRule]) -> str:
    for r in rules:
        text = r.pattern.sub(r.repl, text)
    return text


_MD_FENCE_RE = re.compile(r"^\s*(```+|~~~+)")

# Match inline markdown links: [text](url) and ![alt](url)
# We only rewrite the visible text/alt, not the URL, to avoid breaking paths.
_MD_LINK_RE = re.compile(r"(!?\[)([^\]]+)(\]\()([^)]+)(\))")


def rewrite_markdown_line_outside_code(line: str, rules: list[ReplaceRule]) -> str:
    # Split by inline code `...` and only rewrite non-code segments.
    parts = line.split("`")
    for i in range(0, len(parts), 2):  # even indices are outside inline code
        seg = parts[i]

        # Rewrite plain text outside links, and for links rewrite visible text only (keep URL intact).
        out: list[str] = []
        pos = 0
        for m in _MD_LINK_RE.finditer(seg):
            out.append(apply_rules(seg[pos : m.start()], rules))
            pre, text, mid, url, suf = m.groups()
            out.append(f"{pre}{apply_rules(text, rules)}{mid}{url}{suf}")
            pos = m.end()
        out.append(apply_rules(seg[pos:], rules))
        parts[i] = "".join(out)
    return "`".join(parts)


def rewrite_markdown(text: str, rules: list[ReplaceRule]) -> str:
    out_lines: list[str] = []
    in_fence = False
    fence_marker = ""

    for line in text.splitlines(keepends=True):
        m = _MD_FENCE_RE.match(line)
        if m:
            marker = m.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker[:3]  # normalize ``` or ~~~
            else:
                # close fence if marker matches opening fence type
                if marker.startswith(fence_marker):
                    in_fence = False
                    fence_marker = ""
            out_lines.append(line)
            continue

        if in_fence:
            out_lines.append(line)
            continue

        out_lines.append(rewrite_markdown_line_outside_code(line, rules))

    return "".join(out_lines)


def rewrite_plain_text(text: str, rules: list[ReplaceRule]) -> str:
    # For non-markdown files (e.g., mkdocs.yml) we can apply rules directly.
    return apply_rules(text, rules)


def iter_target_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        if p.is_dir():
            for fp in p.rglob("*"):
                if fp.is_dir():
                    continue
                # Avoid generated site output
                if "site" in fp.parts:
                    continue
                if fp.suffix.lower() in {".md", ".yml", ".yaml", ".py"}:
                    files.append(fp)
        else:
            files.append(p)
    # stable order for deterministic output
    return sorted(set(files))


def process_file(path: Path, rules: list[ReplaceRule], apply: bool) -> tuple[bool, str]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".md":
        new = rewrite_markdown(raw, rules)
    else:
        new = rewrite_plain_text(raw, rules)

    if new == raw:
        return False, ""

    if apply:
        path.write_text(new, encoding="utf-8")
    return True, f"{path}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rewrite Mainland-style Chinese engineering terms to Taiwan-preferred terms, safely for Markdown."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes to files. Without this flag, runs in check mode and prints files that would change.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["rag-handbook", "skills", "mkdocs.yml"],
        help="Paths to scan (files or directories). Defaults: rag-handbook skills mkdocs.yml",
    )
    args = parser.parse_args()

    rules = build_rules()
    targets = iter_target_files([Path(x) for x in args.paths])

    changed: list[str] = []
    for fp in targets:
        ok, msg = process_file(fp, rules, apply=args.apply)
        if ok:
            changed.append(msg)

    mode = "APPLIED" if args.apply else "CHECK"
    print(f"[{mode}] {len(changed)} file(s) would change." if not args.apply else f"[{mode}] Updated {len(changed)} file(s).")
    for c in changed:
        print(f"- {c}")


if __name__ == "__main__":
    main()

