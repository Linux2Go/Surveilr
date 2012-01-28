#!/usr/bin/python
#
#    Surveilr - Log aggregation, analysis and visualisation
#
#    Copyright (C) 2011  Linux2Go
#
#    This program is free software: you can redistribute it and/or
#    modify it under the terms of the GNU Affero General Public License
#    as published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public
#    License along with this program.  If not, see
#    <http://www.gnu.org/licenses/>.
#
from setuptools import setup

def get_install_requires():
    install_requires = []
    with open('tools/pip-requirements.txt', 'r') as fp:
        for l in fp:
            l = l.strip()
            if l.startswith('#'):
                continue
            elif l.startswith('-e'):
                install_requires.append(l[l.index('#egg=')+5:])
            else:
                install_requires.append(l)
    return install_requires

setup(
    name='surveilr',
    version='0.1a1',
    description='Monitoring System evolved',
    author='Soren Hansen',
    license='AGPL',
    author_email='soren@linux2go.dk',
    url='http://surveilr.org/',
    packages=['surveilr'],
    install_requires=get_install_requires(),
    entry_points = {
        'console_scripts': [
            'surveilr-admin = surveilr.admin:main',
        ],
    },
    test_suite='nose.collector',
    install_package_data=True,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Internet :: Log Analysis',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking :: Monitoring',
    ]
)
