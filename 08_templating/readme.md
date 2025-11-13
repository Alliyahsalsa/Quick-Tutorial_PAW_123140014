# Templating dengan Chameleon

Dokumen ini menganalisis transisi dari respons HTML hardcoded (ditulis langsung di Python) ke sistem templating (cetakan) profesional menggunakan pyramid_chameleon.

Ini adalah pilar utama pengembangan web modern: memisahkan Logika (Python) dari Presentasi (HTML).

---

## Objektif (Tujuan Utama)

**Pemisahan Wewenang:** Menghentikan praktik buruk menulis HTML di dalam file Python (Response('<body>...</body>')). Logika harus di Python, markup harus di file HTML/template.

**Memperkenalkan Templating Engine:** Menginstal dan mengonfigurasi pyramid_chameleon sebagai add-on Pyramid.

**Memahami Konsep Renderer:** Mempelajari bagaimana Pyramid, melalui renderer, secara otomatis mengubah dictionary Python sederhana menjadi halaman web HTML yang lengkap.

**Adaptasi Tes:** Memodifikasi unit test kita untuk mencerminkan perubahan tanggung jawab view (dari membuat HTML menjadi hanya menyediakan data).

---

## Cara Menjalankan

**Aktifkan venv (jika belum):**
```bash
..\venv\Scripts\Activate.ps1
````

**Install Dependensi (PENTING):**
Perintah ini akan membaca setup.py dan menginstal pyramid_chameleon yang baru ditambahkan.

```bash
(venv) PS C:\...> pip install -e .
```

**Jalankan Aplikasi:**

```bash
(venv) PS C:\...> pserve development.ini --reload
```

Buka [http://localhost:6543/](http://localhost:6543/) di browser Anda.

**Jalankan Tes:**

```bash
(venv) PS C:\...> pytest tutorial/tests.py
```

---

## Anatomi Proyek

Perubahan ini memengaruhi hampir setiap bagian dari aplikasi kita. Mari kita bedah mengapa.

### 1. setup.py (Dependensi Inti Baru)

```python
# ...
requires = [
    'pyramid',
    'waitress',
    'pyramid_chameleon', 
]
# ...
```

**Analisis:** Kita menambahkan pyramid_chameleon ke install_requires (dependensi inti).

Kenapa? Tidak seperti pytest (hanya untuk tes) atau pyramid_debugtoolbar (hanya untuk development), templating engine adalah bagian vital dari aplikasi. Aplikasi kita tidak dapat berjalan di server produksi tanpanya. Oleh karena itu, ini adalah dependensi inti, bukan "extra".

---

### 2. tutorial/templates/home.pt (File Template Baru)

```html
<!-- File: tutorial/templates/home.pt -->
<div metal:define-macro="main">
    <h1>Hi ${name}</h1>
    <p>Visit <a href="/howdy">hello</a></p>
</div>
```

**Analisis:**

Ini pada dasarnya adalah file HTML (yang mematuhi standar XML, yang disyaratkan Chameleon).

Ia tidak tahu apa-apa tentang Python atau Pyramid.

Bagian kuncinya adalah ${name}. Ini adalah placeholder (penampung). Template engine akan mencari data bernama name dari Python dan "menyuntikkannya" ke sini.

---

### 3. tutorial/**init**.py (Aktivasi Add-on)

```python
def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.include('pyramid_chameleon') 
        config.add_route('home', '/')
        config.add_route('hello', '/howdy')
        config.scan('.views')
        return config.make_wsgi_app()
```

**Analisis:** config.include('pyramid_chameleon') adalah perintah yang "mengaktifkan" add-on. Ini memberi tahu Pyramid: "Hei, jika kamu melihat renderer yang menunjuk ke file .pt, gunakan Chameleon untuk menanganinya."

---

### 4. tutorial/views.py (Perubahan Paling Fundamental)

```python
# ... (impor) ...

@view_config(route_name='home', 
             renderer='tutorial:templates/home.pt') # <-- Bagian 1: Renderer
def home(request):
    """View untuk halaman utama."""
    return {'name': 'Project'} # <-- Bagian 2: Dictionary
```

**Analisis (Bagian 1: renderer=...):**

Kita menambahkan argumen renderer ke @view_config.

Ini adalah "lem" ajaib. Ini memberi tahu Pyramid: "Saat rute home dipanggil, eksekusi fungsi home ini. Setelah selesai, ambil hasil dari fungsi home dan berikan ke file template home.pt untuk di-render."

**Analisis (Bagian 2: return {'name': 'Project'}):**

Perubahan Terbesar: View kita TIDAK LAGI mengembalikan Response! Ia sekarang mengembalikan Python Dictionary sederhana.

Dictionary ini disebut "context".

Pyramid (karena kita menentukan renderer) secara otomatis melakukan ini:

* Menjalankan home(request) dan mendapatkan {'name': 'Project'}.
* Memuat file home.pt.
* Memberikan dictionary ke template. Chameleon mengganti ${name} dengan "Project".
* Menghasilkan HTML final.
* Membungkus HTML itu dalam objek Response dan mengirimkannya ke browser.

**Kesimpulan:** Tugas view telah berubah. Tugasnya bukan lagi "membuat HTML", tapi hanya "menyediakan data".

---

### 5. tutorial/tests.py (Adaptasi Tes)

Karena output dari fungsi home() berubah (dari Response menjadi dict), unit test kita juga harus berubah.

**Unit Test (BERUBAH):**

```python
def test_home(self):
    from tutorial.views import home
    request = testing.DummyRequest()
    response = home(request) # 'response' sekarang adalah dictionary
    self.assertEqual(response, {'name': 'Project'})
```

**Analisis:** Unit test kita sekarang menguji output langsung dari fungsi home(). Kita memvalidasi bahwa view kita mengembalikan dictionary context yang benar. Ini adalah tes yang lebih murni dan lebih fokus pada "logika".

**Functional Test (HAMPIR TIDAK BERUBAH):**

```python
def test_functional_home(testapp):
    res = testapp.get('/', status=200)
    assert b'Hi Project' in res.body 
```

**Analisis:** Functional test kita (tes "black box") hampir tidak perlu berubah. Tes ini tidak peduli bagaimana HTML dibuat (apakah hardcoded atau dari template). Ia hanya peduli pada hasil HTML akhir. Ini membuktikan betapa berharganya functional test saat melakukan refactoring besar-besaran seperti ini.

---

## Kesimpulan Analisis

Dengan memperkenalkan templating, kita telah mengambil langkah besar dalam profesionalisme. Kode kita sekarang jauh lebih bersih, lebih mudah dikelola, dan mengikuti prinsip fundamental Separation of Concerns (Pemisahan Wewenang).

Tugas view menjadi lebih sederhana (hanya menyiapkan data), unit test kita menjadi lebih tajam (hanya menguji data), dan functional test kita memastikan semuanya tetap terhubung dengan benar.

---

## Tampilan di localhost :

- Tampilan "Hi Home View"
<img width="831" height="359" alt="Screenshot 2025-11-13 014525" src="https://github.com/user-attachments/assets/ae556dd3-a996-4e57-9d9d-a17c6fb118df" />

- Tampilan "Hi Hello View"
<img width="897" height="338" alt="Screenshot 2025-11-13 020520" src="https://github.com/user-attachments/assets/d8fbc21c-f8d9-4bae-a281-c9d367a6a048" />