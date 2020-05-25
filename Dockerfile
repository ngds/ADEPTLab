FROM cyversevice/jupyterlab-base

COPY jupyter_notebook_config.json /opt/conda/etc/jupyter/jupyter_notebook_config.json

RUN mkdir /opt/config

RUN mkdir /opt/base

ADD requirements.txt /opt/config/

COPY find_similarities/ /opt/base/find_similarities/

RUN pip install -r /opt/config/requirements.txt

RUN python -m spacy download en_trf_bertbaseuncased_lg

### START DATA TRANSFER
COPY test_data/ /opt/base/test_data/
### END DATA TRANSFER

ENTRYPOINT ["jupyter", "lab", "/opt/base/find_similarities/find_similarities.ipynb"]