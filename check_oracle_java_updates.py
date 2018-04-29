#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2017 Mohamed El Morabity <melmorabity@fedoraproject.com>
#
# This module is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not,
# see <http://www.gnu.org/licenses/>.


import contextlib
from distutils.version import LooseVersion
import os.path
import re
import subprocess
import urllib2
from urllib2 import HTTPError
from xml.etree.ElementTree import ElementTree

from pynag import Plugins


_JAVA_VERSION_RE = re.compile(
    r'^java version "(?P<version>(?P<major_version>1\.[45678]\.0|[0-9]+?)[_\.].*?)".*?\n'
    r'Java\(TM\) (?:SE Runtime Environment|2 Runtime Environment, Standard Edition).*? '
    r'\(build (?P<build>.+?)\)$', re.MULTILINE
)
_JAVA_UPDATE_URL = 'https://www.java.com/applet/javaLatestVersion.xml'


helper = Plugins.PluginHelper()

# Specify arguments to the plugin
helper.parser.description = 'This plugin checks the installed version of Oracle Java and ' \
                            'compares it to the latest available version.'
helper.parser.add_option('-j', '--java-home', help='Java location')
helper.parser.add_option('-s', '--security-only', help='Ignore non-security updates',
                         action='store_true')
helper.parse_arguments()


# Get current Java version
java_exes = []
if helper.options.java_home is not None:
    java_exes.append(os.path.join(helper.options.java_home, 'jre', 'bin', 'java'))
    java_exes.append(os.path.join(helper.options.java_home, 'bin', 'java'))
# Fallback: get java from current PATH
java_exes.append('java')

for java in java_exes:
    try:
        process = subprocess.Popen([java, '-version'], stdout=None, stderr=subprocess.PIPE)
        output = process.communicate()[1]
        match = _JAVA_VERSION_RE.search(output)
        if match is None:
            continue
        major_version = match.group('major_version')
        version = match.group('version')
        break
    except OSError:
        continue
else:
    helper.status(Plugins.unknown)
    helper.add_summary('No Oracle Java found')
    helper.exit()


try:
    with contextlib.closing(urllib2.urlopen(_JAVA_UPDATE_URL)) as response:
        update_data = ElementTree(file=response)
        major_version_data = update_data.find('./family[@id="{}"]'.format(major_version))
        if major_version_data is None:
            helper.status(Plugins.unknown)
            helper.add_summary(
                'No update status available for Oracle Java {}'.format(major_version)
            )
            helper.exit()

        # Check whether Java version is still supported
        if major_version_data.find('ranges') is not None:
            helper.status(Plugins.critical)
            helper.add_summary(
                'No more public updates available for Oracle Java {}'.format(major_version)
            )
            helper.exit()

        baseline_version = major_version_data.find('baselineVersion').text
        latest_version = major_version_data.find('latestVersion').text

        # Check whether Java version is greater or equal to the latest baseline
        if LooseVersion(baseline_version) > LooseVersion(version):
            helper.status(Plugins.critical)
            helper.add_summary(
                'Oracle Java {} available as a security update'.format(baseline_version)
            )
            helper.exit()

        # Check whether Java is up-to-date
        if not helper.options.security_only and \
           LooseVersion(latest_version) > LooseVersion(version):
            helper.status(Plugins.warning)
            helper.add_summary('Oracle Java {} available'.format(latest_version))
            helper.exit()

        helper.status(Plugins.ok)
        helper.add_summary('Oracle Java {} is up-to-date'.format(version))
        helper.exit()

except HTTPError as e:
    helper.status(Plugins.unknown)
    helper.add_summary(str(e))
    helper.exit()
