# Contenedores-Oscar Montes

<h1>DOCKERS</h1>

En esta práctica desplegaremos un microservicio capaz de interactuar con una BBDD MYSQL. Para ello dockerizaremos una aplicación Flask ubicada en un contenedor, la cual apuntará a las BBDD, ubicada en otro contenedor.

<b>Requisitos:</b><br>
<ul>
<li> Instalar el Docker engine siguiendo las instrucciones del <a href="https://docs.docker.com/engine/install/">enlace </a> </li>
<li> Instalar - en caso de que no lo esté aun - docker compose siguiendo las instrucciones del <a href="https://docs.docker.com/compose/install/">enlace</a> </li>
</lu>

<h1>Flask-Counter-Mysql</h1>
Descargar el contendido de la carpeta flask-counter-mysql del Repositorio en el directo local <b>"flask-counter-mysql"</b>. Estos ficheros permitirán desplegar la Aplicación/BBDD mediante docker compose.

En el fichero de requiremientos, encontraremos las librerías necesarias para desplegar el fichero app.py 
```bash
flask
flask-mysqldb
 ```
En el Dockerfile se añadirá el software y las librerías pertinentes. En el fichero .env encontraremos las variables que se aplicarán en los ficheros del despliegue.

<h1>Docker Multistage</h1>

Llevado a cabo para reducir el tamaño del contenedor de la app

```bash
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
```
Esta sería imagen resultante:

```bash
REPOSITORY                    TAG       IMAGE ID       CREATED          SIZE
flask-counter-mysql-app       latest    3cdec075acaf   18 minutes ago   116MB


```
Tras construirla, la subi a mi repositorio de Docker Hub repository: oscarmontes/contenedores:flask-app

<h1>Docker Compose</h1>

Formado por dos servicios, una serie de variables definidas en el .env y los puertos y el forwarding.

Para desplegar los contenedores, ejecutar:
 
 ```bash
 docker-compose up
 ```
Ejecutando curl http://192.168.49.1:5000 repetidas veces, veremos que el contador aumenta.

 ```bash
<html><body> VISITANTES: <table style='border:1px solid red'><tr><td>1</td></tr></body></html>
<html><body> VISITANTES: <table style='border:1px solid red'><tr><td>2</td></tr></body></html>
<html><body> VISITANTES: <table style='border:1px solid red'><tr><td>3</td></tr></body></html>
<html><body> VISITANTES: <table style='border:1px solid red'><tr><td>4</td></tr></body></html>
<html><body> VISITANTES: <table style='border:1px solid red'><tr><td>5</td></tr></body></html>
<html><body> VISITANTES: <table style='border:1px solid red'><tr><td>6</td></tr></body></html>
 ```
 
 
<h1>Despliegue en Kubernetes</h1>

Instalamos Minikube 
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

Arrancamos el Cluster de Minikube 
```bash
minikube start
```

Para esta práctica, utilizaremos el Namespace por Defecto.

<h1>Gestión de credenciales con Kubernetes secrets</h1> 
 
 Para la generación de la clave cifrada, hemos seguido el siguiente procedimiento:
 ```bash
 echo -n 'elegir_contraseña' | base64
```
Copiando la salida de la misma en el fichero de contraseñas (secret.yaml en nuestro caso) a las cuentas que utilicemos; por ejemplo:

```bash
 c2VjcmV0MTIzNDU=
```

```bash
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
  namespace: flask-api
type: Opaque
data:
  userpassword: c2VjcmV0MTIzNDU= <<<<<<<
  username: dXN1YXJpb2Ri
```

Para la utilización de variables con datos no sensibles, utilizaremos configmap:

```bash
apiVersion: v1
kind: ConfigMap
data:
  MYSQL_USER: keepcoding
  MYSQL_HOST: bbdd1
  MYSQL_DATABASE: contador-db
  FLASK_APP: app.py
  FLASK_ENV: development
  FLASK_RUN_HOST: 0.0.0.0
metadata:
  name: flask-config
  ```

Para la ejecución de sentecias sql en la bbdd para generar los objetos necesarios para que funcione la app, utilizaremos otro configmap:

```bash
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-initdb-config
data:
  init.sql: |
    USE contador-db;
    CREATE TABLE tabla_contador (contador int NOT NULL);
    INSERT INTO tabla_contador VALUES (0);
  ```
