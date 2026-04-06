# AI Code Detector (Heuristic-Based)

Web application berbasis Streamlit untuk memperkirakan apakah kode tampak seperti hasil AI. Proyek ini awalnya hanya untuk Python, lalu diperluas agar bisa menganalisis kode web PHP secara lebih relevan.

## Dukungan Bahasa

- Python (`.py`)
- PHP untuk aplikasi web sederhana atau file campuran PHP + HTML (`.php`)
- Dart/Flutter (`.dart`)

## Cara Kerja

Detector memakai heuristic scoring, bukan model machine learning dan bukan API eksternal. Sistem menilai pola struktur dan bahasa yang sering muncul pada kode hasil AI.

### Sinyal Umum

- Rasio komentar
- Komentar generik atau terlalu menjelaskan
- Panjang rata-rata baris
- Rasio baris kosong
- Ada atau tidaknya debug statement
- Placeholder/demo text
- Nama identifier yang terlalu generik
- Pola baris yang berulang

### Sinyal Python

- Jumlah fungsi
- Jumlah `try/except`
- Jumlah docstring
- Struktur AST valid

### Sinyal PHP Web

- Docblock berlebih
- Campuran PHP, HTML, CSS, JavaScript, database, dan form dalam satu file
- Pola single-file full-stack page
- Penggunaan superglobal/form/database yang bercampur tanpa pemisahan concern

### Sinyal Dart/Flutter

- Banyak komentar generik yang menjelaskan widget atau flow secara terlalu eksplisit
- Placeholder/demo text pada UI
- Widget tree sangat besar dalam satu file
- Boilerplate named parameter yang terlalu seragam
- Pola single large widget file tanpa pemisahan widget kecil

## Klasifikasi

- `0-40%`: Likely Human
- `41-70%`: Suspicious / Mixed
- `71-100%`: Likely AI-generated

## Instalasi

```bash
pip install -r requirements.txt
```

## Menjalankan Aplikasi

```bash
streamlit run app.py
```

Lalu upload file `.py`, `.php`, atau `.dart` untuk melihat hasil analisis.

## Disclaimer

Heuristic-based detection tidak 100% akurat dan tidak boleh dianggap sebagai bukti tunggal. Hasil terbaik didapat bila dipakai bersama review manual terhadap gaya penamaan, arsitektur file, dan konteks proyek.
