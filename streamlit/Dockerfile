FROM continuumio/miniconda3

WORKDIR /home/app

RUN apt-get update
RUN apt-get install nano unzip
RUN apt install curl -y
#RUN pip install pandas streamlit scikit-learn plotly numpy openpyxl
COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

COPY . /home/app

CMD streamlit run --server.port $PORT app.py