from os import path as ospath
from tkinter import filedialog
from typing import List
from email.mime.multipart import MIMEMultipart

from libs import SecretSanta, LastOneException, MatchingErrorException, csv_import

"""
    DATA STRUCTURE
"""
csv_filter = ("CSV files", "*.csv")
csv_path = filedialog.askopenfile(initialdir="/", title="Select a File", filetypes=[csv_filter]).name

if not ospath.isfile(csv_path) or not csv_path.endswith(".csv"):
    raise RuntimeError("Csv file imported not valid!")

entries = csv_import(csv_path)


secret_santa = SecretSanta(entries)

emails: List[MIMEMultipart] = []

for _ in range(10):
    emails.clear()
    try:
        emails = secret_santa.calc_secret_santa()
    except LastOneException:
        raise
    except MatchingErrorException:
        pass
    else:
        break

secret_santa.print()

"""
    EMAIL SENDING

context = ssl.create_default_context()

for email in emails:
    # * only Gmail!
    # * port = 465  # for SSL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(sender_email, app_password)
        receiver_email = str(email["To"])
        smtp.sendmail(sender_email, receiver_email, email.as_string())
"""
