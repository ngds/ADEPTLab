import sys
import os
from datetime import date

from colorama import Fore, Style, init

from src.token_class import Token
from src.output_types import spacy, stanfordnlp, rawtext
from src.notebook import file_chooser, clear

valid_inputs = ["0", "1", "2", "3", "4", "5", "6", "7"]

PARTIAL_ANNS = os.path.join("partial_annotations")

num_tokens = 0
pos = 0
window = 5
back = 0
curr_token = 0
output_dir = ""
filename = ""
internal = []
words = []
annotation_types = [spacy, stanfordnlp, rawtext]

notebook_version = False
exit_flag = False

def exit():
    # workaround exit for Jupyter notebook, if necessary
    if notebook_version:
        global exit_flag
        exit_flag = True
    else:
        sys.exit(0)

def print_status(token_idx):
    num_blocks_filled = int((token_idx/num_tokens) * 10)
    blocks_filled = '=' * num_blocks_filled
    blocks_empty = ' ' * (10 - num_blocks_filled)
    print(f"Progress: {Fore.BLUE}[{blocks_filled}{blocks_empty}]{Style.RESET_ALL} - {int(token_idx / num_tokens * 100)}% of {num_tokens} tokens")


def print_tags():
    print("TAG OPTIONS: (press enter to leave untagged, b to go back, p to save progress and exit)")
    print("0 people, including fictional\t\t4 companies, institutions, etc.")
    print("1 nationalities, religions\t\t5 countries, cities, states")
    print("2 mountains, rivers, etc.\t\t6 events--named hurricanes, etc")
    print("3 buildings, airports, etc.\t\t7 measurements (e.g. weight, distance)")

def get_partial():
    partial_versions = [file.split("partial-")[1].split(".pkl")[0] for file in os.listdir(PARTIAL_ANNS) if
                        filename + "-partial" in file]
    valid = False
    if len(partial_versions) > 0:
        for num, version in enumerate(partial_versions):
            print(str(num + 1) + ".\t" + version)
        user_choice = int(input("There is at least one partial annotation for this document."
                                " Select the partial annotation to use, or type 0 to start fresh."))
        if 0 <= user_choice <= len(partial_versions):
            valid = True
        while not valid:
            user_choice = int(input("Please type a number on the list (or 0 to start fresh)."))
            if 0 <= user_choice <= len(partial_versions):
                valid = True
        if user_choice != 0:
            global curr_token, internal, filename
            import pickle
            internal = pickle.load(open(os.path.join(PARTIAL_ANNS, filename+"-partial-"+partial_versions[user_choice-1]+".pkl"), 'rb'))
            curr_token = len(internal)


def annotate(fp):
    global num_tokens, curr_token, internal, filename, words
    filename = filename.split("/")[-1].split(".")[0]
    init()
    file = fp.readlines()
    readin(file)
    get_partial()
    while(curr_token < num_tokens):
        get_tag()

    compute_all()

def readin(file):
    global num_tokens, words
    for line in file:
        words.extend(line.split())
        if len(line.split()) > 0:
            words[-1] += '\n'
    num_tokens = len(words)

def pause():
    global filename
    import pickle
    pickle.dump(internal, open(os.path.join(PARTIAL_ANNS, filename + "-partial-" + date.today().strftime("%b-%d-%Y") + ".pkl"), 'wb'))
    print("The annotation progress so far has been saved. To continue annotating this document, simply "
          "select the document as the input document again. The program will ask if you want to use this "
          "set of annotations")
    exit()

def setup_doc():
    from src.notebook.file_chooser import doc_loc
    fp = open(doc_loc.selected)
    global num_tokens, curr_token, internal, filename, words, notebook_version
    notebook_version = True
    curr_token = 0
    filename = doc_loc.selected.split("/")[-1].split(".")[0]
    init()
    get_partial()
    file = fp.readlines()
    readin(file)
    fp.close()

def takedown():
    global output_dir, exit_flag
    if exit_flag:
       return # do nothing, just exit silently

    from src.notebook.file_chooser import output_loc
    output_dir = output_loc.selected
    compute_all()
    print("The document has been annotated! Check the output folder to see the annotations saved as files prefixed with \"" + filename + "\"")

def not_done():
    global curr_token, num_tokens, exit_flag
    return not exit_flag and curr_token < num_tokens

def get_tag():
    global back, pos, internal, curr_token, words
    curr_token_word = words[curr_token]
    print_status(curr_token)
    print_tags()
    for j in range(curr_token - window, curr_token):
        if j >= 0:
            print(words[j].strip('\n') + " ", end="")

    print(f"{Fore.GREEN} <<" + curr_token_word.strip('\n') + f">> {Style.RESET_ALL}", end="")

    for k in range(curr_token + 1, curr_token + window + 1):
        if k < len(words):
            print(" " + words[k].strip('\n'), end="")

    if len(internal) <= curr_token:
        # add current token to internal list
        internal.append(Token(words[curr_token], pos, len(words[curr_token])))

    tag = input("\n\tTAG? ")
    if tag == "b" and curr_token > 0:
        pos -= internal[curr_token - 1].length + 1 # step back to the beginning of last word
        curr_token -= 1
    elif tag == "p":
        pause()
    elif tag == "" or tag in valid_inputs:
        if tag in valid_inputs:
            internal[curr_token].tag = tag
        pos += internal[curr_token].length + 1
        curr_token += 1
    else:
        print(f"\n{Fore.RED}Sorry, not sure what that meant. Try again.{Style.RESET_ALL}")
    print()


def compute_all():
    global internal, output_dir, filename
    for tok in internal:
        for output_type in annotation_types:
            output_type.add_annotation(tok)
    for output_type in annotation_types:
        output_type.finalize(output_dir, filename)

if __name__ == "__main__":
    init()
    if len(sys.argv) < 3:
        print(f"{Fore.RED}Please provide both a file to annotate and an output directory. Exiting now.{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)
    else:
        filename = sys.argv[1]
        output_dir = sys.argv[2]
        if len(sys.argv) > 3:
            window = int(sys.argv[3])

    if not os.path.isdir(output_dir):
        print(f"{Fore.RED}The output directory is not a valid directory. Exiting now.{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)
    try:
        annotate(open(filename, encoding="utf8"))
    except FileNotFoundError:
        print(f"{Fore.RED}The file to annotate was not found. Exiting now.{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)
