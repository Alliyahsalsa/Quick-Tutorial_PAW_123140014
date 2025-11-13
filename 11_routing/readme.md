# Perutean (Routing) Dinamis

Dokumen ini menganalisis transisi dari URL hardcoded (ditulis langsung di template) ke sistem perutean yang dinamis dan terpusat.
Ini adalah langkah krusial untuk membuat aplikasi yang mudah dipelihara (maintainable). Masalahnya: Jika URL (/howdy) ditulis di banyak template atau view, dan suatu hari Anda ingin mengubah URL itu menjadi (/greet), Anda harus mencari dan menggantinya di semua file. Ini rapuh dan rawan kesalahan.

Solusinya adalah **Pemisahan Wewenang**:

- **Definisi Rute:** Satu file (routes.py) menjadi "sumber kebenaran" untuk semua URL.
- **Pemanggilan Rute:** View dan template tidak lagi menggunakan URL, melainkan nama rutenya (misal: 'hello').
- **Generasi Dinamis:** Kita menggunakan `request.route_url()` untuk meminta Pyramid "Apa URL untuk rute bernama 'hello'?"

---

## Objektif (Tujuan Utama)
- **Pemisahan Wewenang:** Memindahkan semua definisi rute (add_route) dari `__init__.py` ke file `routes.py` yang terpusat.  
- **Pola includeme:** Mempelajari pola `config.include` dan `includeme` untuk mendaftarkan modul konfigurasi (seperti rute) ke aplikasi utama.  
- **URL Dinamis:** Berhenti menulis URL secara manual di view atau template.  
- **request.route_url():** Mempelajari cara menggunakan `request.route_url('nama_rute')` untuk menghasilkan URL secara dinamis.  
- **Adaptasi Tes:** Memperbarui unit test agar "sadar" akan sistem perutean saat menguji view.  

---

## Cara Menjalankan

Aktifkan venv (jika belum):
```powershell
..\venv\Scripts\Activate.ps1
````

Install Dependensi (jika ada perubahan):

```powershell
(venv) PS C:\...> pip install -e .
(venv) PS C:\...> pip install -e ".[dev]"
(venv) PS C:\...> pip install -e ".[test]"
```

Jalankan Aplikasi:

```powershell
(venv) PS C:\...> pserve development.ini --reload
```

Buka [http://localhost:6543/](http://localhost:6543/) di browser Anda.

Jalankan Tes:

```powershell
(venv) PS C:\...> pytest tutorial/tests.py
```

---

## Anatomi Proyek 

### 1. File Baru: tutorial/routes.py (Pusat Kendali Rute)

Ini adalah file baru yang sekarang memegang "peta" seluruh situs kita.

```python
# File: tutorial/routes.py
def includeme(config):
    """
    Fungsi ini dipanggil secara otomatis saat 
    config.include('.routes') dieksekusi.
    """
    config.add_route('home', '/')
    config.add_route('hello', '/howdy')
    # ... (rute dinamis dari percobaan 10 juga pindah ke sini) ...
    config.add_route('hello_name', '/hello/{name}')
```

**Analisis includeme(config):**
Ini adalah pola standar Pyramid. Saat kita memanggil `config.include('.routes')` di `__init__.py`, Pyramid mencari fungsi bernama `includeme` di dalam file `routes.py` dan mengeksekusinya.
**Pemisahan Wewenang:** `__init__.py` tidak perlu lagi tahu setiap URL di aplikasi. Tugasnya hanya "merakit" modul (`.views`, `.routes`, dll.). File `routes.py` ini sekarang menjadi satu-satunya sumber kebenaran untuk semua URL.

---

### 2. tutorial/**init**.py (Delegasi Tugas)

File main kita sekarang menjadi lebih bersih dan bertindak sebagai "manajer" yang mendelegasikan tugas.

```python
# File: tutorial/__init__.py
def main(global_config, **settings):
    # ...
    with Configurator(settings=settings) as config:
        config.include('pyramid_chameleon')
        
        # 'add_route' HILANG DARI SINI
        
        # mendelegasikan ke file routes.py
        config.include('.routes')
        
        config.scan('.views')
        return config.make_wsgi_app()
