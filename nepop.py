from src.TagPopulator import NerTrainSet
import sys
from tqdm import tqdm

file_list = [file for file in sys.argv[1:] if file.split('.')[-1] in ['docx', 'pdf']]

for idx, file in zip(tqdm(range(len(file_list))),file_list):
    print(file)
    NerTrainSet(file).file_io()

