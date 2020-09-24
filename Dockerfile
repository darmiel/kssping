FROM python:3
LABEL maintainer="d2a <admin@d2a.io>"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./check.py" ]