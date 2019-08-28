# Resume Generator

## Requirements.txt
```
Jinja2==2.10
MarkupSafe==1.1.0
pdfkit==0.6.1
PyYAML==3.13
```

## File Structure
```
 - resume.py
 - Publish\
     |- (publish 1)\
     |- (publish 2)\
 - python_env\
 - Resume Data\
     |- Default\
     |- (resume 1)\
     |- (resume 2)\
 - Resume1.py
```

## Resume1.py
```
from resume import build

options = {
    template = '',
    source_dir = ''
}

build(name[, options])      # options default to 'default' 
```

## Run
    python Resume1.py

## Resume Data
Templates currently use the following files and properties:

### Header.yaml
 - name
 - address
 - cell
 - email
 - web   
 - title


### Performance profile.yaml
 - (string)

### Skills.yaml
 category : 
    - list of skills ...

### Experience
 