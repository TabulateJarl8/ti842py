from datetime import datetime


def getTime():
	now = datetime.now()
	return [now.hour, now.minute, now.second]


def getDate():
	now = datetime.now()
	return [now.year, now.month, now.day]


def dayOfWk(year, month, day):
	dt = datetime.strptime('{year}-{month:02d}-{day:02d}'.format(year=year, month=month, day=day), '%Y-%m-%d')
	return int(dt.strftime('%w')) + 1 # sunday would be zero, so shift everything up by 1 so that sunday is 1