""" Мы устроились на новую работу. Бывший сотрудник начал разрабатывать модуль для работы с почтой,
но не успел доделать его. Код рабочий. Нужно только провести рефакторинг кода.

1. Создать класс для работы с почтой;
2. Создать методы для отправки и получения писем;
3. Убрать "захардкоженный" код. Все значения должны определяться как аттрибуты класса, либо аргументы методов;
4. Переменные должны быть названы по стандарту PEP8;
5. Весь остальной код должен соответствовать стандарту PEP8;
6. Класс должен инициализироваться в конструкции if __name__ == '__main__'. """

import email
import imaplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from getpass import getpass

class Email:
    GMAIL_SMTP = "smtp.gmail.com"
    GMAIL_IMAP = "imap.gmail.com"

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def send_message(self):
        """ Метод отправляет письма"""
        subject = input('Enter subject: '),
        message_text = input('Enter message: ')
        if message_text:
            if not subject:
                print('not subject')
                subject = ''
            recipients = []
            if not recipients:
                recipient = input('Enter recipient: ')
                while recipient != '':
                    recipients.append(recipient)
                    recipient = input('Enter recipient: ')
                else:
                    if not recipients:
                        return "No recipients. Message can't be sent."
            print(recipients)
            print(*recipients)
            message = MIMEMultipart()
            message['From'] = self.username
            message['To'] = ', '.join(recipients)
            print(message['To'])
            message['Subject'] = subject
            message.attach(MIMEText(message_text))
            mail_server = smtplib.SMTP(self.GMAIL_SMTP, port=25)

            mail_server.ehlo()  # identify ourselves to smtp gmail client
            mail_server.starttls()  # secure our email with tls encryption
            mail_server.ehlo()  # re-identify ourselves as an encrypted connection

            mail_server.login(self.username, self.password)
            mail_server.sendmail(self.username, message['To'], message.as_string())

            mail_server.quit()
            return "Message was sent"
        return "No message to send"

    def recieve(self):
        """ Метод получает письма в inbox"""
        mail_box = imaplib.IMAP4_SSL(self.GMAIL_IMAP)
        mail_box.login(self.username, self.password)
        mail_box.select("inbox")
        header = input('Enter header: ')
        if header:
            criterion = f'(HEADER Subject {header})'
        else:
            criterion = 'ALL'
        result, data = mail_box.uid('search', criterion)
        assert data[0], 'There are no letters with current header'
        latest_email_uid = data[0].split()[-1]
        result, data = mail_box.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = str(data[0][1])
        # print(raw_email)
        email_message = email.message_from_string(raw_email)
        print(email_message)
        mail_box.logout()


if __name__ == '__main__':
    username = input('Input your Google username ')
    if "@gmail.com" not in username:
        username = username + '@gmail.com'
    print(username)

    password = getpass("Input password: ")

    mail_box = Email(username, password)
    print(mail_box.send_message())
    mail_box.recieve()
