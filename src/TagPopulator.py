import re
import spacy
import textract
import os
from spacy.matcher import Matcher
from nltk.corpus import stopwords
import glob
import pandas as pd
import os, glob, re
from pprint import pprint
import nltk
from os.path import exists
import pickle
from fastai.text.all import * 


class NerTrainSet:


    def __init__(self, resume_path):
        self.skill_corpus = [skill.lower() for skill in list(pd.read_csv('data/skills.csv').columns)]
        self.tokenizer = Tokenizer(tok=SpacyTokenizer('en'))
        self.skill_corpus = [' '.join([token for token in self.tokenizer(skill) if token not in ['xxbos', 'xxmaj']]) for skill in self.skill_corpus]
        self.skill_corpus = [skill.encode("ascii", "ignore").decode().replace(
            '+', '<plus>').replace(
            '/', '<fwslash>').replace(
            '*', '<star>'
        ) for skill in self.skill_corpus]
        self.skill_corpus = [skill for skill in self.skill_corpus if ')' not in skill]
        self.skill_corpus = [skill for skill in self.skill_corpus if '(' not in skill]
        self.resume = textract.process(resume_path).decode().encode("ascii", "ignore").decode().replace(
            '+', '<plus>').replace(
            '/', '<fwslash>').replace(
            '*', '<star>'
        )
        self.resume = self.resume + os.popen('pdf2txt.py ' + resume_path).read().encode("ascii", "ignore").decode().replace(
            '+', '<plus>').replace(
            '/', '<fwslash>').replace(
            '*', '<star>'
        )

    
    def resume2str(self):
        tok_string = ' '.join(
            list(
                self.tokenizer(
                    ' '.join(
                        [token for token in ' xxtab '.join(
                            [tabsp for tabsp in ' xxbup '.join(
                                [bullet_point.strip() for bullet_point in ' '.join(
                                    [page.strip() for page in ' '.join(
                                        [line.strip() for line in self.resume.split(
                                            '\n')]).split(
                                        '\x0c')]).strip().split(
                                    '•') if bullet_point.strip()]).strip().split(
                                '\t') if tabsp.strip()]).split(
                            ' ') if token])
                )))
        
        return ' '. join([tok for tok in tok_string.split(' ') if tok not in ['xxmaj', 'xxup']])

    def list_of_skills(self, *args):
        if len(args) == 0:
            return [skill for skill in self.skill_corpus if skill.lower() in self.resume2str()]
        else:
            return [skill for skill in self.skill_corpus if skill.lower() in args[0]]

    def ne_list(self):
        ner_train = []
        resume_str = self.resume2str()
        for line in resume_str.split(' . '):
            ner_train.append(
                (
                    line, 
                    {
                    'entities': []
                    }
                )
            )
            for skill in self.list_of_skills(resume_str):
                for w in re.finditer(skill, line.lower()):
                    if w.start():
                        start_condition = line[w.start() - 1] in [',', ' ', ':']
                    else:
                        start_condition = True
                    if len(line) != w.end():
                        end_condition = line[w.end()] in [',', ' ', ':']
                    else:
                        end_condition = True
                    if start_condition and end_condition:    
                        ner_train[-1][1]['entities'].append((*w.span(), 'skill'))
        print(ner_train)
        return ner_train
    
    def file_io(self):
        if exists('data/ser_train.pkl'):
            with open('data/ser_train.pkl', "rb") as fp:
                ser_train = pickle.load(fp)
                ser_train.extend(self.ne_list())
        else:
            ser_train = self.ne_list()
        with open('data/ser_train.pkl', "wb") as fp:
            pickle.dump(ser_train, fp)
            
