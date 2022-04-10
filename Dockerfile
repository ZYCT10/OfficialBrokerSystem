FROM ubuntu:latest
LABEL author="Fiatum Group"
RUN apt-get update -y
RUN apt-get install -y python3-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 12000
ENV BROKER_API_KEY="4FvCCc2h8H2TlNKXrpddZRAkB9qRVIlbDIOBZ3D9k9IWwbgt8NhQpp83spQ5E6Ml"
ENV BROKER_API_SECRET="KZRdux9jA4q3VE43ePkhmx63kdFSn04IS0FEKbIDggZlaRyC0fVuFPCd0nv1Hii8"
ENV SECURITY_TOKEN="superFiatumTokenForBinance019291029"
ENTRYPOINT ["python3", "app.py"]