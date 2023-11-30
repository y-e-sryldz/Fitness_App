from flask import Flask, render_template, request, redirect, url_for
import pyodbc

app = Flask(__name__)

# Azure SQL Database bağlantı ayarları
server = 'sari.database.windows.net'
database = 'yazlab2'
username = 'sqladmin'
password = 'Sari1234'
driver = '{ODBC Driver 18 for SQL Server}'  # Sürücü adınızı doğru sürücü ile değiştirin

conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def connect_db():
    return pyodbc.connect(conn_str)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if check_user(username, password):
            return render_template('html/danisan.html', username=username)
        else:
            return render_template('html/main.html', error='Kullanıcı adı veya şifre hatalı.')

    return render_template('html/main.html')

def check_user(username, password):
    with connect_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM kullanicilar WHERE e_posta = ? AND sifre = ?"
        result = cursor.execute(query, (username, password)).fetchone()

        return result is not None

if __name__ == '__main__':
    app.run(debug=True)
