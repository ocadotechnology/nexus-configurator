from setuptools import setup
import glob

setup(
  name='nexus_configurator',
  version='0.0.4',
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
  data_files=[('groovy', glob.glob('groovy/*.groovy'))]
)
