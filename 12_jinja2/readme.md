# Templating Alternatif (Jinja2)

Dokumen ini menganalisis proses penggantian template engine (mesin cetak) dari Chameleon (bawaan Pyramid, file .pt) ke Jinja2 (mesin cetak populer lainnya, file .jinja2).  
Ini adalah studi kasus yang sangat baik tentang fleksibilitas dan sifat agnostik framework Pyramid. Ini membuktikan bahwa inti aplikasi (logika view, routing) tidak terikat pada satu sistem template tertentu.

---

## Objektif (Tujuan Utama)
- **Interoperabilitas:** Menunjukkan bahwa Pyramid adalah template-agnostic dan dapat diintegrasikan dengan add-on pihak ketiga seperti pyramid_jinja2.  
- **Logika Sisi Template:** Memperkenalkan konsep template yang "lebih pintar" yang dapat mengakses request secara langsung (misalnya, untuk menghasilkan URL).  
- **Refactor View:** Menyederhanakan logika view dengan memindahkan tanggung jawab (seperti pembuatan URL) dari view (Python) ke template (Jinja2).  
- **Adaptasi Tes:** Mengadaptasi unit test untuk mencerminkan tanggung jawab baru (yang lebih sederhana) dari view.

---

## Cara Menjalankan

Aktifkan venv (jika belum):
```bash
..\venv\Scripts\Activate.ps1
````

Install Dependensi (PENTING):
Perintah ini akan membaca setup.py dan menginstal pyramid_jinja2 yang baru ditambahkan.

```bash
(venv) PS C:\...> pip install -e .
```

Jalankan Aplikasi:

```bash
(venv) PS C:\...> pserve development.ini --reload
```

Buka `http://localhost:6543/` di browser Anda.

Jalankan Tes:

```bash
(venv) PS C:\...> pytest tutorial/tests.py
```

---

## Anatomi Proyek (Analisis Mendalam)

### 1. setup.py (Dependensi Inti Baru)

```python
# ...
requires = [
    'pyramid',
    'waitress',
    'pyramid_chameleon',
    'pyramid_jinja2',   
]
# ...
```

**Analisis:**
Kita menambahkan pyramid_jinja2 ke install_requires (dependensi inti).
Kenapa? Tidak seperti pytest (hanya untuk tes) atau pyramid_debugtoolbar (hanya untuk development), template engine adalah bagian vital dari aplikasi.
Aplikasi kita tidak dapat berjalan di server produksi tanpanya. Oleh karena itu, ini adalah dependensi inti, bukan "extra".

---

### 2. tutorial/**init**.py (Aktivasi & Konfigurasi Add-on)

```python
def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        # 1. Mengaktifkan 'chameleon' (jika masih dipakai)
        config.include('pyramid_chameleon') 
        
        # 2. Mengaktifkan 'jinja2'
        config.include('pyramid_jinja2')

        # 3. Memberi tahu Jinja2 di mana mencari file template
        config.add_jinja2_search_path('tutorial:templates')
        
        config.include('.routes')
        config.scan('.views')
        return config.make_wsgi_app()
```

**Analisis (Langkah 2 & 3):**
Ini adalah konfigurasi add-on dua langkah yang khas:

* `config.include('pyramid_jinja2')`: "Menyalakan" add-on Jinja2. Ini memberi tahu Pyramid cara menangani renderer yang berakhiran .jinja2.
* `config.add_jinja2_search_path(...)`: Ini memberi tahu Jinja2 di mana direktori template global kita berada.

---

### 3. File Baru: tutorial/templates/home.jinja2

```html
<!-- File: tutorial/templates/home.jinja2 -->
<!DOCTYPE html>
<html>
<head>
    <title>Quick Tutorial: {{ project }}</title>
</head>
<body>
    <h1>Hi {{ project }}!</h1>
    
    <p>Visit <a href="{{ request.route_url('hello') }}">hello</a></p>
</body>
</html>
```

