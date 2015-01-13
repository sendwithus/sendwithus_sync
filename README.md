Sendwithus Sync Tool
===================

## Install

```sh
git clone git@github.com:sendwithus/sendwithus_sync.git
```

## Dependencies

```sh
pip install -r requirements.txt
```

## Usage

```sh
sendwithus_sync.py [-h] -a APIKEY [-d DATA] [-e EMAIL] {pull,push,render,send} ...
Sync sendwithus resources to/from local filesystem, renders and sends
templates.
positional arguments:
 {pull,push,render,send}
 commands
 pull process pull templates and snippets
 push process push templates and snippets
 render process render templates
 send process send email
optional arguments:
 -h, --help show this help message and exit
 -a APIKEY, --apikey APIKEY required, used for authentication
 -d DATA, --data DATA optional, required only in conjunction with render command, specifies a file containing data used for template rendering
 -e EMAIL, --email EMAIL optional, required only in conjunction with send command, specifies the email address to which the email will be sent to
```
Note: Please note that this tool supports incremental push. On pull/push 
a new .swu file is created under templates/snippets which holds the last changes 
time stamp. When pushing content the tool checks if each file has modification date 
greater than the .swu file and if it is not - the file is skipped. 
If you need to push the whole content again, please manually delete the corresponding .swu file.

### pull
```sh
usage: sendwithus_sync.py pull [-h] {templates,snippets} [directory]
positional arguments:
 {templates,snippets}
 directory
optional arguments:
 -h, --help show this help message and exit
```
Example:
Pull snippets to local filesystem:
```sh
$ python sendwithus_sync.py pull snippets ./sendwithus
Writing ./sendwithus/snippets/header.html
Writing ./sendwithus/snippets/name again.html
Writing ./sendwithus/snippets/css_sample.html
Writing ./sendwithus/snippets/Footer_Standard.html
Writing ./sendwithus/snippets/api?.html
Writing ./sendwithus/snippets/api? 2.html
```
Pull templates to local filesystem:
```sh
$ python sendwithus_sync.py pull templates ./sendwithus
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

### push
```sh
usage: sendwithus_sync.py push [-h] {templates,snippets} [directory]
positional arguments:
 {templates,snippets}
 directory
optional arguments:
 -h, --help show this help message and exit
```

Push snippets to sendwithus:
```sh
$ python sendwithus_sync.py push snippets ./sendwithus
Updating snippet: api? 2
Updating snippet: api?
Updating snippet: css_sample
Updating snippet: Footer_Standard
Updating snippet: header
Updating snippet: name again
```

Push templates to sendwithus:
```sh
$ python sendwithus_sync.py push templates ./sendwithus
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

### render
The command 'render' returns the rendered template in the system output. The intention of this functionality is to utilize the OS command output redirection feature so instead of printing the rendered template into the console, we are going to redirect it to an html file that can be previewed. For more information about output redirection please refer the examples below and the following articles - Using command redirection operators (Windows), I/O Redirection (Linux).

```sh
usage: sendwithus_sync.py render [-h] [template]
positional arguments:
 template required, specifies path to template version which is to be
 rendered
optional arguments:
 -h, --help show this help message and exit
```
Example:
```sh
$ python sendwithus_sync.py -a <api key> -d .\test\data\data.json render .\src\templates\Template\Version1.html > .\test\output\Version1Email.html
```
### send
```sh
usage: sendwithus_sync.py send [-h] [template]
positional arguments:
 template Required, specifies path to template version which is to be sent. <template_name>/<template_version>.html
optional arguments:
 -h, --help show this help message and exit
```
Example:
```sh
$ python sendwithus_sync.py -a <api key> -d .\test\data\data.json -e email@example.com send .\src\templates\Template\Version1.html
```