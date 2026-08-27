# Bifrost

**Bifrost carries your resume from raw content to finished PDF.**

Each section — summary, skills, experience, projects, education, certifications, volunteering — lives in its own file inside `sections/`. Edit the content, run one script, and Bifrost assembles a single `resume.tex` ready to paste into Overleaf.

One source of truth, multiple output variants. Swap the config to reorder or drop sections for a different role, without touching the content files.

> **Note:** the files in this repo are placeholders. Replace the contents of `sections/` with your own details.

---

## Why

Editing LaTeX directly is miserable when all you want to do is reword a bullet. Bifrost separates **what you say** (YAML and Markdown) from **how it looks** (Jinja2 templates), so day-to-day edits never involve touching LaTeX.

It is also **ATS-safe by default**:

- Standard section headings that parsers recognise
- Type 1 fonts, so `fi` and `ff` ligatures extract as real characters — without this, "finance" can extract as "nance" and the keyword is lost
- Job title before company name, so parsers assign fields correctly
- No tables, text boxes, headers, or footers
- LaTeX special characters (`& % $ # _ { } ~ ^`) escaped automatically

---

## Requirements

```bash
pip install jinja2 pyyaml
```

No local LaTeX install needed — Overleaf compiles the generated `.tex`. To compile locally instead, install a TeX distribution (TeX Live or MacTeX).

---

## Quick start

```bash
git clone https://github.com/saagarnkashyap/Bifrost.git
cd Bifrost
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt   # or: pip install jinja2 pyyaml
python build_resume.py
```

Then on Overleaf: **New Project → Blank Project**, paste `resume.tex` into `main.tex`, compile with **pdfLaTeX**.

Or bundle it:

```bash
python build_resume.py --zip      # -> overleaf_upload.zip
```

and use **New Project → Upload Project**.

---

## Layout

```
bifrost/
  sections/
    basics.yaml           contact header
    summary.md            prose
    skills.yaml
    experience.yaml
    projects.yaml
    education.yaml
    certifications.yaml
    volunteering.md       prose
  templates/
    base.tex.j2           preamble, header, section includes
    summary.tex.j2        one partial per section
    skills.tex.j2
    experience.tex.j2
    projects.tex.j2
    education.tex.j2
    certifications.tex.j2
    volunteering.tex.j2
  config.yaml             section order, headings, page settings
  build_resume.py
  requirements.txt
```

`summary` and `volunteering` are single paragraphs, so they are plain `.md` files rather than YAML — no block scalars, no indentation to mind.

---

## Usage

| Command | Result |
|---|---|
| `python build_resume.py` | Build `resume.tex` using `config.yaml` |
| `python build_resume.py --fontsize 10pt --margin 0.45in` | Squeeze onto one page |
| `python build_resume.py --config config.alt.yaml --out resume_alt.tex` | Build a variant |
| `python build_resume.py --zip` | Also produce `overleaf_upload.zip` |

Every run prints an entry count per section:

```
Loading sections:
  summary          54 words
  skills           5 entries
  experience       2 entries
  ...
```

A `MISSING` or a count of `0` means a file is absent or misnamed — catch it here, not after you've exported the PDF.

---

## Content format

Replace these placeholders with your own content.

### `sections/basics.yaml`

```yaml
name: YOUR NAME
location: City, Country
phone: "+00 0000000000"
email: you@example.com
links:
  - label: linkedin.com/in/yourhandle
    url: https://www.linkedin.com/in/yourhandle
  - label: github.com/yourhandle
    url: https://github.com/yourhandle
```

### `sections/summary.md`

```markdown
One paragraph describing what you do, the tools you use, and the kind of outcome
you deliver. Plain text — no YAML syntax needed.
```

### `sections/experience.yaml`

```yaml
- role: "Your Job Title"
  company: "Company Name"
  location: "City, Country"
  start: "January 2025"
  end: "Present"
  bullets:
    - "Did the thing, using these tools, producing this measurable outcome."
    - "Second achievement, ideally with a number attached."

- role: "Earlier Job Title"
  company: "Previous Company"
  location: ""
  start: "June 2024"
  end: "December 2024"
  bullets:
    - "What you owned and what changed as a result."
```

