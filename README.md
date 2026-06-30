# resumepy

A command-line tool to build a resume from YAML data files and a Jinja2 theme template.

Resume content is stored as a set of YAML files — one per section — in a project folder.
The tool renders them through a chosen theme to produce a single output file (HTML, text, etc.).
Variations of a resume (e.g. targeted for a specific role) are handled by creating a subfolder
containing only the files that differ; everything else falls back to the base folder.

## Installation

With [uv](https://docs.astral.sh/uv/):

```
uv tool install .
```

Or with pip:

```
pip install .
```

## Quickstart

Create a sample resume folder in the current directory:

```
resumepy init
```

This copies the bundled sample YAML files into a new `resume/` folder. Build it:

```
resumepy build resume/
```

Output is written to `dist/resume.html` by default. You can also run the build from
inside the project folder itself:

```
cd resume/
resumepy build .
```

## Usage

### File structure

```
my-resume/                  ← your YAML source folder
  Header.yaml
  Experience.yaml
  Education.yaml
  Skills.yaml
  Performance profile.yaml
  coding/                   ← variant subfolder (only files that differ)
    Header.yaml
    Experience.yaml

dist/                       ← output (created automatically)
  my-resume.html
  my-resume-coding.html     ← variant output
```

### Commands

```
Usage: resumepy [OPTIONS] COMMAND [ARGS]...

Commands:
  build  Build a resume from a folder of YAML files.
  init   Create a sample resume folder in the current directory.
```

#### build

```
Usage: resumepy build [OPTIONS] SOURCE_DIR

  Build a resume from a folder of YAML files.

  SOURCE_DIR is the path to a folder of YAML files. Pass '.' to use the
  current directory.

Options:
  --variant TEXT                    Subfolder of SOURCE_DIR containing
                                    override YAML files.
  --theme TEXT                      Bundled theme name or path to a custom
                                    template file. Default: default.
  --palette [red|nord|grayscale]    Color palette. Default: red.
  --output TEXT                     Output directory. Default: dist.
  --name TEXT                       Output filename base. Defaults to the
                                    source folder name.
  --help                            Show this message and exit.
```

#### init

```
Usage: resumepy init [NAME]

  Create a sample resume folder in the current directory.

  NAME is the folder to create. Default: resume.
```

### Variants

A variant is a subfolder within your source folder containing only the YAML
files that differ from the base. When a variant is specified, its files are
loaded on top of the base, overriding any sections with the same name.

```
my-resume/
  Header.yaml           ← base
  Experience.yaml       ← base
  coding/
    Header.yaml         ← overrides base Header.yaml
    Experience.yaml     ← overrides base Experience.yaml
```

```
resumepy build my-resume/ --variant coding
```

The variant name is automatically appended to the output filename:

```
dist/my-resume-coding.html
```

Use `--name` to override the output filename entirely.

### Themes

Bundled themes are selected by name. The theme's file extension determines
the output file format.

| Theme name    | Output  | Description                    |
|---------------|---------|--------------------------------|
| `default`     | `.html` | Single-column clean layout     |
| `alt1`        | `.html` | Two-column table layout        |
| `default-txt` | `.txt`  | Plain text, 72-character width |

```
resumepy build my-resume/ --theme alt1
```

To use a custom template, pass a path to any Jinja2 template file. The
output extension is taken from the file's own extension:

```
resumepy build my-resume/ --theme ~/templates/my-resume.html
```

### Color palettes

The HTML themes support named color palettes applied via CSS custom properties.

| Palette     | Description                          |
|-------------|--------------------------------------|
| `red`       | Default — crimson accent             |
| `nord`      | Cool blue, based on the Nord theme   |
| `grayscale` | Neutral grayscale                    |

```
resumepy build my-resume/ --theme alt1 --palette nord
```

### Section ordering

By default, sections are rendered in a fixed order built into each theme.
To change the order — or to promote a custom section higher up — add a
`sections` list to `Header.yaml`:

```yaml
name: Jane Smith
contact info:
  ...
sections:
  - Experience
  - Programming & Open Source
  - Skills
  - Education
  - Certifications
```

Section names correspond to YAML filenames with spaces preserved (the tool
normalises them internally). This is most useful in variant `Header.yaml`
files where the target role calls for a different emphasis.

### Custom sections

Any YAML file not matching a known section name is automatically picked up
and rendered as a free-form section at the end of the document. The section
heading is derived from the filename.

For plain text content, write the value directly at the top level of the file:

```yaml
# Programming & Open Source.yaml
Proficient in Python for engineering automation. Creator of bomkit and metk.
```

For richer content — paragraphs, bullet lists, bold text — use a YAML block
scalar (`|`) and write Markdown:

```yaml
# Programming & Open Source.yaml
|
  Proficient in Python for engineering automation.

  - Creator of **bomkit** (BOM-flattening utility, 33 stars/11 forks)
  - Creator of **metk** (weld/bolt/section analysis suite)
```

The Markdown is converted to HTML at render time. This applies to all
free-form sections in the HTML themes; the plain text theme renders the
content as-is.

## YAML schemas

Each section of the resume is a separate YAML file. Only the files relevant
to your content are required; sections not present are simply skipped.

### Header.yaml

```yaml
name     : <name>
title    : <title>
contact info :
  address : <value>
  cell    : <value>
  email   : <value>
  web     : <value>
sections :           # optional — controls section order and visibility
  - Experience
  - Skills
```

### Performance profile.yaml

```yaml
<paragraph of text>
```

### Skills.yaml

```yaml
<category title> :
  - <skill>
  - <skill>

(repeat)
```

### Experience.yaml

```yaml
<company name> :
  location: <location>
  positions :
    <position title> :
      dates : <dates>
  summary : >
    <summary paragraph>
  selected achievements :
    - <item>
    - <item>

(repeat)
```

### Education.yaml

```yaml
<degree> :
  school  : <name>
  date    : <date>
  address : <address>
  gpa     : <gpa>    # optional

(repeat)
```

### Certifications.yaml

```yaml
<certification name> :
  license number : <number>
  state          : <state>
  expiration     : <date>

(repeat)
```

### Training.yaml

```yaml
<title> :
  description : <description>
  date        : <date>

(repeat)
```

### Patents.yaml

```yaml
<patent name> :
  patent number : <number>
  issued        : <date>
  description   : <value>

(repeat)
```

### Custom sections

Any filename not matching one of the above becomes a free-form section.
The file content should be a plain string or a Markdown block scalar (see
[Custom sections](#custom-sections) above).

## Dependencies

- [Jinja2](https://jinja.palletsprojects.com/)
- [PyYAML](https://pyyaml.org/)
- [click](https://click.palletsprojects.com/)
- [mistune](https://mistune.lepture.com/)