Crearemos un Servicio ClusterIp para conectar el pod de la app con el pod de la bbdd.

Crearemos un Nodeport para conectar el Cluster con la app en uno de los pods, vía puerto 5000.

Crearemos un ingress para conectar desde fuera, gracias a un proxy-inverso, vía puerto 80


<h1>Despliegue</h1>

Ejecutamos los siguientes comandos:

```bash
# Despliegue ClusterIP
  kubectl apply -f cluster_ip_bbdd.yaml
# Despliegue NodePort
  kubectl apply -f nodeport_app.yaml
# Despliegue Secrets
  kubectl apply -f secrets.yaml
# Despliegue Ingress
  kubectl apply -f ingress.yaml
# Despliegue ConfigMap con comandos de BBDD
  kubectl apply -f bbdd-cm.yaml
# Despliegue ConfigMap con variables no sensibles
  kubectl apply -f flask-cm.yaml
# Despliegue de la APP  
  kubectl apply -f deploy_bbdd.yaml
# Despliegue de la BBDD
  kubectl apply -f deploy_app.yaml
```

Chequeamos los recursos desplegados:

```bash
#kubectl get all

NAME                                        READY   STATUS    RESTARTS   AGE
pod/app-mysql-0                             1/1     Running   0          53m
pod/flask-app-deployment-6ccc544684-sm2m5   1/1     Running   0          53m

NAME                 TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
service/app1         NodePort    10.97.62.85      <none>        5000:30082/TCP   53m
service/bbdd1        ClusterIP   10.108.135.154   <none>        3306/TCP         53m
service/kubernetes   ClusterIP   10.96.0.1        <none>        443/TCP          54m

NAME                                   READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/flask-app-deployment   1/1     1            1           53m

NAME                                              DESIRED   CURRENT   READY   AGE
replicaset.apps/flask-app-deployment-6ccc544684   1         1         1       53m

NAME                         READY   AGE
statefulset.apps/app-mysql   1/1     53m
```

```bash
#Kubectl get ingress my-flask (en el que vemos el campo ADDRESS vacío)
NAME       CLASS    HOSTS         ADDRESS   PORTS   AGE
my-flask   <none>   foo.bar.com             80      55m
```
```bash
#kubectl get configmap
NAME                  DATA   AGE
flask-config          6      55m
kube-root-ca.crt      1      55m
mysql-initdb-config   1      55m
```

```bash
#NAME            TYPE     DATA   AGE
secret-manual   Opaque   2      57m
```

<h1>Instalamos el Ingress Controller</h1>
Procedimiento en el <a href="https://kubernetes.github.io/ingress-nginx/deploy/">enlace </a>

Chequeamos los recursos generados:

```bash
NAME                                           READY   STATUS      RESTARTS   AGE
pod/ingress-nginx-admission-create-q9lvn       0/1     Completed   0          89m
pod/ingress-nginx-admission-patch-mnb2m        0/1     Completed   1          89m
pod/ingress-nginx-controller-77669ff58-hg8zt   1/1     Running     0          27m

NAME                                         TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
service/ingress-nginx-controller             NodePort    10.100.106.113   <none>        80:30178/TCP,443:30452/TCP   89m
service/ingress-nginx-controller-admission   ClusterIP   10.100.83.176    <none>        443/TCP                      89m

NAME                                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/ingress-nginx-controller   1/1     1            1           89m

NAME                                                  DESIRED   CURRENT   READY   AGE
replicaset.apps/ingress-nginx-controller-5d44985b66   0         0         0       89m
replicaset.apps/ingress-nginx-controller-77669ff58    1         1         1       27m

NAME                                       COMPLETIONS   DURATION   AGE
job.batch/ingress-nginx-admission-create   1/1           26s        89m
job.batch/ingress-nginx-admission-patch    1/1           27s        89m


```

Habilitamos los Ingress Addons

```bash
# minikube addons enable ingress
ingress was successfully enabled
```
Chequeamos Ingress

