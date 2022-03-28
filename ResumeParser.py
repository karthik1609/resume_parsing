import textract
import spacy
import re
import pandas as pd
import stanza
import spacy_stanza
import pickle
from os.path import exists

stanza.download('en')

class parse:
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.resume = textract.process(self.file_path).decode()
        self.nlp_name_loc = spacy.load('en_core_web_trf')
        self.nlp_skills = spacy.load('en_core_web_md')
        self.nlp_edu = spacy.load('en_core_web_sm')
        self.doc_nmlc = self.nlp_name_loc(self.resume)
        self.doc_skills = self.nlp_skills(self.resume)
        self.doc_edu = self.nlp_edu(self.resume)
        self.nlp_stanza = spacy_stanza.load_pipeline('en')
    
    def extract_phone_number(self):
        items = re.finditer(r'\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}', self.resume)
        return [(self.resume[item.span()[0]:item.span()[1]], item.span()) for item in items]    
    
    def extract_email(self):
        items = re.finditer(r'[\w\.-]+@[\w\.-]+', self.resume)
        return [(self.resume[item.span()[0]:item.span()[1]], item.span()) for item in items]
    
    def extract_dob(self):
        items = re.finditer(r"[\d]{1,2}-[\d]{1,2}-[\d]{4}", self.resume)
        return [(self.resume[item.span()[0]:item.span()[1]], item.span()) for item in items]
    
    def extract_name(self, *args):
        if len(args) and args[0] in ['en_core_web_trf', 'en_core_web_md', 'en_core_web_sm', 'en_core_web_lg']:
            doc_nmlc_ = spacy.load(args[0])(self.resume)
        elif len(args) and args[0] == 'en':
            doc_nmlc_ = spacy_stanza.load_pipeline("en")(self.resume)
        else:
            doc_nmlc_ = self.doc_nmlc
        return [(ent.text, (ent.start_char, ent.end_char)) for ent in doc_nmlc_.ents if ent.label_ == 'PERSON']
    
    def extract_location(self, *args):
        if len(args) and args[0] in ['en_core_web_trf', 'en_core_web_md', 'en_core_web_sm', 'en_core_web_lg']:
            doc_nmlc_ = spacy.load(args[0])(self.resume)
        elif len(args) and args[0] == 'en':
            doc_nmlc_ = spacy_stanza.load_pipeline("en")(self.resume)
        else:
            doc_nmlc_ = self.doc_nmlc
        return [(ent.text, (ent.start_char, ent.end_char)) for ent in doc_nmlc_.ents if ent.label_ in ['GPE', 'LOC']]
    
    def extract_skills_and_edu(self, *args):
        if len(args) and args[0] in ['en_core_web_trf', 'en_core_web_md', 'en_core_web_sm', 'en_core_web_lg']:
            doc_skills_ = spacy.load(args[0])(self.resume)
        elif len(args) and args[0] == 'en':
            doc_skills_ = spacy_stanza.load_pipeline("en")(self.resume)
        else:
            doc_skills_ = self.doc_skills
        skills_edu = [ent.text.encode("ascii", "ignore").decode() for ent in doc_skills_.ents if ent.label_ in ['PRODUCT', 'ORG']]
        #skills_edu = [(ent.text, (ent.start_char, ent.end_char)) for ent in doc_skills_.ents if ent.label_ in ['PRODUCT', 'ORG']]
        tokens = [token.text.lower().encode("ascii", "ignore").decode() for token in doc_skills_ if not token.is_stop]
        with open('data/exclusions_skills.pkl', "rb") as fp:
            skill_master_list = pickle.load(fp)
        skills = [skill.lower().strip().encode("ascii", "ignore").decode() for skill in skill_master_list]
        skillset = [token.capitalize().encode("ascii", "ignore").decode() for token in tokens if token.lower().strip() in skills]
        skillset.extend(
            [token.text.capitalize().strip().encode("ascii", "ignore").decode() for token in doc_skills_.noun_chunks if token.text.lower().strip() in skills])
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

    #def extract_resume_numbering(self):
        # file_list = glob.glob(os.path.join(os.getcwd(), "/home/anudeepadi/Documents/Fw__Sample_resumes_", "*.docx"))
        # resumes = [textract.process(file_path).decode() for file_path in file_list]
        # remove /n and /r from the resumes
        # resumes = [re.sub(r'[\n\r]', '', resume) for resume in resumes]
        # for every /t in resumes[1] split the string and store it in a list
        # others = [[item] for item in resumes[1].split('\t') if (item != ' ' or item != '')]
        # for item in others:
        #     for j in item:
        #         if j == ' ' or j == '':
        #             item.remove(j)
        # # remove empty lists from the list
        # others = [x for x in others if x != []]
        # trythis = enumerate(others)
        # return list(trythis)      # remove /n and /r from the resumes

 
    def output(self, *args):
        return {
            'name': self.extract_name(),
            'phone number': self.extract_phone_number(),
            'e-mail': self.extract_email(),
            'DoB': self.extract_dob(),
            'location': self.extract_location(),
            'skills': self.extract_skills()
        }
    
    
class edit_data:
    
    
    def add_skills(*ags):
        if len(args) == 1 and type(args[0]) == 'str':
            with open('data/skills.pkl', "rb") as fp:
                skills = pickle.load(fp)
            skills.append(args[0])
            with open('data/skills.pkl', "wb") as fp:
                pickle.dump(skills, fp)
            return 'Success'
        elif len(args) > 1 and all([type(arg) == 'str' for arg in args]):
            skills.extend(args)
            with open('data/skills.pkl', "wb") as fp:
                pickle.dump(skills, fp)
            return 'Success'
        else:
            return 'Please sent string or list of strings'
        
            
            
            
        
    
    
    
    
