FROM continuumio/miniconda3 AS builder

RUN conda create -n audiolizer python==3.7

# Make RUN commands use the new environment:
RUN echo "conda activate audiolizer" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]

RUN conda install defaults::conda-pack
RUN conda install pandas
RUN conda install -c conda-forge jupyter 
RUN conda install -c plotly jupyter-dash 
RUN conda install pyaudio
RUN conda install git

FROM builder AS build1

RUN conda-pack -n audiolizer -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# RUN conda-pack -n audiolizer -o /tmp/env.tar && \
#   mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
#   rm /tmp/env.tar

RUN /venv/bin/conda-unpack

FROM python:3.7-slim-buster AS runtime

# Copy /venv from the previous stage:
COPY --from=build1 /venv /venv

SHELL ["/bin/bash", "-c"]
RUN source /venv/bin/activate


# Don't know how to install with conda
RUN pip install dash-daq dash-audio-components pandas \
	Historic-Crypto audiogen-p3 MIDIUtil mkdocs \
	mkdocs-material jupytext dash-bootstrap-components 
RUN pip install git+https://github.com/predsci/psidash.git


COPY . /home/audiolizer

WORKDIR /home/audiolizer/audiolizer

ENV AUDIOLIZER_TEMP /home/audiolizer/audiolizer/history

# CMD jupyter notebook audiolizer/audiolizer.py --port=8888 --no-browser --ip=0.0.0.0 --allow-root

# When image is run, run the code with the environment
# activated:
SHELL ["/bin/bash", "-c"]
ENTRYPOINT source /venv/bin/activate && \
           python audiolizer.py


