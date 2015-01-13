import argparse
import json
import os
import datetime
import sendwithus
import json


DESCRIPTION = 'Sync sendwithus resources to/from local filesystem, renders and sends templates.'

CMD_RESOURCES = ['templates', 'snippets']

def listdir_nohiddenfiles(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

def touch(fname):
    open(fname, 'a').close()
    os.utime(fname, None)

def _read_file(path, default=None):
    if not os.path.exists(path):
        if default:
            return default

    with open(path, 'r') as f:
        content = f.read()
    return content


def _write_file(path, content):
    print 'Writing {}'.format(path)

    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    with open(path, 'w') as f:
        f.write(content.encode('utf-8'))


def pull_snippets(swu, directory):
    snippets = swu.snippets().json()
    for snippet in snippets:
        path = os.path.join(directory, 'snippets', '{}.html'.format(snippet['name']))
        _write_file(path, snippet['body'])
    touch(os.path.join(directory, 'snippets', '.swu'))


def push_snippets(swu, directory):
    updated = False	
    snippets = swu.snippets().json()
    snippet_dir = os.path.join(directory, 'snippets')
    if os.path.exists(os.path.join(snippet_dir, '.swu')):
        lastpush =  os.path.getmtime(os.path.join(snippet_dir, '.swu'))
    else:
        lastpush = 0
        
    for root, subFolders, files in os.walk(snippet_dir):
        for snippet_file in files:
            path = os.path.join(root, snippet_file)
            if os.path.getmtime(path) > lastpush:
                path = os.path.join(root, snippet_file)
                if os.path.realpath(root) == os.path.realpath(snippet_dir):
                    name = '.'.join(snippet_file.split('.')[:-1])
                else:
                    name = '.'.join(path[path.find(snippet_dir) + len(snippet_dir) + 1:].split('.')[:-1]).replace('\\', '/')

                body = _read_file(path)

                # Does snippet exists?
                for snippet in snippets:
                    if snippet['name'] == name:
                        print 'Updating snippet: {}'.format(name)
                        swu.update_snippet(snippet['id'], name, body)
                        break
                else:
                    print 'Creating snippet: {}'.format(name)
                    swu.create_snippet(name, body)
                updated = True

    if not updated:
        print "There are no snippets that has been modified since the last push."
    touch(os.path.join(snippet_dir, '.swu'))


def pull_templates(swu, directory):
    templates = swu.templates().json()
    for template in templates:
        for version in template['versions']:
            raw_version = swu.get_template(template['id'], version=version['id']).json()

            path = os.path.join(directory, 'templates', template['name'], version['name'])
            _write_file('{}.html'.format(path), raw_version['html'])
            _write_file('{}.txt'.format(path), raw_version['text'])

            meta = {
                'subject': raw_version['subject']
            }
            _write_file('{}.json'.format(path), json.dumps(meta))
    touch(os.path.join(directory, 'templates', '.swu'))


def push_templates(swu, directory):
    updated = False	
    templates = swu.templates().json()	
    templates_dir = os.path.join(directory, 'templates')

    if os.path.exists(os.path.join(templates_dir, '.swu')):
        lastpush =  os.path.getmtime(os.path.join(templates_dir, '.swu'))
    else:
        lastpush = 0

    template_names = listdir_nohiddenfiles(templates_dir)
    for template_name in template_names:
        version_names = os.listdir(os.path.join(templates_dir, template_name))
        version_names = list(set([os.path.splitext(p)[0] for p in version_names]))

        for version_name in version_names:
            path = os.path.join(templates_dir, template_name, version_name)

            if (os.path.exists('{}.html'.format(path)) and os.path.getmtime('{}.html'.format(path)) > lastpush) or (os.path.exists('{}.txt'.format(path)) and os.path.getmtime('{}.txt'.format(path)) > lastpush) or (os.path.exists('{}.json'.format(path)) and os.path.getmtime('{}.json'.format(path)) > lastpush) :
                print 'Processing {}'.format(path)
                # HTML?
                html = _read_file('{}.html'.format(path), '')
                if not os.path.exists('{}.txt'.format(path)):
                    _write_file('{}.txt'.format(path), 'Text version')
                text = _read_file('{}.txt'.format(path), '')
                meta = json.loads(_read_file('{}.json'.format(path), '{}'))

                template_id = None
                version_id = None

                for template in templates:
                    if template['name'] == template_name:
                        # Template exists
                        template_id = template['id']
                        for version in template['versions']:
                            if version['name'] == version_name:
                                version_id = version['id']

                if not template_id:
                    print '  Creating template: {}'.format(template_name)

                    new_template = swu.create_template(
                        name=template_name,
                        subject='placeholder',
                        html='<html><head></head><body>placeholder</body></html>',
                        text='placeholder'
                    ).json()
                    new_template = swu.get_template(new_template['id']).json()
                    templates.append(new_template)

                    template_id = new_template['id']
                    version_id = new_template['versions'][0]['id']

                if not version_id:
                    print '  Creating version: {}'.format(version_name)
                    swu.create_new_version(
                        name=version_name,
                        subject=meta.get('subject', ''),
                        text=text,
                        html=html,
                        template_id=template_id
                    )
                else:
                    print '  Updating version: {}'.format(version_name)
                    swu.update_template_version(
                        name=version_name,
                        subject=meta.get('subject', ''),
                        template_id=template_id,
                        version_id=version_id,
                        text=text,
                        html=html
                    )
                updated = True
    if not updated:
        print "There are no templates that has been modified since the last push."
    touch(os.path.join(templates_dir, '.swu'))
    
def get_template_info_by_path(swu, template_path):
    path_elements_list = os.path.normpath(template_path).split(os.sep)
    version_name = os.path.splitext(os.path.basename(path_elements_list[-1]))[0]
    template_name = path_elements_list[-2]
    templates = swu.templates().json()
    template_id = None
    version_id = None
    for template in templates:
                    if template["name"] == template_name:
                        template_id = template["id"]
                        for version in template["versions"]:
                            if version["name"] == version_name:
                                version_id = version["id"]
                                break
                        break       
    return json.dumps(dict(template_name=template_name, template_id=template_id, version_name=version_name, version_id = version_id))
    
def render_template(swu, data_file, template):
        if not data_file:
            print 'No source data provided.'
        elif not template:
            print 'No template provided, please provide a valid template to be rendered'
        else:
            path_elements_list = os.path.normpath(template).split(os.sep)
            if len(path_elements_list) > 2:
                version_name = os.path.splitext(os.path.basename(path_elements_list[-1]))[0]
                template_name = path_elements_list[-2]
                if os.path.exists(data_file):
                    data = _read_file(data_file)
                    template_info = json.loads(get_template_info_by_path(swu, template))
                    
                    render_result = swu.render(template_info['template_id'], json.loads(data), template_info['version_id'], template_info['version_name'])
                    print render_result.json()['html'].encode("utf-8")
                else:
                    print 'File {} not found.'.format(os.path.abspath(data_file))
            else:
                print 'Invalid template name and version provided.'
                
def send_mail(swu, data_file, email, template):
         if not data_file:
            print 'No source data provided.'
         elif not email:
            print 'No recipient provided, please provide a valid email'
         elif not template:
            print 'No template provided, please provide a valid template to be sent'
         else:
            path_elements_list = os.path.normpath(template).split(os.sep)
            if len(path_elements_list) > 2:
                version_name = os.path.splitext(os.path.basename(path_elements_list[-1]))[0]
                template_name = path_elements_list[-2]
                if os.path.exists(data_file):
                    data = _read_file(data_file)
                    template_info = json.loads(get_template_info_by_path(swu, template))
                    recipient = json.dumps(dict(address=email))   
                    render_result = swu.send(template_info['template_id'], json.loads(recipient), json.loads(data), None, None, None, None, None, template_info['version_name'])
                    try:
                        response = render_result.json();
                        if response['success']:
                            print 'An email is successfully sent to {}. Template name: \'{}\', version name: \'{}\''.format(email, template_name, version_name)
                    except:
                        print 'An error occurred while sending an email - {}'.format(render_result.content)
                else:
                    print 'File {} not found.'.format(os.path.abspath(data_file))
            else:
                 print 'Invalid template name and version provided.'
def main():
    main_parser = argparse.ArgumentParser(description=DESCRIPTION)
    main_parser.add_argument('-a', '--apikey', type=str, required=True, help="required, used for authentication")
    main_parser.add_argument('-d', '--data', type=str, required=False, help="optional, required only in conjunction with render command, specifies a file containing data used for template rendering")
    main_parser.add_argument('-e', '--email', type=str, required=False, help="optional, required only in conjunction with send command, specifies the email address to which the email will be sent to")

    subparsers = main_parser.add_subparsers(help='commands', dest='command')
    
    pull_parser = subparsers.add_parser('pull', help='process pull templates and snippets')
    pull_parser.add_argument('resource', choices=CMD_RESOURCES)
    pull_parser.add_argument('directory', nargs='?', default='.')
    
    push_parser = subparsers.add_parser('push', help='process push templates and snippets')
    push_parser.add_argument('resource', choices=CMD_RESOURCES)
    push_parser.add_argument('directory', nargs='?', default='.')
    
    render_parser = subparsers.add_parser('render', help='process render templates')
    render_parser.add_argument('template', nargs='?', help="Required, specifies path to template version which is to be rendered. <template_name>/<template_version>.html")
    
    send_parser = subparsers.add_parser('send', help='process send email')
    send_parser.add_argument('template', nargs='?', help="Required, specifies path to template version which is to be sent. <template_name>/<template_version>.html")

    args = main_parser.parse_args()
    swu = sendwithus.api(args.apikey)

    func_map = {
        'pull': {
            'snippets': pull_snippets,
            'templates': pull_templates
        },
        'push': {
            'snippets': push_snippets,
            'templates': push_templates
        }
    }

    try:
        if args.command == 'render':
            render_template(swu, args.data, args.template)
        elif args.command == 'send':
            send_mail(swu, args.data, args.email, args.template)
        else:
            func = func_map[args.command][args.resource]
            func(swu, args.directory)
    except KeyError:
        print 'Unknown Command: {} {}'.format(args.command, args.resource)

if __name__ == "__main__":
    main()