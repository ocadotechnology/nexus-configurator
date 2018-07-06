from setuptools import setup

setup(
  name='nexus_configurator',
  version='0.2.0',
  description='Manipulate Nexus with Python',
  url='https://github.com/ocadotechnology/nexus-configurator',
  author='Tuskens, stuart-warren',
  install_requires=[
      'requests',
      'pyyaml',
      'jinja2',
  ],
  packages=['nexus_configurator'],
  scripts=['bin/nexus_configurator'],
  package_data={'nexus_configurator': ['groovy/*.groovy']}
)
