import textract
import spacy
import re
import pandas as pd
import stanza
import spacy_stanza
import pickle
from os.path import exists
from src.TagPopulator import NerTrainSet

stanza.download('en')

class parse:
    
    def __init__(self, file_path):
        resume_skill_fetch = NerTrainSet(file_path)
        self.file_path = file_path
        self.resume = resume_skill_fetch.resume
        #self.resume = textract.process(self.file_path).decode()
        self.nlp_name_loc = spacy.load('en_core_web_trf')
        self.nlp_skills = spacy.load('en_core_web_trf')
        self.nlp_edu = spacy.load('en_core_web_sm')
        #self.doc_nmlc = self.nlp_name_loc(self.resume)
        #self.doc_skills = self.nlp_skills(self.resume)
        #self.doc_edu = self.nlp_edu(self.resume)
        self.nlp_stanza = spacy_stanza.load_pipeline('en',use_gpu=False)
        self.skill_corpus = resume_skill_fetch.skill_corpus
    
    def extract_phone_number(self):
        items = re.finditer(r'\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}', self.resume)
        return_ = [(self.resume[item.span()[0]:item.span()[1]], item.span()) for item in items]    
        if return_:
            return return_[0]
        else:
            return None
    def extract_email(self):
        items = re.finditer(r'[\w\.-]+@[\w\.-]+', self.resume)
        return_ = [(self.resume[item.span()[0]:item.span()[1]], item.span()) for item in items]
        if return_:
            return return_[0]
        else:
            return None
    
    def extract_dob(self):
        items = re.finditer(r"[\d]{1,2}-[\d]{1,2}-[\d]{4}", self.resume)
        return_ = [(self.resume[item.span()[0]:item.span()[1]], item.span()) for item in items]
        if return_:
            return return_[0]
        else:
            return None
    
    def extract_name(self, *args):
        if len(args) and args[0] in ['en_core_web_trf', 'en_core_web_md', 'en_core_web_sm', 'en_core_web_lg']:
            doc_nmlc_ = spacy.load(args[0])(self.resume)
        elif len(args) and args[0] == 'en':
            doc_nmlc_ = spacy_stanza.load_pipeline("en",use_gpu=False)(self.resume)
        else:
            doc_nmlc_ = self.nlp_name_loc(self.resume)
        return_ = [(ent.text, (ent.start_char, ent.end_char)) for ent in doc_nmlc_.ents if ent.label_ == 'PERSON']
        if return_:
            return return_[0]
        else:
            return None

    def extract_location(self, *args):
        if len(args) and args[0] in ['en_core_web_trf', 'en_core_web_md', 'en_core_web_sm', 'en_core_web_lg']:
            doc_nmlc_ = spacy.load(args[0])(self.resume)
        elif len(args) and args[0] == 'en':
            doc_nmlc_ = spacy_stanza.load_pipeline("en",use_gpu=False)(self.resume)
        else:
            doc_nmlc_ = self.nlp_name_loc(self.resume)
        return_ = [(ent.text, (ent.start_char, ent.end_char)) for ent in doc_nmlc_.ents if ent.label_ in ['GPE', 'LOC']]
        if return_:
            return return_[0]
        else:
            return None

    def extract_skills_and_edu(self, *args):
        if len(args) and args[0] in ['en_core_web_trf', 'en_core_web_md', 'en_core_web_sm', 'en_core_web_lg']:
            doc_skills_ = spacy.load(args[0])(self.resume)
        elif len(args) and args[0] == 'en':
            doc_skills_ = spacy_stanza.load_pipeline("en",use_gpu=False)(self.resume)
        else:
            doc_skills_ = self.nlp_skills(self.resume)
        skills_edu = []
        #skills_edu.extend([ent.text.encode("ascii", "ignore").decode() for ent in doc_skills_.ents if ent.label_ in ['PRODUCT', 'ORG']])
        #nlp = spacy.load('trf_model/model-best')
        #skills_edu.extend([ent_.text for ent_ in nlp(NerTrainSet(self.file_path).resume2str()).ents])
        #skills_edu = [(ent.text, (ent.start_char, ent.end_char)) for ent in doc_skills_.ents if ent.label_ in ['PRODUCT', 'ORG']]
        tokens = [token.text.lower().encode("ascii", "ignore").decode() for token in doc_skills_ if not token.is_stop]
        skills = [skill.lower().strip().encode("ascii", "ignore").decode() for skill in self.skill_corpus]
        skillset = []
        skillset.extend([token.capitalize().encode("ascii", "ignore").decode() for token in tokens if token.lower().strip() in skills])
        resume_skills = [skill for skill in skills if skill in self.resume]
        for skill in resume_skills:
            for line in self.resume.split('\n'):
                for w in re.finditer(skill, line.lower()):
                    if w.start():
                        start_condition = line[w.start() - 1] in [',', ' ', ':', '.']
                    else:
                        start_condition = True
                    if len(line) != w.end():
                        end_condition = line[w.end()] in [',', ' ', ':', '.']
                    else:
                        end_condition = True
                    if start_condition and end_condition:
                        skillset.append(skill)
        
        #skillset.extend(
        #    [token.text.capitalize().strip().encode("ascii", "ignore").decode() for token in doc_skills_.noun_chunks if token.text.lower().strip() in skills])
        skills_edu.extend(skillset)
        return list(set(skills_edu))
    
    def extract_skills(self, *args):
        skills_edu = self.extract_skills_and_edu(*args)
        if exists('data/exclusions_skills.pkl'):
            with open('data/exclusions_skills.pkl', "rb") as fp:
                edu_company = pickle.load(fp)
            return [skill for skill in skills_edu if not any([exclusion.lower().strip() in skill.lower().strip() for exclusion in edu_company])]
        else:
            return 'Error: No exclusion list available'
        
    def output(self, *args):
        return {
            'name': self.extract_name('en'),
            'phone number': self.extract_phone_number(),
            'e-mail': self.extract_email(),
            'DoB': self.extract_dob(),
            'location': self.extract_location('en'),
            'skills': self.extract_skills('en')
        }
    
    
class edit_data:
    
    
    def __init__(self, *args):  
        self.args = list(args)
    
    def add_skills(self):
        with open('data/skills.pkl', "rb") as fp:
            skills = pickle.load(fp)
        if len(self.args) == 1 and str(type(self.args[0])) == "<class 'str'>":
            skills.append(self.args[0])
            skills = list(set(skills))
            with open('data/skills.pkl', "wb") as fp:
                pickle.dump(skills, fp)
            return 'Success'
        elif len(self.args) > 1 and all([str(type(arg)) == "<class 'str'>" for arg in self.args]):
            skills.extend(self.args)
            skills = list(set(skills))
            with open('data/skills.pkl', "wb") as fp:
                pickle.dump(skills, fp)
            return 'Success'
        else:
            return 'Please send string or comma separated sequence of strings'
        
