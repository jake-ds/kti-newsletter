import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

def test_smtp_connection():
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    email_login = os.environ.get('EMAIL_LOGIN')
    email_password = os.environ.get('EMAIL_PASSWORD')
    
    print(f"Testing SMTP connection to {smtp_server}:{smtp_port}")
    print(f"Using email: {email_login}")
    print(f"Using password: {email_password}")
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("1. Server connected")
            server.starttls()
            print("2. STARTTLS successful")
            server.login(email_login, email_password)
            print("3. Login successful")
            
            # 테스트 이메일 전송
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'SMTP Test Email'
            msg['From'] = email_login
            msg['To'] = os.environ.get('RECIPIENTS', email_login)
            
            text = "This is a test email from GitHub Actions"
            part = MIMEText(text, 'plain')
            msg.attach(part)
            
            server.send_message(msg)
            print("4. Test email sent successfully")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e

if __name__ == "__main__":
    test_smtp_connection() 
