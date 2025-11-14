import smtplib
import os
from email.message import EmailMessage
from typing import Optional

class GoogleEmailProvider:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("SMTP_USERNAME", "")
        self.email_password = os.getenv("SMTP_PASSWORD", "")

    def send_otp_email(self, to_email: str, otp_code: str, first_name: Optional[str] = None) -> bool:
        """
        Send OTP code to user's email

        Args:
            to_email: Recipient email address
            otp_code: 4-digit OTP code

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message using EmailMessage (modern approach)
            msg = EmailMessage()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = "[Kheng Leong report automation system] Your One-Time Code for Password Reset"

            # Email body
            body = f"""Hi {first_name if first_name else 'there'},

We received a request to reset your password. To proceed, please use the one-time code below:

Your One-Time Code: {otp_code} (This code will expire in 30 minutes) 

If you didn’t request a password reset, please ignore this email or contact our support team immediately.

Thanks,
The Kheng Leong Team"""

            msg.set_content(body)

            # For development/testing, if email credentials are not configured,
            # just log the OTP instead of actually sending email
            if not self.email_user or not self.email_password:
                print(f"[EMAIL SERVICE] OTP for {to_email}: {otp_code}")
                return True

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()

            return True

        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

# Global email service instance
email_provider = GoogleEmailProvider()
