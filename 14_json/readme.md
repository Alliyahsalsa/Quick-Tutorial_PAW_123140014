# Renderer JSON (Membuat API)

Dokumen ini menganalisis cara Pyramid beralih dari menyajikan halaman web HTML (untuk manusia) menjadi menyajikan data mentah JSON (untuk mesin/JavaScript).

Ini adalah langkah fundamental dalam pengembangan web modern. Aplikasi tidak lagi hanya website; mereka juga bertindak sebagai API (Application Programming Interface) yang menyediakan data untuk aplikasi seluler, framework JavaScript (seperti React/Vue), atau layanan lainnya. Pyramid membuat transisi ini menjadi sangat mudah.

---

## Objektif (Tujuan Utama)

- **Memperkenalkan json Renderer:** Mempelajari cara menggunakan renderer json bawaan Pyramid.  
- **Pemisahan Wewenang (Data vs. Presentasi):** Menunjukkan bagaimana logika view (mengembalikan dictionary) dapat tetap sama, baik output-nya berupa HTML (via Jinja2) maupun JSON.  
- **API Endpoint:** Membuat endpoint API (.json) baru yang hidup berdampingan dengan endpoint HTML yang sudah ada.  
- **Adaptasi Tes:** Memperbarui functional test untuk memvalidasi header application/json dan konten JSON, bukan HTML.  

---

## Cara Menjalankan

Aktifkan venv (jika belum):
```bash
..\venv\Scripts\Activate.ps1
````

Install Dependensi:

```
(Tidak ada dependensi baru di langkah ini, karena renderer JSON sudah bawaan Pyramid. 
Tapi menjalankan ini akan memastikan "jembatan" pip menunjuk ke folder yang benar).
(venv) PS C:\...> pip install -e .
(venv) PS C:\...> pip install -e ".[dev]"
(venv) PS C:\...> pip install -e ".[test]"
```

Jalankan Aplikasi:

```bash
(venv) PS C:\...> pserve development.ini --reload
```

Buka `http://localhost:6543/` (Halaman HTML lama).
Buka `http://localhost:6543/hello.json` (Endpoint API baru).

Jalankan Tes:

```bash
(venv) PS C:\...> pytest tutorial/tests.py
```

---

## Anatomi Proyek 

### 1. tutorial/**init**.py (Menambah Rute API)

Kita hanya perlu menambahkan satu rute baru untuk endpoint JSON kita.

```python
# File: tutorial/__init__.py
def main(global_config, **settings):
    # ...
    with Configurator(settings=settings) as config:
        # ... (include, add_static_view, dll) ...
        
        config.add_route('home', '/')
        config.add_route('hello', '/howdy')
        
        # Rute untuk API
        config.add_route('hello_json', '/hello.json')

        config.scan('.views')
        return config.make_wsgi_app()
```

**Analisis:**
Kita menambahkan rute baru bernama `hello_json` yang menunjuk ke URL `/hello.json`.
Penggunaan akhiran `.json` adalah konvensi yang baik untuk memperjelas bahwa endpoint ini mengembalikan JSON, meskipun secara teknis tidak wajib.
Aplikasi kita sekarang akan merespons ke rute HTML (`/howdy`) **DAN** rute JSON (`/hello.json`).

---

### 2. tutorial/views.py (Kekuatan Renderer)

Ini adalah perubahan paling elegan. Kita menambahkan method baru yang logikanya hampir identik dengan view HTML kita.

```python
# File: tutorial/views.py
@view_defaults(renderer='home.jinja2') # Default untuk HTML
class TutorialViews:
    def __init__(self, request):
        self.request = request

    # ... (method 'home' dan 'hello' sebelumnya) ...
    # ... (Menggunakan renderer default .jinja2) ...

    # INI METHOD BARU UNTUK API
    @view_config(route_name='hello_json', renderer='json')
    def hello_json(self):
        """View yang mengembalikan JSON."""
        return {'name': 'Hello View'}
```

