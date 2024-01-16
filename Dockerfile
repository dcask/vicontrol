FROM python:3.11.2-alpine

EXPOSE 80

RUN mkdir -p /app
COPY ./app /app

WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip uninstall jwt
RUN pip install -r /app/requirements.txt

CMD ["uvicorn", "main:app", "--host","0.0.0.0", "--port", "80"]