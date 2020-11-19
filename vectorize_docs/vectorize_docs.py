import sys
import json
import time
import spacy
import pickle
import requests
import asyncio
import panel as pn
from requests.exceptions import HTTPError
from ipyfilechooser import FileChooser
import ipywidgets as widgets


MODEL = "en_vectors_web_lg"
DOCS_PER_PICKLE = 10
OUTPUT_LOC = ""

PARSED_JSON = None

api_list = {}
button_list = {}

def init(json_loc, output_loc):
    global PARSED_JSON, OUTPUT_LOC
    pn.extension()
    PARSED_JSON = json.loads(open(json_loc, 'r', encoding='utf-8').read())
    OUTPUT_LOC = output_loc
    print("Init")
    asyncio.create_task(get_apis_to_download())

def wait_for_change(widget):
    future = asyncio.Future()
    def getvalue(change):
        future.set_result(change.description)
        widget.on_click(getvalue, remove=True) 
        # we need to free up the binding to getvalue to avoid an InvalidState error
        # buttons don't support unobserve
        # so use `remove=True` 
    widget.on_click(getvalue)
    return future

"""
given the parsed json from a file with API url,key, and products will request them and combine
them into a single dataset
"""
def download_data():
    print("Downloading data")
    if PARSED_JSON is None:
        exit()
    
    base_url = PARSED_JSON.get("url").get("endpoint")
    products = PARSED_JSON.get("products")[0].get("product")
    """ Not sure how to combine pructs into query, needs clarification
    for product in self.PARSED_JSON["products"]:
        products = f"{products}"
    """
    docs = dict()
    for api_name in button_list.keys():
        if button_list.get(api_name).value == False:
            continue
        try:
            api_url = f'{base_url}?api_key={api_list.get(api_name)}&products={products}'
            print("Requesting " + api_name + "...")
            response = requests.get(api_url)
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
            resp_json = response.json()
            print("Prepping " + api_name + "...")
            docs[api_name] = parse_api_response(resp_json, products)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
    return docs

"""
given the json response of an API call, parses out the documents and returns the fulltexts
compiled together
"""
def parse_api_response(resp_json, product):
    doc_fulltexts = []

    results = resp_json.get("success").get("data").get("results")

    for result in results:
        sections = result.get(product).get("metadata").get("sections")

        fulltext = ""
        if sections:
            for section in sections:
                if section.get("heading"):
                    fulltext += section.get("heading") + "\n"
                fulltext += section.get("text") + "\n"
        
        abstract = result.get(product).get("metadata").get("abstractText")
        if abstract is not None:
            fulltext += abstract + '\n'
        
        doc_fulltexts.append(fulltext)
    
    return doc_fulltexts

def tokenize_and_vectorize_files(docs):
    nlp = spacy.load(MODEL)

    files_parsed = {}
    num_processed = 0
    time_total = time.time()
    for title in docs.keys():
        print("Vectorizing docs from " + title)
        fulltexts = docs.get(title)
        i = 0
        for file_text in fulltexts:
            timestart = time.time()
            num_processed += 1

            try:
                # TODO: Change naming scheme
                files_parsed[f"{title}_{i}"] = nlp(file_text)
                i += 1
            except Exception as e:
                print(str(e))
            time_end = time.time()
            if num_processed % DOCS_PER_PICKLE == 0:
                pickle.dump(files_parsed, 
                    open(f"{OUTPUT_LOC}v_{title}{num_processed - DOCS_PER_PICKLE}to{num_processed}.p", 
                    "wb"))
                files_parsed = {}
            print(f"Current: {time_end - timestart}\tAvg: {(time_end - time_total) / num_processed}")
        print("Finished " + title)
    pickle.dump(files_parsed, 
                open(f"{OUTPUT_LOC}v_{title}{num_processed - (num_processed % DOCS_PER_PICKLE)}to{num_processed}.p", 
                "wb"))
        
def submit():
    for button in button_list.values():
        button.disabled = True
    print("Disabled buttons")
    docs = download_data()
    print("Downloaded data")
    tokenize_and_vectorize_files(docs)

async def get_apis_to_download():
    for api in PARSED_JSON.get("testsets"):
        name = api.get("name")
        api_list[name] = api.get("key")
        button_list[name] = pn.widgets.Checkbox(name=name)
        display(button_list.get(name))

    submit_button = widgets.Button(description="Submit")
    display(submit_button)
    await wait_for_change(submit_button)
    submit()
        


print("Starting...")

json_loc = sys.argv[1]
output_filename = sys.argv[2]
output_filename = output_filename.strip('\\/') + '/'
print("Json loc: " + str(json_loc))
print("Output loc: " + str(output_filename))

init(json_loc, output_filename)
