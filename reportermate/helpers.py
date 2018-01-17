import global_stuff as g

# helper functions

# Just formats a number nicely

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
	return g.df[col].iloc[row]

def getColByRowValue(con, col1, value, col2):
	return df[df[col1] == value][col2].iloc[0]		

# Sorts dataframe based on a given column name in ascending order

def sortAscending(sortby):
	result = g.df.sort_values(sortby, True)
	return result

# Sorts dataframe based on a given column name in ascending order, then gets the nth cell value for a given column

def getRankedItemAscending(con, col, sortby, row):
	sortedDf = sortAscending(sortby)
	return getCell(sortedDf, col, row)

# Sorts dataframe based on a given column name in descending order

def sortDescending(sortby):
	result = g.df.sort_values(sortby,ascending=False)
	return result

# Sorts dataframe based on a given column name in descending order, then gets the nth cell value for a given column

def getRankedItemDescending(con, col, sortby, row):
	sortedDf = sortDescending(sortby)
	return sortedDf[col].iloc[row]

# Sums values across rows, creates a new column named total. Note - probably breaks if a total column already exists

def sumAllCols():
	totalColName = 'total'
	newDf = g.df
	if 'total' in newDf:
		totalColName = 'newTotal'
	newDf[totalColName] = newDf.sum(axis=1)
	return newDf

# Sum of the total column

def totalSumOfAllCols(con):
	totalColName = 'total'
	newDf = g.df
	if 'total' in newDf:
		totalColName = 'newTotal'
	newDf[totalColName] = newDf.sum(axis=1)
	return newDf[totalColName].sum()

# def testParent(df,blah):
# 	return blah['Name'].iloc[0]

# def testChild(df,foo):
# 	df['total'] = 100
# 	return df['total'].iloc[0]

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




