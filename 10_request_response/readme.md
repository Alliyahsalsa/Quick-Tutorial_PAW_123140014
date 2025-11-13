# Objek Request dan Response

Dokumen ini menganalisis cara kerja objek request dan response dalam Pyramid. Ini adalah inti dari aplikasi web dinamis: menerima input (data) dari pengguna dan menggunakannya untuk menghasilkan output (tampilan) yang spesifik.
Kita akan fokus pada input yang paling umum: data dari segmen URL dinamis (misalnya, /hello/Budi).

---

## Objektif (Tujuan Utama) 
- **Rute Dinamis:** Memahami cara mendefinisikan rute yang berisi placeholder (seperti /hello/{name}).  
- **Objek Request:** Mempelajari cara "mengekstrak" data dari URL menggunakan atribut `request.matchdict`.  
- **Adaptasi Tes:** Memperbarui unit test dan functional test kita untuk menangani dan memvalidasi rute dinamis ini.

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

Buka [http://localhost:6543/hello/NamaAnda](http://localhost:6543/hello/NamaAnda) di browser Anda.

Jalankan Tes:

```powershell
(venv) PS C:\...> pytest tutorial/tests.py
```

---

## Anatomi Proyek (Analisis Mendalam)

### 1. tutorial/**init**.py (Rute Dinamis)

Kita menambahkan rute baru yang berisi segmen dinamis (`{name}`).

```python
# Dari tutorial/__init__.py
def main(global_config, **settings):
    # ...
    with Configurator(settings=settings) as config:
        # ... (rute 'home' sebelumnya) ...
        config.add_route('hello', '/howdy')
        
        # Rute Dinamis
        config.add_route('hello_name', '/hello/{name}')

        config.scan('.views')
        return config.make_wsgi_app()
```

**Analisis:**
`config.add_route('hello_name', '/hello/{name}')`:
Kita mendaftarkan rute baru bernama `hello_name`.
Bagian `{name}` adalah placeholder dinamis. Pyramid akan "menangkap" bagian apa pun dari URL setelah `/hello/` dan menyimpannya.
Contoh: URL `/hello/Andi` akan cocok, dan Pyramid akan menyimpan `name = 'Andi'`.

---

### 2. tutorial/views.py (Mengakses Data Request)

Kita menambahkan method baru di kelas `TutorialViews` kita untuk menangani rute baru ini.

```python
# Dari tutorial/views.py
# ... (class TutorialViews) ...

    # ... (method 'home' dan 'hello' sebelumnya) ...

    @view_config(route_name='hello_name', renderer='tutorial:templates/hello.pt')
    def hello_name(self):
        """
        Method view untuk route dinamis 'hello_name'.
        """
        name = self.request.matchdict['name']
        return {'name': name}
```

**Analisis `self.request.matchdict`:**
`self.request` (yang kita simpan di `__init__`) adalah "pintu masuk" kita ke semua data input.
`request.matchdict` adalah dictionary khusus yang dibuat oleh Pyramid.
Saat rute `{name}` dicocokkan, Pyramid secara otomatis menempatkan nilai dari URL ke dalam dictionary ini.
`name = self.request.matchdict['name']`: Baris ini mengekstrak nilai (misalnya, 'Andi') dari matchdict dan menyimpannya ke variabel `name`.
`return {'name': name}`: Kita kemudian meneruskan nama dinamis ini ke template kita.

---

### 3. tutorial/templates/hello.pt (Template Baru)

Kita membuat template baru yang mirip, tetapi mungkin sedikit berbeda untuk view baru ini.

```html
<!-- File: tutorial/templates/hello.pt -->
<div metal:define-macro="main">
    <h1>Hi ${name}!</h1>
    <p>Go back <a href="/">home</a></p>
</div>
```

**Analisis:**
Template ini sama-sama menggunakan `${name}`, tetapi sekarang ia akan diisi oleh data dinamis yang ditarik dari URL.

---

### 4. tutorial/tests.py (Menguji Kode Dinamis)

Ini adalah bagian yang paling penting. Bagaimana kita menguji sesuatu yang dinamis?
Kita perlu memperbarui unit test dan functional test.

#### Unit Test (BERUBAH):

Unit test menguji secara terisolasi. Ia tidak tahu apa-apa tentang URL.
Jadi, kita harus "memalsukan" (mock) `matchdict` secara manual.

```python
# Dari tutorial/tests.py

# ... (test_home dan test_hello sebelumnya) ...

def test_hello_name(self):
    from tutorial.views import TutorialViews
    request = testing.DummyRequest()

    # Kita "memalsukan" apa yang seharusnya dilakukan
    # oleh Pyramid (mengisi matchdict)
    request.matchdict = {'name': 'TestUser'} 

    inst = TutorialViews(request)
    response = inst.hello_name()
    self.assertEqual(response['name'], 'TestUser')
```

**Analisis:**
Kita membuat `DummyRequest` dan secara manual menyisipkan `matchdict` palsu.
Tes ini membuktikan bahwa jika `matchdict` ada, method `hello_name` akan menggunakannya dengan benar.

---

#### Functional Test (BERUBAH):

Functional test menguji keseluruhan alur. Ia tidak perlu "memalsukan" apa pun.
Kita bisa langsung mengakses URL dinamisnya.

```python
# Dari tutorial/tests.py

# ... (test_home dan test_hello fungsional sebelumnya) ...

def test_hello_name_functional(self, testapp):
    # Kita memanggil URL dinamisnya secara langsung
    res = testapp.get('/hello/TestUser', status=200)

    # Kita cek HTML final yang di-render
    assert b'Hi TestUser!' in res.body
```

**Analisis:**
Tes ini jauh lebih kuat. Ia membuktikan bahwa seluruh sistem bekerja:
`add_route` berhasil menangkap `{name}`, `matchdict` diisi dengan benar,
view dieksekusi, dan template me-render `TestUser` di HTML akhir.

---

## Kesimpulan Analisis
Eksperimen ini adalah inti dari aplikasi web. Kita belajar bahwa `request` adalah objek yang kaya, berisi semua input dari pengguna.
`request.matchdict` adalah mekanisme elegan Pyramid untuk mengubah segmen URL dinamis menjadi data yang dapat digunakan di dalam view kita.
Kita juga membuktikan bahwa kita dapat menguji perilaku dinamis ini secara menyeluruh menggunakan kombinasi **unit test** (dengan mocking) dan **functional test** (dengan request nyata).

---

## Tampilan di localhost :