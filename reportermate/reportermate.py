# -*- coding: utf-8 -*-

import pandas as pd
import dateinfer
import os
from datetime import datetime
from pybars import Compiler
import simplejson as json
import io
import csv
import itertools

# import global_stuff as g
# import helpers as _hlp

df = None

# Helper function for strings

def _cleanString(string):
	return string.lower().strip()

# Get information about the data

def _getDataInfo(fileObj):
	
	sample = []

	with open(fileObj) as csvFile:
		reader = csv.reader(csvFile)
		headers = next(reader)
		for row in itertools.islice(reader, 100):
			sample.append(row)

	# If column has a date-like word in it, try getting the date format

	dateHeaders = ['year','month','fy','day','date']
	dateMatches = {"%a":"Day","%A":"Day","%w":"Day","%d":"Day","%-d":"Day","%b":"Month","%B":"Month","%m":"Month","%-m":"Month","%y":"Year","%Y":"Year"}
	
	possibleDates = []

	for i, header in enumerate(headers):
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

	return {"dateColumns":dateColumns}

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

def analyseAndRender(dataLocation,templateLocation,optionsLocation=""):
	global df
	
	if optionsLocation != "":
		with open(optionsLocation) as json_file:
			options = json.load(json_file)

	# For local csv

	if ".csv" in dataLocation and "https://docs.google.com" not in dataLocation:
		df = _makeDataFrame(dataLocation)

	# For google sheets as csv

	elif "https://docs.google.com" in dataLocation:
		print("It's a google sheet")

	# If its already a dataframe
		
	else:
		df = dataLocation

	with io.open(templateLocation, 'r', encoding='utf-8') as tempSource:
		compiler = Compiler()
		template = compiler.compile(tempSource.read())

	helpers = {
		"getCellByNumber":getCellByNumber,
		"getCellByLabel":getCellByLabel,
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
		"groupByTime":groupByTime,
		"filterBy":filterBy,
		"summariseCol":summariseCol,
		"checkDifferenceBetweenResults":checkDifferenceBetweenResults,
		"uniqueValues":uniqueValues,
		"summariseColByTimePeriod":summariseColByTimePeriod,
		"makeList":makeList
		}

	output = template(df,helpers=helpers)

	# String replacements
	if optionsLocation != "":
		if 'replacements' in options:
			output = _replaceStrings(options['replacements'], output)

	# print(output.encode('utf-8'))
	return output	

def _getCurrentDataframe(ds):
	if type(ds) is str:
		return df
	else:
		return ds
			
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

# All the helper functions required to run pandas functions on the data from the template

# Get a specific cell from a dataframe given a dataframe, column label, and row number

def getCellByNumber(con, ds, col, row):
	currDf = _getCurrentDataframe(ds)
	return currDf[col].iloc[row]

# Get a specific cell from a dataframe given a dataframe, column label, and row label

def getCellByLabel(con, ds, col, row):
	currDf = _getCurrentDataframe(ds)
	return currDf[col].loc[row]

# Get the column based on the vale of a row

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

# Sorts dataframe based on a given column name in descending order, then gets the rank of a specific cell

def getRankOfItemDescending(con, ds, col, sortBy, row):
	currDf = _getCurrentDataframe(ds)
	sortedDf = currDf.sort_values(sortBy,ascending=False)
	result = sortedDf[col].iloc[row]
	return result	

# Does maths on a specific column, eg sum, mean, count, mode

def summariseCol(con,ds,col,operator):
	currDf = _getCurrentDataframe(ds)
	result = getattr(currDf[col], operator)()
	return result

# Get monthly average for a col

def summariseColByTimePeriod(con,ds,dateCol,col,freq,operator):
	currDf = _getCurrentDataframe(ds)
	dg = currDf.groupby(currDf['date'].dt.month, as_index=False)
	# dg = currDf.groupby(currDf[dateCol].dt[freq], as_index=False)
	result = getattr(dg, operator)()
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

def checkDifferenceBetweenValues(con, ds, col, row1, row2, text):
	currDf = _getCurrentDataframe(ds)

	val1 = currDf[col].iloc[row1]
	val2 = currDf[col].iloc[row2]
	textList = text.split(",")

	if val1 > val2:
		# eg gone up
		return textList[0]

	if val1 < val2:
		# eg dropped
		return textList[1]

	if val1 == val2:
		# eg stayed the same
		return textList[2]

def checkDifferenceBetweenResults(con, val1, val2, text):

	textList = text.split(",")

	if val1 > val2:
		# eg is higher than
		return textList[0]

	if val1 < val2:
		# eg is lower than
		return textList[1]

	if val1 == val2:
		# eg is the same
		return textList[2]

# Checks a cell from a column against the rolling mean of that column

def checkAgainstRollingMean(con, col, row, length, text):
	textList = text.split(",")
	val = df[col].iloc[row]
	mean = df[col].rolling(window=length).mean().iloc[-1]
	if val > mean:
		return textList[0]
	if val < mean:
		return textList[1]
	if val == mean:
		return textList[2]	

# Returns the rolling mean for a defined number of periods

def getRollingMean(con, col, length):
	mean = df[col].rolling(window=length).mean().iloc[-1]
	return mean

# Returns the difference between two cells

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

# Group by the year, month or day and return a specific month, day or year

def groupByTime(con, ds, groupByThis, timePeriod, operator):

	currDf = _getCurrentDataframe(ds)
	dg = currDf.groupby(getattr(currDf[groupByThis].dt, timePeriod))
	result = getattr(dg, operator)()
	return result

def uniqueValues(con, ds, col):
	currDf = _getCurrentDataframe(ds)
	result = currDf[col].nunique()
	return result

def makeList(con, ds, limit=None):

	currDf = _getCurrentDataframe(ds)
	if limit != None:
		return currDf.to_dict('records')[:limit]
	else:
		return currDf.to_dict('records')	

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

