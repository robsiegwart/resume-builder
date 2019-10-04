# Resume Generator

A Python program to construct a resume based on data stored in YAML files.

The motivation is to separate data from presentation in order to more quickly generate different forms of a resume based on the desired data to be included. Additionally, different templates can be used in order to create differently formatted versions of a resume from the same set of data.

## Usage

### File Structure

       resume.py                           (program)
       [Resume.py]                         (run file)
    +- Publish                             (output directory)
         +- [publish directories]
         +- ...
    +- Resume Data                         (resume data files)
         +- Default
         +- ...                            (additional data directories)

### Resume Data

Data is stored in YAML files within a directory in the `Resume Data` directory. A `Default` directory must exist, which serves as the base set of data. Additional directories are then added which overide the data of Default. Only data that changes needs included in these directories.

Templates currently use the following files and properties:

#### Certifications.yaml

    Certifications :
      <Cert> :
        <property>: <value>
        <property>: <value>

#### Education.yaml

    Education:
      degree : <degree>
      school : <name>
      date: <date>
      address: <address>

#### Experience.yaml

    Experience :
      <company 1 name> :
        location: <location>
        positions :
          <position name> :
            dates : <dates>
          <position name> :
            dates : <dates>
        summary : >
          <summary paragraph>
        selected achievements :
          - <item>
          - <item>
          - ...
      <company 2 name> :
        location : <location>
        positions :
          <position name> :
            dates : <dates>
        summary : >
          <summary paragraph>

#### Header.yaml

    name     : <name>
    title    : <title>
    contact info :
        address : <value>
        cell    : <value>
        email   : <value>
        web     : <value>

#### Patents.yaml

    Patents :
      <Patent name> :
        patent number : <number>
        issued : <date>
        description : <value>

#### Performance profile.yaml

    Performance profile : >
        <paragraph>

#### Skills.yaml

    Skills :
      <category header> :
        - <skill>
        - <skill>
        - <skill>
      <category header> :
        - <skill>
        - <skill>

#### Training.yaml

    Training :
      <title>:
        description : <description>
      <title>:
        description : <description>

## Installation

### 3rd Party Applications

`wkhtmltopdf` (wkhtmltopdf.org)

### Python Packages

- Jinja2
- pdfkit
- PyYAML

## Example

### Resume Data

### Build File

    from resume import build
    
    options = {
        template = '',
        source_dir = ''
    }
    
    build(name[, options])      # options default to 'default'
