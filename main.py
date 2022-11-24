from typing import List
from random import choice as ran_choice, shuffle
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender_email: str = "noreply.babbo.natale.segreto@gmail.com"
# gmail password for external app allowance
app_password: str = "eelpxplqroyebizq"

budget: float = 20.
attempts: int = 10

"""
    DATA STRUCTURE
"""


class LastOneException(Exception):
    pass


class MatchingErrorException(Exception):
    pass


class SecretSantaEntry():

    def __init__(self, user_name: str, user_mail: str, exc_list: str) -> None:
        self.user_name: str = user_name
        self.user_mail: str = user_mail
        self.exc_list: list = exc_list


class SecretSanta():
# TODO: html parser that reads external html file

    html_header = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Document</title>
        <style>
        @import url("https://fonts.googleapis.com/css2?family=Raleway:ital,wght@1,200&display=swap");

        * {
            margin: 0;
            padding: 0;
            border: 0;
        }

        body {
            font-family: "Raleway", sans-serif;
            background-color: #d8dada;
            font-size: 19px;
            max-width: 800px;
            margin: 0 auto;
            padding: 3%;
        }

        img {
            max-width: 100%;
        }

        header {
            width: 98%;
        }

        #logo {
            max-width: 120px;
            margin: 3% 0 3% 3%;
            float: left;
        }

        #wrapper {
            background-color: #f0f6fb;
        }

        h1,
        h4,
        p {
            margin: 3%;
        }
        .btn {
            float: right;
            margin: 0 2% 4% 0;
            background-color: #303840;
            color: #f6faff;
            text-decoration: none;
            font-weight: 800;
            padding: 8px 12px;
            border-radius: 8px;
            letter-spacing: 2px;
        }

        hr {
            height: 1px;
            background-color: #303840;
            clear: both;
            width: 96%;
            margin: auto;
        }

        #contact {
            text-align: center;
            padding-bottom: 3%;
            line-height: 16px;
            font-size: 12px;
            color: #303840;
        }
        </style>
    </head>
    <body>
        <div id="wrapper">
        <div id="banner">
            <img
            src="https://cdn.pixabay.com/photo/2016/12/16/15/25/christmas-1911637_960_720.jpg"
            alt=""
            />
        </div>
        <div class="one-col">
            <h1>Ciao -GIFTER-!</h1>

            <p>Questo Natale devi fare un regalo ad una persona molto speciale:
            </p>

            <h4>-RECEIVER-
            </h4>

            <p>&#9924;&#9924;&#9924;</p>

            <p>Mi raccomando il budget è di <b>-BUDGET-€</b> e acqua in bocca!
            </p>

            <hr>

            <p>P.S. purtroppo quest'anno è la versione 1.0 quindi niente wishlist &#128583;
            </p>

            <footer>
            <img
            src="https://cdn.pixabay.com/photo/2015/11/13/15/45/christmas-1042149_960_720.jpg"
            alt=""
            >
            </footer>
        </div>
        </div>
    </body>
    </html>"""

    def __init__(self, entries: List[SecretSantaEntry]) -> None:
        self.entries: List[SecretSantaEntry] = entries

    def _get_mails_list(self) -> List[str]:
        return [x.user_mail for x in self.entries]

    """def _get_users_list(self) -> List[str]:
        return [x.user_name for x in self.entries]"""

    """def _get_exc_list_by_mail(self, mail: str) -> List[str]:
        for entry in self.entries:
            if entry.user_mail == mail:
                return entry.exc_list
        return []"""

    def _get_user_name_by_mail(self, mail: str) -> str:
        for entry in self.entries:
            if entry.user_mail == mail:
                return entry.user_name

        raise RuntimeError("No entry with this email!!")

    """def _get_entry_by_mail(self, mail: str) -> SecretSantaEntry:
        for entry in self.entries:
            if entry.user_mail == mail:
                return entry

        raise RuntimeError("No entry with this email!")"""

    def _create_email_message(self,
                              receiver: SecretSantaEntry,
                              lucky_one: str) -> MIMEMultipart:
        subject = "Un messaggio dal Babbo Natale Segreto. Shhhh"

        email_msg = MIMEMultipart("alternative")
        email_msg["Subject"] = subject
        email_msg["From"] = sender_email
        email_msg["To"] = receiver.user_mail

        format_dict = {
            "-GIFTER-": receiver.user_name,
            "-RECEIVER-": lucky_one,
            "-BUDGET-": f"{budget:.0f}"}

        body = self.html_header

        for key, value in format_dict.items():
            body = body.replace(key, value)

        msg = MIMEText(body, "html")
        email_msg.attach(msg)

        return email_msg

    def calc_secret_santa(self) -> List[MIMEMultipart]:
        return_msgs = []
        all_mails = self._get_mails_list()
        senders_list = all_mails

        shuffle(self.entries)
        for entry in self.entries:
            # if I already assigned a lucky one to this chap
            if entry.user_mail not in senders_list:
                continue

            # se ultima combinazione
            if len(senders_list) == 1:
                if entry.user_mail == senders_list:
                    raise RuntimeError("Last one remaining. Ankwaaaard")

                # TODO: trovare un modo per ricalcolare le soluzioni
                if senders_list[0] in entry.exc_list:
                    # TODO: VERIFICO ED EFFETTUO UNO SWITCH TRA LE COMBINAZIONI
                    if not self._try_switch():
                        raise RuntimeError("Last possible solution can't be accepted! Mail in exception list")

                lucky_user_name = self._get_user_name_by_mail(senders_list[0])
                em = self._create_email_message(entry, lucky_user_name)

                return_msgs.append(em)
                return return_msgs

            def condition(x: str, entry: SecretSantaEntry):
                return x not in entry.exc_list and x != entry.user_mail

            # recupero valore casuale da lista
            possible_lucky_ones = [x for x in all_mails if condition(x, entry)]

            if not possible_lucky_ones:
                raise RuntimeError("The exceptions set for {} are too restrictive!!".format(entry.user_mail))

            # get a random one out from possible_lucky_ones
            lucky_one = ran_choice(possible_lucky_ones)

            lucky_one_name = self._get_user_name_by_mail(lucky_one)
            em = self._create_email_message(entry, lucky_one_name)

            return_msgs.append(em)

            senders_list.remove(entry.user_mail)


example_metadata = [
    SecretSantaEntry(
        "Alessandro",
        "alexbernini97@gmail.com",
        ["valentinazanelli3@gmail.com"]),
    SecretSantaEntry(
        "Valentina",
        "valentinazanelli3@gmail.com",
        ["alexbernini97@gmail.com"]),
    SecretSantaEntry(
        "Sylvie",
        "tassisylvie@gmail.com",
        []),
    SecretSantaEntry(
        "Raffaele",
        "raffaelebernini@live.it",
        []),
    SecretSantaEntry(
        "Marghe",
        "marghebernini@gmail.com",
        []),
    SecretSantaEntry(
        "Franco",
        "tassi.francesco1942@gmail.com",
        ["mariefrance.dimier43@gmail.com"]),
    SecretSantaEntry(
        "Marie France",
        "mariefrance.dimier43@gmail.com",
        ["tassi.francesco1942@gmail.com"]),
    SecretSantaEntry(
        "Christophe",
        "tassinoel72@gmail.com",
        ["lau.erre@gmail.com"]),
    SecretSantaEntry(
        "Laura",
        "lau.erre@gmail.com",
        ["tassinoel72@gmail.com"])]


secret_santa = SecretSanta(example_metadata)

emails: List[MIMEMultipart] = []

for _ in range(attempts):
    emails.clear()
    try:
        emails = secret_santa.calc_secret_santa()
    except LastOneException:
        raise
    except MatchingErrorException:
        pass
    else:
        break

context = ssl.create_default_context()

for email in emails:
    # * only Gmail!
    # * port = 465  # for SSL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(sender_email, app_password)
        receiver_email = str(email["To"])
        smtp.sendmail(sender_email, receiver_email, email.as_string())


# TODO: emails = secret_santa.calc_secret_santa()
# TODO: send_emails(emails)
# * OR
# TODO: secret_santa.send_emails()
# * instead of double call
"""
    EMAIL SENDING

email_msg = EmailMessage()
email_msg["From"] = sender_email
email_msg["To"] = receiver_email

subject = "This is a test email from secret santa"
email_msg["Subject"] = subject

body = "test body"
email_msg.set_content(body)

context = ssl.create_default_context()

# * only Gmail!
# * port = 465  # for SSL

with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
    smtp.login(sender_email, app_password)
    smtp.sendmail(sender_email, receiver_email, email_msg.as_string())
"""
