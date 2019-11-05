# Resume Generator

A Python program to construct a resume based on data stored in YAML files.

The motivation is to easily build different resumes based on modular data. This allows several forms of a resume to be generated at once (e.g. PDF, text, HTML), specifially when content needs to be tailored for a specific aim. Additionally, different templates can be used in order to create differently formatted versions of a resume from the same content (e.g. regular resume, CV-type resume).

Tailoring of a resume can be accomplished by creating a new folder with only those YAML files having the changed content.

## Usage

### File Structure

       resume.py
       config.ini                   <- configuration file
    +- Publish/                     <- output directory
       +- [publish directories]
       +- ...
    +- Resume Data                  <- resume data files, SOURCE_DIR arg is the
       +- Default/                     name of a folder here
       +- ...
    +- Templates/                   <- templates directory
       +- html/
          default.html              <- Default HTML template
          css/
             style.css
             bootstrap.min.css
             ...
       +- text/
          default.txt               <- Default text template

### Command Line Tool
```
Usage: resume.py build [OPTIONS] SOURCE_DIR

  Generate html, pdf, and text versions of a resume and save them in a
  directory.

  SOURCE_DIR is the name of a folder in the 'Resume Data' folder.

Options:
  --html_template TEXT  Template to use for HTML rendering.
  --text_template TEXT  Template name to use for text rendering.
  --title               Toggle title on/off.
  --help                Show this message and exit.
```

### Resume Data

Data is stored in YAML files within a directory in the `Resume Data` directory. A `Default` directory must exist, which serves as the base set of data. Additional directories are then added which overide the data of Default. Only data that changes needs included in these directories.

Templates currently use the following files and properties:

#### Header.yaml

    name     : <name>
    title    : <title>
    contact info :
        address : <value>
        cell    : <value>
        email   : <value>
        web     : <value>

#### Performance profile.yaml

    <string>

#### Skills.yaml

    <category title> :
      - <skill>
      - <skill>
      - <skill>
    
    (repeat)

#### Experience.yaml

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

#### Education.yaml

    <degree> :
      school : <name>
      date: <date>
      address: <address>
      gpa: <number>
    
    (repeat)

#### Training.yaml

    <title>:
      description : <description>
    
    (repeat)

#### Certifications.yaml

    <Certification name> :
      <property>: <value>
      ...

    (repeat)

#### Patents.yaml

    <Patent name> :
      patent number : <number>
      issued : <date>
      description : <value>


## config.ini

A `config.ini` file may be placed in the top-level directory with the following as valid settings (the pdf options are just those for `pdfkit`):

  - PDF_MARGIN_TOP
  - PDF_MARGIN_BOTTOM
  - PDF_MARGIN_LEFT
  - PDF_MARGIN_RIGHT
    * Set the margins in the pdf file; accepts a string with units (e.g. '0.75in')
  - PDF_PAGE_SIZE
    * 'Letter', 'A4', etc.
  - PDF_DISABLE_EXTERNAL_LINKS
    * Include this and set to 'False' to enable this flag
  - SKILLS_LAYOUT
    * Enter a pipe and comma separated string denoting the columns and order of headers in the "Skills" section. For example:
      `engineering, programming | writing, data analysis | software, fabrication`
    This tells it to create 3 columns with the order of the headings as listed. The headings must match those listed in the `Skills.yaml` file.

## Dependencies

**3rd Party Applications:**

 - wkhtmltopdf (wkhtmltopdf.org)

**Python Packages:**

- Jinja2
- pdfkit
- PyYAML
- click