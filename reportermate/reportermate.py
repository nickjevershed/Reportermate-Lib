# -*- coding: utf-8 -*-

import pandas as pd
import dateinfer	
from tableschema import Table
import os
from datetime import datetime
from pybars import Compiler
import simplejson as json
import io
# import global_stuff as g
# import helpers as _hlp

df = None

# Helper function for strings

def _cleanString(string):
	return string.lower().strip()

# Get information about the data

def _getDataInfo(fileObj):
	
	# Start with using tableschema to infer headers and types
	table = Table(fileObj)
	table.infer()
	headers = table.headers
	sample = table.read(limit=100)
	
	# If column has a date-like word in it, try getting the date format

	dateHeaders = ['year','month','fy','day','date']
	dateMatches = {"%a":"Day","%A":"Day","%w":"Day","%d":"Day","%-d":"Day","%b":"Month","%B":"Month","%m":"Month","%-m":"Month","%y":"Year","%Y":"Year"}
	
	possibleDates = []

	for i, header in enumerate(table.headers):
		for dateString in dateHeaders:
			if dateString == _cleanString(header):
				# print("Possible date column:", header)
				possibleDates.append(i)
	
	dateColumns = []

	if possibleDates:
		hyphenReplace = False
		for colIndex in possibleDates:
			dateSample = []
			for row in sample:
				
				# Work around because dateinfer breaks on dates like Jul-1976 and I don't know why 

				if "-" in row[colIndex]:
					hyphenReplace = True
					dateSample.append(row[colIndex].replace("-","/"))
				else:	
					dateSample.append(row[colIndex])	
			# print dateSample
			dateGuess = dateinfer.infer(dateSample).replace("%M","%y")  # hack to stop years showing as minutes
			
			# For single days, months and years	
			# print(dateGuess)
			
			# Work around because dateinfer breaks on dates like Jul-1976 and I don't know why 

			if hyphenReplace:
				dateGuess = dateGuess.replace("/","-")

			dateColumns.append({"index":colIndex,"format":dateGuess})
	
	return {"tableschema":table.schema.descriptor,"dateColumns":dateColumns}

def _makeDataFrame(fileObj):

	# Get the headers and more detailed information about column types

	fileInfo = _getDataInfo(fileObj)

	# Work out which ones are columns with a proper date

	dateColumns = fileInfo['dateColumns']

	# Read the CSV into a pandas dataframe

	newDf = pd.read_csv(fileObj)

	# print(newDf.dtypes)

	# Parse any dates in place that need to be parsed

	if dateColumns:
		for obj in dateColumns:
			dateFormat = obj['format']
			dateIndex = obj['index']
			newDf[newDf.columns[dateIndex]] = pd.to_datetime(newDf[newDf.columns[dateIndex]], format=dateFormat) 

	return newDf

def _replaceStrings(replacements,output):
	for replacement in replacements:
		for key, value in replacement.items():
			output = output.replace(key, value)

	return output

# This is the main function for doing things 

def analyseAndRender(dataLocation,templateLocation,replaceLocation=""):
	global df
	df = _makeDataFrame(dataLocation)

	with io.open(templateLocation, 'r', encoding='utf-8') as tempSource:
		compiler = Compiler()
		template = compiler.compile(tempSource.read())

	helpers = {
		"getCell":getCell,
		"checkDifferenceBetweenValues":checkDifferenceBetweenValues,
		"checkAgainstRollingMean":checkAgainstRollingMean,
		"getRollingMean":getRollingMean,
		"getDifference":getDifference,
		"sortAscending":sortAscending,
		"sortDescending":sortDescending,
		"getRankedItemDescending":getRankedItemDescending,
		"sumAcrossAllCols":sumAcrossAllCols,
		"totalSumOfAllCols":totalSumOfAllCols,
		"formatNumber":formatNumber,
		"groupBy":groupBy,
		"filterBy":filterBy,
		"summariseCol":summariseCol,
		"checkDifferenceBetweenResults":checkDifferenceBetweenResults,
		"uniqueValues":uniqueValues
		}

	output = template(df,helpers=helpers)

	if replaceLocation != "":
		with open(replaceLocation) as json_file:
			replacements = json.load(json_file)

		output = _replaceStrings(replacements, output)

	# print(output.encode('utf-8'))
	return output	

def _getCurrentDataframe(ds):
	if type(ds) is str:
		return df
	else:
		return ds
			
# All the helper functions required to run pandas functions on the data from the template

def formatNumber(con, num):
	if num >= 1000000:
		num = num / 1000000.0

		if num % 1 != 0:
			return "{0:,.1f}".format(num) + "m"
		else:	
			return "{0:,.0f}".format(num) + "m"
	else:		
		if num % 1 != 0:
			return "{0:,.1f}".format(num)
		else:	
			return "{0:,.0f}".format(num)

