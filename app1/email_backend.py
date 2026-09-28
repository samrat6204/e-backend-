import ssl
from django.core.mail.backends.smtp import EmailBackend


class NoVerifyEmailBackend(EmailBackend):
    """
    Custom SMTP backend that skips SSL certificate verification.
    Needed on Windows where the system CA store may not include
    the root certificate for Gmail's SMTP server.

    Drop-in replacement for the default SMTP backend — just point
    EMAIL_BACKEND at this class and everything works automatically.
    """

    def open(self):
        if self.connection:
            return False

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self.connection = self.connection_class(
            self.host,
            self.port,
            timeout=self.timeout,
        )
        self.connection.ehlo()
        self.connection.starttls(context=ssl_context)
        self.connection.ehlo()
        self.connection.login(self.username, self.password)

        return True
