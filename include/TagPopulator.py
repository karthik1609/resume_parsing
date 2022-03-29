import re
import spacy
import textract
import os
from spacy.matcher import Matcher
from nltk.corpus import stopwords
import glob
import os
import pandas as pd
import os, glob, re
from pprint import pprint
import nltk

#file_list = [file for file in sys.argv[1:] if file.split('.')[-1] in ['docx', 'pdf']]
#file_list = glob.glob(os.path.join(os.getcwd(), "../Fw__Sample_resumes_/", "*.pdf"))
#resumes = [textract.process(file).decode() for file in file_list]

class NerTrainSet:

    def __init__(self, resume):
        self.skill_corpus = [skill.lower() for skill in list(pd.read_csv('../data/skills.csv').columns)]
        self.resume = resume

    
    def resume2los(self):
        return [
            bullet_point.strip() for bullet_point in ' '.join(
                [page.strip() for page in ' '.join(
                    [line.strip() for line in self.resume.split('\n')]
                ).split('\x0c')]
            ).strip().split('•') if bullet_point.strip()
        ]

    def list_of_skills(self):
        return [skill for skill in self.skill_corpus if skill in ' . '.join(self.resume2los()).lower()]

    def ne_list(self):
        ner_train = []
        for line in self.resume2los():
            ner_train.append(
                (
                    line, 
                    {
                    'entities': []
                    }
                )
            )
            for skill in self.list_of_skills():
                for w in re.finditer(skill, line.lower()):
                    if w.start():
                        start_condition = line[w.start() - 1] == ' '
                    else:
                        start_condition = True
                    if len(line) != w.end():
                        end_condition = line[w.end()] == ' '
                    else:
                        end_condition == True
                    if start_condition and end_condition:    
                        ner_train[-1][1]['entities'].append((*w.span(), 'skill'))
        return ner_train