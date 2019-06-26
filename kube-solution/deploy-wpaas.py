#! /usr/bin/env python3
import argparse
import base64
import contextlib
from jinja2 import Environment, FileSystemLoader
import os
import random
import string
import subprocess
import tempfile
import yaml

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(THIS_DIR, 'templates')
def gen_password(size=12):
    chars = string.ascii_letters + string.digits
    password = ''.join(random.choice(chars) for _ in range(size))
    return base64.b64encode(password.encode()).decode()

def read_manifests(org, size=2):
    j2_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR),
                            trim_blocks=True)
    context = {
        'org': org,
        'size': size,
        'wp_dbname': base64.b64encode((org + 'db').encode()).decode(),
        'wp_dbuser': base64.b64encode((org + 'user').encode()).decode(),
        'root_pass': gen_password(),
        'wp_dbpass': gen_password()
    }
    ns_manifest = j2_env.get_template('namespace.yaml.j2').render(**context)
    db_manifest = j2_env.get_template('mysql.yaml.j2').render(**context)
    wp_manifest = j2_env.get_template('wordpress.yaml.j2').render(**context)
    return ns_manifest + '\n' + db_manifest + '\n' + wp_manifest

@contextlib.contextmanager
def tmpfile():
    _, filepath = tempfile.mkstemp()
    try:
        yield filepath
    finally:
        os.remove(filepath)


parser = argparse.ArgumentParser(description='Deploy WPaaS Instances')
parser.add_argument('org', help='Organization name')
parser.add_argument('-s', '--size', type=int, default=2,
    help='Number of wordpress instances')
parser.add_argument('--dry-run', action='store_true')

args = parser.parse_args()
manifest = read_manifests(args.org, args.size)
if args.dry_run:
    print(manifest)
else:
    with tmpfile() as filepath:
        with open(filepath, 'w') as fp:
            fp.write(manifest)
        subprocess.run(['kubectl', 'apply', '-f', filepath])
