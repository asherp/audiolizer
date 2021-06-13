FROM continuumio/miniconda3:latest

RUN conda install jupyter

RUN conda install -c conda-forge -c plotly jupyter-dash

RUN pip install dash-daq
RUN pip install dash-audio-components
RUN pip install git+https://github.com/predsci/psidash.git
RUN pip install pandas
RUN pip install Historic-Crypto

# RUN mkdir /temp
# ENV AUDIOLIZER_TEMP /temp

COPY . /home

WORKDIR /home

CMD jupyter notebook audiolizer/audiolizer.py --port=8888 --no-browser --ip=0.0.0.0 --allow-root