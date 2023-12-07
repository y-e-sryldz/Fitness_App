from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
import pyodbc
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Azure SQL Database bağlantı ayarları
server = 'server'
database = 'database'
username = 'username'
password = 'password'
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

            user_id ,role = get_user_info(username)
            print(user_id)
            session['user_id'] = user_id
            session['user_rol'] = role

            if check_user(username, password):
                if role == 1:
                    return yonetici()
                elif role == 2:
                    return Antrenor()
                elif role == 3:
                    return danisan()
                else:
                    flash('Geçersiz kullanıcı rolü.', 'error')
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

# Kullanıcının bilgilerini ve rolünü getiren fonksiyon
def get_user_info(username):
    with connect_db() as conn:
        cursor = conn.cursor()
        query = "SELECT id, rol FROM kullanicilar WHERE e_posta = ?"
        result = cursor.execute(query, (username,)).fetchone()

        if result:
            return result[0], result[1]  # id ve rol değerlerini döndür
        else:
            return None, None  # Eğer kullanıcı bulunamazsa None döndür

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
def danisan_bilgi_ekle():
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
    return render_template('html/main.html')

@app.route('/')
def danisan():
    try:
        # Cursor oluştur
        cursor = connect_db().cursor()

        # Flask session'da kullanıcının user_id değerini kontrol et
        user_id = session.get('user_id')

        # SQL sorgusu
        sql_query = "SELECT * FROM BeslenmeProgramlari WHERE danisan_id = ?"

        # Parametre ile sorguyu çalıştır
        cursor.execute(sql_query, (user_id,))
        rows = cursor.fetchall()
        print(rows)
        print("AAAAAAAAAAAAAA")

        # SQL sorgusu
        sql_query1 = "SELECT * FROM EgzersizProgramlari WHERE danisan_id = ?"

        # Parametre ile sorguyu çalıştır
        cursor.execute(sql_query1, (user_id,))
        rows1 = cursor.fetchall()

        # SQL sorgusu
        sql_query2 = "SELECT * FROM ilerlemeKayitlari WHERE danisan_id = ?"

        # Parametre ile sorguyu çalıştır
        cursor.execute(sql_query2, (user_id,))
        rows2 = cursor.fetchall()

        # Bağlantıyı kapat
        cursor.close()

        return render_template('html/danisan.html', BeslenmeProgramlari=rows, EgzersizProgramlari=rows1, ilerlemeKayitlari=rows2)  # BeslenmeProgramlari değişkeni kullanılabilir
    except Exception as e:
        print(f'Hata oluştu: {str(e)}')
        return render_template('main.html', error_message=str(e))

@app.route('/antrenor_bilgi_ekle', methods=['POST'])
def antrenor_bilgi_ekle():
    if request.method == 'POST':

        user_id = session.get('user_id')
        rol = session.get('user_rol')
        print(user_id)

        # Formdan gelen verileri al
        ad = request.form['ad']
        sifre = request.form['sifre']
        email = request.form['email']
        telefon = request.form['telefon']
        uzmanlik = request.form['uzmanlik']
        deneyim = request.form['deneyim']

        # Veritabanına ekleme işlemleri
        try:
            with connect_db() as conn:
                cursor = conn.cursor()

                # Kullanıcı tablosuna ekle
                cursor.execute("UPDATE kullanicilar SET adi=?, e_posta=?, sifre=?, rol=? WHERE id=?", (ad, email, sifre, rol, user_id))
                conn.commit()
                # Danışanlar tablosuna ekle
                cursor.execute("UPDATE Antrenorler SET Uzmanlik_alanlari=?,  iletisim_bilgileri=?, deneyim=? WHERE id=?", (uzmanlik, telefon, deneyim, user_id))
                conn.commit()

                print('Bilgiler başarıyla kaydedildi.', 'success')

        except Exception as e:
            # Hata durumunda kullanıcıya bilgi ver
            print(f'Hata oluştu: {str(e)}', 'danger')

    return render_template('html/main.html')

@app.route('/Antrenor')
def Antrenor():
    try:
        # Flask session'da kullanıcının user_id değerini kontrol et
        user_id = session.get('user_id')

        # Cursor oluştur
        conn = connect_db()
        cursor = conn.cursor()

        # SQL sorgusu
        danisanlar_query = "SELECT Danisan_id FROM Antrenor_DanisanAtama WHERE antrenor_id = ?"

        # Parametre ile sorguyu çalıştır
        danisanlar = cursor.execute(danisanlar_query, (user_id,))
        danisan_id_listesi = [danisan[0] for danisan in danisanlar]

        # Danışanların isimlerini bul
        danisan_adi_query = "SELECT adi FROM Kullanicilar WHERE id IN ({})".format(
            ','.join(['?'] * len(danisan_id_listesi)))
        danisan_adi_listesi = cursor.execute(danisan_adi_query, danisan_id_listesi).fetchall()

        print(danisan_adi_listesi)

        # Bağlantıyı kapat
        cursor.close()

        return render_template('html/antrenor.html', danisan_adi_listesi=danisan_adi_listesi)
    except Exception as e:
        print(f'Hata oluştu: {str(e)}')
        return render_template('main.html', error_message=str(e))

