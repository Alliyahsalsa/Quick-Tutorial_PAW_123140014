# Views dan Konfigurasi Deklaratif

Dokumen ini menganalisis proses *refactoring* (merapikan) aplikasi Pyramid dengan memisahkan *view* (logika) dari *konfigurasi* (`__init__.py`).

Ini adalah langkah fundamental untuk **skalabilitas**. Saat aplikasi tumbuh besar, kita tidak bisa menumpuk semua *view* di satu file. Kita akan memindahkan *view* ke file-nya sendiri (`views.py`) dan beralih dari konfigurasi **imperatif** (manual) ke **deklaratif** (otomatis).

-----

## Objektif (Tujuan Utama)

  * **Pemisahan Wewenang (Scalability):** Memindahkan logika *view* keluar dari `__init__.py` ke file `tutorial/views.py` agar proyek lebih rapi dan mudah dikelola.
  * **Konfigurasi Deklaratif:** Memperkenalkan dekorator `@view_config` sebagai cara "pasif" bagi *view* untuk "mengumumkan" dirinya sendiri ke *framework*.
  * **Scanning (Pemindaian):** Memperkenalkan `config.scan()` sebagai mekanisme "otomatis" Pyramid untuk menemukan dan mendaftarkan *view* yang sudah dihiasi dekorator.

-----

## Cara Menjalankan

Proyek ini dijalankan menggunakan `pserve` dan diuji menggunakan `pytest`.

1.  **Aktifkan venv (jika belum):**

    ```powershell
    ..\venv\Scripts\Activate.ps1
    ```

2.  **Install Dependensi (jika ada perubahan):**

    ```powershell
    (venv) PS C:\...> pip install -e ".[dev]"
    (venv) PS C:\...> pip install -e ".[test]"
    ```

3.  **Jalankan Aplikasi:**

    ```powershell
    (venv) PS C:\...> pserve development.ini --reload
    ```

    Buka `http://localhost:6543/` di browser Anda.

4.  **Jalankan Tes:**

    ```powershell
    (venv) PS C:\...> pytest tutorial/tests.py
    ```

-----

## Anatomi Proyek

Mari kita bedah perubahan di setiap file dan *mengapa* kita melakukannya.

### 1\. File Baru: `tutorial/views.py` (Pemisahan Logika)

Ini adalah file baru tempat semua logika *view* kita akan tinggal.

```python
from pyramid.response import Response
from pyramid.view import view_config

@view_config(route_name='hello')
def hello_world(request):
    """View callable that returns a simple Hello World response."""
    return Response('<body><h1>Hello World!</h1></body>')
```

  * **Analisis:**
      * Fungsi `hello_world` (dan impor `Response`) telah **dipindahkan** ke sini dari `__init__.py`.
      * **Pemisahan Wewenang:** `__init__.py` sekarang bersih dan hanya berfokus pada *konfigurasi* dan *perakitan* aplikasi, sementara `views.py` berfokus murni pada *logika bisnis* (apa yang harus dilakukan saat URL diakses).
      * **Skalabilitas:** Jika kita punya 50 *view* (misal: `login`, `logout`, `dashboard`), kita tinggal menambahkannya di file ini, bukan mengotori `__init__.py`.

### 2\. Dekorator `@view_config` (Konfigurasi Deklaratif)

Ini adalah "sihir" dari Pyramid. Perhatikan baris `@view_config(route_name='hello')`.

  * **Analisis:**
      * **Apa itu?** Ini adalah *dekorator* (penghias) yang "menandai" fungsi `hello_world`.
      * **Apa fungsinya?** Ini adalah cara "pasif" bagi *view* untuk memberi tahu Pyramid: "Hei, jika ada yang memanggil rute bernama `hello`, saya adalah fungsi yang harus dieksekusi."
      * **Menggantikan Apa?** Ini menggantikan panggilan manual `config.add_view(hello_world, route_name='hello')` yang sebelumnya kita tulis di `__init__.py`.

### 3\. `tutorial/__init__.py` (Modifikasi `main`)

File ini sekarang menjadi jauh lebih bersih dan sederhana.

```python
from pyramid.config import Configurator

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        # 1. Rute masih didaftarkan di sini
        config.add_route('hello', '/') 
        
        # 2. 'add_view' HILANG, diganti 'scan'
        config.scan('.views')
        
        return config.make_wsgi_app()
```

  * **Analisis `config.scan('.views')`:**

      * **Apa itu?** `config.scan()` adalah perintah "otomatis" Pyramid. Kita menyuruh `Configurator` untuk "memindai" modul `tutorial.views` (disingkat `.views`).
      * **Apa yang dicari?** Ia mencari dekorator `@view_config` yang kita pasang di `views.py`.
      * **Apa yang terjadi?** Saat `scan` menemukan `@view_config(route_name='hello')` di atas fungsi `hello_world`, ia secara otomatis menjalankan `config.add_view(hello_world, route_name='hello')` untuk kita di latar belakang.

  * **Analisis `config.add_route` (Kenapa Masih Ada?):**

      * Tutorial ini memisahkan **definisi rute** (`add_route`) dari **konfigurasi *view*** (`view_config`).
      * `config.add_route('hello', '/')` mendefinisikan URL dan memberinya nama (`hello`).
      * `@view_config(route_name='hello')` menghubungkan nama rute itu ke fungsi.
      * Ini adalah pola yang sangat umum: `__init__.py` bertindak sebagai "peta" URL terpusat, sementara setiap `views.py` menangani tujuannya masing-masing.

### 4\. `tutorial/tests.py` (Modifikasi Impor)

Tes kita gagal jika kita tidak memperbaruinya, karena lokasi `hello_world` telah berubah.

  * **Kode Lama (Error):**
    `from tutorial import hello_world`

  * **Kode Baru (Benar):**
    `from tutorial.views import hello_world`

  * **Analisis:**

      * Ini adalah bagian penting dari *maintenance* (perawatan) kode. Ketika Anda me-*refactor* (memindahkan) kode, Anda juga harus memperbarui tes yang menggunakannya.
      * Tes fungsional (`test_root`) tidak perlu diubah sama sekali, karena tes itu tidak peduli *di mana* `hello_world` berada. Ia hanya mengakses URL `/` (black box) dan itu sudah cukup.

-----

## Kesimpulan Analisis

Ini adalah langkah penting untuk "mendewasakan" aplikasi kita.

Dengan memindahkan *view* ke file terpisah dan menggunakan `config.scan()`, kita membuat proyek yang **jauh lebih mudah untuk dikembangkan**. *File* `__init__.py` kita sekarang bersih dan stabil. Jika kita ingin menambah 10 halaman baru, kita hanya perlu bekerja di dalam `views.py` (menambah fungsi dan dekorator) tanpa perlu menyentuh `__init__.py` lagi.

---

## Tampilan di localhost :

- Tampilan "Visit hello"
<img width="926" height="464" alt="Screenshot 2025-11-13 003210" src="https://github.com/user-attachments/assets/2726ddba-345e-48fe-9ef5-79faa03ad1d0" />

- Tampilan "Go back home"
<img width="804" height="328" alt="image" src="https://github.com/user-attachments/assets/0e0f4bc4-9ba7-4a51-9c2f-970b070ded77" />