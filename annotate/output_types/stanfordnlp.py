from string import punctuation
import os

stanford_partial = []
converter = {"0": "PERSON", "1": "O", "2": "LOCATION", "3": "O",
             "4": "O", "5": "LOCATION", "6": "O", "7": "O"}
filename_end = "-stanford.tsv"

def init():
    global stanford_partial
    stanford_partial = []

def add_annotation(tok):
    clean_tok = tok.word.strip(punctuation)
    stanford_tag = converter.get(tok.tag, 'O')
    stanford_partial.append(clean_tok + "\t" + stanford_tag + "\n")


def finalize(output_folder, filename):
    file = os.path.join(output_folder, filename + filename_end)
    with open(file, 'w+', encoding="utf8") as f:
        f.writelines(stanford_partial)