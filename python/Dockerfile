FROM python:3.10-alpine

RUN addgroup -S mercari && adduser -S trainee -G mercari
# RUN chown -R trainee:mercari /path/to/db

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN pip3 install uvicorn

COPY main.py main.py

COPY ./db/mercari.sqlite3 /db/mercari.sqlite3

VOLUME /db

USER trainee


CMD ["sh", "-c", "uvicorn main:app --reload --port 9000"]