```

**Analisis config.include('.routes'):**
Ini menggantikan semua panggilan `config.add_route` yang dulu ada di sini.
`main` sekarang hanya berkata, "Untuk semua hal yang berhubungan dengan rute, silakan lihat ke modul .routes."
Ini membuat aplikasi lebih modular dan mudah dikelola.

---

### 3. tutorial/views.py (Adaptasi View untuk URL Dinamis)

View kita sekarang harus menghasilkan URL secara dinamis, bukan menuliskannya secara manual di template.

```python
# File: tutorial/views.py
# ... (class TutorialViews) ...

    @view_config(route_name='home', renderer='tutorial:templates/home.pt')
    def home(self):
        # Kita panggil NAMA rute 'hello', bukan URL '/howdy'
        hello_url = self.request.route_url('hello')
        
        # Kita teruskan URL yang sudah jadi ke template
        return {'project': 'MyProject', 'hello_url': hello_url}

    # ... (method 'hello' dan 'hello_name' lainnya) ...
```

**Analisis request.route_url('hello'):**
Inilah inti dari perbaikan ini. View kita tidak lagi "tahu" bahwa URL-nya adalah `/howdy`.
Ia hanya meminta Pyramid: "Berikan saya URL yang terkait dengan rute bernama 'hello'."
Pyramid melihat ke `routes.py`, menemukan `'hello' -> '/howdy'`, dan mengembalikan string `/howdy` (atau URL lengkapnya, misal `http://localhost:6543/howdy`).
`{'project': 'MyProject', 'hello_url': hello_url}` kemudian meneruskan URL ini ke template.

---

### 4. tutorial/templates/home.pt (Adaptasi Template)

Template kita sekarang menjadi "lebih bodoh" dan hanya me-render data yang diberikan oleh view.

```html
<!-- File: tutorial/templates/home.pt -->
...
    <p>Visit <a href="${hello_url}">hello</a></p>
...
```

**Analisis:**
Template tidak lagi membuat asumsi tentang URL. Ia hanya me-render variabel `hello_url` yang disuplai oleh view.
**Manfaat Terbesar:** Sekarang, jika Anda ingin mengubah URL dari `/howdy` menjadi `/greet`, Anda hanya perlu mengubah satu baris di `routes.py`.
`views.py` dan `home.pt` akan otomatis ikut ter-update tanpa perlu disentuh.

---

### 5. tutorial/tests.py (Adaptasi Unit Test)

Unit test kita gagal karena view `home` sekarang memanggil `self.request.route_url()`.
`DummyRequest` standar tidak tahu apa-apa tentang rute dan akan crash.

```python
# File: tutorial/tests.py
class TutorialViewTests(unittest.TestCase):
    def setUp(self):
        # Setup standar
        self.config = testing.setUp()
        
        # "Ajari" lingkungan tes kita
        # tentang rute-rute yang ada di aplikasi.
        self.config.include('tutorial.routes') 

    # ... (tearDown) ...

    def test_home_view(self):
        from tutorial.views import TutorialViews
        request = testing.DummyRequest()
        view = TutorialViews(request)
        response = view.home()
        
        # Tes kita sekarang juga memvalidasi URL yang digenerate
        self.assertEqual(response['project'], 'MyProject')
        self.assertEqual(response['hello_url'], '[http://example.com/howdy](http://example.com/howdy)')
```

**Analisis self.config.include('tutorial.routes'):**
Kita menambahkan ini ke `setUp` unit test.
Ini memuat semua rute dari `routes.py` ke dalam lingkungan tes kita.
Sekarang, ketika `view.home()` dipanggil dan mengeksekusi `request.route_url('hello')`, request "tahu" bahwa rute `'hello'` menunjuk ke `'/howdy'` dan mengembalikan URL yang benar (`http://example.com/howdy` adalah default domain dalam tes).

---

## Kesimpulan Analisis
Ini adalah salah satu refactor terpenting dalam siklus hidup aplikasi. Dengan memisahkan definisi rute (`routes.py`) dan menggunakan generator URL dinamis (`request.route_url`), kita telah menciptakan aplikasi yang:

* **Robust:** Perubahan URL di satu tempat otomatis diperbarui di semua tempat.
* **Modular:** `__init__.py` sekarang bersih dan hanya merakit komponen.
* **Mudah Dikelola:** "Peta situs" kita sekarang ada di satu file yang terpusat (`routes.py`).

---

## Tampilan di localhost :

<img width="804" height="367" alt="Screenshot 2025-11-13 183447" src="https://github.com/user-attachments/assets/d6a2f81a-d860-42d3-be26-4c0768042f4f" />
