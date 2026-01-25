# KTI Portfolio News Bot

매주 월-금요일 아침 7시(KST)에 자동으로 포트폴리오 회사 관련 뉴스를 수집하고, AI로 관련성을 필터링하여 이메일로 전송하는 봇입니다.

## 주요 기능

### 3단계 하이브리드 필터링 파이프라인

1. **키워드 검색**: Naver 뉴스에서 회사명/키워드로 뉴스 검색
2. **중복 제거**: OpenAI Embedding으로 유사한 기사 자동 제거 (코사인 유사도 0.85)
3. **AI 관련성 필터링**: GPT-4o-mini로 뉴스와 회사 사업의 관련성 평가 (0-10 점수)

### 특징
- **74개 포트폴리오 회사** 뉴스 자동 수집
- **AI 기반 관련성 평가**로 노이즈 제거
- 담당자별 맞춤 뉴스 전송 (담당 포트폴리오사 뉴스가 상단에 배치)
- GitHub Actions 기반 자동 실행

## 환경 설정

1. `.env.example`을 `.env`로 복사하고 실제 값으로 수정:

   ```bash
   cp .env.example .env
   ```

2. 필요한 환경변수 설정:

   **기본 설정:**
   - `SMTP_SERVER`: 이메일 서버 (예: smtp.gmail.com)
   - `SMTP_PORT`: SMTP 포트 (예: 587)
   - `EMAIL_LOGIN`: 이메일 주소
   - `EMAIL_PASSWORD`: 이메일 앱 비밀번호 (일반 비밀번호가 아닌 앱 비밀번호 사용)
   - `OPENAI_API_KEY`: OpenAI API 키
   - `TEST_EMAIL`: (선택) 테스트 모드일 때 사용할 이메일 주소. 설정 시 모든 이메일이 이 주소로 발송됨

   **AI 관련성 필터링 설정:**
   - `ENABLE_RELEVANCE_FILTER`: AI 필터링 활성화 여부 (기본값: `true`)
     - `true`: GPT-4o-mini로 뉴스 관련성 평가 후 필터링
     - `false`: 키워드 매칭과 중복 제거만 수행
   - `RELEVANCE_THRESHOLD`: 관련성 점수 임계값 0-10 (기본값: `6`)
     - `10`: 회사 핵심 사업 직접 관련 뉴스만
     - `7-9`: 사업 분야 밀접 관련 뉴스
     - `6`: 산업/시장 간접 관련 뉴스 포함 (권장)
     - `4-5`: 넓은 범위 뉴스 포함
     - `0-3`: 거의 모든 뉴스 포함
   - `BETA_TEST_MODE`: 베타 테스트 모드 (기본값: `false`)
     - `true`: 필터링될 뉴스도 이메일에 포함하되 `[관련성 낮음 - 필터링 예정]` 태그 표시
       - 필터링 품질 확인 및 피드백 수집 가능
       - 모든 뉴스에 관련성 점수 표시
     - `false`: 임계값 미만 뉴스는 완전히 제외 (정식 운영 모드)

3. Gmail 앱 비밀번호 생성 방법:
   - Google 계정 설정 → 보안
   - 2단계 인증 활성화
   - 앱 비밀번호 생성
   - 생성된 16자리 앱 비밀번호를 `EMAIL_PASSWORD`에 설정

## GitHub Actions 설정

1. GitHub Repository의 Settings → Secrets and variables → Actions에서 다음 secrets 추가:

   **필수 환경 변수:**
   - `SMTP_SERVER`
   - `SMTP_PORT`
   - `EMAIL_LOGIN`
   - `EMAIL_PASSWORD` (앱 비밀번호 사용)
   - `OPENAI_API_KEY`

   **선택 환경 변수:**
   - `ENABLE_RELEVANCE_FILTER` (기본값: true)
   - `RELEVANCE_THRESHOLD` (기본값: 6)
   - `BETA_TEST_MODE` (기본값: false)
     - 베타 테스트 기간 동안 `true`로 설정하여 필터링 품질 확인
     - 정식 운영 시 `false`로 변경
   - `TEST_EMAIL`: 테스트용 이메일 주소 (설정 시 모든 이메일이 이 주소로 발송)

