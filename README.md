# resumepy

A Python program to construct a resume based on data stored in YAML files.

The motivation is to easily build different resumes based on modular data. This
allows several forms of a resume to be generated at once (e.g. PDF, text, HTML),
specifially when content needs to be tailored for a specific aim. Additionally,
different templates can be used in order to create differently formatted
versions of a resume from the same content (e.g. regular resume, CV-type resume).

A default set of resume data is stored in the `Default` directory. Tailoring of
a resume can be accomplished by creating a new folder with only those YAML files
having changed content.

## Quickstart

After downloading and installing (i.e. `pip install .`), issuing the
initialization command:

`resumepy init`

will copy the included sample data into the current working directory. This will
import the folders `Sample Data` and `Sample Templates` and a global `config.ini`
file (only if they don't already exist).

## Usage

### File Structure

    Publish/                     (Output directory)
    Resume Data/                 (Store YAML files in subdirectories here)
       Default/                  
          Header.yaml
          Experience.yaml
           ...
          config.ini             (Local configuration file)
    Templates/                   (Templates directory)
       html/
          default.html           (Default HTML template)
      text/
         default.txt             (Default text template)

### Command Line Tool

```
Usage: resumepy [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  build  Generate HTML, PDF, and text versions of a resume and save them in...
  init   Scaffold a basic file structure in the current directory.
```

```
Usage: resumepy build [OPTIONS] SOURCE_DIR

  Generate HTML, PDF, and text versions of a resume and save them in a
  directory.

Options:
  --name TEXT         Specify an alternate filename for published files.
                      Default is source_dir.

  --config TEXT       Specify a config group within local config.ini
  --overwrite         Overwrite output files.
  --html / --no-html  Create an html version. Default is true.
  --text / --no-text  Create a text version. Default is true.
  --pdf / --no-pdf    Create a pdf version. Default is true. (HTML is also
                      enabled.)

  --help              Show this message and exit.
```

### Resume Data

Data is stored in YAML files within a directory (e.g. `Resume Data`). A
`Default` directory must exist within this directory, which serves as the base
set of data. Additional directories are then added which overide the data of
`Default`. Only data that changes needs included in these directories. Enter
the name of this folder as the argument to `build` to specify which set of data
to use in creating the resume.

A `config.ini` file may be placed either at the root level of the project or
within a specific resume data directory with any options to override the default
options. Local config files within a resume data folder take highest priority.
Various options for a config file are listed in the sample config.ini that is
imported when issuing `resumepy init`.

Templates currently use the following files and properties:

- [Certifications.yaml](#Certifications)
- [Education.yaml](#Education)
- [Experience.yaml](#Experience)
- [Header.yaml](#Header)
- [Patents.yaml](#Patents)
- [Performance profile.yaml](#Performance_profile)
- [Skills.yaml](#Skills)
- [Training.yaml](#Training)


#### <a id="Header"></a>Header.yaml

    name     : <name>
    title    : <title>
    contact info :
        address : <value>
        cell    : <value>
        email   : <value>
        web     : <value>

#### <a id="Performance_profile"></a>Performance profile.yaml

    <string>

#### <a id="Skills"></a>Skills.yaml

    <category title> :
      - <skill>
      - <skill>
      - <skill>
    
    (repeat)

#### <a id="Experience"></a>Experience.yaml

    <company 1 name> :
      location: <location>
      positions :
        <position 1 name> :
          dates : <dates>
        <position 2 name> :
          dates : <dates>
      summary : >
        <summary paragraph>
      selected achievements :
        - <item>
        - <item>
        - ...
    
    (repeat)

#### <a id="Education"></a>Education.yaml

    <degree> :
      school : <name>
      date: <date>
      address: <address>
      gpa: <number>
    
    (repeat)

#### <a id="Training"></a>Training.yaml

    <title>:
      description : <description>
    
    (repeat)

#### <a id="Certifications"></a>Certifications.yaml

    <Certification name> :
      <property>: <value>
      ...

    (repeat)

#### <a id="Patents"></a>Patents.yaml

    <Patent name> :
      patent number : <number>
      issued : <date>
      description : <value>


## Configuration files

### Global

A `config.ini` file placed at the root of the project is used to specify
alternate directories for resume data, the templates directory, and the
publish directory. These are set with the following parameters and their
defaults:

  - TEMPLATES_DIR (Templates)
  - SOURCES_DIR (Resume Data)
  - PUBLISH_DIR (Publish)
  - HTML_TEMPLATE (default)
  - TEXT_TEMPLATE (default)
  - PDF_MARGIN_TOP (0.5in)
  - PDF_MARGIN_RIGHT (0.5in)
  - PDF_MARGIN_BOTTOM (0.5in)
  - PDF_MARGIN_LEFT (0.5in)
  - PDF_PAGE_SIZE (Letter)
  - PDF_DISABLE_EXTERNAL_LINKS ("")
  - TITLE ("")


### Local

A `config.ini` file may be placed in a resume data directory with any of the
global settings or any from wkhtmltopdf. wkhtmltopdf settings must be prefixed
with 'PDF_'. Additionally a SKILLS_LAYOUT setting can be used to layout the
order of groups in the Skills section.

  - PDF_MARGIN_RIGHT, PDF_MARGIN_LEFT, ...
    * Set the margins in the pdf file; accepts a string with units (e.g. '0.75in')
  - PDF_PAGE_SIZE
    * 'Letter', 'A4', etc.
  - SKILLS_LAYOUT
    * Enter a pipe and comma separated string denoting the columns and order of
      headers in the "Skills" section. For example:
         `engineering, programming | writing, data analysis | software, fabrication`
      This tells it to create 3 columns with the order of the headings as listed.
      The headings must match those listed in the `Skills.yaml` file.


## Dependencies

**3rd Party Applications:**

 - wkhtmltopdf (wkhtmltopdf.org)

**Python Packages:**

- Jinja2
- pdfkit
- PyYAML
- click