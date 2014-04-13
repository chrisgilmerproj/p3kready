#! /usr/bin/python

"""
Implemented with Twisted
"""

import argparse
import re

from pip.req import parse_requirements
from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor

PYPI_URL = 'https://pypi.python.org/pypi'
RE_LINE = re.compile(r"(?P<module>\w+)\s*(?P<conditional><=?|>=?|==|!=)\s*(?P<version>(\w|[-.])+)").match


def printError(error):
    print('error', error)


def print_release_data(pkg_data):
    classifier_py3 = 'Programming Language :: Python :: 3'
    classifier_py2 = 'Programming Language :: Python :: 2 :: Only'

    classifiers = str(pkg_data.get('classifiers', None))
    py3_ready = classifier_py3 in classifiers
    py2_only = classifier_py2 in classifiers
    if pkg_data and not py3_ready:
        pkg_data['name']


def main(args):
    req_file = args.file
    requirements = parse_requirements(req_file)
    endlist = [str(pkg.req) for pkg in requirements]
    endlist.sort()

    proxy = Proxy(args.index_url)
    for pkg in endlist:
        m = RE_LINE(str(pkg))
        if m:
            data = m.groupdict()
            name = data['module']
            vers = data['version']

            p = proxy.callRemote('release_data', name, vers)
            p.addCallback(print_release_data)
            p.addErrback(printError)
        else:
            print(str(pkg))
    reactor.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Determine if your requirements are p3k ready')
    parser.add_argument('-f', '--file', help='requirements.txt file location')
    parser.add_argument('-i', '--index-url',
                        default=PYPI_URL, help='PyPI index url to use')
    args = parser.parse_args()
    main(args)
