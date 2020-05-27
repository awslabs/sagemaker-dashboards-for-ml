FROM python:3.7.4-slim-stretch

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
COPY src/ src/

RUN pip install -r requirements.txt

EXPOSE 80

ENTRYPOINT [ "streamlit", "run", "src/app.py", \
             "--server.port", "80", \
             "--server.enableCORS", "true", \
             "--browser.serverAddress", "0.0.0.0", \
             "--browser.serverPort", "443"]
