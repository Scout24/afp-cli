import sys

from pybuilder.core import use_plugin, init, Author

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin('copy_resources')
use_plugin("filter_resources")
use_plugin('python.cram')

name = 'afp-cli'
summary = 'Command line client for AWS federation proxy api'
authors = [Author('Stefan Neben', "stefan.neben@immobilienscout24.de"),
           Author('Tobias Vollmer', "tobias.vollmer@immobilienscout24.de"),
           Author('Stefan Nordhausen', "stefan.nordhausen@immobilienscout24.de"),
           Author('Enrico Heine', "enrico.heine@immobilienscout24.de"),
           Author('Valentin Haenel', "valentin.haenel@immobilienscout24.de"),
           ]
url = 'https://github.com/ImmobilienScout24/afp-cli'
version = '1.3.1'
description = open("README.rst").read()
license = 'Apache License 2.0'

default_task = ["clean", "analyze", "publish"]


@init
def set_properties(project):
    project.build_depends_on("unittest2")
    project.build_depends_on("mock")
    project.build_depends_on("six")
    project.build_depends_on("bottle")
    # BottleDaemon dependencies
    project.build_depends_on("lockfile")
    project.build_depends_on("python-daemon")
    if sys.version_info[0:2] < (2, 7):
        project.depends_on("ordereddict")
    project.depends_on("yamlreader>=3.0.1")
    project.depends_on("requests")
    project.depends_on("docopt")
    project.set_property('flake8_include_test_sources', True)
    project.set_property('flake8_break_build', True)
    project.set_property('copy_resources_target', '$dir_dist')

    project.set_property("distutils_classifiers", [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        ])

    project.set_property('distutils_console_scripts', ['afp=afp_cli.cli:main'])
    project.set_property('distutils_console_scripts', ['afpv2=afp_cli.cliv2:main'])
    project.set_property('install_dependencies_upgrade', True)
    project.set_property('coverage_exceptions', ['afp_cli.config',
                                                 'afp_cli.cli'])


@init(environments='teamcity')
def set_properties_for_teamcity_builds(project):
    import os
    project.set_property('teamcity_output', True)
    project.version = '%s-%s' % (project.version,
                                 os.environ.get('BUILD_NUMBER', 0))
    project.default_task = ['clean', 'install_build_dependencies', 'publish']
    project.set_property('install_dependencies_index_url',
                         os.environ.get('PYPIPROXY_URL'))
    project.rpm_release = os.environ.get('RPM_RELEASE', 0)
    project.set_property('copy_resources_target', '$dir_dist')
    project.get_property('copy_resources_glob').extend(['setup.cfg'])
    project.get_property('filter_resources_glob').extend(['**/setup.cfg'])
