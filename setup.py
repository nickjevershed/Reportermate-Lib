import os
from setuptools import setup
with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(name='reportermate',
      version='0.2',
      description='Automated news stories and reports from datasets',
      long_description=open('README.rst').read(),
      classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
      ],
      keywords='data-analysis text data analysis',
      url='http://reportermate.com/',
      author='Nick Evershed',
      author_email='nick.evershed@gmail.com',
      license='MIT',
      entry_points = {
        "console_scripts":['reportermate = reportermate.command_line:main']
        },
      packages=['reportermate'],
      install_requires=['pandas','pybars3','messytables','dateinfer'],
      zip_safe=False)