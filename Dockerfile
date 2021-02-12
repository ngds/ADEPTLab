FROM jupyter/scipy-notebook:68d2d835fb16

USER root

RUN mkdir /opt/config

RUN mkdir /home/jovyan/base

ADD requirements.txt /opt/config

RUN pip install spacy

RUN python -m spacy download en_core_web_trf


# Install a few dependencies for iCommands, text editing, and monitoring instances
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    gcc \
    gnupg \
    htop \
    less \
    libfuse2 \
    libpq-dev \
    libssl1.0 \
    lsb \
    nano \
    nodejs \
    software-properties-common \
    vim

RUN python -m pip install requests
    
# Install iCommands
# RUN wget -qO - https://packages.irods.org/irods-signing-key.asc | apt-key add - \
#    && echo "deb [arch=amd64] https://packages.irods.org/apt/ bionic main" | tee /etc/apt/sources.list.d/renci-irods.list \
#    && apt-get update && apt-get install -y irods-runtime irods-icommands

# Install Jupyter SQL
RUN pip install ipython-sql jupyterlab_sql psycopg2 \
    && conda update -n base conda \
    && conda install -c conda-forge nodejs \
    && jupyter serverextension enable jupyterlab_sql --py --sys-prefix \
    && jupyter lab build

# install the irods plugin for jupyter lab -- non-functional beyond JupyterLab v1.0.9
RUN pip install jupyterlab_irods \
    && jupyter serverextension enable --py jupyterlab_irods \
    && jupyter labextension install ijab

# install jupyterlab hub-extension, lab-manager, bokeh
RUN jupyter lab --version \
    && jupyter labextension install --debug @jupyter-widgets/jupyterlab-manager
                                    

# install jupyterlab git extension
RUN jupyter labextension install @jupyterlab/git && \
        pip install --upgrade jupyterlab-git && \
        jupyter serverextension enable --py jupyterlab_git

# install jupyterlab github extension
RUN jupyter labextension install @jupyterlab/github

RUN jupyter labextension install @pyviz/jupyterlab_pyviz

# Install and configure jupyter lab.
COPY jupyter_notebook_config.json /opt/conda/etc/jupyter/jupyter_notebook_config.json

# Add the jovyan user to UID 1000
RUN groupadd jovyan && usermod -aG jovyan jovyan && usermod -d /home/jovyan -u 1000 jovyan
RUN chown -R jovyan:jovyan /home/jovyan

# copy over program files
RUN pip install jupyterlab

RUN pip install -r /opt/config/requirements.txt

RUN pip install ipywidgets

WORKDIR /home/jovyan/base

COPY find_similarities/ find_similarities/

COPY vectorize_docs/ vectorize_docs/

COPY annotate/ annotate/

COPY train_model/ train_model/

RUN chmod -R 777 /home/jovyan/base

RUN jupyter serverextension enable --py jupyterlab --sys-prefix

USER jovyan

RUN mkdir /home/jovyan/test_dir

EXPOSE 8888

COPY entry.sh /bin
RUN mkdir -p /home/jovyan/.irods

ENTRYPOINT ["bash", "/bin/entry.sh"]