```bash
# kubectl get ingress (campo ADDRESS completado)
NAME       CLASS    HOSTS         ADDRESS        PORTS   AGE
my-flask   <none>   foo.bar.com   192.168.49.2   80      22m

```
Tras meter la entrada "192.168.49.2 foo.bar.com" en el fichero /etc/hosts, probamos la conectividad con la App:

```bash
vagrant@tierra:/vagrant/practica-docker-k8s/k8s$ curl http://foo.bar.com
<html><body> VISITANTES: <table style='border:1px solid red'><tr><td>5</td></tr></body></html>
vagrant@tierra:/vagrant/practica-docker-k8s/k8s$ curl http://foo.bar.com
<html><body> VISITANTES: <table style='border:1px solid red'><tr><td>6</td></tr></body></html>
vagrant@tierra:/vagrant/practica-docker-k8s/k8s$ curl http://foo.bar.com
<html><body> VISITANTES: <table style='border:1px solid red'><tr><td>7</td></tr></body></html>
vagrant@tierra:/vagrant/practica-docker-k8s/k8s$ curl http://foo.bar.com
<html><body> VISITANTES: <table style='border:1px solid red'><tr><td>8</td></tr></body></html>
```


<h1>Helm Charts</h1>

En este apartado, obviaré la descripción de los ficheros y los chequeos a realizar ya descritos en el apartado anterior.

En el fichero de configuración, values.yaml, tendremos las variables (entre las que se encuentran las del autoescalado):

```bash# Ingress
ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: nginx
  hosts:
    - host: foo2.bar.com
      paths:
      - "/"
# Secret
db:
  rootpassword: root1234
  userpassword: patodegoma
  username: keepcoding

# Configmap
dbname: contador-db
host: mysql

# Deployment
replicaCount: 1
image:
  app: "oscarmontes/contenedores:flask-app"
  db: "mysql"
  pullPolicy: IfNotPresent

# Service
service:
  type: Nodeport
  app: 5000
  port: 3306

# Autoscalado
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 2
  targetCPUUtilizationPercentage: 70
```


Desde el directorio helm, desplegamos del siguiente modo:

```bash
# helm install version1 flaskapp
NAME: version1
LAST DEPLOYED: Thu Feb 23 15:48:39 2023
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

Habiliamos las métricas para Minicube 
```bash
Minikube enable metrics-server addon
```

Verificamos el correcto despliegue:

```bash
vagrant@tierra:/vagrant/helm/charts$ kubectl get all
NAME                                         READY   STATUS    RESTARTS   AGE
pod/version1-flaskapp-app-76b58b85f4-jtglr   1/1     Running   0          15m
pod/version1-flaskapp-db-0                   1/1     Running   0          15m

NAME                           TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
service/kubernetes             ClusterIP   10.96.0.1    <none>        443/TCP    42m
service/version1-flaskapp-db   ClusterIP   None         <none>        3306/TCP   15m

NAME                                    READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/version1-flaskapp-app   1/1     1            1           15m

NAME                                               DESIRED   CURRENT   READY   AGE
replicaset.apps/version1-flaskapp-app-76b58b85f4   1         1         1       15m

NAME                                    READY   AGE
statefulset.apps/version1-flaskapp-db   1/1     15m

NAME                                                    REFERENCE                          TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/version1-flaskapp   Deployment/version1-flaskapp-app   2%/70%    1         2         1          15m
```

En la parte inferior de la salida anterior, podemos ver los datos relativos al autoescalado.

También podemos ver el manifiesto de la version desplegada, ejecutando:

```bash
helm get manifest version1
```
Por último, comprobamos la app:
```bash
curl http://foo.bar.com
<html><body> VISITANTES: <table style='border:1px solid red'><tr><td>2</td></tr></body></html>
vagrant@tierra:/vagrant/practica-docker-k8s/k8s$ curl http://foo.bar.com
<html><body> VISITANTES: <table style='border:1px solid red'><tr><td>3</td></tr></body></html>
vagrant@tierra:/vagrant/practica-docker-k8s/k8s$ curl http://foo.bar.com
<html><body> VISITANTES: <table style='border:1px solid red'><tr><td>4</td></tr></body></html>
vagrant@tierra:/vagrant/practica-docker-k8s/k8s$ curl http://foo.bar.com
<html><body> VISITANTES: <table style='border:1px solid red'><tr><td>5</td></tr></body></html>
```




