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

## 프로젝트 시작하기 (Fork 및 초기 설정)

> **참고**: 이 프로젝트는 GitHub Actions에서만 실행되며, 로컬 환경 설정은 필요하지 않습니다.

### 1. Repository Fork

1. 원본 Repository 페이지로 이동
2. 우측 상단의 **Fork** 버튼 클릭
3. Fork할 계정/조직 선택
4. Repository 이름 확인 후 **Create fork** 클릭

### 2. 데이터 파일 확인

Fork한 Repository에 다음 파일들이 포함되어 있는지 확인:
- `company_info.json`: 회사 정보 (키워드, 설명, 담당자)
- `user_info.json`: 이메일 수신자 정보

**데이터 파일이 없다면:**
- 원본 Repository에서 해당 파일들을 확인하고 필요시 추가

### 3. GitHub Actions 설정

Fork한 Repository에서 GitHub Secrets 설정:

1. **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 클릭
3. 필수 Secrets 추가:
   - `OPENAI_API_KEY`
   - `SMTP_SERVER`
   - `SMTP_PORT`
   - `EMAIL_LOGIN`
   - `EMAIL_PASSWORD`

자세한 설정 방법은 아래 [GitHub Actions 설정](#github-actions-설정) 섹션 참고

### 4. 워크플로우 확인 및 테스트

1. **Actions** 탭으로 이동
2. 워크플로우가 정상적으로 보이는지 확인:
   - `Daily News Bot`: 정식 실행 워크플로우
   - `Test News Bot (Beta)`: 테스트용 워크플로우
3. **Test News Bot (Beta)** 워크플로우를 수동 실행하여 테스트
   - "Run workflow" 버튼 클릭
   - 브랜치 선택 (기본: main)
   - "Run workflow" 실행
4. 실행 결과 확인:
   - 로그에서 에러가 없는지 확인
   - 테스트 이메일이 정상적으로 발송되었는지 확인

### 5. 스케줄 확인 및 수정 (선택)

`daily-news.yml` 파일의 cron 스케줄 확인:
```yaml
schedule:
  - cron: "0 22 * * 0-4" # UTC 22:00 = KST 07:00 (월-금)
```

#### Cron 표현식 설명

Cron 표현식은 5개의 필드로 구성되며, 각 자리는 다음을 의미합니다:

```
분 시 일 월 요일
│  │  │  │  │
│  │  │  │  └─ 요일 (0-7, 0과 7은 일요일)
│  │  │  └───── 월 (1-12)
│  │  └───────── 일 (1-31)
│  └───────────── 시 (0-23, UTC 기준)
└───────────────── 분 (0-59)
```

**현재 설정 `"0 22 * * 0-4"`의 의미:**
- `0`: 0분 (정각)
- `22`: 22시 (UTC 기준)
- `*`: 매일
- `*`: 매월
- `0-4`: 일요일(0)부터 목요일(4)까지
- **결과**: 매주 일요일~목요일 UTC 22:00 (한국시간 월~금 07:00)

**특수 문자:**
- `*`: 모든 값
- `,`: 값 목록 (예: `1,3,5`)
- `-`: 범위 (예: `1-5`)
- `/`: 증분 (예: `*/2`는 2마다)

필요시 스케줄을 수정할 수 있습니다:
1. `.github/workflows/daily-news.yml` 파일 편집
2. cron 표현식 수정
3. 변경사항 커밋 및 푸시

## 환경 변수 설명

GitHub Actions에서 사용하는 환경 변수들:

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

### GitHub Secrets 설정 방법

1. GitHub Repository 페이지로 이동
2. **Settings** 탭 클릭
3. 왼쪽 메뉴에서 **Secrets and variables** → **Actions** 클릭
4. **New repository secret** 버튼 클릭
5. 아래 환경 변수들을 하나씩 추가:

   **필수 환경 변수 (반드시 설정 필요):**
   - `SMTP_SERVER`: 이메일 서버 주소 (예: `smtp.gmail.com`)
   - `SMTP_PORT`: SMTP 포트 (예: `587`)
   - `EMAIL_LOGIN`: 발신 이메일 주소
   - `EMAIL_PASSWORD`: 이메일 앱 비밀번호 (Gmail의 경우 16자리 앱 비밀번호)
   - `OPENAI_API_KEY`: OpenAI API 키 (예: `sk-...`)

   **선택 환경 변수 (설정하지 않으면 기본값 사용):**
   - `ENABLE_RELEVANCE_FILTER`: AI 필터링 활성화 여부
     - 설정하지 않으면 기본값 `true` 사용
     - `true`: AI 관련성 필터링 활성화
     - `false`: AI 필터링 비활성화 (키워드 매칭만 수행)
   
   - `RELEVANCE_THRESHOLD`: 관련성 점수 임계값
     - 설정하지 않으면 기본값 `6` 사용
     - `0-10` 사이의 숫자 (권장: `6`)
   
   - `BETA_TEST_MODE`: 베타 테스트 모드
     - 설정하지 않으면 기본값 `false` 사용
     - `true`: 필터링될 뉴스도 포함하되 경고 태그 표시
     - `false`: 임계값 미만 뉴스는 완전히 제외
   
   - `TEST_EMAIL`: 테스트용 이메일 주소
     - 설정 시 모든 이메일이 이 주소로만 발송됨
     - 실제 운영 시에는 설정하지 않음

### 환경 변수 설정 예시

**최소 설정 (필수만):**
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_LOGIN=your-email@gmail.com
EMAIL_PASSWORD=your-16-digit-app-password
OPENAI_API_KEY=sk-...
```

**추가 설정 (AI 필터링 커스터마이징):**
```
ENABLE_RELEVANCE_FILTER=true
RELEVANCE_THRESHOLD=6
BETA_TEST_MODE=false
```

**테스트 모드:**
```
TEST_EMAIL=test@example.com
BETA_TEST_MODE=true
```

## 주의사항

- 절대로 `.env` 파일을 Git에 커밋하지 마세요
- 항상 앱 비밀번호를 사용하세요 (일반 비밀번호 사용 금지)
- 민감한 정보는 반드시 GitHub Secrets를 통해 관리하세요

## 워크플로우 실행 방법

### 자동 실행 (스케줄)
- **실행 시간**: 매주 월-금요일 아침 7시(KST) (UTC 22:00, 전날)
- **워크플로우**: `daily-news.yml`
- GitHub Actions가 자동으로 실행합니다

### 수동 실행
1. GitHub Repository → **Actions** 탭
2. 실행할 워크플로우 선택:
   - `Daily News Bot`: 전체 회사 뉴스 수집 및 발송
   - `Test News Bot (Beta)`: 테스트 모드 (5개 회사만)
3. **Run workflow** 버튼 클릭
4. 브랜치 선택 후 **Run workflow** 실행

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

## 테스트

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

## 인수인계 체크리스트

새로운 담당자가 프로젝트를 인수받을 때 확인해야 할 사항:

### ✅ 필수 확인 사항

- [ ] Repository Fork 완료
- [ ] GitHub Secrets 설정 완료 (5개 필수 Secrets)
  - [ ] `OPENAI_API_KEY`
  - [ ] `SMTP_SERVER`
  - [ ] `SMTP_PORT`
  - [ ] `EMAIL_LOGIN`
  - [ ] `EMAIL_PASSWORD`
- [ ] `company_info.json` 파일 확인 (회사 정보)
- [ ] `user_info.json` 파일 확인 (이메일 수신자 정보)
- [ ] GitHub Actions 테스트 워크플로우 수동 실행 성공
- [ ] 테스트 이메일 정상 수신 확인

### 📋 계정 및 API 키 확인

- [ ] OpenAI API 키 발급 및 설정
- [ ] Gmail 앱 비밀번호 생성 및 설정
- [ ] SMTP 서버 정보 확인 (Gmail 사용 시: `smtp.gmail.com:587`)

### 🔧 설정 확인

- [ ] GitHub Actions 워크플로우 스케줄 확인 (`daily-news.yml`)
- [ ] 실행 시간 확인 (월-금 7시 KST)
- [ ] AI 필터링 설정 확인 (`ENABLE_RELEVANCE_FILTER`, `RELEVANCE_THRESHOLD`)
- [ ] 베타 테스트 모드 설정 확인 (`BETA_TEST_MODE`)

### 📧 이메일 발송 확인

- [ ] 테스트 이메일 발송 성공 확인
- [ ] 수신자 이메일 주소 확인 (`user_info.json`)
- [ ] 이메일 형식 및 내용 확인

### 🔄 데이터 업데이트 방법

- [ ] `portfolio_news_data.csv` 파일 위치 확인
- [ ] 회사 정보 추가/수정 프로세스 이해
- [ ] `company_info.json` 직접 수정 방법 숙지
- [ ] `user_info.json` 직접 수정 방법 숙지
- [ ] 변경사항 커밋 및 푸시 방법 숙지

### 🐛 문제 발생 시

- [ ] GitHub Actions 로그 확인 방법 숙지
  - Actions 탭 → 실패한 워크플로우 클릭 → 로그 확인
- [ ] OpenAI API 사용량 및 비용 확인 방법 숙지
  - OpenAI 대시보드에서 API 사용량 확인
- [ ] 이메일 발송 실패 시 확인 사항
  - SMTP 설정 확인
  - 앱 비밀번호 확인
  - 수신자 이메일 주소 확인

### 📚 추가 문서

- [ ] README.md 전체 내용 숙지
- [ ] 워크플로우 파일 이해 (`.github/workflows/`)
  - `daily-news.yml`: 정식 실행 워크플로우
  - `test-news.yml`: 테스트 워크플로우

# kti-newsletter
