import os
import sys


file_list = [file for file in sys.argv[1:] if file.split('.')[-1] in ['docx', 'pdf']]
output = os.popen('pdf2txt.py ' + file_list[0]).read()
print(output, type(output))
