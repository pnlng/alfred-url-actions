# encoding: utf-8

import sys
import os
import subprocess
import re
import urllib
import json
from workflow import Workflow

# Applescript stuff from Dr. Drang: https://leancrew.com/all-this/2013/03/combining-python-and-applescript/


def asrun(ascript):
    "Run the given AppleScript and return the standard output and error."

    osa = subprocess.Popen(['osascript', '-l', 'JavaScript', '-'],
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    return osa.communicate(ascript)[0]


def asquote(astr):
    "Return the AppleScript equivalent of the given string."

    astr = astr.replace('"', '" & quote & "')
    return '"{}"'.format(astr)


def get_app_id():
    ascript = '''
    Application('System Events').applicationProcesses.where(
        { frontmost: true }).bundleIdentifier()[0]
    '''
    return asrun(ascript).strip()


def get_title(app_id):
    ascript = '''
    Application('{}').windows[0].name() '''.format(app_id)
    title = asrun(ascript).strip()
    return title


def clean_url(url):
    return re.sub(r'(^.*/(?:dp|gp/product)/([^/?]+)).*$', r'\1', url)


def main(wf):
    app_id = get_app_id()
    title = wf.decode(get_title(app_id))
    url = wf.decode(wf.args[0]) if len(wf.args) else None
    clean_amazon = os.environ.get('CLEAN_AMAZON')
    if clean_amazon and clean_amazon.lower() == 'true':
        url = clean_url(url)
    custom_actions_file = os.environ.get('CUSTOM_ACTIONS_FILE', '')
    custom_actions = os.environ.get('CUSTOM_ACTIONS', '')
    if custom_actions_file:
        custom_file_path = wf.datafile(custom_actions_file)
        if os.path.isfile(custom_file_path):
            with open(custom_file_path, "r") as f:
                try:
                    actions = json.load(f)
                except ValueError:
                    raise ValueError(
                        '"{}" is malformed.'.format(custom_actions_file))
        else:
            raise ValueError(
                '"{}" not in workflow data directory. Run "urlact" to show the folder.'.format(custom_actions_file))
    elif custom_actions:
        try:
            actions = json.loads(custom_actions)
        except ValueError:
            raise ValueError('The value of "CUSTOM_ACTIONS" is malformed.')
    else:
        config = wf.workflowfile('default_actions.json')
        with open(config) as f:
            actions = json.load(f)
    for action in actions:
        # Quote title if url is to be opened
        if action.get('encode', False):
            formatted_title = urllib.quote(title.encode('utf-8'))
        else:
            formatted_title = title
        formatted = action['output'].format(
            title=formatted_title, url=url)
        # Use the formatted string as subtitle if it's not specified in the json
        subtitle = action.get('action_subtitle', formatted)
        wf.add_item(title=action['action_title'],
                    subtitle=subtitle,
                    arg=formatted,
                    valid=True)
    wf.send_feedback()
    return 0


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
