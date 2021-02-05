from datetime import datetime
def getTime():
	now = datetime.now()
	return [now.hour, now.minute, now.second]
	
def getDate():
	now = datetime.now()
	return [now.year, now.month, now.day]