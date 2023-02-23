# Contador en flask con mysql

Aquí tenemos un ejemplo de contador en flask utilizando una base de datos mysql.

## Aplicación (descripción)

La app ofrece 2 endpoints:
- `/inicializa-contador`: para inicializarlo a 0
- `/`: para incrementar el contador y mostrar su valor.

La aplicación es configurable mediante 4 variables de entorno:
- MYSQL_HOST --> host al que conectarse
- MYSQL_DB --> base de datos que la app usará
- MYSQL_USERNAME --> usuario para la conexión de la app a la bd
- MYSQL_PASSWORD --> contraseña del usuario.

Echad un vistazo al código y usadlo como referencia.

## Base de datos

Para la base de datos utilizamos la imagen de docker standard `mysql`, utilizando las variables de entorno que la imagen ofrece para la creación automática de base de datos, usuario y contraseña.

El script `db.sh` se monta en la base de datos en el directorio `/docker-entrypoint-initdb.d/db.sh` para que cree la tabla en la base de datos correspondiente e inicialice el contador a 0.
Hemos utilizado un fichero `.sh` en lugar de un `.sql` porque el nombre de la base de datos lo recibimos como variable de entorno y no puede ir hardcoded.

## Lanzando la aplicación

El docker-compose propuesto construye la imagen del contenedor y lanza todo el entorno en local.
Para construir la imagen del contenedor y probar la aplicación:

```
docker-compose up
```

Para probar el acceso:
  - Incrementar visitas: http://localhost:5000
  - Reiniciar contador: http://localhost:5000/inicializa-contador

El dockerfile NO usa multistage, por lo que habría que mejorarlo.
