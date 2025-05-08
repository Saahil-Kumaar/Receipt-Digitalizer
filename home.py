import sys
import subprocess
from datetime import datetime
import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from PIL import Image
import io
import re
import process
import firebase_admin
from firebase_admin import credentials, firestore

# # Configuration for Firebase
# FIREBASE_CONFIG = {
#     "apiKey": "AIzaSyCXWB1lfuOnm1TTGJFbKDZNTQX7JHa0xKs",
#     "authDomain": "receipt-digitalizer.firebaseapp.com",
#     "databaseURL": "https://receipt-digitalizer-default-rtdb.asia-southeast1.firebasedatabase.app",
#     "projectId": "receipt-digitalizer",
#     "storageBucket": "receipt-digitalizer.firebasestorage.app",
#     "messagingSenderId": "324902927921",
#     "appId": "1:324902927921:web:16178e7361f907ccdadf10",
#     "measurementId": "G-Q1L4B0TMVS",
# }

# Regular expression patterns for date recognition
DATE_PATTERNS = [
    r'\b\d{2}/\d{2}/\d{4}\b',   # MM/DD/YYYY
    r'\b\d{2}-\d{2}-\d{4}\b',   # MM-DD-YYYY
    r'\b\d{2}/\d{2}/\d{2}\b',   # MM/DD/YY
    r'\b\d{2}-\d{2}-\d{2}\b',   # MM-DD-YY
    r'\b\d{4}/\d{2}/\d{2}\b',   # YYYY/MM/DD
    r'\b\d{4}-\d{2}-\d{2}\b',   # YYYY-MM-DD
    r'\b\d{2}\.\d{2}\.\d{4}\b',   # DD.MM.YYYY
    r'\b\d{4}\.\d{2}\.\d{2}\b',   # YYYY.MM.DD
    r'\b\d{1}/\d{2}/\d{4}\b',   # M/DD/YYYY
    r'\b\d{1}-\d{2}-\d{4}\b',   # M-DD-YYYY
    r'\b\d{1}/\d{2}/\d{2}\b',   # M/DD/YY
    r'\b\d{1}-\d{2}-\d{2}\b',   # M-DD-YY
    r'\b\d{4}/\d{1}/\d{2}\b',   # YYYY/M/DD
    r'\b\d{4}-\d{1}-\d{2}\b',   # YYYY-M-DD
    r'\b\d{2}\.\d{1}\.\d{4}\b',   # DD.M.YYYY
    r'\b\d{4}\.\d{1}\.\d{2}\b',   # YYYY.M.DD
    r'\b\d{1}/\d{1}/\d{4}\b',  # M/D/YYYY
    r'\b\d{1}-\d{1}-\d{4}\b',  # M-D-YYYY
    r'\b\d{4}/\d{1}/\d{1}\b',  # YYYY/M/D
    r'\b\d{4}-\d{1}-\d{1}\b',  # YYYY-M-D
    r'\b\d{1}\.\d{1}\.\d{4}\b',  # D.M.YYYY
    r'\b\d{4}\.\d{1}\.\d{1}\b'  # YYYY.M.D
]

# Regular expression pattern for price recognition
PRICE_PATTERN = r'\$?\d+\.\d{2}'

# Skip keywords in receipt parsing
SKIP_KEYWORDS = ['total', 'subtotal', 'change', 'cash', 'credit', 'phone', 'receipt']

def check_tesseract():
    """Check if PyTesseract is properly installed and return the module if successful."""
    try:
        import pytesseract
        return pytesseract
    except ImportError as e:
        st.error("PyTesseract import failed. Please check installation.")
        st.error(f"Error details: {str(e)}")
        return None

def parse_date(date_str):
    """Parse the date string and return a formatted date string."""
    date_formats = ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y',
                    '%Y/%m/%d', '%Y-%m-%d', '%d.%m.%Y', '%Y.%m.%d']
    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, date_format)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None

