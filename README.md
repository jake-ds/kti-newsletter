# News Bot

매일 아침 8시에 자동으로 뉴스를 수집하고 필터링하여 이메일로 전송하는 봇입니다.

## 환경 설정

1. `.env.example`을 `.env`로 복사하고 실제 값으로 수정:

   ```bash
   cp .env.example .env
   ```

2. 필요한 환경변수 설정:

   - `SMTP_SERVER`: 이메일 서버 (예: smtp.gmail.com)
   - `SMTP_PORT`: SMTP 포트 (예: 587)
   - `EMAIL_LOGIN`: 이메일 주소
   - `EMAIL_PASSWORD`: 이메일 앱 비밀번호 (일반 비밀번호가 아닌 앱 비밀번호 사용)
   - `OPENAI_API_KEY`: OpenAI API 키
   - `RECIPIENTS`: 테스트용 수신자 이메일

3. Gmail 앱 비밀번호 생성 방법:
   - Google 계정 설정 → 보안
   - 2단계 인증 활성화
   - 앱 비밀번호 생성
   - 생성된 16자리 앱 비밀번호를 `EMAIL_PASSWORD`에 설정

## GitHub Actions 설정

1. GitHub Repository의 Settings → Secrets and variables → Actions에서 다음 secrets 추가:
   - `SMTP_SERVER`
   - `SMTP_PORT`
   - `EMAIL_LOGIN`
   - `EMAIL_PASSWORD` (앱 비밀번호 사용)
   - `OPENAI_API_KEY`
   - `RECIPIENTS`

## 주의사항

- 절대로 `.env` 파일을 Git에 커밋하지 마세요
- 항상 앱 비밀번호를 사용하세요 (일반 비밀번호 사용 금지)
- 민감한 정보는 반드시 GitHub Secrets를 통해 관리하세요

## 설정 방법

1. GitHub Repository 생성 후 코드를 push합니다.

2. GitHub Actions 자동 실행
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
