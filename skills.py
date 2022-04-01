import sys
import spacy
from tqdm import tqdm
from src.TagPopulator import NerTrainSet

file_list = [file for file in sys.argv[1:] if file.split('.')[-1] in ['docx', 'pdf']]

nlp = spacy.load('output/model-best')

for file in file_list:
    print(set([ent_.text for ent_ in nlp(NerTrainSet(file).resume2str()).ents]))