import spacy
import string
import glob
import json
import sys
import os

import pickle
import pandas as pd
import numpy as np
import mplcursors
import matplotlib.pyplot as plt

from ipyfilechooser import FileChooser



class GenerateSimilarities:
    ### Constants ###
    FILES_LOC = ""
    FILES_TYPE = "*.txt"
    BIBJSON = "bibjson.json"
    MODEL = "en_trf_bertbaseuncased_lg"
    TOKEN_FILE = "tokenizd_files_dictionary.p"
    COL_TITLES = ('Title', 'Similarity')
    FILE_TO_READ = ""

    def __init__(self, folder_loc, file_loc):
        self.FILES_LOC = folder_loc
        self.FILE_TO_READ = file_loc

    def parse_bibjson(self):
        with open(self.FILES_LOC + self.BIBJSON, 'r', encoding="utf-8") as f:
            data = json.load(f)
        return data

    def tokenize_and_vectorize_files(self, nlp_model):
        print("Token dictionary file not found... Tokenizing files, please wait:")
        files_parsed = {}
        files = glob.glob(self.FILES_LOC + self.FILES_TYPE)

        json_dict = self.parse_bibjson()
        files_processed = 0

        for filename in files:
            # find the correseponding title in json
            title = ""
            for file_json in json_dict:
                if file_json['_gddid'] == filename[len(self.FILES_LOC):-4]:
                    title = file_json['title']
                    break
            # If we couldn't find the filename then just skip it
            if title == "":
                continue
            
            f = open(os.path.join(os.getcwd(), filename), mode='r', encoding='utf-8')
            file_text = f.read()
            
            file_failed = False
            try:
                files_parsed[(filename, title[:10] + "...")] = nlp_model(file_text)
            except Exception as e:
                f.close()
                file_failed = True
                print(str(e))
            finally:
                files_processed += 1
                print("Processed file [", files_processed, "/", (len(files)), "] - ", filename, end="")
                if file_failed:
                    print("   [FAILED]")
                else:
                    print()

        # Save the tokens to a file so we don't have to parse them again            
        pickle.dump(files_parsed, open(self.FILES_LOC + self.TOKEN_FILE, "wb"))

        return files_parsed        

    def get_model(self, nlp_model):
        if os.path.isfile(self.FILES_LOC + self.TOKEN_FILE):
            return pickle.load( open(self.FILES_LOC + self.TOKEN_FILE, "rb"))
        else:
            return self.tokenize_and_vectorize_files(nlp_model)

    def compute_similarities(self, filename, nlp_model, token_dict):
        print("Calculating similarities")
        if not os.path.isfile(filename):
            print(f"Couldn't find file {filename}! Please make sure that the file exists in the directory and is visible")
            return
        
        with open(filename, mode='r', encoding="utf-8") as f:
            text = f.read()
        new_file_tokens = nlp_model(text)

        # this holds filename:percent
        sim_dict = {}
        for name, tokens in token_dict.items():
            similarity = tokens.similarity(new_file_tokens)
            # round to 2 decimal places
            sim_dict[name[1]] = (similarity * 100)  

        print("Computed all similarities")
        return sim_dict      

    def plot_similarities(self, sim_dict, num_to_display):
        sorted_dict = {k: v for k, v in sorted(sim_dict.items(), key = lambda item: item[1])}

        fig, (ax1, ax2) = plt.subplots(1, 2)

        ax1.set_xticks([])
        ax1.set_yticks([])
        ax1.axis('off')

        fig.suptitle(f"Similarities to [INSERT FILENAME]")

        cell_text = [[str(item[0]), str(round(item[1], 1)) + '%'] for item in list(sorted_dict.items())]

        table = ax1.table(cellText=cell_text, colLabels=self.COL_TITLES, loc='center')
        table.scale(1, 2)
        ax2.plot([1], [1])
        plt.show()

    def run_similarity_finder(self):
        print("Loading spaCy model...")
        # load the spacy model
        nlp = spacy.load(self.MODEL)

        print("Attempting to load token dictionary...")
        token_dict = self.get_model(nlp)

        print("Token dictionary loaded... ")
        
        filename = self.FILE_TO_READ
        sim_dict = self.compute_similarities(filename, nlp, token_dict)

        # Change the number of files to display
        self.plot_similarities(sim_dict, 4)

        

       
if __name__ == "__main__":
    print("Starting...")

    file_loc = sys.argv[1]
    folder_loc = sys.argv[2]

    gs = GenerateSimilarities(folder_loc, file_loc)
    gs.run_similarity_finder()