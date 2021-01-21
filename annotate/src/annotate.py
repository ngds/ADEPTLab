import sys
from colorama import Fore, Style, init
from IPython.display import clear_output

from src.token import Token
from output_types import spacy, stanfordnlp, rawtext

valid_inputs = ["0", "1", "2", "3", "4", "5", "6", "7"]

num_tokens = 0
pos = 0
window = 5
back = 0
words = []
curr_token = 0
output_dir = ""
filename = ""
internal = []
annotation_types = [spacy, stanfordnlp, rawtext]


def print_status(token_idx):
    num_blocks_filled = int((token_idx/num_tokens) * 10)
    blocks_filled = '=' * num_blocks_filled
    blocks_empty = ' ' * (10 - num_blocks_filled)
    print(f"Progress: {Fore.BLUE}[{blocks_filled}{blocks_empty}]{Style.RESET_ALL} - {int(token_idx / num_tokens * 100)}% of {num_tokens} tokens")


def print_tags():
    print("TAG OPTIONS: (press enter to leave untagged, b to go back)")
    print("0 people, including fictional\t\t4 companies, institutions, etc.")
    print("1 nationalities, religions\t\t5 countries, cities, states")
    print("2 mountains, rivers, etc.\t\t6 events--named hurricanes, etc")
    print("3 buildings, airports, etc.\t\t7 measurements (e.g. weight, distance)")

def setup_doc():
    from src.file_chooser import doc_loc
    fp = open(doc_loc.selected)
    global num_tokens, curr_token, internal, filename, words
    curr_token = 0
    filename = doc_loc.selected.split("/")[-1].split(".")[0]
    init()
    file = fp.read()
    words = file.split()
    num_tokens = len(words)
    fp.close()

def takedown():
    global output_dir
    from src.file_chooser import output_loc, doc_loc
    output_dir = output_loc.selected
    compute_all()
    print("The document has been annotated! Check the output folder to see the annotations saved as files prefixed with \"" + filename + "\"")

def annotate(fp):
    global num_tokens, curr_token, internal, filename
    filename = filename.split("/")[-1].split(".")[0]
    init()
    file = fp.read()
    words = file.split()
    num_tokens = len(words)
    while(curr_token < num_tokens):
        clear_output(wait=True)
        get_tag(words[curr_token], words)

    compute_all()

    for tok in internal:
        print(tok)

def not_done():
    global curr_token, num_tokens
    return curr_token < num_tokens

def get_tag():
    global back, pos, internal, curr_token, words
    curr_token_word = words[curr_token]
    clear_output(wait=True)
    print_status(curr_token)
    print_tags()
    for j in range(curr_token - window, curr_token):
        if j >= 0:
            print(words[j] + " ", end="")

    print(f"{Fore.GREEN} <<" + curr_token_word + f">> {Style.RESET_ALL}", end="")

    for k in range(curr_token + 1, curr_token + window + 1):
        if k < len(words):
            print(" " + words[k], end="")

    if len(internal) <= curr_token:
        # add current token to internal list
        internal.append(Token(words[curr_token], pos, len(words[curr_token])))

    tag = input("\n\tTAG? ")
    if tag == "b" and curr_token > 0:
        pos -= internal[curr_token - 1].length + 1 # step back to the beginning of last word
        curr_token -= 1
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

    # avoid duplication issue with notebook version by resetting internal values
    for output_type in annotation_types:
        output_type.init()

    for tok in internal:
        for output_type in annotation_types:
            output_type.add_annotation(tok)
    for output_type in annotation_types:
        output_type.finalize(output_dir, filename)

def prompt_for_file_or_dir():
    pass


if __name__ == "__main__":
    init()
    if len(sys.argv) < 3:
        filename = prompt_for_file_or_dir()
    else:
        filename = sys.argv[1]
        output_dir = sys.argv[2]
        if len(sys.argv) > 3:
            window = int(sys.argv[3])

    annotate(open(filename, encoding="utf8"))


"""
error handling for files
write to out formats
pause mid-annotating file
strip punctuation from spacy distances ?
fix line endings
make going back work for tags
combine spacy tags
"""