def process_receipt_image(image):
    """
    Process the receipt image using OCR and extract relevant information,
    assuming left column contains text and right column contains numbers.
    """
    pytesseract = check_tesseract()
    if not pytesseract:
        return pd.DataFrame()

    try:
        # Convert the image to text using pytesseract
        text = pytesseract.image_to_string(image)

        # Parse the text to extract line items
        lines = text.split('\n')
        items = []
        merchant_found = False
        date_assigned = False

        # Find dates in the text
        dates = []
        for pattern in DATE_PATTERNS:
            found_dates = re.findall(pattern, text)
            dates.extend(found_dates)

        bill_date = dates[0] if dates else datetime.now().strftime("%Y-%m-%d")

        for line in lines:
            if not merchant_found and len(line) > 3:
                merchant_name = line
                merchant_found = True
                continue

            # Skip empty lines and header/footer text
            if not line.strip() or any(skip in line.lower() for skip in SKIP_KEYWORDS):
                continue

            # Look for price patterns at the end of the line
            prices = re.findall(PRICE_PATTERN, line)

            if prices:
                # Get the last price in the line (rightmost)
                price = prices[-1]

                # Extract item name (everything before the last price)
                item_name = line[:line.rfind(price)].strip()

                # Remove any extra prices from the item name
                for p in prices[:-1]:
                    item_name = item_name.replace(p, '').strip()

                # Remove common separators and clean up the item name
                item_name = re.sub(r'[.]{2,}|[@\t]+', ' ', item_name).strip()

                if not date_assigned and dates:
                    bill_date = dates[0]
                    date_assigned = True

                # Only add if we have both an item name and price
                if item_name and not item_name.isspace():
                    items.append({
                        'item': item_name,
                        'price': float(price.replace('$', '')),
                        'timestamp': bill_date,
                        'merchant_name': merchant_name if merchant_found else 'Unknown Merchant'
                    })

        # Create DataFrame and sort by price
        df = pd.DataFrame(items)
        if not df.empty:
            df = df.sort_values('price', ascending=False)

        return df
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return pd.DataFrame()

def initialize_firebase():
    """Initialize Firebase Admin SDK."""
    if not firebase_admin._apps:
        cred = credentials.Certificate('st.secrets["FIRESON"]')
        firebase_admin.initialize_app(cred)

def app():
    """Main application function."""
    st.title("Receipt Scanner")

    # Initialize Firebase Admin SDK
    initialize_firebase()

    # Display system information in the sidebar
    st.sidebar.write("System Information:")
    st.sidebar.write(f"Python version: {sys.version}")

    try:
        # Check Tesseract version
        tesseract_version = subprocess.check_output(['tesseract', '--version']).decode()
        st.sidebar.write(f"Tesseract version: {tesseract_version.split()[1]}")
    except Exception as e:
        st.sidebar.error(f"Tesseract not found: {str(e)}")

    # Add file uploader that accepts images
    if st.session_state.username:
        input_method = st.radio(
            "CHOOSE INPUT METHOD:",
            ("Upload an image", "Use webcam")
        )

        if input_method == "Upload an image":
            image_file = st.file_uploader("Upload a receipt image", type=['png', 'jpg', 'jpeg'])
        else:
            image_file = st.camera_input("Take a picture of your receipt")

        if image_file is not None:
            try:
                # Display the uploaded image
                image = Image.open(image_file)
                st.image(image, caption='Uploaded Receipt', use_container_width=True)

                # Add a button to process the image
                if st.button('Process Receipt'):
                    with st.spinner('Processing receipt...'):
                        # Process the image and extract line items
                        df = process_receipt_image(image)

                        if not df.empty:
                            # Display the extracted items
                            st.subheader("Extracted Items")
                            st.dataframe(df.drop(columns='merchant_name'), hide_index=True)

                            # Add summary statistics
                            st.subheader("Summary")
                            st.write("Change the data if needed.")

                            total_items = len(df)
                            total_amount = f"{df['price'].sum():.2f}"
                            merchant_name = df['merchant_name'].iloc[0]
                            date = df['timestamp'].iloc[0].split()[0]

                            valid_date = parse_date(date)

                            col1, col2 = st.columns(2)
                            query1 = col1.text_input("Merchant Name:", merchant_name)
                            query2 = col2.date_input("Date:", datetime.strptime(valid_date, '%Y-%m-%d')) if valid_date else datetime.now()
                            query3 = col1.text_input("Total Items:", total_items)
                            query4 = col2.text_input("Total Amount:", total_amount)

                            bill_data = {
                                "Merchant Name": query1,
                                "Total_price": query4,
                                "Date": query2.strftime("%Y-%m-%d")
                            }

                            # Store the bill data in the database
                            if st.button('Store Data', use_container_width=True,on_click=process.app(bill_data)):
                                st.success("Data stored successfully!")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    else:
        st.warning("Please log in to access this feature.")
