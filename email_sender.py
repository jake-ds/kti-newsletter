import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os


def send_email(news_dict, user_email):
    msg = MIMEMultipart("alternative")
    msg["From"] = "KTI Portfolio News <sw.joo@kti.vc>"
    msg["To"] = user_email
    msg["Subject"] = "KTI Portfolio Daily News"
    msg.add_header("X-Google-Original-From", "portfolio_news@kti.vc")

    # 이메일 본문 설정
    msg.attach(MIMEText(news_dict, "html"))

    try:
        # 이메일 서버 설정 및 전송
        with smtplib.SMTP(
            os.getenv("SMTP_SERVER", ""), os.getenv("SMTP_PORT", "")
        ) as server:
            server.starttls()
            server.login(
                os.getenv("EMAIL_LOGIN", ""),
                (os.getenv("EMAIL_PASSWORD", "").replace("-", " ")),
            )
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


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
