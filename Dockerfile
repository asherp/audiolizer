FROM continuumio/miniconda3:latest

RUN conda install -c conda-forge jupyter \
 && conda install -c plotly jupyter-dash \
 && conda install pyaudio \
 && pip install dash-daq dash-audio-components pandas \
	Historic-Crypto audiogen-p3 MIDIUtil mkdocs \
	mkdocs-material jupytext dash-bootstrap-components \
 && pip install git+https://github.com/predsci/psidash.git

COPY . /home/audiolizer

WORKDIR /home/audiolizer/audiolizer

ENV AUDIOLIZER_TEMP /home/audiolizer/audiolizer/history

CMD python audiolizer.py
# CMD jupyter notebook audiolizer/audiolizer.py --port=8888 --no-browser --ip=0.0.0.0 --allow-root