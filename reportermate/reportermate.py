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

print('yep')
df = None

# Helper function for strings

def _cleanString(string):
	return string.lower().strip()

# Get information about the data

def _getDataInfo(fileObj):
	
	# Start with using tableschema to infer headers and types
	table = Table(fileObj)
	table.infer()
	print(table.schema.descriptor)
	headers = table.headers
	sample = table.read(limit=100)
	print(sample[:10])
	
	# If column has a date-like word in it, try getting the date format

	dateHeaders = ['year','month','fy','day','period','date']
	dateMatches = {"%a":"Day","%A":"Day","%w":"Day","%d":"Day","%-d":"Day","%b":"Month","%B":"Month","%m":"Month","%-m":"Month","%y":"Year","%Y":"Year"}
	
	possibleDates = []

	for i, header in enumerate(table.headers):
		for dateString in dateHeaders:
			if dateString == _cleanString(header):
				print("Possible date column:", header)
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
			print(dateGuess)
			
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

	print(newDf.dtypes)

	# Parse any dates in place that need to be parsed

	if dateColumns:
		for obj in dateColumns:
			dateFormat = obj['format']
			dateIndex = obj['index']
			newDf[newDf.columns[dateIndex]] = pd.to_datetime(newDf[newDf.columns[dateIndex]], format=dateFormat) 

	return newDf

def _replaceStrings(replacements,output):
	for replacement in replacements:
		key, value = replacement.items()[0]
		output = output.replace(key, value)

	return output

# This is the main function for doing things 

def analyseAndRender(dataLocation,templateLocation,replaceLocation=""):
	global df
	df = _makeDataFrame(dataLocation)

	with io.open(templateLocation, 'r', encoding='utf-8') as tempSource:
		compiler = Compiler()
		template = compiler.compile(tempSource.read())

	helpers = {"getCell":_hlp.getCell,"checkDifference":_hlp.checkDifference,"checkAgainstRollingMean":_hlp.checkAgainstRollingMean,"getRollingMean":_hlp.getRollingMean,"getDifference":_hlp.getDifference,"sortAscending":_hlp.sortAscending,"sortDescending":_hlp.sortDescending,"getRankedItemDescending":_hlp.getRankedItemDescending,"sumAllCols":_hlp.sumAllCols,"testParent":_hlp.testParent,"testChild":_hlp.testChild,"totalSumOfAllCols":_hlp.totalSumOfAllCols,"formatNumber":_hlp.formatNumber}

	output = template(df,helpers=helpers)

	if replaceLocation != "":
		with open(replaceLocation) as json_file:
			replacements = json.load(json_file)

		output = _replaceStrings(replacements, output)

	print(output)
	return output	

# All the helper functions required to run pandas functions on the data from the template

class _hlp():

	def formatNumber(con, num):
		if num >= 1000000:
			num = num / 1000000
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

	def getCell(con, col, row):
		return df[col].iloc[row]

	def getColByRowValue(con, col1, value, col2):
		return df[df[col1] == value][col2].iloc[0]		

	# Sorts dataframe based on a given column name in ascending order

	def sortAscending(sortby):
		result = df.sort_values(sortby, True)
		return result

	# Sorts dataframe based on a given column name in ascending order, then gets the nth cell value for a given column

	def getRankedItemAscending(con, col, sortby, row):
		sortedDf = sortAscending(sortby)
		return getCell(sortedDf, col, row)

	# Sorts dataframe based on a given column name in descending order

	def sortDescending(sortby):
		result = df.sort_values(sortby,ascending=False)
		return result

	# Sorts dataframe based on a given column name in descending order, then gets the nth cell value for a given column

	def getRankedItemDescending(con, col, sortby, row):
		sortedDf = sortDescending(sortby)
		return sortedDf[col].iloc[row]

	# Sums values across rows, creates a new column named total. Note - probably breaks if a total column already exists

	def sumAllCols():
		totalColName = 'total'
		newDf = df
		if 'total' in newDf:
			totalColName = 'newTotal'
		newDf[totalColName] = newDf.sum(axis=1)
		return newDf

	# Sum of the total column

	def totalSumOfAllCols(con):
		totalColName = 'total'
		newDf = df
		if 'total' in newDf:
			totalColName = 'newTotal'
		newDf[totalColName] = newDf.sum(axis=1)
		return newDf[totalColName].sum()

	def testParent(df,blah):
		return blah['Name'].iloc[0]

	def testChild(df,foo):
		df['total'] = 100
		return df['total'].iloc[0]

	def sumSpecificCols(df,cols):
		totalColName = 'total'
		
		if 'total' in df.columns:
			totalColName = 'newTotal'
		
		df[totalColName] = df[cols].sum(axis=1)	
		return df

	def checkDifference(df, col, row1, row2):
		val1 = df[col].iloc[row1]
		val2 = df[col].iloc[row2]
		
		if val1 > val2:
			return "increased"

		if val1 < val2:
			return "decreased"

		if val1 == val2:
			return "stayed steady"

	def checkAgainstRollingMean(df, col, row, length):
		val = df[col].iloc[row]
		mean = df[col].rolling(window=length).mean().iloc[-1]
		if val > mean:
			return "higher than"
		if val < mean:
			return "lower than"
		if val == mean:
			return "the same as"	

	def getRollingMean(df, col, length):
		mean = df[col].rolling(window=length).mean().iloc[-1]
		return mean

	def getDifference(df, col, row1, row2):
		val1 = df[col].iloc[row1]
		val2 = df[col].iloc[row2]
		return val1 - val2

# end _hlp

