#!/usr/bin/python
# encoding: utf-8

import os
import re
import sys

result = sys.argv[1]
raw_url = os.getenv('raw_url')
clean_url = re.sub(r'\?.*', '', raw_url)
sys.stdout.write(result.replace(raw_url, clean_url))