@app.route('/yonetici')
def yonetici():
    try:


        # Cursor oluştur
        conn = connect_db()
        cursor = conn.cursor()

        # SQL sorgusu
        danisanlar_query = "SELECT adi FROM kullanicilar"

        danisan_adi_listesi = cursor.execute(danisanlar_query)





        return render_template('html/yonetici.html',danisan_adi_listesi=danisan_adi_listesi)
    except Exception as e:
        print(f'Hata oluştu: {str(e)}')
        return render_template('main.html', error_message=str(e))
@app.route('/get_student_info', methods=['POST'])
def get_student_info():
    try:
        danisan_index_raw = request.form.get('danisanIndex')
        danisan_index_raw = danisan_index_raw.strip()
        print('danisan_index_raw:', danisan_index_raw)  # Hatanın nedenini anlamak için log

        conn = connect_db()
        cursor1 = conn.cursor()

        # Kullanicilar tablosundan adi sütununda ara ve id sütununa göre eşleşen kaydın adını al
        try:
            cursor1.execute("SELECT id FROM Kullanicilar WHERE adi = ?", (danisan_index_raw))
            result = cursor1.fetchone()
            print("Başarılı sorgu. Sonuç:", result)

            if result is not None:
                print("naber")
        except Exception as e:
            print("Hata oluştu:", e)
        finally:
            conn.close()

        print(result)  # Sorgu sonucunu kontrol etmek için

        print("aa")
        conn = connect_db()
        cursor = conn.cursor()


        # Kullanicilar tablosundan danisanin ID'sini bul
        kullanicilar_query = "SELECT id, adi FROM Kullanicilar ORDER BY id OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
        kullanicilar_result = cursor.execute(kullanicilar_query).fetchone()

        if not kullanicilar_result:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Danisan bilgileri bulunamadı'})
        # Kullanicilar tablosundan danisanin ID'sini bul
        kullanicilar_query = "SELECT adi FROM Kullanicilar WHERE id = ?"
        danisan_adi = cursor.execute(kullanicilar_query,(result)).fetchone()

        # IlerlemeKayitlari tablosundan en son kayıtları çek
        try:
            ilerleme_query = "SELECT kilo, boy, yag_orani, kas_kütlesi, kitle_index, NULL AS tarih FROM IlerlemeKayitlari WHERE danisan_id = ? ORDER BY tarih DESC OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
            ilerleme_result = cursor.execute(ilerleme_query, (result)).fetchone()
        except Exception as e:
            print("Hata oluştu:", e)
        print("bb")

        ilerleme_result = cursor.execute(ilerleme_query, (result)).fetchone()

        danisan_adi = danisan_adi[0] if ilerleme_result else None
        kilo = ilerleme_result[0] if ilerleme_result else None
        boy = ilerleme_result[1] if ilerleme_result else None
        yag_orani = ilerleme_result[2] if ilerleme_result else None
        kas_kutlesi = ilerleme_result[3] if ilerleme_result else None
        kitle_index = ilerleme_result[4] if ilerleme_result else None

        # BeslenmeProgramlari tablosundan bilgileri çek
        beslenme_query = "SELECT hedef, sabah, ogle, aksam, gunluk_ogunler, kalori_hedefin FROM BeslenmeProgramlari WHERE danisan_id = ?"
        beslenme_result = cursor.execute(beslenme_query, (result)).fetchall()

        # EgzersizProgramlari tablosundan bilgileri çek
        egzersiz_query = "SELECT egzersiz_adi, hedefleri, program_baslangicT, program_sure FROM EgzersizProgramlari WHERE danisan_id = ?"
        egzersiz_result = cursor.execute(egzersiz_query, (result)).fetchall()

        # Hedef, sabah, ogle, aksam, gunluk_ogunler ve kalori_hedefin değerlerini elde et
        hedef = beslenme_result[0][0] if len(beslenme_result) > 0 else None
        sabah = beslenme_result[0][1] if len(beslenme_result) > 0 else None
        ogle = beslenme_result[0][2] if len(beslenme_result) > 0 else None
        aksam = beslenme_result[0][3] if len(beslenme_result) > 0 else None
        gunluk_ogunler = beslenme_result[0][4] if len(beslenme_result) > 0 else None
        kalori_hedefi = beslenme_result[0][5] if len(beslenme_result) > 0 else None

        # Egzersiz_adi, hedefleri, program_baslangicT ve program_sure değerlerini elde et
        egzersiz_adi = egzersiz_result[0][0] if len(egzersiz_result) > 0 else None
        hedefleri = egzersiz_result[0][1] if len(egzersiz_result) > 0 else None
        program_baslangicT = egzersiz_result[0][2] if len(egzersiz_result) > 0 else None
        program_sure = egzersiz_result[0][3] if len(egzersiz_result) > 0 else None



        cursor.close()
        conn.close()

        # JSON formatında verileri döndür
        return jsonify({
            'danisan_adi': danisan_adi,
            'kilo': kilo,
            'boy': boy,
            'yag_orani': yag_orani,
            'kas_kutlesi': kas_kutlesi,
            'kitle_index': kitle_index,
            'hedef': hedef,
            'sabah': sabah,
            'ogle': ogle,
            'aksam': aksam,
            'gunluk_ogunler': gunluk_ogunler,
            'kalori_hedefi': kalori_hedefi,
            'egzersiz_adi': egzersiz_adi,
            'hedefleri': hedefleri,
            'program_baslangicT': program_baslangicT,
            'program_sure': program_sure,

        })

    except Exception as e:
        return jsonify({'error': str(e)})



if __name__ == '__main__':
    app.run(debug=True)