## 주의사항

- 절대로 `.env` 파일을 Git에 커밋하지 마세요
- 항상 앱 비밀번호를 사용하세요 (일반 비밀번호 사용 금지)
- 민감한 정보는 반드시 GitHub Secrets를 통해 관리하세요

## 설정 방법

1. GitHub Repository 생성 후 코드를 push합니다.

2. GitHub Actions 자동 실행
   - 매주 월-금요일 아침 7시(KST)에 자동으로 실행됩니다 (UTC 22:00, 전날)
   - Actions 탭에서 수동으로도 실행 가능합니다
   - `daily-news.yml`: 정식 실행 워크플로우
   - `test-news.yml`: 테스트용 워크플로우 (수동 실행만 가능)

## 데이터 파일 구조

프로젝트는 다음 JSON 파일들을 사용합니다:

- **`company_info.json`**: 포트폴리오 회사 정보
  - 각 회사별로 `keyword`, `comment`, `manager` 필드를 포함
  - `manager`는 배열 형태로 여러 담당자 지원
  - 예시:
    ```json
    {
      "회사명": {
        "keyword": ["키워드1", "키워드2"],
        "comment": "회사 사업 설명",
        "manager": ["담당자1", "담당자2"]
      }
    }
    ```

- **`user_info.json`**: 이메일 수신자 정보
  - 각 담당자별 이메일 주소 설정
  - `company_info.json`의 `manager` 필드와 매칭됨
  - 예시:
    ```json
    {
      "담당자명": {
        "email": "email@example.com"
      }
    }
    ```

### 데이터 업데이트

`portfolio_news_data.csv` 파일을 업데이트한 후 다음 명령어로 JSON 파일을 재생성:

```bash
python update_raw_data.py
```

이 스크립트는 CSV 파일을 읽어서 `company_info.json`을 생성합니다.

## 로컬 개발 환경 설정

1. 필요한 패키지 설치:

   ```bash
   pip install -r requirements.txt
   ```

2. 환경 변수 설정:

   - `.env` 파일을 생성하고 다음 내용을 추가:

   ```
   OPENAI_API_KEY=your-api-key
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   EMAIL_LOGIN=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   ```

3. 실행:
   ```bash
   python main.py
   ```

## 테스트

### 로컬 테스트

테스트 모드로 실행하려면:

```bash
python test.py
```

테스트 모드는 소수의 회사만 테스트하고 지정된 이메일(`sw.joo@kti.vc`)로만 발송합니다.

### GitHub Actions 테스트

GitHub Actions에서 테스트 워크플로우를 수동으로 실행할 수 있습니다:
- Actions 탭 → "Test News Bot (Beta)" 워크플로우 선택 → "Run workflow" 클릭
- 테스트 워크플로우는 5개 회사만 처리하고 베타 테스트 모드로 실행됩니다

## 파일 구조

```
news_bot/
├── main.py                    # 메인 실행 스크립트
├── test.py                    # 테스트 스크립트
├── update_raw_data.py         # CSV에서 JSON 생성 스크립트
├── data_loader.py             # JSON 파일 로더
├── fetch_news.py              # 뉴스 수집 모듈
├── filter_similar_news.py     # 중복 제거 및 관련성 필터링
├── email_sender.py            # 이메일 발송 모듈
├── company_info.json          # 회사 정보 (키워드, 설명, 담당자)
├── user_info.json             # 사용자 이메일 정보
├── portfolio_news_data.csv    # 원본 데이터 (CSV)
├── requirements.txt           # Python 패키지 의존성
└── README.md                  # 프로젝트 문서
```

# kti-newsletter
