from flask import Flask
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

app.config['MYSQL_USER'] = os.environ['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
app.config['MYSQL_HOST'] = os.environ['MYSQL_HOST']
app.config['MYSQL_DB'] = os.environ['MYSQL_DATABASE']
mysql = MySQL(app)


@app.route('/inicializa-contador')
def initialize():
    cursor = mysql.connection.cursor()
    cursor.execute(''' UPDATE tabla_contador SET contador=0; ''')
    cursor.execute(''' COMMIT; ''')
    cursor.close()
    return 'Contador inicializado a 0'


@app.route('/')
def conteo():
    s = "<table style='border:1px solid red'>"

    cursor = mysql.connection.cursor()
    cursor.execute(''' UPDATE tabla_contador SET contador = contador + 1; ''')
    cursor.execute(''' COMMIT; ''')
    cursor.close()

    # usamos un segundo cursor porque no sé si se puede reutilizar el primero :)
    # seguro que esto es mejorable

    cursor2 = mysql.connection.cursor()
    cursor2.execute(''' SELECT * FROM tabla_contador; ''')
    for row in cursor2.fetchall():
        s = s + "<tr>"
        for x in row:
            s = s + "<td>" + str(x) + "</td>"
        s = s + "</tr>"
    cursor2.close()
    return "<html><body> VISITANTES: " + s + "</body></html>"
