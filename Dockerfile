FROM continuumio/miniconda3 AS builder

RUN conda create -n audiolizer python==3.8
RUN conda activate audiolizer \
 && conda install -c conda-forge conda-pack \
 && conda install -c conda-forge jupyter \
 && conda install -c plotly jupyter-dash \
 && conda install pyaudio \
 && pip install dash-daq dash-audio-components pandas \
	Historic-Crypto audiogen-p3 MIDIUtil mkdocs \
	mkdocs-material jupytext dash-bootstrap-components \
 && pip install git+https://github.com/predsci/psidash.git \
 && conda-pack -n audiolizer -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# RUN conda-pack -n audiolizer -o /tmp/env.tar && \
#   mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
#   rm /tmp/env.tar

RUN /venv/bin/conda-unpack

FROM python:3.8-slim-buster AS runtime

# Copy /venv from the previous stage:
COPY --from=builder /venv /venv

COPY . /home/audiolizer

WORKDIR /home/audiolizer/audiolizer

ENV AUDIOLIZER_TEMP /home/audiolizer/audiolizer/history

# CMD jupyter notebook audiolizer/audiolizer.py --port=8888 --no-browser --ip=0.0.0.0 --allow-root

# When image is run, run the code with the environment
# activated:
SHELL ["/bin/bash", "-c"]
ENTRYPOINT source /venv/bin/activate && \
           python audiolizer.py


