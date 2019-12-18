# encoding: utf-8

import sys
import os
import subprocess
import re
import urllib
import json
from workflow import Workflow

# Applescript stuff from Dr. Drang: https://leancrew.com/all-this/2013/03/combining-python-and-applescripturl/


def asrun(ascript):
    "Run the given AppleScript and return the standard output and error."

    osa = subprocess.Popen(['osascript', '-'],
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    return osa.communicate(ascript)[0]


def asquote(astr):
    "Return the AppleScript equivalent of the given string."

    astr = astr.replace('"', '" & quote & "')
    return '"{}"'.format(astr)


def get_title():
    # only get the window title if frontmost app is in the list of browsers specified
    browsers = os.environ['BROWSERS']
    ascript = '''
    tell application "System Events" to set frontApp to name of first process whose frontmost is true
    if frontApp is in {0} then
        tell application frontApp to set tabTitle to name of front window
    else
        set tabTitle to ""
    end if
    return tabTitle'''.format(asquote(browsers))
    return asrun(ascript).strip()


def clean_url(url):
    return re.sub(r'(^.*/(?:dp|gp/product)/([^/?]+)).*$', r'\1', url)


def main(wf):
    title = wf.decode(get_title())
    url = wf.decode(wf.args[0]) if len(wf.args) else None
    if os.environ.get('CLEAN_AMAZON') == 'true':
        url = clean_url(url)
    custom_actions = os.environ.get('CUSTOM_ACTIONS', '')
    if custom_actions:
        actions = json.loads(custom_actions)
    else:
        config = wf.workflowfile('default_actions.json')
        with open(config) as f:
            actions = json.load(f)
    for action in actions:
        # quote title if url is to be opened
        if action.get('encode', False):
            formatted_title = urllib.quote(title.encode('utf-8'))
        else:
            formatted_title = title
        formatted = action['output'].format(
            title=formatted_title, url=url)
        # use the formatted string as subtitle if it's not specified in the json
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
