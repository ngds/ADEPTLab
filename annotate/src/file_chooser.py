from IPython.core.display import display
from ipyfilechooser import FileChooser

doc_loc = FileChooser()
output_loc = FileChooser()

def choose():
    global doc_loc, output_loc

    print("Document to tag (.txt file):")
    display(doc_loc)
    print("Output folder to save annotations to:")
    display(output_loc)