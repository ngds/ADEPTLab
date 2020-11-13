import sys
import json
import time
import spacy
import pickle
import requests
from requests.exceptions import HTTPError
from ipyfilechooser import FileChooser


class VectorizeDocs:

    MODEL = "en_vectors_web_lg"
    DOCS_PER_PICKLE = 10

    def __init__(self, json_loc, output_loc):
        self.PARSED_JSON = json.loads(open(json_loc, 'r', encoding='utf-8').read())
        self.OUTPUT_LOC = output_loc

    """
    given the parsed json from a file with API url,key, and products will request them and combine
    them into a single dataset
    """
    def download_data(self):
        if self.PARSED_JSON is None:
            exit()
        
        base_url = self.PARSED_JSON.get("url").get("endpoint")
        products = self.PARSED_JSON.get("products")[0].get("product")
        """ Not sure how to combine pructs into query, needs clarification
        for product in self.PARSED_JSON["products"]:
            products = f"{products}"
        """
        docs = dict()
        for dataset in self.PARSED_JSON.get("testsets"):
            try:
                api_url = f'{base_url}?api_key={dataset.get("key")}&products={products}'
                print("Trying " + api_url)
                response = requests.get(api_url)
                # If the response was successful, no Exception will be raised
                response.raise_for_status()
                resp_json = response.json()
                print("Parsing " + dataset.get("name"))
                docs[dataset.get("name")] = self.parse_api_response(resp_json, products)
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')  # Python 3.6
            except Exception as err:
                print(f'Other error occurred: {err}')  # Python 3.6
        return docs

    """
    given the json response of an API call, parses out the documents and returns the fulltexts
    compiled together
    """
    def parse_api_response(self, resp_json, product):
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

    def tokenize_and_vectorize_files(self, docs):
        nlp = spacy.load(self.MODEL)

        files_parsed = {}
        num_processed = 0
        time_total = time.time()
        for title in docs.keys():
            fulltexts = docs.get(title)
            i = 0
            for file_text in fulltexts:
                timestart = time.time()
                num_processed += 1

                try:
                    files_parsed[f"{title}_{i}"] = nlp(file_text)
                    i += 1
                    print("Vectorizing file in " + title + str(i))
                except Exception as e:
                    print(str(e))
                time_end = time.time()
                if num_processed % self.DOCS_PER_PICKLE == 0:
                    pickle.dump(files_parsed, 
                        open(f"{self.OUTPUT_LOC}v_{title}{num_processed - self.DOCS_PER_PICKLE}to{num_processed}.p", 
                        "wb"))
                    files_parsed = {}
                print(f"Current: {time_end - timestart}\tAvg: {(time_end - time_total) / num_processed}")
            
        pickle.dump(files_parsed, 
                    open(f"{self.OUTPUT_LOC}v_{title}{num_processed - (num_processed % self.DOCS_PER_PICKLE)}to{num_processed}.p", 
                    "wb"))
            

        


if __name__ == "__main__":
    print("Starting...")

    json_loc = sys.argv[1]
    output_filename = sys.argv[2]
    print("Json loc: " + str(json_loc))
    print("Output loc: " + str(output_filename))

    vd = VectorizeDocs(json_loc, output_filename)
    # {'title': [doc1, doc2], 'title': [doc1, doc2] ... }
    docs = vd.download_data()
    vd.tokenize_and_vectorize_files(docs)