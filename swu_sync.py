import argparse
import json
import os

import sendwithus


DESCRIPTION = 'Sync sendwithus resources to/from local filesystem.'

CMD_COMMANDS = ['pull', 'push']
CMD_RESOURCES = ['templates', 'snippets']


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


def push_snippets(swu, directory):
    snippets = swu.snippets().json()

    snippet_dir = os.path.join(directory, 'snippets')
    snippet_files = os.listdir(snippet_dir)
    for snippet_file in snippet_files:
        name = '.'.join(snippet_file.split('.')[:-1])

        path = os.path.join(snippet_dir, snippet_file)
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


def push_templates(swu, directory):
    templates = swu.templates().json()

    templates_dir = os.path.join(directory, 'templates')
    template_names = os.listdir(templates_dir)
    for template_name in template_names:
        version_names = os.listdir(os.path.join(templates_dir, template_name))
        version_names = list(set([os.path.splitext(p)[0] for p in version_names]))

        for version_name in version_names:
            path = os.path.join(templates_dir, template_name, version_name)

            print 'Processing {}'.format(path)

            # HTML?
            html = _read_file('{}.html'.format(path), '')
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


def main():
    global swu

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-a', '--apikey', type=str, required=True)
    parser.add_argument('command', choices=CMD_COMMANDS)
    parser.add_argument('resource', choices=CMD_RESOURCES)
    parser.add_argument('directory', nargs='?', default='.')

    args = parser.parse_args()
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
        func = func_map[args.command][args.resource]
    except KeyError:
        print 'Unknown Command: {} {}'.format(args.command, args.resource)
    else:
        func(swu, args.directory)


if __name__ == "__main__":
    main()
