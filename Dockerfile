FROM ubuntu:latest
LABEL author="Fiatum Group"
RUN apt-get update -y
RUN apt-get install -y python3-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 12000
ENTRYPOINT ["python3", "app.py"]
