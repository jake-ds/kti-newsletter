# News Bot

매일 아침 8시에 자동으로 뉴스를 수집하고 필터링하여 이메일로 전송하는 봇입니다.

## 설정 방법

1. GitHub Repository 생성 후 코드를 push합니다.

2. GitHub Secrets 설정

   - Repository의 Settings > Secrets and variables > Actions 메뉴로 이동
   - 다음 secrets를 추가:
     - `OPENAI_API_KEY`: OpenAI API 키
     - `RECIPIENTS`: 이메일 수신자 주소

3. GitHub Actions 자동 실행
   - 매일 아침 8시(KST)에 자동으로 실행됩니다
   - Actions 탭에서 수동으로도 실행 가능합니다

## 로컬 개발 환경 설정

1. 필요한 패키지 설치:

   ```bash
   pip install -r requirements.txt
   ```

2. 환경 변수 설정:

   - `.env` 파일을 생성하고 다음 내용을 추가:

   ```
   OPENAI_API_KEY=your-api-key
   RECIPIENTS=your-email@example.com
   ```

3. 실행:
   ```bash
   python main.py
   ```
# kti-newsletter
