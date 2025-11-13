# Menyajikan Aset Statis (CSS/JS/Gambar)

Dokumen ini menganalisis cara Pyramid menangani "aset statis" (file-file seperti .css, .js, dan .png yang tidak berubah).

Aplikasi web modern lebih dari sekadar HTML; mereka membutuhkan styling (CSS) dan interaktivitas (JavaScript). Kita tidak bisa menulis CSS di dalam file Python. Oleh karena itu, kita perlu memberi tahu framework kita cara menemukan dan menyajikan file-file ini ke browser.

---

## Objektif (Tujuan Utama)

- **Pemisahan Wewenang:** Memisahkan file styling (CSS) dari file template (HTML) dan logika (Python).  
- **Konsep Asset Specification:** Memperkenalkan `tutorial:static/` sebagai cara standar Pyramid untuk merujuk ke file di dalam paket Python, di mana `tutorial` adalah nama paket dan `static/` adalah direktorinya.  
- **Konfigurasi add_static_view:** Mempelajari cara "memetakan" sebuah URL (seperti `http://localhost:6543/static/`) ke sebuah folder fisik di dalam proyek kita (`tutorial/static/`).  
- **Adaptasi Template:** Memperbarui template HTML agar tahu cara meminta file CSS menggunakan URL statis yang baru.  

---

## Cara Menjalankan

Aktifkan venv (jika belum):
```bash
# Asumsi Anda ada di folder proyek
..\venv\Scripts\Activate.ps1
````

Install Dependensi (jika ada perubahan):

```bash
(venv) PS C:\...> pip install -e .
(venv) PS C:\...> pip install -e ".[dev]"
(venv) PS C:\...> pip install -e ".[test]"
```

Jalankan Aplikasi:

```bash
(venv) PS C:\...> pserve development.ini --reload
```

Buka `http://localhost:6543/` di browser Anda. (Sekarang seharusnya memiliki styling).

Jalankan Tes:

```bash
(Tes tidak berubah di langkah ini)
(venv) PS C:\...> pytest tutorial/tests.py
```

---

## Anatomi Proyek

### 1. Struktur Folder Baru

Kita membuat folder `static` di dalam paket `tutorial` kita. Ini adalah konvensi umum untuk menyimpan file-file yang tidak dieksekusi.

```
tutorial/
├── __init__.py
├── views.py
├── tests.py
├── templates/
│   └── home.jinja2
└── static/            <-- FOLDER BARU
    ├── app.css        <-- FILE BARU
    └── pyramid.png    <-- FILE BARU
```

---

### 2. File Baru: `tutorial/static/app.css`

Ini adalah file CSS standar. Isinya tidak penting; yang penting adalah lokasinya. Ini adalah aset yang ingin kita sajikan.

```css
/* File: tutorial/static/app.css */
body {
    background-color: #eee;
    margin: 2em;
}
```

---

### 3. `tutorial/__init__.py` (Konfigurasi add_static_view)

Kita perlu memberi tahu Pyramid bahwa folder `static/` ada dan harus dapat diakses melalui URL.

```python
# File: tutorial/__init__.py
def main(global_config, **settings):
    # ...
    with Configurator(settings=settings) as config:
        # ... (include jinja2, dll) ...
        
        # INI BARIS BARU
        config.add_static_view(name='static', path='tutorial:static')

        # ... (add_route, scan, dll) ...
        return config.make_wsgi_app()
```

**Analisis `config.add_static_view(...)`:**
Ini adalah perintah "ajaib" yang menciptakan rute khusus untuk file statis.

* `name='static'`: Ini adalah URL yang akan dilihat pengguna. Ini memberi tahu Pyramid untuk membuat rute di `/static/`. (Misal: `http://localhost:6543/static/`).
* `path='tutorial:static'`: Ini adalah lokasi fisik file-file tersebut. Ini menggunakan sintaks *asset specification* Pyramid:

  * `tutorial`: Nama paket (seperti yang didefinisikan di `setup.py`).
  * `:`: Pemisah.
  * `static`: Nama folder di dalam paket tutorial.

**Apa yang terjadi?**
Saat browser meminta `http://localhost:6543/static/app.css`, Pyramid mencegatnya, menerjemahkannya ke `tutorial:static/app.css`, menemukan file fisik di dalam paket Python, dan mengirimkannya kembali ke browser dengan `content-type` yang benar (`text/css`).

---

### 4. `tutorial/templates/home.jinja2` (Menggunakan CSS)

Terakhir, kita perlu memberi tahu template HTML kita untuk memuat file `app.css`.

```html
<!-- File: tutorial/templates/home.jinja2 -->
<!DOCTYPE html>
<html>
<head>
    <title>Quick Tutorial: {{ name }}</title>
    
    <!-- INI BARIS BARU -->
    <link rel="stylesheet"
          href="{{ request.static_url('tutorial:static/app.css') }}">
</head>
<body>
    <!-- INI BARIS BARU -->
    <img src="{{ request.static_url('tutorial:static/pyramid.png') }}"
         alt="Pyramid logo" />

    <h1>Hi {{ name }}!</h1>
    
    <!-- ... (link 'hello' dari sebelumnya) ... -->
</body>
</html>
```

**Analisis `request.static_url(...)`:**
Ini adalah kebalikan dari `request.route_url()`. Ini adalah method yang khusus dibuat untuk menghasilkan URL ke aset statis.

* `'tutorial:static/app.css'`: Kita memberinya *asset specification* lengkap ke file yang kita inginkan.

**Kenapa ini penting?**
Pyramid (melalui `add_static_view`) tahu bahwa *asset spec* `tutorial:static` dipetakan ke URL `/static`.
`request.static_url` secara otomatis mengubah `tutorial:static/app.css` menjadi URL yang benar: `/static/app.css`.

**Manfaat:**
Jika suatu hari Anda memutuskan untuk mengubah `name='static'` menjadi `name='assets'` di `__init__.py`, Anda tidak perlu mengubah template ini. `request.static_url` akan secara otomatis menghasilkan URL baru (`/assets/app.css`). Ini membuat kode sangat mudah dipelihara.

---

### 5. `tutorial/tests.py` (Tidak Berubah!)

**Analisis:**
Unit test kita tidak berubah karena view kita (`home` dan `hello`) tidak berubah sama sekali. Mereka masih mengembalikan dictionary yang sama.

Functional test kita (menggunakan `webtest`) juga tidak perlu berubah. `webtest` adalah browser palsu yang tidak peduli pada CSS atau gambar. Ia hanya peduli pada konten HTML (`b'Hi Home View'`), dan itu tidak berubah.

*(Jika kita ingin, kita bisa menulis tes fungsional baru untuk `res = testapp.get('/static/app.css', status=200)` untuk membuktikan bahwa file CSS itu ada, tapi itu di luar cakupan tutorial ini).*

---

## Kesimpulan Analisis

Menyajikan aset statis adalah persyaratan fundamental aplikasi web. Pyramid menanganinya dengan elegan melalui dua konsep:

1. **`config.add_static_view`**: Sebuah perintah "sekali jalan" di `__init__.py` untuk memetakan URL (`/static/`) ke folder fisik (`tutorial:static/`).
2. **`request.static_url`**: Sebuah helper di template untuk menghasilkan URL yang benar ke file statis, yang membuat template kita tidak rapuh dan mudah dipelihara.

---

## Tampilan di localhost :

<img width="895" height="357" alt="Screenshot 2025-11-13 195404" src="https://github.com/user-attachments/assets/5d36a2d4-c08d-4bef-8335-183c9021c6c2" />
