import json
import os
import smtplib

from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import formatdate
from typing import List

from django.utils import timezone

from core.mails.contact_mail import ContactMail
from core.models.contact.contact_model import Contact
from core.models.mail.mail_model import Mail


class MailerService:

    def __init__(self, debug=False):
        self.debug = debug
        self.enabled = int(os.environ['EMAIL_SMTP_ENABLED']) == 1
        self.host = os.environ['EMAIL_SMTP_HOST']
        self.port = os.environ['EMAIL_SMTP_PORT']
        self.user = os.environ['EMAIL_SMTP_USER']
        self.password = os.environ['EMAIL_SMTP_PASS']
        self.sender_name = os.environ['EMAIL_SMTP_SENDER_NAME']

    def get_smtp_server(self):
        server = smtplib.SMTP(host=self.host, port=self.port)

        if self.debug:
            server.set_debuglevel(1)

        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(self.user, self.password)

        return server

    def send_message(
            self,
            to: List,
            subject: str,
            message_html: str,
            message_text: str,
            reply_to: str = None
    ):
        if not self.enabled:
            return

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = Address(self.sender_name, addr_spec=self.user)
        msg['To'] = ', '.join(to)
        msg.add_header('Date', formatdate(localtime=True))

        msg.set_content(message_text)
        msg.add_alternative(message_html, subtype="html")

        if reply_to:
            msg.add_header('reply-to', reply_to)

        with self.get_smtp_server() as server:
            return server.send_message(
                msg,
                from_addr=self.user,
                to_addrs=to
            )

    def send_from_contact(self, contact: Contact):
        mail = Mail()
        mail.to = os.environ['EMAIL_ADDRESS_CONTACT']
        mail.subject = "Contato via website"

        mail_template = ContactMail(contact)
        mail.message_html = mail_template.parse_html()
        mail.message_text = mail_template.parse_raw()

        mail.reply_to = contact.email
        mail.save()

        self.send_from_mail(mail)

    def send_from_mail(self, mail: Mail):
        if mail.sent or not self.enabled:
            return

        mailer = MailerService()
        send_result = mailer.send_message(
            to=str(mail.to).split(';'),
            subject=str(mail.subject),
            message_html=str(mail.message_html),
            message_text=str(mail.message_text),
            reply_to=str(mail.reply_to)
        )

        mail.sent = True
        mail.sent_at = timezone.now()
        mail.server_response = json.dumps(send_result)

        mail.save()
