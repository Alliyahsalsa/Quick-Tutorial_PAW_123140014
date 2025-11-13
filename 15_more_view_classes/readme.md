# Paket View yang Skalabel

Dokumen ini menganalisis refactoring (penataan ulang) kode dari satu file views.py menjadi sebuah paket Python (sebuah direktori views/ yang berisi banyak file).  
Ini adalah pola desain yang esensial untuk aplikasi yang berkembang. Saat aplikasi tumbuh besar, menempatkan 20 atau 30 view class dalam satu file views.py akan menjadi sangat berantakan. Solusinya adalah mengelompokkan view terkait ke dalam file-file terpisah di dalam sebuah paket views/.

---

## Objektif (Tujuan Utama) 
- **Skalabilitas & Organisasi:** Memecah file views.py yang monolitik menjadi struktur paket yang rapi (views/home.py, views/hello.py, views/admin.py, dll.).  
- **Memperkenalkan Paket views:** Memahami bagaimana mengubah views dari sebuah file (.py) menjadi sebuah paket (direktori) dengan menambahkan file __init__.py.  
- **Kekuatan config.scan():** Menunjukkan bagaimana config.scan() milik Pyramid cukup pintar untuk secara otomatis memindai seluruh direktori paket, sehingga kita tidak perlu mendaftarkan setiap file view baru secara manual.  
- **Adaptasi Tes:** Memperbarui import di dalam file tes untuk mencerminkan lokasi file yang baru.

---

## Cara Menjalankan

Aktifkan venv (jika belum):
```bash
..\venv\Scripts\Activate.ps1
````

Install Dependensi (jika ada perubahan):

```bash
# (Perintah ini penting untuk memastikan "jembatan" pip menunjuk ke folder yang benar)
(venv) PS C:\...> pip install -e .
(venv) PS C:\...> pip install -e ".[dev]"
(venv) PS C:\...> pip install -e ".[test]"
```

Jalankan Aplikasi:

```bash
(venv) PS C:\...> pserve development.ini --reload
```

Buka [http://localhost:6543/](http://localhost:6543/) di browser Anda.

Jalankan Tes:

```bash
(venv) PS C:\...> pytest tutorial/tests.py
```

(Hasil tes harus tetap 5 passed atau 4 passed, tergantung dari mana Anda menyalin)

---

## Anatomi Proyek

### 1. Perubahan Struktur Folder (Perubahan Kunci)

Perubahan paling penting adalah struktur file.

**Struktur LAMA (Tidak Skalabel):**

```
tutorial/
├── __init__.py
├── views.py   <-- SEMUA kelas view ada di sini
├── tests.py
└── templates/
```

**Struktur BARU (Skalabel):**

```
tutorial/
├── __init__.py
├── views/           <-- SEKARANG MENJADI DIREKTORI
│   ├── __init__.py  <-- BARU (Paling Penting!)
│   ├── home.py      <-- BARU (Pindahan)
│   └── hello.py     <-- BARU (Pindahan)
├── tests.py
└── templates/
```

---

### 2. File Kunci: tutorial/views/**init**.py

Ini adalah file baru yang kosong.

**Analisis:**
Kenapa file ini ada? File **init**.py (meskipun kosong) adalah "tanda pengenal" ajaib bagi Python. Ini memberi tahu Python bahwa direktori views/ bukan sekadar folder biasa, melainkan sebuah Paket Python (Python Package).
Kenapa ini penting? Karena views/ sekarang adalah sebuah paket, config.scan('.views') (di file main **init**.py) bisa "melihat" ke dalamnya.

---

### 3. File Pindahan: tutorial/views/home.py & hello.py

File views.py yang lama sekarang telah dipecah.

**File: tutorial/views/home.py**

```python
from pyramid.view import view_config, view_defaults

@view_defaults(renderer='tutorial:templates/home.pt')
class HomeViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='home')
    def home(self):
        return {'name': 'Home View'}
```

**File: tutorial/views/hello.py**

```python
from pyramid.view import view_config, view_defaults

@view_defaults(renderer='tutorial:templates/home.pt')
class HelloViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='hello')
    @view_config(route_name='hello_json', renderer='json')
    def hello(self):
        return {'name': 'Hello View'}
```

**Analisis:**
Perhatikan bahwa kode logika di dalam file-file ini tidak berubah sama sekali.
Kita hanya memindahkan kelas TutorialViews dari views.py lama dan mengganti namanya menjadi HomeViews dan HelloViews di file mereka masing-masing.

---

### 4. tutorial/**init**.py (File main Aplikasi)

Ini adalah bagian paling elegan dari desain Pyramid.

```python
# File: tutorial/__init__.py
def main(global_config, **settings):
    # ...
    with Configurator(settings=settings) as config:
        # ... (include, add_route, add_static_view) ...
        
        config.scan('.views') 
        
        return config.make_wsgi_app()
```

**Analisis config.scan('.views') (Sangat Penting):**
Perintah config.scan('.views') ini tidak perlu diubah.
Di percobaan sebelumnya, .views merujuk ke file tutorial/views.py. Pyramid memindai file itu.
Sekarang, .views merujuk ke paket tutorial/views/ (karena kita menambahkan views/**init**.py).
config.scan() cukup pintar untuk mendeteksi ini dan secara otomatis memindai **SECARA REKURSIF** semua file .py di dalam direktori views/ (home.py, hello.py, dan file lain yang mungkin kita tambahkan).

**Manfaat Terbesar:**
Untuk menambahkan bagian baru ke situs kita (misal: Admin), kita tinggal membuat file tutorial/views/admin.py. Kita tidak perlu menyentuh file **init**.py utama sama sekali. Aplikasi kita otomatis "menemukan" view baru itu saat restart.

---

### 5. tutorial/tests.py (Adaptasi Impor Tes)

Satu-satunya file yang logikanya perlu diubah adalah file tes, karena lokasi import kelas view kita sudah berubah.

**Unit Test (BERUBAH):**

```python
# ...
# KODE LAMA: from tutorial.views import TutorialViews

# KODE BARU:
from tutorial.views.home import HomeViews
from tutorial.views.hello import HelloViews

class TutorialViewTests(unittest.TestCase):
    # ... (setUp/tearDown) ...

    def test_home(self):
        request = testing.DummyRequest()
        inst = HomeViews(request) # <--- Menggunakan kelas baru
        response = inst.home()
        self.assertEqual(response['name'], 'Home View')

    def test_hello(self):
        request = testing.DummyRequest()
        inst = HelloViews(request) # <--- Menggunakan kelas baru
        response = inst.hello()
        self.assertEqual(response['name'], 'Hello View')
```

**Analisis:**
Functional test tidak perlu diubah sama sekali (karena mereka "black box").
Unit test perlu diperbarui untuk mengimpor dari lokasi file yang baru (.views.home dan .views.hello) dan menggunakan nama kelas yang baru (HomeViews dan HelloViews).

---

## Kesimpulan Analisis
Eksperimen ini adalah tentang pengorganisasian kode untuk skalabilitas jangka panjang.
Dengan mengubah views.py (file) menjadi views/ (paket), dan mengandalkan kekuatan config.scan(), kita telah menciptakan arsitektur yang sangat bersih. Sekarang, setiap bagian logis dari aplikasi kita bisa hidup di file-nya sendiri, membuat proyek lebih mudah dipahami, dikelola, dan dikembangkan oleh tim.

---

## Tampilan di localhost :