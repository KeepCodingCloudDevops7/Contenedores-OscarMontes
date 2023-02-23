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

En este apartado, obviaré la descripción de los ficheros y buena parte de los chequeos a realizar, ya que todo esto ya aparece en el apartado anterior.

Desde el directorio helm, desplegamos del siguiente modo:

```bash
elm install version1 flaskapp
NAME: version1
LAST DEPLOYED: Thu Feb 23 15:48:39 2023
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

To build the Heml we are going to package these files:

<ul>
<li> configmap.yaml</li>
<li>laskapp-deployment.yaml</li>
<li>ingress.yaml </li>
<li>mysql-deployment.yaml </li>
<li>secret.yaml </li>
<li> service-flask.yaml </li>
<li> service-mysql.yaml </li>
</lu>

The main objects and helpers used to pass our files to metadata were as follows:

<ul>
<li> {{ include "flaskapp.fullname" . }}</li>
<li>{{ .Release.Namespace }}</li>
<li>{{- include "flaskapp.labels" . | nindent 4 }} --> To match the labels and selector labels </li>
<li>{{ .Values.image.name }}</li>
<li>{{- if .Values.ingress.enabled -}} --> To enable the ingress controller </li>
</lu>


Please have in mind while we are passing the templates in metada, we should be updating the values file to have it aligned and to make it configurable from a single file.

```bash
# Ingress
ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: nginx
  hosts:
    - host: foo.bar.com
      paths:
      - "/"
# Secret
db:
  rootpassword: passw
  userpassword: secret12345
  username: usuariodb

# Configmap
dbname: studentdb
host: mysql

# Deployment
replicaCount: 1
image:
  app: "ramirezy/flask-app:latest"
  db: "mysql:5.6"
  pullPolicy: IfNotPresent

# Service
service:
  type: "LoadBalancer"
  app: 5000
  port: 3306

# Autoscaling
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

Once we have all the files compiled we can test it with the following commands:

```bash
helm template --debug flaskapp
```

After we have cleaned up any error we might have found, we can proceed to install the Helm chart with the command below:

```bash
helm install project flaskapp
```
You will see the output.

```bash
NAME: project
LAST DEPLOYED: Fri Mar 11 19:13:35 2022
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
```
Now we have to verify all the manifests are running as expected.

```bash
kubectl get pod
NAME                                    READY   STATUS    RESTARTS   AGE
project-flaskapp-app-5788b4f85b-s68zt   1/1     Running   3          50s
project-flaskapp-db-6744b7d55d-4rvbw    1/1     Running   0          50s
```
```bash
kubectl get service
NAME                   TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)          AGE
chart-flaskapp-db      ClusterIP      None           <none>          3306/TCP         6h
kubernetes             ClusterIP      10.80.0.1      <none>          443/TCP          22h
project-flaskapp-app   LoadBalancer   10.80.15.217   35.195.175.88   3306:31510/TCP   71s
project-flaskapp-db    ClusterIP      None           <none>          3306/TCP         71s
```
```bash
kubectl get ingress
NAME               CLASS    HOSTS         ADDRESS         PORTS   AGE
project-flaskapp   <none>   foo.bar.com   35.241.175.40   80      92s
```
```bash
kubectl get hpa
NAME               REFERENCE                         TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
flask-ha           Deployment/flask-service          <unknown>/80%   1         10        0          20m
project-flaskapp   Deployment/project-flaskapp-app   <unknown>/80%   1         10        1          3m42s
````
You can also get all the manifest through this command:

```bash
helm get manifest project
```
```bash
---
# Source: flaskapp/templates/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: project-flaskapp-secret
  namespace: default
type: Opaque
data:
  rootpassword: "cGFzc3c="
  userpassword: "c2VjcmV0MTIzNDU="
  username: "dXN1YXJpb2Ri"
---
# Source: flaskapp/templates/configmap.yaml
apiVersion: v1
data:
  dbname: studentdb
  host: project-flaskapp-db
kind: ConfigMap
metadata:
  creationTimestamp: null
  name: project-flaskapp-cm
  namespace: default
---
# Source: flaskapp/templates/mysql-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: project-flaskapp-mysql-pv-claim
  namespace: default
spec:
  storageClassName: standard
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
---
```
After deploying the helm chart, we apply a port-forward towards port 5000 to test the application:
<ul>
<li>http://localhost:5000/create-table </li>
<li>http://localhost:5000/add-students </li>
<li>http://localhost:5000/ </li>
</ul>

```bash
kubectl port-forward svc/project-flaskapp-app 5000:5000
Forwarding from 127.0.0.1:5000 -> 5000
Forwarding from [::1]:5000 -> 5000
Handling connection for 5000
Handling connection for 5000
```
![app_localhost](https://user-images.githubusercontent.com/39458920/158238393-6d8eb13b-8803-455f-b234-25e4f1ed94ab.JPG)

This is how my kubernetes cluster looks like once whole the manifests have been deployed:

![kubernetes](https://user-images.githubusercontent.com/39458920/158015364-1068a695-d314-4f82-a266-6d2401bbb089.JPG)
![services kubernetes](https://user-images.githubusercontent.com/39458920/158015370-5eb37562-fb24-4334-906f-e05712609339.JPG)

