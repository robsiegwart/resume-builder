# Resume Generator

A Python program to construct a resume based on data stored in YAML files.

The motivation is to easily build different resumes based on modular data. This allows several forms of a resume to be generated at once (e.g. PDF, text, HTML), specifially when content needs to be tailored for a specific aim. Additionally, different templates can be used in order to create differently formatted versions of a resume from the same content (e.g. regular resume, CV-type resume).

A default set of resume data is stored in a Default directory. Tailoring of a resume can be accomplished by creating a new folder with only those YAML files having changed content.

## Usage

### File Structure

    resume.py
    config.ini                   (Global configuration file)
    Publish/                     (Default output directory)
    Resume Data/                 (Default resume data files directory)
       Default/                  
          Header.yaml
          Experience.yaml
           ...
          config.ini             (Local configuration file)
    Templates/                   (Default templates directory)
       html/
          default.html           (Default HTML template)
          css/                   (Include any css files)
             style.css
             bootstrap.min.css
             ...
      text/
         default.txt             (Default text template)

### Command Line Tool

Only command available is `build`:

```
Usage: resume.py build [OPTIONS] SOURCE_DIR

  Generate HTML, PDF, and text versions of a resume and save them in a
  directory.

  SOURCE_DIR is the name of a folder in the 'Resume Data' folder.

Options:
  --name TEXT  Specify an alternate filename for published files. Default is
               source_dir.
  --help       Show this message and exit.
```

### Resume Data

Data is stored in YAML files within a directory in the `Resume Data` directory. A `Default` directory must exist, which serves as the base set of data. Additional directories are then added which overide the data of `Default`. Only data that changes needs included in these directories.

A config.ini file may be placed in a resume data directory with options pertaining to PDF generation and template layout. This is considered a local config file. See details below.

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


## Configuration files

### Global

A `config.ini` file placed at the root of the project is used to specify alternate directories for resume data, the templates directory, and the publish directory. These are set with the following parameters:

  - SOURCES_DIR
  - PUBLISH_DIR
  - TEMPLATES_DIR


### Local

A `config.ini` file may be placed in a resume data directory with any of the following as settings:

  - HTML_TEMPLATE
  - TEXT_TEMPLATE
  - PDF_MARGIN_TOP
  - PDF_MARGIN_BOTTOM
  - PDF_MARGIN_LEFT
  - PDF_MARGIN_RIGHT
    * Set the margins in the pdf file; accepts a string with units (e.g. '0.75in')
  - PDF_PAGE_SIZE
    * 'Letter', 'A4', etc.
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