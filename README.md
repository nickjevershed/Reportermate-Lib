ReporterMate
=======================

Reportermate is an open source project to [create an automated news reporting system](http://reportermate.com/). This library forms the base of the system, and combines the pandas data analysis library, the handlebars templating language, and a whole bunch of helper functions to automate the generation of text reports from data.

Installation
-------------

````
pip install reportermate
````

Usage
------

Installing the reportermate lib adds the reportermate function to your command line. 

````
reportermate my-data.csv my-template.txt
````

Using this function will take your data and then analyse and render it according to the template provided.

To use reportermate from within another python script, import the analyseAndRender function:

````Python
from reportermate import analyseAndRender
analyseAndRender(my-data.csv,my-template.txt)
````

Both the commandline and analyseAndRender have an optional third argument, which is the location of an json file defining various reportermate options, eg:

````
reportermate my-data.csv my-template.txt my-options.json
````

This can be used to replace strings when compiling the final story, and will have futher options added in future such as defininf date columns and formats.

Most of the work is done by the template through the use of helper functions. To see working examples and templates, check out the tests folder.

Template helper functions
-----------

Reportermate uses the handlebars template language to define the analysis of the dataset, and how the results should be rendered into text. The template functions are the key to generating your text results.

**getCellByNumber**

Get a specific cell from a dataframe given a dataframe, column label, and row number. Use 'default' for ds unless chaining helper functions.

````
{{getCellByNumber ds='default' col='column_name' row='10'}}
````
**getCellByLabel**

Get a specific cell from a dataframe given a dataframe, column label, and row label. Use 'default' for ds unless chaining helper functions.

````
{{getCellByLabel ds='default' col='column_name' row='row_name'}}
````

**checkDifferenceBetweenValues**

Evaluates the difference between two cells, and returns the corresponding text given a comma-delimited string

````
{{checkDifferenceBetweenValues ds='default' col='column_name' row1='1' row2='2' 'higher than,lower than,the same'}}
````

**checkAgainstRollingMean**

Checks a cell from a column against the rolling mean of that column, and returns the corresponding text given a comma-delimited string. Length is the time window to use

````
{{checkAgainstRollingMean ds='default' col='column_name' row='1' length='6' 'higher than average,lower than average,the same'}}
````

**getRollingMean**

Returns the rolling mean of a given column for a defined number of periods 

````
{{getRollingMean ds='default' col='column_name' length='6'}}
````

**getDifference**

Returns the difference between two cells

````
{{getDifference ds='default' col='column_name' row1='1' row2='2'}}
````

**sortAscending**

Sorts data based on a given column name in ascending order

````
{{sortAscending ds='default' sortBy='column_name'}}
````

**sortDescending**

Sorts data based on a given column name in descending order

````
{{sortDescending ds='default' sortBy='column_name'}}
````

**getRankedItemDescending**

Sorts data based on a given column name in descending order, then gets the nth cell value for a given column

````
{{getRankedItemDescending ds='default' sortBy='column_name' row='1'}}
````

**sumAcrossAllCols**

Sums values across rows, creates a new column named total. Note - probably breaks if a total column already exists

````
{{sumAcrossAllCols ds='default'}}
````

**groupBy**

Groupby column or columns, then perform an operation (sum, count, mean) on the result. eg sum by category

````
{{groupBy ds='default' groupByThis='column_name' operator='sum'}}
````

**groupByTime**

Group by the year, month or day and return a specific month, day or year

````
{{groupByTime ds='default' groupByThis='column_name' timePeriod='time_period' operator='sum'}}
````

**filterBy**

Returns a new dataframe filtered by the given value/s for the given column/s

````
{{filterBy ds='default' cols='column_name1,column_name2' timePeriod='time_period' operator='sum'}}
````

**summariseCol**

Does maths on a specific column, eg sum, mean, count, mode

````
{{summariseCol ds='default' col='column_name' operator='sum'}}
````

**checkDifferenceBetweenResults**

Tests greater than, less than, or equal to with two values, and returns a string from a comma-seperated list 

````
{{checkDifferenceBetweenResults ds='default' val1='1' val2='2' 'higher than,lower than,the same'}}
````

**uniqueValues**

````
{{uniqueValues ds='default' col='column_name'}}
````

**summariseColByTimePeriod**

Groups by a given time period, then performs the given operation. eg. get the monthly average

````
{{summariseColByTimePeriod ds='default' dateCol='column_name' col='column_name' freq='6' operator='mean'}}
````

**makeList**

Turns a dataframe into a list of dicts, so it can be accessed by the default pybars iterator functions like {{#each}} 

````
{{makeList ds='dataframe' limit=None}}
````