**Analisis (Sintaks):**
Perubahan paling jelas adalah sintaksnya: `{{ ... }}` (Jinja2) menggantikan `${...}` (Chameleon).

**Analisis (Konsep):**
Perubahan paling fundamental ada di `{{ request.route_url('hello') }}`.
Add-on pyramid_jinja2 secara default memberikan akses ke objek request global di dalam template.
Ini berarti template tidak lagi "bodoh". Ia bisa secara aktif menghasilkan URL-nya sendiri dengan memanggil request.route_url() langsung di HTML.

---

### 4. tutorial/views.py (Logika View yang Disederhanakan)

Karena template sekarang bisa membuat URL-nya sendiri, view kita menjadi lebih sederhana.

```python
# File: tutorial/views.py
@view_defaults(renderer='home.jinja2') # <-- Berubah ke .jinja2
class TutorialViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='home')
    def home(self):
        # 'hello_url' HILANG DARI SINI
        return {'project': 'MyProject'} 

    @view_config(route_name='hello')
    def hello(self):
        return {'name': 'Hello View'}

    # ... (view lainnya) ...
```

**Analisis:**

* `renderer='home.jinja2'`: Kita memberi tahu @view_defaults untuk menggunakan renderer Jinja2 yang baru.
* `return {'project': 'MyProject'}`: Perhatikan, view home tidak perlu lagi menghitung dan meneruskan hello_url.
  Tanggung jawab itu telah dipindahkan ke template.

**Pola Desain:**
View kita sekarang murni berfokus pada penyediaan data inti ('project'), dan menyerahkan urusan presentasi data (termasuk URL terkait) sepenuhnya kepada template.

---

### 5. tutorial/tests.py (Adaptasi Unit Test)

Karena tanggung jawab view home berubah, unit test-nya juga harus berubah.

**Unit Test (BERUBAH):**

```python
# File: tutorial/tests.py
class TutorialViewTests(unittest.TestCase):
    # ... (setUp/tearDown) ...

    def test_home(self):
        from tutorial.views import TutorialViews
        request = testing.DummyRequest()
        view = TutorialViews(request)
        response_dict = view.home()

        self.assertEqual(response_dict['project'], 'MyProject')
```

**Analisis:**
Unit test kita menjadi lebih sederhana. Ia sekarang dengan tepat menguji satu-satunya tanggung jawab view home: yaitu mengembalikan dictionary `{'project': 'MyProject'}`.

**Functional Test (TIDAK BERUBAH):**

```python
def test_home_functional(self, testapp):
    res = testapp.get('/', status=200)
    assert b'Hi MyProject' in res.body
    assert b'<a href="/howdy">' in res.body 
```

**Analisis:**
Functional test (tes "black box") tidak perlu diubah sama sekali. Tes ini tidak peduli bagaimana HTML-nya dibuat (Chameleon/Jinja2).
Ia hanya peduli pada hasil HTML akhir. Ini membuktikan nilai dari functional test saat melakukan refactor.

---

## Kesimpulan Analisis

Eksperimen ini menunjukkan kekuatan Pyramid sebagai framework yang "agnostik" dan dapat diperluas.
Kita bisa mengganti komponen rendering (Chameleon ke Jinja2) tanpa mengubah logika inti aplikasi kita.

Ini juga menyoroti trade-off desain yang fundamental:

* **Template "Bodoh" (Chameleon):**
  View (Python) melakukan semua pekerjaan (mengambil data, menghasilkan URL) dan memberikan semuanya ke template yang hanya menampilkan data.

* **Template "Pintar" (Jinja2):**
  View (Python) hanya menyediakan data inti. Template (Jinja2) secara aktif mengambil data tambahan yang diperlukannya (seperti request.route_url).

Pyramid mendukung kedua pola ini, memungkinkan developer memilih pendekatan yang paling sesuai untuk proyek mereka.

---

## Tampilan di localhost :