**Analisis (Bagian 1: `renderer='json'`):**
Ini adalah kunci dari semuanya. Dengan menentukan `renderer='json'`, kita memberi tahu Pyramid:

> "Ambil dictionary yang dikembalikan oleh fungsi ini, ubah menjadi string JSON, dan kirim ke klien dengan header Content-Type: application/json."

Kita tidak perlu `import json` atau `json.dumps()` atau membuat objek `Response` secara manual. Pyramid menangani semuanya secara otomatis.

**Analisis (Bagian 2: `return {'name': 'Hello View'}`):**
Perhatikan bahwa body (isi) dari method `hello_json()` ini identik dengan method `hello()` yang menggunakan Jinja2.

Ini adalah konsep fundamental Pyramid: **Tugas view adalah menyediakan data (dalam bentuk dictionary).**
Tugas renderer (`.jinja2` atau `json`) adalah memformat data tersebut untuk klien.

Logika bisnis kita (`return {'name': 'Hello View'}`) tidak peduli apakah hasilnya akan menjadi HTML atau JSON.
Ini adalah contoh sempurna dari **Separation of Concerns (Pemisahan Wewenang).**

---

### 3. tutorial/tests.py (Menguji Endpoint JSON)

Karena kita punya endpoint baru, kita perlu tes baru. Cara kita menguji JSON sangat berbeda dengan cara kita menguji HTML.

#### Unit Test (BARU):

```python
# File: tutorial/tests.py
class TutorialViewTests(unittest.TestCase):
    # ... (test_home dan test_hello sebelumnya) ...

    # INI UNIT TEST BARU
    def test_hello_json_view(self):
        from tutorial.views import TutorialViews
        request = testing.DummyRequest()
        inst = TutorialViews(request)

        # Panggil method baru
        response_dict = inst.hello_json() 

        # Tesnya IDENTIK dengan test_hello
        self.assertEqual(response_dict['name'], 'Hello View')
```

**Analisis:**
Unit test untuk `hello_json` identik dengan unit test untuk `hello`.
Ini membuktikan poin di atas: logika view (yang sedang kita uji) adalah sama, hanya renderer-nya yang berbeda.

#### Functional Test (BARU):

Functional test adalah "black box" dan harus berubah drastis karena output-nya berbeda.

```python
# File: tutorial/tests.py
class TutorialFunctionalTests(unittest.TestCase):
    # ... (test_home dan test_hello fungsional sebelumnya) ...

    # INI FUNCTIONAL TEST BARU
    def test_hello_json_functional(self):
        # 1. Panggil endpoint .json
        res = self.testapp.get('/hello.json', status=200)

        # 2. Cek Content-Type header
        self.assertEqual(res.content_type, 'application/json')

        # 3. Cek isi data JSON
        #    'res.json' otomatis mem-parsing JSON kembali ke dictionary
        self.assertEqual(res.json['name'], 'Hello View') 
```

**Analisis:**
Kita memanggil URL baru (`/hello.json`).
Kita tidak lagi memeriksa `b'...' in res.body` (HTML).
Sebaliknya, kita memeriksa `res.content_type` untuk memastikan server mengirim JSON.
Kita menggunakan `res.json` (fitur dari webtest) untuk secara otomatis mengonversi body respons dari string JSON kembali menjadi dictionary Python, sehingga kita bisa mengujinya dengan mudah (`res.json['name']`).

---

## Kesimpulan Analisis

Pyramid membuat pembuatan API JSON menjadi sangat sepele.
Dengan hanya menambahkan `renderer='json'` ke `@view_config`, framework ini menangani semua "pekerjaan kotor" (serialisasi JSON dan pengaturan header).

Hal ini memungkinkan kita untuk fokus pada **logika bisnis view (menyediakan data)** dan membiarkan renderer menangani **bagaimana data itu disajikan ke klien**, baik itu sebagai halaman HTML maupun endpoint API.

---

## Tampilan di localhost :