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
  entry_points={
    'console_scripts': [
      'nexus_configurator=nexus_configurator.nexus_configurator:main',
    ],
  },
  package_data={'nexus_configurator': ['groovy/*.groovy']}
)
