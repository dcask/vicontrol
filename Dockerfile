FROM python:3.11.2-alpine

EXPOSE 80

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install uvicorn
RUN pip uninstall jwt
RUN pip install pyjwt
RUN pip install pymongo
RUN pip install requests
RUN pip install fastapi[standard]
RUN pip install cryptography
RUN pip install paramiko

CMD ["uvicorn", "main:app", "--host","0.0.0.0", "--port", "80"]