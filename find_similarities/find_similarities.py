import os
import sys
import glob
import json
import spacy
import param
import panel as pn
import string
import pickle
import subprocess

import numpy as np
import pandas as pd
from ipyfilechooser import FileChooser


class GenerateSimilarities:
    ### Constants ###
    FILES_LOC = ""
    FILES_TYPE = "*.txt"
    BIBJSON = "bibjson.json"
    MODEL = "en_trf_bertbaseuncased_lg"
    TOKEN_FILE = "tokenizd_files_dictionary.p"
    FILE_TO_READ = ""
    RAW_CSS = '''
    .file-sim-button .bk-btn-group button {
        background: #03cafc;
        border: 1px solid #007391;
        color: #ffffff;
        border-radius: 0px;
        white-space: pre;  
        height: 50px; 
    }
    '''

    def __init__(self, folder_loc, file_loc):
        pn.extension(raw_css=[self.RAW_CSS])
        self.FILES_LOC = folder_loc
        self.FILE_TO_READ = file_loc
        self.final_data = []

    def run_similarity_finder(self):
        self.json_dict = self.parse_bibjson()
        self.FILE_TO_READ_TITLE = self.extract_json_info('_gddid', self.FILE_TO_READ.split('/')[-1].split('.')[0], 'title')
        print("Loading spaCy model...")
        # load the spacy model
        nlp = spacy.load(self.MODEL)

        print("Attempting to load token dictionary...")
        token_dict = self.get_model(nlp)

        print("Token dictionary loaded... ")
        
        filename = self.FILE_TO_READ
        sim_dict = self.compute_similarities(filename, nlp, token_dict)
        self.final_data = list(sim_dict.items())

        # Change the number of files to display
        self.prepare_display()
        self.update_table()

    def get_model(self, nlp_model):
        if os.path.isfile(self.FILES_LOC + self.TOKEN_FILE):
            return pickle.load( open(self.FILES_LOC + self.TOKEN_FILE, "rb"))
        else:
            return self.tokenize_and_vectorize_files(nlp_model)

    def parse_bibjson(self):
        with open(self.FILES_LOC + self.BIBJSON, 'r', encoding="utf-8") as f:
            data = json.load(f)
        return data

    """
    field is the name of the field in the json, value is the value to compare it to, ret_field is the field in
    the json to return once the correct value has been found
    """
    def extract_json_info(self, field, value, ret_field):
        for file_json in self.json_dict:
            if file_json[field] == value:
                return file_json[ret_field]

    def tokenize_and_vectorize_files(self, nlp_model):
        print("Token dictionary file not found... Tokenizing files, please wait:")
        files_parsed = {}
        files = glob.glob(self.FILES_LOC + self.FILES_TYPE)

        files_processed = 0

        for filename in files:
            # find the correseponding title in json
            title = self.extract_json_info('_gddid', filename[len(self.FILES_LOC):-4], 'title')

            # If we couldn't find the filename then just skip it
            if title == "":
                continue
            
            f = open(os.path.join(os.getcwd(), filename), mode='r', encoding='utf-8')
            file_text = f.read()
            
            file_failed = False
            try:
                files_parsed[(filename, title)] = nlp_model(file_text)
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
            sim_dict[name[1]] = int(similarity * 100)

        print("Computed all similarities")
        return sim_dict      

    def prepare_display(self):
        self.result_to_show_slider = pn.widgets.IntSlider(name="Results to show", start=1, end=len(self.final_data), step=1, value=3)
        self.file_column = pn.Column("Similarities", css_classes=[])
        self.result_to_show_slider.param.watch(self.update_table, ['value'])
        self.result_display = pn.Row()

    """
    Data given like 
    [ [Papername, %Sim],
      [Papername, %Sim] ]
    """
    def update_table(self, events=None):
        self.file_column.clear()
        self.result_display.clear()
        for filesim in self.final_data[:self.result_to_show_slider.value]:
            button = pn.widgets.Button(name=f"{filesim[0]}\t|\t{filesim[1]}%", margin=0, css_classes=['file-sim-button'])
            button.on_click(self.display_info_for_file)
            self.file_column.append(button)
        self.file_column.append(self.result_to_show_slider)
        self.result_display.append(self.file_column)
        display(self.result_display)

    def display_info_for_file(self, *events):
        self.update_table()
        for event in events:
            filename = event.obj.name.split('|')
            mkdn = pn.pane.Markdown(f'''
            ###{filename[0]}  
            ``{filename[1]} to`` **{self.FILE_TO_READ_TITLE}**  
            <{self.extract_json_info('title', self.FILE_TO_READ_TITLE, 'link')[0]['url']}>  
            ''')
            self.result_display.append(pn.Spacer())
            self.result_display.append(mkdn)
            display(self.result_display)

if __name__ == "__main__":
    print("Starting....")

    file_loc = sys.argv[1]
    folder_loc = sys.argv[2]
    
    gs = GenerateSimilarities(folder_loc, file_loc)
    gs.run_similarity_finder()

