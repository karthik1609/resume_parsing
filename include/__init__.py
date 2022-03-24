import textract
import spacy

def __init__(self, file_path):
    self.file_path = file_path
    self.resume = textract.process(self.file_path).decode()
    self.nlp_name_loc = spacy.load('en_core_web_trf')
    self.nlp_skills = spacy.load('en_core_web_md')
    self.nlp_edu = spacy.load('en_core_web_sm')