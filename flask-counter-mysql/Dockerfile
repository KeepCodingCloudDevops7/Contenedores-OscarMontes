FROM python:3.7-alpine as compile

RUN apk add --no-cache gcc musl-dev linux-headers curl mysql-client mysql-dev 

WORKDIR /app
COPY . ./

RUN pip install --prefix=/install -r requirements.txt

FROM python:3.7-alpine as final
RUN apk add --no-cache mysql-client mysql-dev 
COPY --from=compile /install /usr/local
WORKDIR /app
COPY . ./

ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV MYSQL_USER=keepcoding
ENV MYSQL_PASSWORD=patodegoma
ENV MYSQL_HOST=db01
ENV MYSQL_DATABASE=contador-db

EXPOSE 5000

CMD flask run