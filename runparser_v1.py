from src.ResumeParser import parse
import glob
import os
import json
import sys
os.environ["TOKENIZERS_PARALLELISM"] = "false"

file_list = [file for file in sys.argv[1:] if file.split('.')[-1] in ['docx', 'pdf']]
for file in file_list:
    with open(
        'data/outputs/' + '_'.join(
            file_list[0].split('/')[-1].split('.')[0].split(' ')) + '_' + file_list[0].split('/')[-1].split('.')[1] + '.json', "w"
    ) as outfile:
        json.dump(parse(file).output('en'), outfile, indent = 4)
