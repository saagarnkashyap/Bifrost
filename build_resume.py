#!/usr/bin/env python3
"""
build_resume.py -- assemble sections/*.yaml + templates/*.tex.j2 into resume.tex

Usage:
    python build_resume.py
    python build_resume.py --config config.gf.yaml --out resume_gf.tex
    python build_resume.py --fontsize 10pt --margin 0.45in   # squeeze to one page
    python build_resume.py --zip                             # overleaf_upload.zip
"""

import argparse
import re
import sys
import zipfile
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

HERE = Path(__file__).parent
SECTIONS = HERE / "sections"

# Sections stored as plain prose (.md) instead of YAML.
PROSE = {"summary", "volunteering"}

# LaTeX-safe Jinja: << value >>, %% for / %% if, <% ... %>
ENV = Environment(
    loader=FileSystemLoader(HERE),
    variable_start_string="<<",
    variable_end_string=">>",
    block_start_string="<%",
    block_end_string="%>",
    comment_start_string="<#",
    comment_end_string="#>",
    line_statement_prefix="%%",
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=False,
    undefined=StrictUndefined,
    keep_trailing_newline=True,
)

ESCAPES = {
    "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}
RAW_KEYS = ("url", "link", "email", "phone")


def tex_escape(s):
    return re.sub(r"[&%$#_{}~^]", lambda m: ESCAPES[m.group()], str(s))


def clean(node, key=None):
    """Escape LaTeX specials everywhere except URL/email/phone fields."""
    if isinstance(node, dict):
        return {k: clean(v, k) for k, v in node.items()}
    if isinstance(node, list):
        return [clean(v, key) for v in node]
    if isinstance(node, str):
        if key and any(r in key.lower() for r in RAW_KEYS):
            return node.strip()
        return tex_escape(node.strip())
    return node


def load_section(name):
    """Load sections/<name>.md (prose) or sections/<name>.yaml (structured)."""
    if name in PROSE:
        f = SECTIONS / f"{name}.md"
        if not f.exists():
            return None
        text = " ".join(f.read_text(encoding="utf-8").split())
        return text or None

    f = SECTIONS / f"{name}.yaml"
    if not f.exists():
        print(f"  ! sections/{name}.yaml not found -- section skipped")
        return None
    return yaml.safe_load(f.read_text(encoding="utf-8"))


def describe(name, data):
    if data is None:
        return "MISSING"
    if isinstance(data, list):
        return f"{len(data)} entries"
    if isinstance(data, str):
        return f"{len(data.split())} words"
    return "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--out", default="resume.tex")
    ap.add_argument("--fontsize", choices=["10pt", "11pt", "12pt"])
    ap.add_argument("--margin", help="e.g. 0.45in (overrides config)")
    ap.add_argument("--zip", action="store_true")
    args = ap.parse_args()

    cfg = yaml.safe_load((HERE / args.config).read_text(encoding="utf-8"))
    page = cfg.get("page", {})
    if args.fontsize:
        page["fontsize"] = args.fontsize
    if args.margin:
        page["margin"] = args.margin

    basics = load_section("basics")
    if not basics:
        sys.exit("sections/basics.yaml is required.")

    order = cfg["section_order"]
    ctx, rendered = {}, []
    print("Loading sections:")
    for name in order:
        data = load_section(name)
        print(f"  {name:<16} {describe(name, data)}")
        if data:
            ctx[name] = clean(data, name if name in PROSE else None)
            rendered.append(name)

    missing = [s for s in order if s not in rendered]
    if missing:
        print(f"  -> not rendered: {', '.join(missing)}")

    tex = ENV.get_template("templates/base.tex.j2").render(
        b=clean(basics),
        sections=rendered,
        headings=cfg.get("headings", {}),
        page=page,
        **ctx,
    )

    out = HERE / args.out
    out.write_text(tex, encoding="utf-8")
    print(f"\nwrote {out.name}  ({len(tex.splitlines())} lines)")

    if args.zip:
        z = out.with_name("overleaf_upload.zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(out, "main.tex")
        print(f"wrote {z.name}  -> Overleaf > New Project > Upload Project")


if __name__ == "__main__":
    main()
