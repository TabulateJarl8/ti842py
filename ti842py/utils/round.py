def ti_round(value, decimals):
	if isinstance(value, list):
		return [round(item, decimals) for item in value]
	else:
		return round(value, decimals)
