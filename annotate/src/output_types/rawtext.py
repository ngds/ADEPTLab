import os

rawtext_partial = ""
filename_end = "-rawtext.txt"

def add_annotation(tok):
    global rawtext_partial
    rawtext_partial += tok.word + " "

def finalize(output_folder, filename):
    global rawtext_partial, filename_end
    file = os.path.join(output_folder, filename + filename_end)
    with open(file, 'w+', encoding="utf8") as f:
        f.write(rawtext_partial)
