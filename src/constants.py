"""Record variables used in the implementation.


@created: 11 Mar, 2014

@author: Raju Chinthala, <raju.chinthala@imaginea.com>
"""

# Words that are not considered in the analysis.
STOP_WORDS = frozenset([
    '__main__', 'desc', 'true', 'false', 'service', 'type', 'none', 'to', 'in',
    'up', 'for', 'or', 'not', 'is', 'all', 'date', 'exit', 'and', 'about',
    'yes', 'but', 'from', 'dir', 'use', 'with', 'by', 'juju', 'charm', 'charms',
    'on', 'other', 'home', 'stdout', 'stderr', 'it', 'even', 'as', 'the',
    'sudo', 'of', 'start', 'stop', 'apt-get', 'with', '__init__.py', '{0}',
    '{}', 'out', 'has', 'changed', 'so', 'can', 'could', 'are', 'no', 'hello'
    'download', 'print', 'aptitude', 'install', 'installed', 'installation',
    'en', 'min', 'max', 'user', 'name', 'now', 'null', 'unable', 'started',
    'stopping', 'stopped', 'updating', 'updated', 'update', 'charm-helper-sh',
    'installing', 'cannot', 'data', 'are', 'foo', 'bar', 'changes', 'changed',
    'do', 'does', 'done', 'error', 'exists', 'exist', 'exiting', 'fail',
    'failed', 'failure', 'has', 'helper', 'id', 'include', 'into', 'list',
    'min', 'max', 'modules', 'name', 'must', 'new', 'on', 'pass', 'option',
    'options', 'req', 'required', 'self', 'sh', 'than', 'unable', 'update',
    'updating', 'warning', 'where', 'debug', 'info', 'critical', 'juju-log',
    'add', 'already', 'charm-pre-install', 'charmhelpers', 'check', 'status',
    'running', 'run', 'joined', 'status', 'there', 'according', 'main', 'parse',
    'return', 'returned', 'generate', 'generating', 'dumping', 'dump', 'be',
    'check', 'checking', 'an', 'if', 'else', 'end', 'function', 'args', 'arg1',
    'arg2', 'free', 'this', 'come', 'alter', 'last', 'test', 'testing', 'hot',
    'argument', 'upgrade-charm', 'website-relation-joined', 'charm_dir', 'its',
    'version', 'following', 'init', 'apply', 'applying', 'directory', 'it','db',
    'doing', 'found', 'file', 'overrides', 'remove', 'removing', 'invalid',
    'adding', 'git','input',
    ])

INSTALL = '{0}install{0}'.format(' ')

# Input data location.
PATH = '/home/raju/Work/classification/data/'

# List of characters, if any present, the keywords are ignored.
SPECIAL_CHARS = frozenset([
    '\\', '|', '/', ':', ';', '%', '$', '=',
    ])

PYTHON = 'python'
BASH = 'bash'
SHELL = 'bin/sh'
