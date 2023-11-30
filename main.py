from flask import Flask, render_template, request, flash, redirect, url_for
import pyodbc

app = Flask(__name__)

# Azure SQL Database bağlantı ayarları
server = 'sari.database.windows.net'
database = 'yazlab2'
username = 'sqladmin'
password = 'Sari1234'
driver = '{ODBC Driver 18 for SQL Server}'  # Sürücü adınızı doğru sürücü ile değiştirin

conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

app.secret_key = 'bu_gizli_anahtar_cok_guvenli_olmali'

def connect_db():
    return pyodbc.connect(conn_str)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        submit_button = request.form.get('submit_button')

        if submit_button == 'login':
            username = request.form['username']
            password = request.form['password']

            if check_user(username, password):
                return render_template('html/danisan.html', username=username)
            else:
                flash('Kullanıcı adı veya şifre hatalı.', 'error')

        elif submit_button == 'forgot_password':
            email = request.form['username']

            if not email:
                flash('E-posta alanı boş bırakılamaz.', 'error')
            else:
                # E-posta kontrolü başarılı, e-posta değerini kullan
                return render_template('html/reset_password.html', email=email)

    return render_template('html/main.html')

def check_user(username, password):
    with connect_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM kullanicilar WHERE e_posta = ? AND sifre = ?"
        result = cursor.execute(query, (username, password)).fetchone()

        return result is not None


def update_user_password(email, new_password):
    # Azure Database bağlantısını yap
    conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            # Kullanıcının şifresini güncelle
            query = "UPDATE kullanicilar SET sifre = ? WHERE e_posta = ?"
            cursor.execute(query, (new_password, email))
            conn.commit()

            # Başarı mesajı ekleyebilirsiniz
            flash('Şifreniz başarıyla değiştirildi.', 'success')
    except Exception as e:
        # Hata durumunda kullanıcıya bilgi verebilirsiniz
        flash(f'Hata oluştu: {str(e)}', 'danger')

@app.route('/reset_password', methods=['POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('new_password')

        # Veritabanındaki şifreyi güncelle
        update_user_password(email, new_password)

        # Kullanıcıyı ana sayfaya yönlendir
        return redirect(url_for('home'))

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
