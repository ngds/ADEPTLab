# ADEPT Lab

A Dockerized Jupyter Lab repository for ADEPT notebooks. The collection includes:
+ An NER annotator
+ A Doc2Vec vectorizer
+ A document similarity finder
+ A spaCy NER model trainer

## Running ADEPTLab locally
#### To use the latest ADEPTLab docker image:
1. Pull the image with `docker pull josephacevedo/adept_lab`
2. Run the image locally with 
``docker run -it --rm -v /$HOME:/app --workdir /app -p 8888:8888 -e REDIRECT_URL=http://localhost:8888 josephacevedo/adept_lab``

#### To build ADEPTLab from source:
1. Clone the repo from Github at https://github.com/ngds/ADEPTLab
2. Build the docker image with ``docker build -t [TAG NAME] .`` where [TAG NAME] is the name of the tag you want ot give it.
3. Run the image with `docker run` command above, changing 'josephacevedo/adept_lab' to [TAG NAME]

## An overview of each of the notebooks
### NER Annotator
The NER annotator takes in a text file and has a user label each word in the file as either one of the listed named entities, or as not an entity. The list of entity tags can be changed by modifying the source file and adding/removing the tags. At any point the user can stop tagging the file and it will save three output files to the selected directory:
+ A file containing the tags in a form usable with Standford CoreNLP
+ A file containing the tags in a form usable with spaCy
+ The rawtext of the file

### Doc2Vec Vectorizer
The vectorizer takes in a JSON file that contains an API url and the products to gather from the url (designed for use with NGDS). It requests all of the files and uses spaCy to vectorize them and saves the vectorized collection into pickle files that contain subsets of the collection. These can be loaded at a later point to be used for various other tasks

### Document Similarity Finder
Takes in the location of a folder of files, and a specific file and will attempt to find the most similar file in the folder. All of the files are vectorized and then a simple distance measure is used to find how similar two files are to each other. The top results are displayed using Python Panel, a jupyter lab display

### spaCy NER model trainer
Takes in the output of the NER annotator and creates/updates a model with the new tags.
