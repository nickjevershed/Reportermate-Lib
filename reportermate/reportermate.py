#!/usr/bin/env python

import pandas as pd
import messytables as mt
import dateinfer
import os
from datetime import datetime
from pybars import Compiler
import io
import helpers as hlp

# Helper function for strings

def _cleanString(string):
	return string.lower().strip()

# Get information about the data

def _getDataInfo(fileObj):
	
	# Start with using messytable for headers and types

	# Sample size for type detection
	
	n = 100
	f = open(fileObj, 'rb')
	table_set = mt.CSVTableSet(f)
	table_set.window = n
	row_set = table_set.tables[0]
	offset, headers = mt.headers_guess(row_set.sample)
	row_set.register_processor(mt.offset_processor(offset + 1))
	types = mt.type_guess(row_set.sample, strict=True)

	# If column has a date-like word in it, try getting the date format

	dateHeaders = ['year','month','fy','day','period','date']
	dateMatches = {"%a":"Day","%A":"Day","%w":"Day","%d":"Day","%-d":"Day","%b":"Month","%B":"Month","%m":"Month","%-m":"Month","%y":"Year","%Y":"Year"}
	possibleDates = []

	for i, header in enumerate(headers):
		for dateString in dateHeaders:
			if dateString == _cleanString(header):
				possibleDates.append(i)
		
	if possibleDates:
		hyphenReplace = False
		for colIndex in possibleDates:
			dateSample = []
			for row in row_set.sample:
				
				# Work around because dateinfer breaks on dates like Jul-1976 and I don't know why 

				if "-" in row[colIndex].value:
					hyphenReplace = True
					dateSample.append(row[colIndex].value.replace("-","/"))
				else:	
					dateSample.append(row[colIndex].value)	
			# print dateSample
			dateGuess = dateinfer.infer(dateSample).replace("%M","%y")  # hack to stop years showing as minutes
			
			# For single days, months and years	
			# print dateGuess
			
			# Work around because dateinfer breaks on dates like Jul-1976 and I don't know why 

			if hyphenReplace:
				dateGuess = dateGuess.replace("/","-")
			
			if len(dateGuess) <= 3:
				types[colIndex] = "{dateMatch}({dateGuess})".format(dateMatch=dateMatches[dateGuess],dateGuess=dateGuess)

			# For other dates

			else:
				types[colIndex] = "Date({dateGuess})".format(dateGuess=dateGuess)

	f.close()

	# Check for day, month, year cols and get positions

	dayPos = None 
	monthPos = None
	yearPos = None

	for i, headerType in enumerate(types):
		if 'Day' in str(headerType):
			dayPos = i

	for i, headerType in enumerate(types):
		if 'Month' in str(headerType):
			monthPos = i
			
	for i, headerType in enumerate(types):
		if 'Year' in str(headerType):
			yearPos = i		

	return {"offset":offset,"headers":headers,"types":types,"splitDates":[dayPos,monthPos,yearPos]}

def _makeDataFrame(fileObj):

	# Get the headers and more detailed information about column types

	fileInfo = _getDataInfo(fileObj)

	# Work out which ones are columns with a proper date

	dateColumns = []

	for i, colType in enumerate(fileInfo['types']):
		if "Date" in str(colType):
			dateColumns.append(i)

	# Read the CSV into a pandas dataframe

	df = pd.read_csv(fileObj)

	# Parse any dates in place that need to be parsed

	if dateColumns:
		for i in dateColumns:
			dateFormat = str(fileInfo['types'][i]).split("(")[1].split(")")[0]
			df[df.columns[i]] = pd.to_datetime(df[df.columns[i]], format=dateFormat) 

	# check if there is day, month, year in seperate columns and parse if so

	if fileInfo['splitDates'][0] and fileInfo['splitDates'][1] and fileInfo['splitDates'][2]:

		dateFormat = str(fileInfo['types'][fileInfo['splitDates'][0]]).split("(")[1].split(")")[0] + "-" + str(fileInfo['types'][fileInfo['splitDates'][1]]).split("(")[1].split(")")[0] + "-" + str(fileInfo['types'][fileInfo['splitDates'][2]]).split("(")[1].split(")")[0]
		
		print dateFormat

		dayHeader = list(df)[fileInfo['splitDates'][0]]
		monthHeader = list(df)[fileInfo['splitDates'][1]]
		yearHeader = list(df)[fileInfo['splitDates'][2]]

		df['newDate'] = df.apply(lambda row :
                          datetime.strptime(str(row[dayHeader]) + "-" + str(row[monthHeader]) + "-" + str(row[yearHeader]), dateFormat).isoformat(' '), 
                          axis=1)

	return df

def analyseAndRender(dataLocation,templateLocation):
	
	df = _makeDataFrame(os.path.dirname(os.getcwd()) + dataLocation)

	with io.open(os.path.dirname(os.getcwd()) + templateLocation, 'r', encoding='utf-8') as tempSource:
		compiler = Compiler()
		template = compiler.compile(tempSource.read())

	helpers = {"getCell":hlp.getCell,"checkDifference":hlp.checkDifference,"checkAgainstRollingMean":hlp.checkAgainstRollingMean,"getRollingMean":hlp.getRollingMean,"getDifference":hlp.getDifference}

	output = template(df,helpers=helpers)

	print output

# Testing locally

# analyseAndRender('/testdata/Labor force demo data.csv','/testdata/test.txt')
