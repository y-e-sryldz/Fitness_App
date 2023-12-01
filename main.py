from flask import Flask, render_template, request, flash, redirect, url_for, session
import pyodbc
from werkzeug.utils import secure_filename

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

            user_id = get_user_id_by_email(username)
            print(user_id)
            session['user_id'] = user_id

            if check_user(username, password):

                return render_template('html/danisan.html', username=username, user_id=user_id)
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

#giriş kontrolü sağlayan kod parçası
def check_user(username, password):
    with connect_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM kullanicilar WHERE e_posta = ? AND sifre = ?"
        result = cursor.execute(query, (username, password)).fetchone()
        return result is not None


#kullanıcı adını tuutan id fonksiyonu
def get_user_id_by_email(email):
    with connect_db() as conn:
        cursor = conn.cursor()
        query = "SELECT id FROM kullanicilar WHERE e_posta = ?"
        result = cursor.execute(query, (email,)).fetchone()

        if result:
            return result[0]  # id değerini döndür
        else:
            return None  # Eğer e-posta bulunamazsa None döndür


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

@app.route('/kisisel_bilgi_ekle', methods=['POST'])
def kisisel_bilgi_ekle():
    if request.method == 'POST':

        user_id = session.get('user_id')
        print(user_id)

        # Formdan gelen verileri al
        ad = request.form['ad']
        sifre = request.form['sifre']
        dogum_tarihi = request.form['dogum-tarihi']
        cinsiyet = request.form['cinsiyet']
        email = request.form['email']
        telefon = request.form['telefon']

        # Formdan gelen dosyayı al
        profil_foto = request.files['profil-foto']

        # Dosya adını güvenli bir şekilde al
        guvenli_dosya_adi = secure_filename(profil_foto.filename)

        # Dosyayı kaydetmek için uygun bir klasöre kaydet
        dosya_yolu = f'uploads/{guvenli_dosya_adi}'
        profil_foto.save(dosya_yolu)

        # Veritabanına ekleme işlemleri
        try:
            with connect_db() as conn:
                cursor = conn.cursor()

                # Kullanıcı tablosuna ekle
                cursor.execute("UPDATE kullanicilar SET adi=?, e_posta=?, sifre=?, rol=? WHERE id=?", (ad, email, sifre, 3, user_id))
                conn.commit()
                # Danışanlar tablosuna ekle
                cursor.execute("UPDATE Danisanlar SET dogum_tarihi=?, cinsiyet=?, telefon_numarasi=?, pp=? WHERE id=?", (dogum_tarihi, cinsiyet, telefon, dosya_yolu, user_id))
                conn.commit()

                print('Bilgiler başarıyla kaydedildi.', 'success')

        except Exception as e:
            # Hata durumunda kullanıcıya bilgi ver
            print(f'Hata oluştu: {str(e)}', 'danger')
    return render_template('html/danisan.html')


if __name__ == '__main__':
    app.run(debug=True)
