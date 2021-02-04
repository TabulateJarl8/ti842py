import ti842py
import traceback
import os

print("")
print("")
print(u"\u001b[33m===================================================================\u001b[0m")
print(u"\u001b[36mInitializing test! (1/2)")
try:
	print(u"\u001b[33m===================================================================\u001b[0m")
	print("ti842py.transpile(\"program.txt\", \"output.py\")")
	ti842py.transpile("program.txt", "output.py")
	print(u"\u001b[33m===================================================================\u001b[0m")
	print("")
except Exception as e:
	print(u"\u001b[31m===================================================================\u001b[0m")
	print(u"\u001b[31mWhoops! Error on calling transpile!\u001b[0m")
	traceback.print_exc()
	print(u"\u001b[31m===================================================================\u001b[0m")
	exit(2)
print(u"\u001b[33m===================================================================\u001b[0m")
print(u"\u001b[32mSuccessful Test! (1/2 COMPLETE)\u001b[0m")
print(u"\u001b[33m===================================================================\u001b[0m")
print(u"\u001b[36mInitializing test! (2/2)")
try:
	print(u"\u001b[33m===================================================================\u001b[0m")
	print("ti842py -i program.txt -o output.py")
	os.system("ti842py -i program.txt -o output.py")
	print(u"\u001b[33m===================================================================\u001b[0m")
	print("")
except Exception as e:
	print(u"\u001b[31m===================================================================\u001b[0m")
	print(u"\u001b[31mWhoops! Error on calling ti842py!\u001b[0m")
	traceback.print_exc()
	print(u"\u001b[31m===================================================================\u001b[0m")
	exit(2)
print(u"\u001b[33m===================================================================\u001b[0m")
print(u"\u001b[32mSuccessful Test! (2/2 COMPLETE)\u001b[0m")
print(u"\u001b[35mTerminating!\u001b[0m")
print(u"\u001b[33m===================================================================\u001b[0m")
exit()