# Get a specific cell from a dataframe given a dataframe, row and column

def getCell(con, ds, col, row):
	currDf = _getCurrentDataframe(ds)
	return currDf[col].iloc[row]

def getColByRowValue(con, ds, col1, value, col2):
	currDf = _getCurrentDataframe(ds)
	return currDf[currDf[col1] == value][col2].iloc[0]		

# Sorts dataframe based on a given column name in ascending order

def sortAscending(con, ds, sortBy):
	result = ds.sort_values(sortBy, True)
	return result

# Sorts dataframe based on a given column name in ascending order, then gets the nth cell value for a given column

def getRankedItemAscending(con, ds, col, sortBy, row):
	currDf = _getCurrentDataframe(ds)
	sortedDf = currDf.sort_values(sortBy)
	result = getCell(sortedDf, col, row)
	return result

# Sorts dataframe based on a given column name in descending order

def sortDescending(con, ds, sortBy):
	result = ds.sort_values(sortBy,ascending=False)
	return result

# Sorts dataframe based on a given column name in descending order, then gets the nth cell value for a given column

def getRankedItemDescending(con, ds, col, sortBy, row):
	currDf = _getCurrentDataframe(ds)
	sortedDf = currDf.sort_values(sortBy,ascending=False)
	result = sortedDf[col].iloc[row]
	return result

# Does maths on a specific column, eg sum, mean, count, mode

def summariseCol(con,ds,col,operator):
	currDf = _getCurrentDataframe(ds)
	result = getattr(currDf[col], operator)()
	return result

# Sums values across rows, creates a new column named total. Note - probably breaks if a total column already exists

def sumAcrossAllCols(con, ds):
	currDf = _getCurrentDataframe(ds)
	totalColName = 'total'
	newDf = currDf
	if 'total' in newDf:
		totalColName = 'newTotal'
	newDf[totalColName] = newDf.sum(axis=1)
	return newDf

# Sum of the total column

def totalSumOfAllCols(con, ds):
	currDf = _getCurrentDataframe(ds)
	totalColName = 'total'
	newDf = currDf
	if 'total' in newDf:
		totalColName = 'newTotal'
	newDf[totalColName] = newDf.sum(axis=1)
	return newDf[totalColName].sum()

def sumAcrossSpecificCols(con, ds, cols):
	totalColName = 'total'
	
	if 'total' in df.columns:
		totalColName = 'newTotal'
	
	df[totalColName] = df[cols].sum(axis=1)	
	return df

def checkDifferenceBetweenValues(con, ds, col, row1, row2):
	currDf = _getCurrentDataframe(ds)

	val1 = currDf[col].iloc[row1]
	val2 = currDf[col].iloc[row2]
	
	if val1 > val2:
		return "increased"

	if val1 < val2:
		return "decreased"

	if val1 == val2:
		return "stayed steady"

def checkDifferenceBetweenResults(con, val1, val2):

	if val1 > val2:
		return "higher than"

	if val1 < val2:
		return "lower than"

	if val1 == val2:
		return "the same"

def checkAgainstRollingMean(con, col, row, length):
	val = df[col].iloc[row]
	mean = df[col].rolling(window=length).mean().iloc[-1]
	if val > mean:
		return "higher than"
	if val < mean:
		return "lower than"
	if val == mean:
		return "the same as"	

def getRollingMean(con, col, length):
	mean = df[col].rolling(window=length).mean().iloc[-1]
	return mean

def getDifference(con, col, row1, row2):
	val1 = df[col].iloc[row1]
	val2 = df[col].iloc[row2]
	return val1 - val2

def groupBy(con, ds, groupByThis, operator):
	currDf = _getCurrentDataframe(ds)

	if "," in groupByThis:
		groupByThis = groupByThis.split(",")
	else:
		groupByThis = [groupByThis]	
	
	dg = currDf.groupby(groupByThis, as_index=False)
	result = getattr(dg, operator)()
	return result

def uniqueValues(con, ds, col):
	currDf = _getCurrentDataframe(ds)
	result = currDf[col].nunique()
	return result

def filterBy(con, ds, cols, filterByThis):
	currDf = _getCurrentDataframe(ds)

	# For multi-column filtering

	if "," in filterByThis:
		filterByThis = filterByThis.split(",")
		cols = cols.split(",")

		queryStr = ''
		for i in range(0, len(cols)):
			join = ' and '
			if i == len(cols) - 1:
				join = ''
			queryStr = queryStr + cols[i] + ' == "' + filterByThis[i] + '"' + join

		result = currDf.query(queryStr)
		return result

	# For single column filtering
		
	else:
		result = currDf.loc[currDf[cols] == filterByThis]
		return result	

