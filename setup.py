import os
from setuptools import setup
with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(name='reportermate',
      version='0.1',
      description='Automated news stories and reports from datasets',
      long_description='Reportermate is an open source project to create an automated news reporting system.',
      classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
      ],
      keywords='data-analysis text data analysis',
      url='',
      author='Nick Evershed',
      author_email='nick.evershed@gmail.com',
      license='MIT',
      packages=['reportermate'],
      install_requires=required,
      zip_safe=False)