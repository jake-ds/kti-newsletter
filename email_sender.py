import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(content, recipients):
    # SMTP 서버 설정
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    email_login = os.environ.get('EMAIL_LOGIN')
    email_password = os.environ.get('EMAIL_PASSWORD')

    print("email_login", email_login)
    print("email_password", email_password)

    # 수신자가 비어있는 경우 처리
    if not recipients:
        print("Warning: No recipients specified")
        return

    # 이메일 전송
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()  # SMTP 서버와 연결 시작
            server.starttls()  # TLS 보안 시작
            server.ehlo()  # TLS 후 다시 연결
            server.login(email_login, email_password)  # 로그인
            
            # 각 수신자에게 개별적으로 전송
            for recipient in recipients:
                # 각 수신자별로 새로운 메시지 생성
                msg = MIMEMultipart('alternative')
                msg['Subject'] = 'KTI Portfolio Daily News'
                msg['From'] = email_login
                msg['To'] = recipient
                
                # HTML 형식의 본문 추가
                html_part = MIMEText(content, 'html')
                msg.attach(html_part)
                
                # 메시지를 문자열로 변환
                text = msg.as_string()
                
                # sendmail 메서드 사용
                server.sendmail(email_login, [recipient], text)
                print(f"Email sent successfully to {recipient}")
                
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        print(f"SMTP settings - Server: {smtp_server}, Port: {smtp_port}, Login: {email_login}")
        raise

def format_email_content(news_data, user_name):
    email_body = "<h1> KTI Portfolio Daily News </h1>"
    email_body += f"<p> 안녕하세요 {user_name}님. KTI 투자포트폴리오사의 뉴스리스트 메일링입니다</p><br><br>"
    email_body += """
    <div style="font-family: Arial, sans-serif; font-size: 14px; color: #555;">
        <p style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; border: 1px solid #ddd;">
            <strong>업데이트 소식:</strong><br>
            수신자별로 담당 포트폴리오사의 뉴스가 상단에 배치됩니다. <br>
            각 회사별 검색 키워드도 함께 제공됩니다. <br>
            ** 키워드 추가/변경/삭제를 원하실 경우 언제든 말씀해주세요!<br>
            ** 회사별 키워드는 <a href="https://drive.google.com/drive/u/0/folders/1Y_SD1yqjnijE6pY52c1xRp2yxBePHuzq" style="color: #1a73e8; text-decoration: none;">KTI 공용드라이브의 구글시트</a>에서 관리 중입니다. 변경하실 경우 담당자에게 변경사실을 알려주세요
        </p>
    </div>
    <br>
    """
    for company, news_detail in news_data.items():
        keywords = " / ".join(news_detail["keyword"])
        email_body += f"<h2 style='background-color: #FFD700;'>{company}</h2>"
        email_body += f"<p><strong>검색 키워드:</strong> {keywords}</p>"
        email_body += "<hr>"  # 회사 구분선
        for news in news_detail["news_list"]:
            title, description, url = news
            email_body += f"<h3>{title}</h3>"
            email_body += f"<p>{description}</p>"
            email_body += f'<a href="{url}">Link</a><br>'
            email_body += "<hr>"  # 뉴스 항목 구분선
        email_body += "<br>"  # 각 회사의 뉴스 섹션을 구분하기 위한 줄바꿈

    return email_body
