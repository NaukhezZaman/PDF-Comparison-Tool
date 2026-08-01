# 📄 PDF Comparison Tool

A Python-based PDF Comparison Tool that compares two PDF documents at the word level, highlights the differences, and generates a detailed Excel report.

The project is designed with a modular architecture, making it easy to maintain and extend with additional comparison features in the future.

---

## ✨ Features

- Compare two PDF documents
- Word-level comparison
- Detect:
  - Modified words
  - Inserted words
  - Deleted words
- Generate highlighted source and target PDFs
- Generate a professional Excel comparison report
- Timestamp-based report filenames to prevent overwriting

---

## 📂 Project Structure

```text
PDF_Comparison_Tool/
│
├── input/
├── output/
├── models/
│
├── extractor.py
├── matcher.py
├── comparer.py
├── highlighter.py
├── report_generator.py
├── config.py
├── main.py
└── README.md
```

---

## 🛠 Technologies Used

- Python 3.12
- PyMuPDF
- pdfplumber
- RapidFuzz
- OpenPyXL
- ReportLab
- Pandas

---

## 🚀 How to Run

1. Clone the repository.

```bash
git clone https://github.com/<your_username>/PDF-Comparison-Tool.git
```

2. Install the required packages.

```bash
pip install -r requirements.txt
```

3. Place the source and target PDFs inside the `input` folder.

4. Run the application.

```bash
python main.py
```

---

## 📄 Output

The application generates:

```text
output/
├── source_highlighted.pdf
├── target_highlighted.pdf
└── source_target_comparison_report_01_Aug_2026_170822.xlsx
```

---

## 🗺 Roadmap

### ✅ Implemented

- PDF text extraction
- Word matching
- Difference detection
- PDF highlighting
- Excel report generation
- Timestamp-based report naming

### 🚧 Planned

- Image comparison
- Font comparison
- Table comparison
- HTML report
- JSON export

---

## 📜 License

License information will be added in a future release.