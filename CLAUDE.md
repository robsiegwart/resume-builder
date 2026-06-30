# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install (editable) with dev dependencies
uv pip install -e ".[dev]"
# or
pip install -e ".[dev]"

# Run tests
pytest

# Run a single test
pytest tests/test_cli.py::test_build_produces_html_by_default

# Run the CLI
resumepy build <source_dir> [--variant <name>] [--theme <name>] [--palette red|nord|grayscale] [--output <dir>] [--name <base>] [--pdf]
resumepy init [<folder-name>]
```

## Architecture

The project is a small CLI tool (`resumepy` entry point → `resumepy.cli:cli`) that renders YAML resume data through Jinja2 templates.

**Data flow:**

1. `cli.py` — Click CLI; validates args, constructs `Resume`, calls `publish()` / `publish_pdf()`
2. `resume.py` — `Resume` class: loads YAML files from `source_dir` (then overlays `variant` subfolder if given), normalises keys to `snake_case`, renders through Jinja2, writes output
3. `palettes.py` — dict of CSS color palettes passed into the template as `palette`
4. `quickstart.py` — copies bundled `sample-data/` YAML files to a new folder for `resumepy init`

**YAML loading (`Resume._load_yaml`):** iterates `*.yaml` in a directory alphabetically; filename stem is normalised (`spaces/hyphens → underscores, lowercase`) to become the template context key (e.g. `Header.yaml` → `context['header']`). Variant files are loaded on top of base files, so they override entire sections.

**Themes:** stored under `resumepy/themes/<name>/<name>.<ext>`. The file extension determines the output format. The Jinja2 `Environment` uses `FileSystemLoader` from the theme directory. A `markdown` filter (via `mistune`) is registered so templates can call `{{ value | markdown }}` to render Markdown to HTML.

**PDF export:** `publish_pdf()` opens the generated HTML file via a `file://` URI in headless Chromium using Playwright — requires `playwright install chromium` to be run once.

## Key conventions

- YAML filenames are not case sensitive, but pre-configured sections must be named identical to the section names in the template. The stem becomes the template context key after replacing spaces/hyphens with underscores.
- `Header.yaml` is special: its `sections` list (if present) controls render order and is also normalised to snake_case keys.
- Custom sections (any filename not matching known section names) are rendered as free-form blocks; their content may be a plain string or a Markdown block scalar.
