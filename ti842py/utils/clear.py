import os


def clear():
	if os.system("clear") != 0:
		if os.system("cls") != 0:
			print("Clearing the screen is not supported on this device")
