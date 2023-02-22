# Contenedores-OscarMontes

 contenedores-kubernetes-OscarMontes

<h1>DOCKERS</h1>

This practice is intended to deploy a microservice that is able to read and write in a database. To implement this I built a dockerized flask application running in one container which points out toward the database running in another container.

![flask app_v01](https://user-images.githubusercontent.com/39458920/158245730-c86f330d-4ed3-4795-ae9d-adb225c797a5.jpg)

<b>Requirements:</b><br>
<ul>
<li> First of all install Docker engine for your OS as described <a href="https://docs.docker.com/engine/install/">here </a> </li>
<li>You would need to install docker compose to run the application and database. You can find the steps <a href="https://docs.docker.com/compose/install/">over here</a> </li>
<li>Python 3.7-alpine, Flask, MySQL 5.7, Docker and Docker Compose already installed</li>
</lu>

<h1>Docker compose installation</h1>
Using the following command to install Docker compose. I am installing it under Linux OS.

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
Applying permissions to make the binary executable

```bash
sudo chmod +x /usr/local/bin/docker-compose
```
Finally you can verify the installation by this command:
```bash
docker-compose --version
```
It will deploy the following info:
```bash
docker-compose version 1.29.2, build 5becea4c
```
<h1>Flask MySQL App</h1>
Now I am going to create a directory called <b>"flask-mysql-app"</b> to store there all files needed to dockerize it through docker compose.

```bash
mkdir flask-mysql-app
 ```
First of all, I am going to define the app.py file to configure flask app and the database settings for establishing the communication between them.
Also, there has been defined environment variables(hardcoded) for sensitive information such as, MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST and MYSQL_DB to make it configurable from only one file.
```bash
from flask import Flask
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

app.config['MYSQL_USER'] = os.environ['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
app.config['MYSQL_HOST'] = os.environ['MYSQL_HOST']
app.config['MYSQL_DB'] = os.environ['MYSQL_DB']
mysql = MySQL(app)


@app.route('/create-table')
def createtable():
    cursor = mysql.connection.cursor()
    cursor.execute(''' CREATE TABLE students(id INT NOT NULL AUTO_INCREMENT,
                                             name VARCHAR(50) NOT NULL,
                                             email VARCHAR(100) NOT NULL,
                                             phone INT NOT NULL,
                                             address VARCHAR(250) NOT NULL, PRIMARY KEY (`id`)) ''')
    cursor.close()
    return 'Tabla Creada'


@app.route('/add-students')
def addstudents():
    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO students (id,name,email,phone,address) VALUES(1,'Pedro Romero','pedro_romero@gmail.com',657798564,'Sant Joan DEspi');
                       INSERT INTO students (id,name,email,phone,address) VALUES(2,'Nazaret Olivieri','nazaret_olivieri@gmail.com',610432987,'Cornella de Llobregat'); commit; ''')
    cursor.close()
    return 'Estudiantes añadidos del primer año'


@app.route('/')
def students():
    s = "<table style='border:1px solid red'>"

    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM students; ''')
    for row in cursor.fetchall():
        s = s + "<tr>"
        for x in row:
            s = s + "<td>" + str(x) + "</td>"
        s = s + "</tr>"

    cursor.close()
    return "<html><body>" + s + "</body></html>"
    
@app.route('/ping')
def ping():
    return 'pong
```

Now into the requirements file, I included the required libraries for app.py file
```bash
flask
flask-mysqldb
 ```
For building the app, I have disegned a Dockerfile to add the required dependencies, software or libraries. Notice there were also included the environment variables for MySQL configuration, as it should be synchronized with the application.

There was also introduced the variable <b>FLASK_ENV=development</b>, which reloads the application when it detects any change.

![dockerfile](https://user-images.githubusercontent.com/39458920/156876664-29752dc3-e913-4043-9713-5aa6b473b46e.JPG)

<h1>Creating a Multistage  Docker build for Flask app</h1>

I have adjusted the Dockerfile to make the image smaller.

```bash
FROM python:3.7-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apk add --no-cache gcc musl-dev linux-headers curl mysql-client mysql-dev
RUN pip install -r requirements.txt

COPY . ./

ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV MYSQL_USER=usuariodb
ENV MYSQL_PASSWORD=''
ENV MYSQL_HOST=db
ENV MYSQL_DB=studentdb

EXPOSE 5000

CMD flask run
```
```bash
docker build -t flask-app .

docker image ls
REPOSITORY                    TAG          IMAGE ID       CREATED          SIZE
ramirezy/flask-app          latest       74a15c780d02   36 minutes ago     250MB
```
Once built the flask image, I have uploaded it in my Docker hub repository to make it available to pull.

<h1>Docker compose</h1>

Now the final part is create the docker compose file, where are specified the services for flask and MySQL app, the container's image, the environments, ports, and volumenes to make it persistents for both database and flask app.

```bash
version: '3.9'

services:
  app:
    build: .
    ports:
     - 5000:5000
    depends_on:
      - db
    volumes:
      - ./app.py:/app/app.py
  db:
    image: mysql:5.7
    command: --default-authentication-plugin=mysql_native_password
    restart: always
    environment:
     MYSQL_ROOT_PASSWORD: "passw"
     MYSQL_DATABASE: "studentdb"
     MYSQL_USER: "usuariodb"
     MYSQL_PASSWORD: ""
    ports:
     - 3306:3306
    expose:
     - 3306
    volumes:
     - /my-db:/var/lib/mysql

volumes:
 my-db:
 ```

Once deployed the dockerfile, docker compose, and any other the files required, now you can run the application through the command below:
 
 ```bash
 docker-compose up
 ```
 The output should be as follows:
 
 ![docker](https://user-images.githubusercontent.com/39458920/156846760-316557b8-bc69-42d7-88f7-8fbabd14b19b.JPG)
 
 Now you can see the output by typing the url shown above http://172.18.0.3:5000/ on your Unix shell terminal or your browser.
 To see the output of table creation, type the command:  
 
 ```bash
 http://172.18.0.3:5000/create-table
 ```
 You will see the following output on your Unix terminal/browser:

![create-table](https://user-images.githubusercontent.com/39458920/156878380-cd7e6253-e47e-4aab-9ec5-eb188baa699a.JPG)

To see the output of added students, type the command:  
 ```bash
 http://172.18.0.3:5000/add-students
 ```
You will see the following output on your Unix terminal/browser:

![add-students](https://user-images.githubusercontent.com/39458920/156878176-3f0cb950-f870-4c59-ba98-1577547bed4b.JPG)
 
 To see the output of table students, type the command: 
  ```bash
 http://172.18.0.3:5000/
 ```
 You will see the following output on your Unix terminal/browser:
 ![output_db](https://user-images.githubusercontent.com/39458920/157477439-3835c41a-8769-4a76-9d30-eead3e4323c6.JPG)
  
<h1>Verifying the logs for database and flask app are being sent to standard output (STDOUT/STDERR)</h1>

![mysql_logs](https://user-images.githubusercontent.com/39458920/156889548-cbc012dc-a797-4328-9157-92150338a255.JPG)

![flask_logs](https://user-images.githubusercontent.com/39458920/156889585-cec4ba8d-a1c0-4183-ad89-50c0fbdcba48.JPG)

<h1>Deploying the application in Kubernetess</h1>
First of all you will need to create a cluster in Google Cloud console to associate it to Kubernetes environment.

Creating namespace for each manifest.
```bash
k create ns database --dry-run -oyaml > ns.yaml
k create ns flask-api --dry-run -oyaml > ns-flask-api.yaml

k create -f ns.yaml
k create -f ns-flask-api.yaml
```
<h1>Storing database credentials in Kubernetes secrets</h1> 
 
 The vulnerable data in the database should be stored as Base64 encoded strings thorugh the following command:
 ```bash
 echo -n 'rootpassword' | base64
```

This command will output a string of characters, as shown below.
```bash
 c2VjcmV0MTIU=
```
Once the rootpassword is encoded, we deployeed a secret file for each namespace created.

```bash
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
  namespace: database
type: Opaque
data:
  rootpassword: cGFzc3c=
```
```bash
k create -f mysql-secret.yaml
```

```bash
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
  namespace: flask-api
type: Opaque
data:
  userpassword: c2VjcmV0MTIzNDU=
  username: dXN1YXJpb2Ri
```
```bash
k create -f flaskapi-secrets.yaml
```
Now let's provide persistence to the database with Persistent Volume Claim. For this is needed to check the storage classes from the cluster.

According to the output below, it seems to be standard:
```bash
kubectl get storageclasses.storage.k8s.io
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
premium-rwo          pd.csi.storage.gke.io   Delete          WaitForFirstConsumer   true                   8d
standard (default)   kubernetes.io/gce-pd    Delete          Immediate              true                   8d
```
Now we can define the manifest for Persistent Volume Claim:

```bash
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pv-claim
  namespace: database
spec:
  storageClassName: standard
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

```bash
k create -f mysql-pvc.yaml
```
As you can see Persistent Volume Claim has been successfully created and bound.

```bash
kubectl get pvc -n database
NAME             STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
mysql-pv-claim   Bound    pvc-618b86aa-310f-426a-8fd1-70d650c1bb42   20Gi       RWO            standard       10h
```
Additionally, we can see persistent volume is automatically created.

```bash
kubectl get persistentvolume
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                     STORAGECLASS   REASON   AGE
pvc-618b86aa-310f-426a-8fd1-70d650c1bb42   20Gi       RWO            Delete           Bound    database/mysql-pv-claim   standard                11h
```

We created a configmap file for the database instance in order to make the environment variable (MYSQL_DATABASE) available in the MySQL deployment.

```bash
apiVersion: v1
data:
  dbname: studentdb
  host: mysql
kind: ConfigMap
metadata:
  name: flaskapi-cm
  namespace: database
  ```

<h1>Deploying MySQL in Kubernetess</h1>

Now we can run the mysql instance with a deployment workload.

```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
  namespace: database
spec:
  selector:
    matchLabels:
      app: mysql
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - image: mysql:5.6
        name: mysql
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: rootpassword
        - name: MYSQL_DATABASE
          valueFrom:
            configMapKeyRef:
              name: flaskapi-cm
              key: dbname
        - name: MYSQL_USER
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: username
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: userpassword
        ports:
        - containerPort: 3306
          name: mysql
        volumeMounts:
        - name: mysql-persistent
          mountPath: /var/lib/mysql
      volumes:
      - name: mysql-persistent
        persistentVolumeClaim:
          claimName: mysql-pv-claim
  ```
We can see the associated pod to mysql instance, which is in status running.

```bash
kubectl get pods -n database
NAME                     READY   STATUS    RESTARTS   AGE
mysql-54dccfbfbd-vslwh   1/1     Running   0          10h
```
Creating a service to provide MySQL access towards Flask app or any other pod inside the cluster.

```bash
apiVersion: v1
kind: Service
metadata:
  name: mysql
  namespace: database
spec:
  ports:
  - port: 3306
  selector:
    app: mysql
  clusterIP: None
```

```bash
kubectl create -f service-mysql.yaml
```

<h1>Storing database credentials in Kubernetes Configmap</h1> 

I have specified the variables MYSQL_HOST and MYSQL_DB into the configmap configuration.

```bash
apiVersion: v1
data:
  dbname: studentdb
  host: mysql
kind: ConfigMap
metadata:
  creationTimestamp: null
  name: flaskapi-cm
  namespace: flask-api
```

```bash
k create -f configmap.yaml
```

<h1>Deploying Flask app in Kubernetess</h1>
Now I set the environment variales in this deployment, using the values specified in the secret and configmap file.
The flask image was built from Dockerfile configuration.

```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flaskapp-deployment
  namespace: flask-api
  labels:
    app: flaskapp
spec:
  selector:
    matchLabels:
      app: flaskapp
  replicas: 1
  template:
    metadata:
      labels:
        app: flaskapp
    spec:
      containers:
        - name: flaskapp
          image: ramirezy/flask-app
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5000
          env:
            - name: MYSQL_HOST
              valueFrom:
                configMapKeyRef:
                  name: flaskapi-cm
                  key: host
            - name: MYSQL_DB
              valueFrom:
                configMapKeyRef:
                  name: flaskapi-cm
                  key: dbname
            - name: MYSQL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: userpassword
            - name: MYSQL_USER
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: username
```
Applying the flask app deployment

```bash
kubectl create -f flaskapp-deployment.yaml
```
```bash
kubectl get pods -n flask-api
NAME                                   READY   STATUS    RESTARTS   AGE
flaskapp-deployment-7bd7ccf9b6-h254l   1/1     Running   0          151m
```
Creating a service to expose the deployment ousite of the cluster through a LoadBalancer.

```bash
apiVersion: v1
kind: Service
metadata:
  name: flask-service
  namespace: flask-api
  labels:
    app: flaskapp
spec:
  ports:
  - port: 5000
    protocol: TCP
    targetPort: 5000
  selector:
    app: flaskapp
  type: LoadBalancer
```
```bash
kubectl create -f service-flask.yaml
```
Now we can check all the resources deployed in each instance.

Database instance
```bash
kubectl get all -n database
NAME                         READY   STATUS    RESTARTS   AGE
pod/mysql-54dccfbfbd-vslwh   1/1     Running   0          11h

NAME            TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
service/mysql   ClusterIP   None         <none>        3306/TCP   5h34m

NAME                    READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/mysql   1/1     1            1           11h

NAME                               DESIRED   CURRENT   READY   AGE
replicaset.apps/mysql-54dccfbfbd   1         1         1       11h
```

Flask instance
```bash
kubectl get all -n flask-api
NAME                                       READY   STATUS    RESTARTS   AGE
pod/flaskapp-deployment-5fcb4ddbcf-qxj5x   1/1     Running   0          67m

NAME                    TYPE           CLUSTER-IP     EXTERNAL-IP    PORT(S)          AGE
service/flask-service   LoadBalancer   10.80.11.168   35.240.60.60   5000:30209/TCP   67m

NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/flaskapp-deployment   1/1     1            1           67m

NAME                                             DESIRED   CURRENT   READY   AGE
replicaset.apps/flaskapp-deployment-5fcb4ddbcf   1         1         1       67m
```

<h1>Creating an Ingress Resource</h1>
You will need to install the ingress controller as per the info here <a href="https://kubernetes.github.io/ingress-nginx/deploy/">here </a>

Now you can check the pods and resources generated by the ingress controller:

```bash
kubectl get all --namespace=ingress-nginx
NAME                                            READY   STATUS      RESTARTS   AGE
pod/ingress-nginx-admission-create-wnmd2        0/1     Completed   0          4d1h
pod/ingress-nginx-admission-patch-5kx9m         0/1     Completed   0          4d1h
pod/ingress-nginx-controller-54d8b558d4-9xwjl   1/1     Running     0          4d1h

NAME                                         TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)                      AGE
service/ingress-nginx-controller             LoadBalancer   10.80.9.203    35.241.175.40   80:30588/TCP,443:30823/TCP   4d1h
service/ingress-nginx-controller-admission   ClusterIP      10.80.14.114   <none>          443/TCP                      4d1h

NAME                                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/ingress-nginx-controller   1/1     1            1           4d1h

NAME                                                  DESIRED   CURRENT   READY   AGE
replicaset.apps/ingress-nginx-controller-54d8b558d4   1         1         1       4d1h

```

I create an ingress resource with anotation <b>kubernetes.io/ingress.class: nginx</b> to access Flask service 

```bash
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: flask-ingress
  namespace: flask-api
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
  - host: foo.bar.com
    http:
      paths:
      - path: '/'
        pathType: Prefix
        backend:
          service:
            name: flask-service
            port:
              number: 5000
```
Checking ingress

```bash
k get ingress -n flask-api
NAME            CLASS    HOSTS         ADDRESS         PORTS   AGE
flask-ingress   <none>   foo.bar.com   35.241.175.40   80      56m
```
We can check the nginx access through this IP address 32.241.175.40

![nginx_access](https://user-images.githubusercontent.com/39458920/158379292-bb9a0301-29d7-47e1-a472-fd1ecd383440.JPG)


As per the log below, we can see the ingress controller is enabled

```bash
kubectl describe svc -n flask-api
Name:                     flask-service
Namespace:                flask-api
Labels:                   app=flaskapp
Annotations:              cloud.google.com/neg: {"ingress":true}
Selector:                 app=flaskapp
Type:                     LoadBalancer
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.80.1.183
IPs:                      10.80.1.183
LoadBalancer Ingress:     35.205.88.13
Port:                     <unset>  5000/TCP
TargetPort:               5000/TCP
NodePort:                 <unset>  31506/TCP
Endpoints:                10.76.0.17:5000
Session Affinity:         None
External Traffic Policy:  Cluster
Events:                   <none>

```

<h1>Horizontal Autoscaling</h1>
We have implemented the following autoscaling for the application Pod in case it needs more load, then HPA will increase more pods automatically.

```bash
apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
  name: flask-ha
  namespace: flask-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: flask-service
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

<h1>Helm Charts</h1>
Once we have the application deployed in Kubernetes, now we are going to package the code with Helm Charts.

You may need to install it before to proceed, for more info you can check this <a href="https://helm.sh/docs/intro/install/">Quickstart guide </a>
The working direcory of Helm chart

```bash
└── flaskapp
    ├── charts
    ├── Chart.yaml
    ├── templates
    │   ├── configmap.yaml
    │   ├── flaskapp-deployment.yaml
    │   ├── _helpers.tpl
    │   ├── hpa.yaml
    │   ├── ingress.yaml
    │   ├── mysql-deployment.yaml
    │   ├── mysql-pvc.yaml
    │   ├── secret.yaml
    │   ├── service-flask.yaml
    │   ├── service-mysql.yaml
    │   └── tests
    └── values.yaml
```

First of all, you would need to create the project name, where will be deployed the helm configuration:

```bash
helm create flaskapp
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

