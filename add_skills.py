from src.ResumeParser import edit_data
import sys

string_list = [string for string in sys.argv[1:]]
edit = edit_data(*string_list)
edit.add_skills()

