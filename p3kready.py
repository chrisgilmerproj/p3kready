#!/usr/bin/python

import argparse
import datetime
import logging
import traceback
import urllib.parse
import xmlrpc.client

from pip.req import parse_requirements


PYPI_URL = 'https://pypi.python.org/pypi'
logging.basicConfig()


def get_package_info(client, name):
    """Cribbed directly from https://code.google.com/p/python3wos"""
    release_list = client.package_releases(name, True)

    downloads = 0
    py3 = False
    py2only = False
    url = urllib.parse.urljoin(PYPI_URL, name)
    for release in release_list:
        for i in range(3):
            try:
                urls_metadata_list = client.release_urls(name, release)
                release_metadata = client.release_data(name, release)
                break
            except xmlrpclib.ProtocolError as e:
                # retry 3 times
                strace = traceback.format_exc()
                logging.error("retry %s xmlrpclib: %s" % (i, strace))
        url = release_metadata['package_url']

        # to avoid checking for 3.1, 3.2 etc, lets just str the classifiers
        classifiers = str(release_metadata['classifiers'])
        if 'Programming Language :: Python :: 3' in classifiers:
            py3 = True
        elif 'Programming Language :: Python :: 2 :: Only' in classifiers:
            py2only = True

        for url_metadata in urls_metadata_list:
            downloads += url_metadata['downloads']

    # NOTE: packages with no releases or no url's just throw an exception.
    info = dict(
        py2only=py2only,
        py3=py3,
        downloads=downloads,
        name=name,
        url=url,
        timestamp=datetime.datetime.utcnow().isoformat(),
    )

    return info


def main(args):
    req_file = args.file
    requirements = parse_requirements(req_file)
    client = xmlrpc.client.ServerProxy(args.index_url)
    print("The following requirements are not yet p3k ready:")
    for r in requirements:
        try:
            info = get_package_info(client, r.name)
            if not info['py3']:
                print(info['name'])
        except Exception as e:
            print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Determine if your requirements are p3k ready')
    parser.add_argument('-f', '--file', help='requirements.txt file location')
    parser.add_argument('-i', '--index-url',
                        default=PYPI_URL, help='PyPI index url to use')
    args = parser.parse_args()
    main(args)
