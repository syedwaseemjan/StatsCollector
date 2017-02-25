import logging
import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr

import paramiko
from celery import Celery
from models import Stats

from app import settings

logger = logging.getLogger()
app = Celery("tasks", broker=settings.get("CELERY", "CELERY_BROKER"))


@app.task
def upload_collector(ip, port, user, passwd):
    """This method uses the provided input to ssh the client machine and uploads
    client.sh . sftp.put is used for uploading the file.

    Attributes:
            ip (str): IP address of client machine
            PORT (int): Port to connect on with client machine
            USERNAME (str): Client instance's username
            PASSWORD (str): Client instance's password
    """

    try:
        logger.info("Connecting to client %s:%s ..." % (ip, port))
        client = paramiko.SSHClient()
        # In case the server's key is unknown,
        # we will be adding it automatically to the list of known hosts
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_host_keys(
            os.path.expanduser(os.path.join("~", ".ssh", "known_hosts"))
        )

        client.connect(ip, port=port, username=user, password=passwd)

        logger.info("Transfering files to and from the remote machine")
        sftp = client.open_sftp()
        client_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), settings.get("STATS", "CLIENT_FILE")
            )
        )
        sftp.put(client_file, settings.get("STATS", "CLIENT_REMOTE_PATH"))
        sftp.close()

        logger.info("Starting client on %s:%s" % (ip, port))
        stdin, stdout, stderr = client.exec_command(
            "(cd /tmp; chmod u+x client.sh; ./client.sh)"
        )

        output = stdout.readlines()
        process_response(ip, float(output[0]), float(output[1]), output[2])

        logger.info("Closing ssh connection")
        client.close()

    except Exception as exe:
        logger.exception(exe)
        try:
            client.close()
        except Exception as exe:
            logger.exception(exe)


def process_response(ip, cpu_usage, mem_usage, uptime):
    """process_response is used to  save the response
    to sqlite DB and and send email alerts.

    Attributes:
            ip (str): IP address of client machine
            cpu_usage (int): Percent CPU usage of client machine
            mem_usage (str): Percent MEMORY usage of client machine
    """
    try:

        stats = Stats.update(ip, cpu_usage, mem_usage, uptime)
        Stats.save(stats)
        cpu_alert, mem_alert = check_threshold(stats)

    except Exception as e:
        raise e


@app.task
def send_email(receiver, subject, body):
    """This method sends emails in the background so that
    the running process won't get block.

    Attributes:
            receiver (str): Email address of the person who
            will recieve the email. subject (str): Subject of
            the email. body (int): Text message of the email.
    """
    sender = settings.get("SMTP", "MAIL_USERNAME")
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = formataddr(
        (str(Header(settings.get("SMTP", "MAIL_DEFAULT_SENDER"), "utf-8")), sender)
    )
    try:
        smtpObj = smtplib.SMTP(
            settings.get("SMTP", "MAIL_SERVER"),
            settings.get("SMTP", "MAIL_PORT", integer=True),
        )
        smtpObj.set_debuglevel(1)
        smtpObj.login(
            settings.get("SMTP", "MAIL_USERNAME"), settings.get("SMTP", "MAIL_PASSWORD")
        )
        smtpObj.sendmail(sender, receiver, msg.as_string())
        smtpObj.quit()
        logging.info("Successfully sent email")
    except smtplib.SMTPException as e:
        logging.exception(e)


def get_subject_text(device):
    return "Alert for your instance's {} usage".format(device)


def get_message_text(device, threshold, usage):
    return """Your {} usage has crossed your threshold.
            <h2>{} threshold: {}%</h2>
            <h2>{} current usage: {}%</h2>
            """.format(
        device, device, threshold, device, usage
    )


def check_threshold(stats):
    """Checks if any of the stats we have collected is crossing the
    threshold client has provided.

    Attributes:
            stats (Stats): Client's machine stats. Sqlalchemy model
    """
    cpu_alert = mem_alert = False
    if stats.cpu_usage > stats.cpu_threshold:
        cpu_alert = True
        send_email.delay(
            stats.email,
            get_subject_text("CPU"),
            get_message_text("CPU", stats.cpu_threshold, stats.cpu_usage),
        )

    if stats.mem_usage > stats.mem_threshold:
        mem_alert = True
        send_email.delay(
            stats.email,
            get_subject_text("MEMORY"),
            get_message_text("MEMORY", stats.mem_threshold, stats.mem_usage),
        )
    return cpu_alert, mem_alert
