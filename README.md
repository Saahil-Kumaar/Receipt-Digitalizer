# 🧾 Receipt-Digitalizer

A **Streamlit-based web application** for digitizing your paper receipts, extracting key information using OCR, and organizing your expenses—all in one place!

---

## ✨ Features

* 📸 **Upload Receipts** – Upload scanned images of your receipts or upload then via WebCam.
* 🤖 **OCR Processing** – Automatically extract text such as date, amount, and vendor using OCR.
* 📊 **Expense Tracking** – Organize and view your past receipts in one dashboard.
* 👤 **User Accounts** – Log in and manage your own set of receipts securely.
* 🖥️ **Simple UI** – Clean, interactive interface powered by Streamlit.

---

## 🚀 Getting Started

Follow these steps to set up and run the app locally:

### 1. Clone the Repository

```bash
git clone https://github.com/Saahil-Kumaar/Receipt-Digitalizer.git
cd Receipt-Digitalizer
```

### 2. Install Dependencies

Make sure Python is installed. Then run:

```bash
pip install -r requirements.txt
```

### 3. Launch the App

```bash
streamlit run main.py
```

---

## 🗂️ Project Structure

```
Receipt-Digitalizer/
│
├── main.py               # Main app launcher
├── about.py              # About section
├── account.py            # User authentication
├── home.py               # Landing page
├── process.py            # Receipt text processing (OCR)
├── your_posts.py         # View uploaded receipts
├── requirements.txt      # Python dependencies
├── packages.txt          # Additional package info
└── .streamlit/           # Streamlit config
```

---

## 📸 How It Works

1. 🧾 **Upload** an image of your receipt.
2. 🤖 The app processes it using OCR (Pytesseract or similar).
3. 📤 Extracted data is displayed and saved to your account.
4. 📚 **Manage** all your receipts under "Your Posts."

---

## 💡 Technologies Used

* [Streamlit](https://streamlit.io/)
* [Python](https://www.python.org/)
* [Pytesseract](https://pypi.org/project/pytesseract/)
* [Pandas](https://pandas.pydata.org/)
* [Pillow](https://python-pillow.org/)

---

## 🛠️ Contributing

Contributions are welcome! 🎉

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Commit your changes.
4. Push to the branch and create a Pull Request.

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 📬 Contact

* ✉️ Email: [sk7593277@gmail.com](mailto:sahill.kumaarr@gmail.com)
* 🧑‍💻 GitHub: [Saahil-Kumaar](https://github.com/Saahil-Kumaar)
Thankyou