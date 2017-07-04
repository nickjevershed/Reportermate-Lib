# helper functions for rendering

def formatNumber(num):
	if num % 1 != 0:
		return "{0:,.1f}".format(num)
	else:	
		return "{0:,.0f}".format(num)

def getCell(df, col, row):
	return formatNumber(df[col].iloc[row])

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
	return formatNumber(val1 - val2)
