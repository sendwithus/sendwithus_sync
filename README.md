Sendwithus Sync Tool
===================

## Install
```
git clone git@github.com:sendwithus/sendwithus_sync.git
```

## Dependencies
```
pip install -r requirements
```

## Usage
```
python sendwithus_sync.py [-h] -a APIKEY <command> <resource> [directory]
```

Commands:
- pull
- push

Resources:
- snippets
- templates

### Snippets

Pull to local filesystem:

```
python sendwithus_sync.py pull snippets ./sendwithus
Writing ./sendwithus/snippets/header.html
Writing ./sendwithus/snippets/name again.html
Writing ./sendwithus/snippets/css_sample.html
Writing ./sendwithus/snippets/Footer_Standard.html
Writing ./sendwithus/snippets/api?.html
Writing ./sendwithus/snippets/api? 2.html
```

Push snippets to sendwithus:
```
python sendwithus_sync.py push snippets ./sendwithus
Updating snippet: api? 2
Updating snippet: api?
Updating snippet: css_sample
Updating snippet: Footer_Standard
Updating snippet: header
Updating snippet: name again
```

### Templates

Pull templates to local filesystem:
```
python sendwithus_sync.py pull templates ./sendwithus
Writing ./sendwithus/templates/Sanity Check/New Version.html
Writing ./sendwithus/templates/Sanity Check/New Version.txt
Writing ./sendwithus/templates/Sanity Check/New Version.json
Writing ./sendwithus/templates/_new_template_/a.html
Writing ./sendwithus/templates/_new_template_/a.txt
Writing ./sendwithus/templates/_new_template_/a.json
Writing ./sendwithus/templates/asdf/testing.html
Writing ./sendwithus/templates/asdf/testing.txt
Writing ./sendwithus/templates/asdf/testing.json
Writing ./sendwithus/templates/snippet testing/New Version.html
Writing ./sendwithus/templates/snippet testing/New Version.txt
Writing ./sendwithus/templates/snippet testing/New Version.json
Writing ./sendwithus/templates/Test Welcome Email 2/Version A.html
Writing ./sendwithus/templates/Test Welcome Email 2/Version A.txt
Writing ./sendwithus/templates/Test Welcome Email 2/Version A.json
Writing ./sendwithus/templates/Test Welcome Email 2/Version B.html
Writing ./sendwithus/templates/Test Welcome Email 2/Version B.txt
Writing ./sendwithus/templates/Test Welcome Email 2/Version B.json
```

Push templates to sendwithus:
```
python sendwithus_sync.py push templates ./sendwithus
Processing ./sendwithus/templates/_new_template_/a
  Updating version: a
Processing ./sendwithus/templates/asdf/testing
  Updating version: testing
Processing ./sendwithus/templates/Sanity Check/New Version
  Updating version: New Version
Processing ./sendwithus/templates/snippet testing/New Version
  Updating version: New Version
Processing ./sendwithus/templates/Test Welcome Email 2/Version A
  Updating version: Version A
Processing ./sendwithus/templates/Test Welcome Email 2/Version B
  Updating version: Version B
```
