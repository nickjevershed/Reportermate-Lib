import pandas as pd
import messytables as mt
import dateinfer
import os

# Helper function for strings

def cleanString(string):
	return string.lower().strip()

# Get information about the data

def getDataInfo(fileObj):
	
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
			if dateString in cleanString(header):
				possibleDates.append(i)
				
	if possibleDates:
		for colIndex in possibleDates:
			dateSample = []
			for row in row_set.sample:
				dateSample.append(row[colIndex].value)
			dateGuess = dateinfer.infer(dateSample).replace("%M","%y")  # hack to stop years showing as minutes
			
			# For single days, months and years	

			if len(dateGuess) <= 3:
				types[colIndex] = "{dateMatch}({dateGuess})".format(dateMatch=dateMatches[dateGuess],dateGuess=dateGuess)

			# For other dates

			else:
				types[colIndex] = "Date({dateGuess})".format(dateGuess=dateGuess)

	f.close()
	return {"offset":offset,"headers":headers,"types":types}

def analyseData(fileObj):

	# Get the headers and more detailed information about column types

	fileInfo = getDataInfo(fileObj)

	# Work out which ones are columns with a proper date

	dateColumns = []

	for i, colType in enumerate(fileInfo['types']):
		if "Date" in str(colType):
			dateColumns.append(i)

	print dateColumns		
	print fileInfo['types']

	# Read the CSV into a pandas dataframe

	df = pd.read_csv(fileObj)

	# Parse any dates in place that need to be parsed

	if dateColumns:
		for i in dateColumns:
			dateFormat = str(fileInfo['types'][i]).split("(")[1].split(")")[0]
			print dateFormat
			df[df.columns[i]] = pd.to_datetime(df[df.columns[i]], format=dateFormat) 

	print df[:10]		

# Testing locally

analyseData(os.path.dirname(os.getcwd()) + '/testdata/date-test.csv')
