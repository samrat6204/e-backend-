"""
Saauzi — Custom Email Backend
==============================
Problem:
  On Windows, Python cannot verify Gmail's SSL certificate chain.
  The default Django SMTP backend raises:
    ssl.SSLCertVerificationError: CERTIFICATE_VERIFY_FAILED

Solution:
  This custom backend extends Django's built-in SMTP backend and overrides
  the open() method to inject a custom SSL context that skips certificate
  verification (ssl.CERT_NONE).

Usage:
  Set in settings.py:
    EMAIL_BACKEND = 'app1.email_backend.NoVerifyEmailBackend'

  After that, every email.send() call anywhere in the project
  automatically uses this backend — no changes needed in views.

Note:
  CERT_NONE means we trust Gmail's server without verifying the certificate.
  This is acceptable for a development/internship project on Windows.
  In production on Linux/Mac, the default backend works fine without this fix.
"""

import ssl
from django.core.mail.backends.smtp import EmailBackend


class NoVerifyEmailBackend(EmailBackend):
    """
    Drop-in replacement for Django's default SMTP backend.
    The only difference is that STARTTLS uses a custom SSL context
    with certificate verification disabled.
    """

    def open(self):
        """
        Open an SMTP connection to Gmail.

        Steps:
          1. Check if connection already exists (avoid duplicate connections).
          2. Create SSL context with certificate check disabled.
          3. Connect to Gmail SMTP server (port 587).
          4. Say hello (EHLO).
          5. Upgrade connection to encrypted (STARTTLS).
          6. Say hello again after encryption.
          7. Login with Gmail credentials from settings.py.
        """

        # If a connection already exists, do not open a new one.
        if self.connection:
            return False

        # Create SSL context that skips certificate verification.
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False   # Do not check hostname in cert
        ssl_context.verify_mode = ssl.CERT_NONE  # Skip cert verification

        # Connect to Gmail SMTP server on port 587 (plain, then upgrade).
        self.connection = self.connection_class(
            self.host,       # smtp.gmail.com
            self.port,       # 587
            timeout=self.timeout,
        )

        self.connection.ehlo()                        # Introduce ourselves
        self.connection.starttls(context=ssl_context) # Upgrade to encrypted
        self.connection.ehlo()                        # Re-introduce after TLS
        self.connection.login(self.username, self.password)  # Gmail login

        return True
