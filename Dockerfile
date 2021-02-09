FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y nano mariadb-server

RUN curl -sSL https://sdk.cloud.google.com > /tmp/gcl && bash /tmp/gcl --install-dir=/root --disable-prompts

ENV PATH $PATH:/root/google-cloud-sdk/bin

RUN gcloud components install kubectl -q --no-user-output-enabled 

COPY . .
COPY credentials.json credentials.json

RUN gcloud auth activate-service-account --key-file credentials.json

# Individual kubernetes clusters can be added here: 
RUN gcloud container clusters get-credentials <cluster name> --zone <zone> --project <project>
RUN kubectl config rename-context <old cluster context> <new cluster context>

EXPOSE 5000

ENV FLASK_APP=src/main.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["sh", "-c", "gunicorn -w 4 -t 100 -k gevent -b 0.0.0.0:5000 main:app --chdir src"]
