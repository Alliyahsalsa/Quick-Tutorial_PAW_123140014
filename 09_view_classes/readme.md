# View Classes (Tampilan Berbasis Kelas)

Dokumen ini menganalisis refactoring (penataan ulang) kode dari view berbasis fungsi menjadi view berbasis kelas (class-based views). Ini adalah pola desain yang sangat umum dan kuat dalam pengembangan web. Tujuannya adalah untuk mengelompokkan view yang terkait secara logis dan mengurangi duplikasi kode dengan berbagi state (seperti request atau koneksi database) melalui instance kelas.

---

## Objektif (Tujuan Utama)

**Pengorganisasian Kode:** Mengelompokkan view yang saling terkait (misalnya home dan hello) ke dalam satu kelas (TutorialViews) agar file views.py lebih rapi.

**Prinsip DRY (Don't Repeat Yourself):** Menggunakan __init__ untuk menginisialisasi objek yang sama (seperti request) satu kali dan membagikannya ke semua method view di dalam kelas tersebut.

**Adaptasi Tes:** Memperbarui unit test agar memahami cara menginisialisasi dan menguji view berbasis kelas.

---

## Cara Menjalankan

**Aktifkan venv (jika belum):**
```bash
..\venv\Scripts\Activate.ps1
````

**Install Dependensi (jika ada perubahan):**

```bash
(venv) PS C:\...> pip install -e .
(venv) PS C:\...> pip install -e ".[dev]"
(venv) PS C:\...> pip install -e ".[test]"
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

(Hasil tes harus tetap 4 passed)

---

## Anatomi Proyek

### 1. tutorial/views.py (Perubahan Paling Fundamental)

Di sinilah perubahan utama terjadi. Dua fungsi home dan hello kini menjadi method di dalam satu kelas.

```python
from pyramid.view import view_config

# Tidak ada lagi impor 'Response'
# karena kita hanya mengembalikan dictionary.

class TutorialViews:
    def __init__(self, request):
        """
        Konstruktor yang dipanggil Pyramid setiap kali
        ada request baru. 'request' disuntikkan secara otomatis.
        """
        self.request = request

    @view_config(route_name='home', renderer='tutorial:templates/home.pt')
    def home(self):
        """
        Method view untuk route 'home'.
        Tidak perlu (request) lagi, karena sudah ada di self.request.
        """
        return {'name': 'Home View'}

    @view_config(route_name='hello', renderer='tutorial:templates/home.pt')
    def hello(self):
        """
        Method view untuk route 'hello'.
        """
        return {'name': 'Hello View'}
```

**Analisis **init**(self, request):**
Ini adalah kunci dari pola ini. Saat Pyramid perlu memanggil view di kelas ini, ia akan pertama-tama menginisialisasi kelasnya dan secara otomatis "menyuntikkan" request ke dalam konstruktor **init**.
Kita menyimpan request sebagai self.request.

**Analisis home(self) dan hello(self):**
Pola Pikir Baru: Perhatikan bahwa method ini tidak lagi menerima request sebagai parameter!
**Prinsip DRY:** Jika home atau hello perlu mengakses request, mereka bisa langsung menggunakan self.request yang sudah disimpan.

**Manfaat:** Bayangkan jika Anda perlu mendapatkan data pengguna yang sedang login.

* **Cara Lama (Fungsi):**

  ```python
  def home(request):
      user = get_user(request)
  def hello(request):
      user = get_user(request)
  ```

  (Duplikasi kode).
* **Cara Baru (Kelas):**

  ```python
  def __init__(self, request):
      self.user = get_user(request)
  ```

  Sekarang self.home() dan self.hello() bisa langsung pakai self.user tanpa duplikasi.

---

### 2. tutorial/**init**.py (Tidak Berubah!)

```python
# ...
def main(global_config, **settings):
    # ...
    with Configurator(settings=settings) as config:
        config.include('pyramid_chameleon')
        config.add_route('home', '/')
        config.add_route('hello', '/howdy')
        config.scan('.views')
        return config.make_wsgi_app()
```

**Analisis:**
Tidak ada perubahan yang diperlukan di file main.
Perintah config.scan('.views') cukup "pintar". Ia secara otomatis memindai views.py dan tahu cara menangani dekorator @view_config baik pada fungsi maupun pada kelas.
Ini menunjukkan betapa fleksibelnya mekanisme scanning Pyramid.

---

### 3. tutorial/tests.py (Adaptasi Unit Test)

Unit test kita perlu diubah karena kita tidak bisa lagi memanggil home(request) secara langsung. Kita harus "meniru" apa yang dilakukan Pyramid: buat instance kelasnya terlebih dahulu.

**Unit Test (BERUBAH):**

```python

# Impor KELAS-nya, bukan fungsinya
from tutorial.views import TutorialViews 

class TutorialViewTests(unittest.TestCase):
    # ... (setUp/tearDown tetap sama) ...

    def test_home(self):
        request = testing.DummyRequest()
        # 1. Buat instance kelasnya
        view = TutorialViews(request) 
        # 2. Panggil method-nya
        response_dict = view.home() 
        self.assertEqual(response_dict['name'], 'Home View')

    def test_hello(self):
        request = testing.DummyRequest()
        # 1. Buat instance kelasnya
        view = TutorialViews(request)
        # 2. Panggil method-nya
        response_dict = view.hello()
        self.assertEqual(response_dict['name'], 'Hello View')
```

**Analisis:** Unit test kita sekarang secara akurat mencerminkan bagaimana kode kita diatur. Kita menguji method dari sebuah instance kelas.

**Functional Test (TIDAK BERUBAH):**

```python
# ...
def test_functional_home(testapp):
    res = testapp.get('/', status=200)
    assert b'Hi Home View' in res.body 
# ...
```

**Analisis:**
Functional test kita tidak perlu diubah sama sekali.
Ini adalah bukti terbesar dari nilai functional test. Tes ini adalah "black box"; ia tidak peduli bagaimana view diimplementasikan (apakah fungsi atau kelas). Ia hanya peduli bahwa URL / mengembalikan HTML yang benar.
Fakta bahwa kita bisa me-refactor kode secara besar-besaran (dari fungsi ke kelas) dan tes fungsional kita tetap lulus adalah pencapaian besar.

---

## Kesimpulan Analisis

Beralih ke View Classes adalah langkah penting untuk skalabilitas. Ini memungkinkan kita:

* Mengelompokkan view yang serupa secara logis.
* Menerapkan prinsip DRY (Don't Repeat Yourself) dengan berbagi state (seperti self.request atau self.user) melalui **init**.

---

## Tampilan di localhost :

- Tampilan "Hi Home View"
<img width="868" height="357" alt="Screenshot 2025-11-13 090716" src="https://github.com/user-attachments/assets/d702db71-299c-4cf0-b679-48ff5ed840c7" />

- Tampilan "Hi Hello View"
<img width="923" height="375" alt="Screenshot 2025-11-13 090735" src="https://github.com/user-attachments/assets/e13b284b-d8fe-4cb2-bed0-ba43d93c3759" />
