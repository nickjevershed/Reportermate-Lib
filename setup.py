import os
from setuptools import setup

setup(name='reportermate',
      version='0.6.2',
      description='Automated news stories and reports from datasets',
      long_description=open('README.rst').read(),
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Information Analysis',
      ],
      keywords='data-analysis text data analysis',
      url='https://github.com/nickjevershed/Reportermate-Lib',
      author='Nick Evershed',
      author_email='nick.evershed@gmail.com',
      license='MIT',
      entry_points = {
        "console_scripts":['reportermate = reportermate.command_line:main']
        },
      packages=['reportermate'],
      install_requires=['pandas','pybars3','pydateinfer','simplejson'],
      zip_safe=False)