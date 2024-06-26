FROM python:3.10

WORKDIR /app

# requirements.txt in das Arbeitsverzeichnis kopieren
#COPY requirements.txt .
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000

# Definiere den Befehl zum Starten der Anwendung
CMD python ./sciencehub.py
