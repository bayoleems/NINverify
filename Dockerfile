FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install --upgrade pip

RUN  python -m pip install -r requirements.txt

RUN  python -m playwright install chromium

RUN  python -m playwright install-deps  

COPY . /app

EXPOSE 300

CMD [ "python", "app.py" ]