### `sections/projects.yaml`

```yaml
- name: "Project Name"
  stack: "Python, Library, Framework"
  url: "https://example.com/project"
  bullets:
    - "What it does and who it is for."
    - "Notable feature or technical detail."

- name: "Another Project"
  stack: "Tool, Tool, Tool"
  url: ""
  bullets:
    - "Leave url empty to omit the link."
```

### `sections/skills.yaml`

```yaml
- group: Category One
  items: [Skill, Skill, Skill]
- group: Category Two
  items: [Skill, Skill, Skill]
```

### `sections/education.yaml`

```yaml
- degree: "Degree, Field of Study"
  institution: "Institution Name"
  start: "2021"
  end: "2025"
  detail: "GPA or honours"
```

### `sections/certifications.yaml`

```yaml
- name: "Certification Name"
  issuer: "Issuing Body"
```

### `sections/volunteering.md`

```markdown
One paragraph covering leadership roles, volunteering, or community work.
```

---

## Customising

**Reorder or drop a section** — edit `section_order` in `config.yaml`. Removing a name skips that section entirely; the content file stays put for later.

**Rename a heading** — edit the `headings` map in `config.yaml`.

**Add a new section** — three steps: add `sections/<name>.yaml`, add `templates/<name>.tex.j2`, add the name to `section_order` and `headings`. No Python changes needed.

**Role variants** — copy `config.yaml` to `config.<role>.yaml`, adjust its `section_order`, then build with `--config`. Section files are shared across variants, so a fixed typo propagates everywhere.

---

## Fitting one page

In rough order of what to reach for first:

1. `page.section_spacing` in `config.yaml` — the gap above each heading. Cheapest win.
2. `page.compact_certifications: true` — one line instead of a bullet list.
3. `--fontsize 10pt`
4. `--margin 0.45in`
5. Drop a section from `section_order`.

---

## Template syntax

Jinja2 with LaTeX-safe delimiters, since the defaults collide with LaTeX braces:

| Purpose | Syntax |
|---|---|
| Value | `<< name >>` |
| Logic | `%% for` / `%% if` / `%% endfor` at the start of a line |
| Block | `<% ... %>` |
| Comment | `<# ... #>` |

The `%%` directives **must** begin a line. If a template's line breaks are lost — a common copy-paste casualty — Jinja stops recognising them and you get errors like `'l' is undefined`.

URLs, emails, and phone numbers skip escaping; everything else is escaped automatically. Any field whose key contains `url`, `link`, `email`, or `phone` is treated as raw.

---

## Troubleshooting

**`summary MISSING`** — the file is `sections/summary.md`, not `.yaml`. On Windows, Notepad silently appends `.txt`, giving `summary.md.txt`. Enable **View → File name extensions** in Explorer and check.

**`'l' is undefined`, traceback shows the whole template as line 1** — `base.tex.j2` lost its line breaks. Re-save it with proper newlines.

**A section renders empty** — check the entry count printed at build time, then verify the YAML indentation.

**Overleaf can't find a package** — Bifrost uses only `geometry`, `fontenc`, `lmodern`, and `hyperref`, all standard. If you added packages, confirm they exist in Overleaf's TeX Live.

**PDF text extracts with missing letters** — confirm `\usepackage{lmodern}` and `\input{glyphtounicode}` survived in the preamble.

---

## Submitting your resume

Export PDF from Overleaf unless the application portal specifically asks for `.docx`. Before sending, open the PDF and select-all-copy into a text editor — what you see pasted is roughly what an ATS parses.

---

## Roadmap

- GitHub Action to render YAML → LaTeX → PDF and attach it to releases
- Automatic `overleaf_upload.zip` on each tagged release
- Additional template themes

---

## Contributing

Issues and PRs welcome — bug reports, feature requests, or new templates.

When reporting a LaTeX compile issue, include a minimal YAML example, the template used, and the full error log.

---

## License

MIT — see LICENSE.

---

## Author

[saagarnkashyap](https://github.com/saagarnkashyap)
