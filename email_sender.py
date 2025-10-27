import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()


def send_email(content, recipients):
    # SMTP 서버 설정
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    email_login = os.environ.get("EMAIL_LOGIN")
    email_password = os.environ.get("EMAIL_PASSWORD")
    email_password = email_password.replace("-", " ")

    print(f"Attempting to send email to: {recipients}")
    print(f"Using SMTP server: {smtp_server}:{smtp_port}")

    # 수신자가 비어있는 경우 처리
    if not recipients:
        print("Warning: No recipients specified")
        return

    try:
        # 메시지 생성
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "KTI Portfolio Daily News"
        msg["From"] = email_login
        msg["To"] = recipients

        # HTML 형식의 본문 추가
        html_part = MIMEText(content, "html")
        msg.attach(html_part)

        # SMTP 연결 및 전송
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(email_login, email_password)
            server.sendmail(email_login, recipients, msg.as_string())
            print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        print(f"Recipients: {recipients}")
        raise


def format_email_content(news_data, user_name):
    # 베타 테스트 모드 및 임계값 확인
    beta_test_mode = os.environ.get("BETA_TEST_MODE", "false").lower() == "true"
    relevance_threshold = int(os.environ.get("RELEVANCE_THRESHOLD", "6"))

    email_body = "<h1> KTI Portfolio Daily News </h1>"
    email_body += f"<p> 안녕하세요 {user_name}님. KTI 투자포트폴리오사의 뉴스리스트 메일링입니다</p><br><br>"

    # 베타 테스트 모드 안내 추가
    if beta_test_mode:
        email_body += """
        <div style="font-family: Arial, sans-serif; font-size: 14px; color: #856404; background-color: #fff3cd; padding: 15px; border-radius: 5px; border: 1px solid #ffeaa7; margin-bottom: 20px;">
            <strong>⚠️ 베타 테스트 모드</strong><br>
            현재 AI 관련성 필터링 기능을 테스트 중입니다.<br>
            관련성이 낮은 뉴스는 <span style="background-color: #ffcccc; padding: 2px 5px; border-radius: 3px;">[관련성 낮음 - 필터링 예정]</span> 태그가 표시됩니다.<br>
            정식 운영 시 이러한 뉴스는 자동으로 제외됩니다.<br>
            필터링 품질에 대한 피드백을 주시면 감사하겠습니다!
        </div>
        """

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
            # 베타 모드에서는 4개 요소 (title, description, url, score)
            # 일반 모드에서는 3개 요소 (title, description, url)
            if len(news) == 4:
                title, description, url, score = news
                # 관련성 점수가 임계값 미만이면 경고 태그 추가
                if score < relevance_threshold:
                    title_with_tag = f'<span style="background-color: #ffcccc; padding: 2px 8px; border-radius: 3px; font-size: 12px; font-weight: bold;">[관련성 낮음 - 필터링 예정 (점수: {score}/10)]</span> {title}'
                    email_body += f"<h3>{title_with_tag}</h3>"
                else:
                    # 관련성 높은 뉴스에는 점수 표시 (선택사항)
                    title_with_score = f'<span style="background-color: #d4edda; padding: 2px 8px; border-radius: 3px; font-size: 12px; font-weight: bold;">[관련성: {score}/10]</span> {title}'
                    email_body += f"<h3>{title_with_score}</h3>"
            else:
                # 일반 모드 (3개 요소)
                title, description, url = news
                email_body += f"<h3>{title}</h3>"

            email_body += f"<p>{description}</p>"
            email_body += f'<a href="{url}">Link</a><br>'
            email_body += "<hr>"  # 뉴스 항목 구분선

        email_body += "<br>"  # 각 회사의 뉴스 섹션을 구분하기 위한 줄바꿈

    return email_body
