import re
import spacy
import textract
import os
from spacy.matcher import Matcher
import glob
import os
import random
import pandas as pd
import json


class parse:
    def __init__(self, file_list, nlp):
        self.file_list = file_list
        self.resumes = [textract.process(file_path).decode() for file_path in file_list]
        self.nlp = nlp

    def extract(self):
        ph_list, email_list, dob_list, names_list, location_list, skills_list, skillset_exp = [], [], [], [], [], [], []
        for resume in self.resumes:
            items = re.finditer(r'\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}', resume)
            ph_span = [(resume[item.span()[0]:item.span()[1]], item.span()) for item in items]
            ph_list.append(ph_span)
            items = re.finditer(r'[\w\.-]+@[\w\.-]+', resume)
            em_span = [(resume[item.span()[0]:item.span()[1]], item.span()) for item in items]
            email_list.append(em_span)
            result2 = re.finditer(r"[\d]{1,2}-[\d]{1,2}-[\d]{4}", resume) # DD-MM-YYYY
            dob_span = [(resume[item.span()[0]:item.span()[1]], item.span()) for item in result2]
            dob_list.append(dob_span)
            doc = self.nlp(resume)
            list_ls, list_ns, list_ss = [], [], []
            for ent in doc.ents:
                print(ent.label_)
                if ent.label_ == 'PERSON':
                    list_ns.append(ent.text)
                if ent.label_ in ['GPE', 'LOC']:
                    list_ls.append(ent.text) 
                if ent.label_ in ['PRODUCT', 'ORG']:
                    list_ss.append(ent.text)
            location_list.append(list_ls)
            names_list.append(list_ns)
            skillset_exp.append(list_ss)
            noun_chunks = doc.noun_chunks
            # tokens = [token.text for token in nlp_text if not token.is_stop]
            tokens = [token.text for token in doc if token.is_stop]
            
            data = pd.read_csv("skills.csv") 
            skills = list(data.columns.values)

            skillset = []
            for token in tokens:
                if token.lower() in skills:
                    skillset.append(token)

            for token in noun_chunks:
                token = token.text.lower().strip()
                if token in skills:
                    skillset.append(token)
            

            st = [i.capitalize() for i in set([i.lower() for i in skillset])]
            skills_list.append(st)
            
            
        return ph_list, email_list, dob_list, names_list, location_list, skills_list, skillset_exp 
    
    def dictify(self):
        dict_ = {}
        ph_list, email_list, dob_list, names_list, location_list, skills_list, skillset_exp = self.extract()
        for idx, ph, email, dob, name, location, skills, skills_exp in zip(
            [file.split('.')[-2].split('/')[-1] for file in self.file_list], 
            ph_list, 
            email_list, 
            dob_list, 
            names_list, 
            location_list, 
            skills_list,
            skillset_exp
        ):
            dict_[idx] = {}
            if len(dob):
                dict_[idx]['dob'] = dob[0]
            else:
                dict_[idx]['dob'] = (None, None)
            if len(name):
                dict_[idx]['name'] = name[0]
            else:
                dict_[idx]['name'] = (None, None)
            if len(email): 
                dict_[idx]['email'] = email[0]
            else:
                dict_[idx]['email'] = (None, None)
            if len(ph):
                dict_[idx]['phone'] = ph[0]
            else:
                dict_[idx]['phone'] = (None, None)
            if len(location):
                dict_[idx]['location'] = location[0]
            else:
                dict_[idx]['location'] = (None, None)
            dict_[idx]['skills'] = skills
            dict_[idx]['skills_exp'] = skills_exp
        return dict_ 
