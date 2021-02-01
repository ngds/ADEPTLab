from string import punctuation, whitespace
import os

spacy_partial = []
converter = {"0": "PERSON", "1": "NORP", "2": "LOC", "3": "FAC",
             "4": "ORG", "5": "GPE", "6": "EVENT", "7": "QUANTITY"}
filename_end = "-spacy.pkl"

def add_annotation(tok):
    spacy_tag = converter.get(tok.tag, -1)
    if spacy_tag != -1:
        left_tok = tok.word.lstrip(punctuation)
        clean_tok = tok.word.strip(whitespace).strip(punctuation)
        if tok.word[0] != left_tok[0]:
            tok.pos += len(tok.word) - len(left_tok)  # move start right
        tok.length = len(clean_tok)  # moves end left, if necessary

        # span selection
        if len(spacy_partial) != 0 and spacy_partial[-1][1] == tok.pos - 1 and spacy_partial[-1][2] == spacy_tag:
            spacy_partial[-1] = (spacy_partial[-1][0], tok.pos + tok.length, spacy_tag)
        else:
            spacy_partial.append((tok.pos, tok.pos + tok.length, spacy_tag))

def finalize(output_folder, filename):
    import pickle
    file = os.path.join(output_folder, filename + filename_end)
    with open(file, 'wb+') as f:
        pickle.dump(spacy_partial, f)