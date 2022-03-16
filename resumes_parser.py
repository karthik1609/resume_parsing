import re
import spacy
from spacy.matcher import Matcher

class parse:
    def __init__(self, resume):
        self.resume = resume

    def extract_phone_number(self):
        items = re.finditer(r'\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}', self.resume)
        ph_span = [(self.resume[item.span()[0]:item.span()[1]], item.span()) for item in items]
        return ph_span
    
    def extract_email(self):
        items = re.finditer(r'[\w\.-]+@[\w\.-]+', self.resume)
        em_span = [(self.resume[item.span()[0]:item.span()[1]], item.span()) for item in items]
        return em_span
       
    def extract_name(resume):
        nlp = spacy.load('en_core_web_sm')
        matcher = Matcher(nlp.vocab)
        nlp_text = nlp(resume)
        pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
        matcher.add('NAME', [pattern])
        matches = matcher(nlp_text)

        for match_id, start, end in matches:
            span = nlp_text[start:end]
            return span.text

    def extract_location(self):
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(self.resume)
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC']:
                ls = list(ent.text)
        string = ''.join(ls)
        return string