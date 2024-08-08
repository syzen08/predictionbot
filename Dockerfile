FROM python:3.12.5-slim

WORKDIR /app

COPY ./src/ /app
COPY ./requirements.txt /app
COPY ./token.txt /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD [ "python" , "main.py"]