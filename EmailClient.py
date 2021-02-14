import config
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(arr):
    port = 465  # for ssl
    email_password = config.gmail_pass  # stored in cofig.py
    my_email_addr = config.gmail_user
    mail_to = config.receiver_email

    message = MIMEMultipart("alternative")
    message["Subject"] = config.questionable_subject
    message["From"] = my_email_addr
    message["To"] = mail_to[0]

    master_text = ""
    for x in arr:
        y = str(x)
        z = f"<p> {y} </p><br />"
        master_text += z

    html = config.html
    html2 = html + master_text

    # create plain/html MIMEText objects
    plain = MIMEText(master_text, "plain")
    real = MIMEText(html2, "html")

    # Add plain/real parts to mime multipart message
    message.attach(plain)
    message.attach(real)

    # Create a secure SSL connection
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(my_email_addr, email_password)
        for emails in mail_to:
            server.sendmail(my_email_addr, emails, message.as_string())
