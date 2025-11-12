# Aplikasi File Tunggal (Hello World)

Tutorial ini adalah langkah pertama untuk memahami *framework* Pyramid. Tujuannya bukan hanya menampilkan "Hello World!", tetapi untuk memperkenalkan konsep-konsep paling fundamental dari Pyramid dalam unit terkecil yang mungkin: **satu file Python**.

Ini adalah pendekatan "microframework" yang ditawarkan Pyramid.

## 🚀 Cara Menjalankan (Windows)

Langkah-langkah ini ditulis untuk dieksekusi dari dalam terminal PowerShell dari folder `01_hello_world`.

1.  **Aktifkan Virtual Environment:**
    ```powershell
    ..\venv\Scripts\Activate.ps1
    ```

2.  **Install Paket yang Dibutuhkan:**
    (Hanya perlu dijalankan sekali)
    ```powershell
    pip install pyramid waitress
    ```

3.  **Jalankan Aplikasi:**
    ```powershell
    python app.py
    ```

### Hasil yang Diharapkan

Server akan berjalan. Anda akan melihat *output* di terminal yang mirip dengan:

````

Serving on [http://0.0.0.0:6543](https://www.google.com/search?q=http://0.0.0.0:6543)
Serving on http://[::ffff:0.0.0.0]:6543

````

Buka browser Anda dan kunjungi `http://localhost:6543/`. Anda akan melihat halaman web dengan tulisan "Hello World!".

---

## 🔬 Analisis Percobaan

### Tujuan Utama Pembelajaran

* Membuat aplikasi web yang fungsional hanya dengan satu file `.py`.
* Memahami peran **WSGI Server** (`waitress`) dan **WSGI Application** (`app`).
* Memperkenalkan tiga komponen inti Pyramid: **Configurator**, **Route**, dan **View**.

### Anatomi Kode (`app.py`)

Mari kita bedah file `app.py` untuk menganalisis setiap bagian dan perannya.

```python
from waitress import serve
from pyramid.config import Configurator
from pyramid.response import Response


def hello_world(request):
    print('Incoming request')
    return Response('<body><h1>Hello World!</h1></body>')


if __name__ == '__main__':
    with Configurator() as config:
        config.add_route('hello', '/')
        config.add_view(hello_world, route_name='hello')
        app = config.make_wsgi_app()
    serve(app, host='0.0.0.0', port=6543)
````

-----

### 1\. Impor (Baris 1-3)

  * `waitress (serve)`: Ini adalah **WSGI Server**. Tugasnya adalah "mendengarkan" koneksi HTTP (misalnya di port 6543) dan meneruskan *request* ke aplikasi Python kita. Pyramid tidak memiliki server bawaan untuk produksi, jadi kita menggunakan `waitress`.
  * `pyramid.config (Configurator)`: Ini adalah **otak** dari aplikasi Pyramid Anda. Ini adalah objek yang Anda gunakan untuk "merakit" aplikasi Anda, mendaftarkan rute, *view*, *template*, dll.
  * `pyramid.response (Response)`: Ini adalah objek standar yang *harus* dikembalikan oleh sebuah *view*. Pyramid menangani objek ini dan mengubahnya menjadi respons HTTP yang sebenarnya untuk dikirim ke browser.

### 2\. *View Callable* (Baris 6-8)

```python
def hello_world(request):
    print('Incoming request')
    return Response('<body><h1>Hello World!</h1></body>')
```

  * Ini disebut **View Callable** (fungsi yang bisa dipanggil sebagai *view*).
  * **Analisis:** Ini adalah inti dari logika aplikasi Anda. Tugasnya sederhana: menerima objek `request` dan mengembalikan objek `Response`.
  * Parameter `request` berisi semua informasi tentang permintaan yang masuk (URL, *header*, data formulir, dll.). Meskipun tidak digunakan di sini, parameter ini wajib ada.

### 3\. Titik Masuk (Baris 11)

```python
if __name__ == '__main__':
```

  * **Analisis:** Ini adalah standar Python untuk menandakan bahwa kode di dalam blok ini hanya akan dieksekusi ketika file `app.py` dijalankan secara langsung (misalnya: `python app.py`), bukan saat diimpor sebagai modul oleh file lain.

### 4\. Konfigurasi Aplikasi (Baris 12-15)

Ini adalah bagian terpenting dari tutorial ini.

```python
    with Configurator() as config:
        config.add_route('hello', '/')
        config.add_view(hello_world, route_name='hello')
        app = config.make_wsgi_app()
```

  * **Baris 12:** Kita membuat instance dari `Configurator`. Menggunakan `with` adalah praktik terbaik untuk memastikan *setup* dan *teardown* (jika ada) ditangani dengan benar.
  * **Baris 13:** `config.add_route('hello', '/')`
      * **Analisis:** Ini adalah **pemetaan Rute (Routing)**. Kita memberi tahu Pyramid: "Jika ada *request* yang masuk ke URL *path* `/` (root URL), berikan nama internal `'hello'` pada rute tersebut."
  * **Baris 14:** `config.add_view(hello_world, route_name='hello')`
      * **Analisis:** Ini adalah **pemetaan View (View Configuration)**. Ini adalah langkah krusial yang menghubungkan rute dan *view*. Kita memberi tahu Pyramid: "Jika ada *request* yang cocok dengan rute bernama `'hello'`, tolong eksekusi fungsi `hello_world`."
  * **Baris 15:** `app = config.make_wsgi_app()`
      * **Analisis:** Setelah semua konfigurasi selesai (rute dan *view* ditambahkan), kita memanggil `.make_wsgi_app()`. `Configurator` sekarang "memanggang" semua pengaturan tersebut menjadi satu objek **Aplikasi WSGI** (`app`) yang siap pakai.

### 5\. Menjalankan Server (Baris 16)

```python
    serve(app, host='0.0.0.0', port=6543)
```

  * **Analisis:** Kita sekarang menyerahkan objek `app` (WSGI Application kita) ke server `waitress` (WSGI Server). `waitress` mulai berjalan, mendengarkan di semua alamat IP (`0.0.0.0`) pada port `6543`.

-----

### Konsep Kunci yang Dipelajari

  * **Pemisahan Server dan Aplikasi (WSGI):** Ada perbedaan jelas antara *server* (`waitress`) yang menangani koneksi jaringan, dan *aplikasi* (`app`) yang berisi logika bisnis. Mereka berkomunikasi melalui standar yang disebut **WSGI**.
  * **Configurator Sentral:** `Configurator` adalah pusat dari perakitan aplikasi di Pyramid.
  * **Pola Tiga Langkah: Route -\> View -\> Response:**
    1.  *Request* masuk.
    2.  Pyramid mencocokkannya dengan **Route** (misal: `/` cocok dengan nama `hello`).
    3.  Pyramid menemukan **View** yang terhubung ke nama rute tersebut (fungsi `hello_world`).
    4.  Pyramid mengeksekusi *view*, yang mengembalikan **Response**.
  * **Konfigurasi Imperatif:** Kita secara aktif *memerintahkan* `config` untuk melakukan sesuatu (`.add_route()`, `.add_view()`). Ini adalah ciri khas Pyramid yang membuatnya sangat fleksibel.

### Kesimpulan Analisis

Percobaan "Hello World" ini sangat padat. Ini menunjukkan bahwa Pyramid dapat bertindak sebagai *microframework* tetapi sudah memperkenalkan pola desain utamanya: **konfigurasi eksplisit dan pemisahan yang jelas antara rute, *view*, dan server.**

Tampilan di localhost :

![Tampilan localhost](gambar1.png) 
