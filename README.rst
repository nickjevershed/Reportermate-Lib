ReporterMate
============

Reportermate is an open source project to `create an automated news
reporting system <http://reportermate.com/>`__. This library forms the
base of the system, and combines the pandas data analysis library, the
handlebars templating language, and a whole bunch of helper functions to
automate the generation of text reports from data.

Installation
------------

::

    pip install reportermate

Usage
-----

Installing the reportermate lib adds the reportermate function to your
command line.

::

    reportermate my-data.csv my-template.txt

Using this function will take your data and then analyse and render it
according to the template provided.

To use reportermate from within another python script, import the
analyseAndRender function:

.. code:: python

    from reportermate import analyseAndRender
    analyseAndRender(my-data.csv,my-template.txt)

Templates
---------

Reportermate uses the handlebars template language to define the
analysis of the dataset, and how the results should be rendered into
text. The template functions are the key to generating your text
results.

*Template function definitions and examples coming soon...*
