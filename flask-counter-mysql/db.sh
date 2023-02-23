#!/bin/bash

mysql --password=$MYSQL_ROOT_PASSWORD -u root <<EOS
USE $MYSQL_DATABASE;


CREATE TABLE tabla_contador (
  contador int NOT NULL
);

INSERT INTO tabla_contador VALUES (0);
EOS