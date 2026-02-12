# KTI Portfolio News Bot

매주 월-금요일 아침 7시(KST)에 자동으로 포트폴리오 회사 관련 뉴스를 수집하고, AI로 관련성을 필터링하여 이메일로 전송하는 봇입니다.

## 주요 기능

### 3단계 하이브리드 필터링 파이프라인

1. **키워드 검색**: Naver 뉴스에서 회사명/키워드로 뉴스 검색
2. **중복 제거**: Gemini Embedding으로 유사한 기사 자동 제거 (코사인 유사도 0.85)
3. **AI 관련성 필터링**: Gemini로 뉴스와 회사 사업의 관련성 평가 (0-10 점수)

### 특징

- **74개 포트폴리오 회사** 뉴스 자동 수집
- **AI 기반 관련성 평가**로 노이즈 제거
- 담당자별 맞춤 뉴스 전송 (담당 포트폴리오사 뉴스가 상단에 배치)
- GitHub Actions 기반 자동 실행

## 프로젝트 시작하기

> **참고**: 이 프로젝트는 GitHub Actions에서만 실행되며, 로컬 환경 설정은 필요하지 않습니다.

### 1. Repository Fork

1. 원본 Repository 페이지로 이동
2. 우측 상단의 **Fork** 버튼 클릭
3. Fork할 계정/조직 선택
4. Repository 이름 확인 후 **Create fork** 클릭

### 2. 데이터 파일 확인

Fork한 Repository에 다음 파일들이 포함되어 있는지 확인:
- `portfolio_news_data.csv`: 회사 정보의 단일 소스 (기업명, 회사소개, 담당자, 키워드)
- `user_info.json`: 이메일 수신자 정보

### 3. GitHub Secrets 설정

1. **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 버튼 클릭
3. 아래 환경 변수들을 하나씩 추가:

#### 필수 환경 변수

- `GEMINI_API_KEY`: Google Gemini API 키
- `SMTP_SERVER`: 이메일 서버 주소 (예: `smtp.gmail.com`)
- `SMTP_PORT`: SMTP 포트 (예: `587`)
- `EMAIL_LOGIN`: 발신 이메일 주소
- `EMAIL_PASSWORD`: 이메일 앱 비밀번호 (Gmail의 경우 16자리 앱 비밀번호)

**Gmail 앱 비밀번호 생성 방법:**
- Google 계정 설정 → 보안
- 2단계 인증 활성화
- 앱 비밀번호 생성
- 생성된 16자리 앱 비밀번호를 `EMAIL_PASSWORD`에 설정

#### AI 관련성 필터 설정 (파일)

- **`filter_config.json`** (프로젝트 루트): .env가 아닌 별도 파일로 관리
  - `enable_relevance_filter`: **Gemini 2.5-flash 관련성 필터** 켜기/끄기 (`true` / `false`)
  - `relevance_threshold`: 관련성 점수 임계값 `0-10` (권장 `6`)
  - `beta_test_mode`: 베타 테스트 모드 (`true`면 필터링될 뉴스도 `[관련성 낮음 - 필터링 예정]` 태그로 포함)

필요 시 환경 변수 `ENABLE_RELEVANCE_FILTER`, `RELEVANCE_THRESHOLD`, `BETA_TEST_MODE`로 위 값을 덮어쓸 수 있습니다.

#### 선택 환경 변수 (기본값 사용 가능)

- `TEST_EMAIL`: 테스트용 이메일 주소
  - 설정 시 모든 이메일이 이 주소로만 발송됨
  - 실제 운영 시에는 설정하지 않음

### 4. 워크플로우 테스트

1. **Actions** 탭으로 이동
2. **Test News Bot (Beta)** 워크플로우 선택
3. **Run workflow** 버튼 클릭 → 브랜치 선택 (기본: main) → 실행
4. 실행 결과 확인:
   - 로그에서 에러가 없는지 확인
   - 테스트 이메일이 정상적으로 발송되었는지 확인

## 워크플로우 실행

### 자동 실행 (스케줄)

- **실행 시간**: 매주 월-금요일 아침 7시(KST) (UTC 22:00, 전날)
- **워크플로우**: `daily-news.yml`
- GitHub Actions가 자동으로 실행합니다

### 수동 실행

1. GitHub Repository → **Actions** 탭
2. 실행할 워크플로우 선택:
   - `Daily News Bot`: 전체 회사 뉴스 수집 및 발송
   - `Test News Bot (Beta)`: 테스트 모드 (5개 회사만)
3. **Run workflow** 버튼 클릭 → 브랜치 선택 → 실행

### 스케줄 수정

`daily-news.yml` 파일의 cron 스케줄을 수정할 수 있습니다:

```yaml
schedule:
  - cron: "0 22 * * 0-4" # UTC 22:00 = KST 07:00 (월-금)
```

#### Cron 표현식 설명

Cron 표현식은 5개의 필드로 구성됩니다:

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

**요일 번호:**
- `0` 또는 `7`: 일요일
- `1`: 월요일
- `2`: 화요일
- `3`: 수요일
- `4`: 목요일
- `5`: 금요일
- `6`: 토요일

**특수 문자:**
- `*`: 모든 값
- `,`: 값 목록 (예: `1,3,5`)
- `-`: 범위 (예: `1-5`)
- `/`: 증분 (예: `*/2`는 2마다)

## 데이터 파일 구조

### 파일 설명

- **`portfolio_news_data.csv`**: 포트폴리오 회사 정보의 단일 소스 (프로젝트 **최상위**에 위치)
  - 컬럼: 기업명, 회사소개, 담당자, 키워드
  - 담당자 여러 명: `/`로 구분 (예: `김진수/최우석`)
  - 키워드 여러 개: ` / `로 구분 (예: `스토어링크/퍼그샵`)
  - 런타임에 이 CSV를 읽어 회사 정보 객체를 생성해 사용합니다. 별도 JSON 파일은 사용하지 않습니다.

- **`user_info.json`**: 이메일 수신자 정보
  - 각 담당자별 이메일 주소 설정
  - CSV의 담당자명과 매칭됨
  - 예시:
    ```json
    {
      "담당자명": {
        "email": "email@example.com"
      }
    }
    ```

### 데이터 업데이트

회사 추가/수정 시 **`portfolio_news_data.csv`**를 직접 편집한 뒤 저장하면 됩니다. JSON 파일 생성은 필요 없습니다.

## 파일 구조

```
news_bot/
├── main.py                    # 메인 실행 스크립트
├── test.py                    # 테스트 실행 스크립트
├── portfolio_news_data.csv    # 회사 정보 단일 소스 (최상위, 기업명/회사소개/담당자/키워드)
├── user_info.json             # 사용자 이메일 정보
├── filter_config.json         # AI 관련성 필터 설정 (enable_relevance_filter, relevance_threshold, beta_test_mode)
├── requirements.txt           # Python 패키지 의존성
├── utils/                     # 공통 모듈
│   ├── data_loader.py         # JSON/CSV 로더 (회사 정보는 CSV에서 로드)
│   ├── email_sender.py        # 이메일 발송
│   ├── fetch_news.py          # 뉴스 수집
│   ├── filter_similar_news.py # 중복 제거 및 AI 관련성 필터링
│   └── csv_from_company_info.py  # JSON→CSV 일회성 변환 (필요 시)
└── README.md                  # 프로젝트 문서
```

- **회사 정보 CSV**는 프로젝트 **최상위**에 있는 `portfolio_news_data.csv` 한 파일만 사용합니다.

## 주의사항

- 절대로 `.env` 파일을 Git에 커밋하지 마세요
- 항상 앱 비밀번호를 사용하세요 (일반 비밀번호 사용 금지)
- 민감한 정보는 반드시 GitHub Secrets를 통해 관리하세요

## 인수인계 체크리스트

새로운 담당자가 프로젝트를 인수받을 때 확인해야 할 사항:

### ✅ 필수 확인 사항

- [ ] Repository Fork 완료
- [ ] GitHub Secrets 설정 완료 (5개 필수 Secrets)
  - [ ] `GEMINI_API_KEY`
  - [ ] `SMTP_SERVER`
  - [ ] `SMTP_PORT`
  - [ ] `EMAIL_LOGIN`
  - [ ] `EMAIL_PASSWORD`
- [ ] `portfolio_news_data.csv` 파일 확인 (회사 정보)
- [ ] `user_info.json` 파일 확인 (이메일 수신자 정보)
- [ ] GitHub Actions 테스트 워크플로우 수동 실행 성공
- [ ] 테스트 이메일 정상 수신 확인

### 📋 계정 및 API 키 확인

- [ ] Gemini API 키 발급 및 설정
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
- [ ] 회사 정보 추가/수정 프로세스 이해 (CSV 직접 편집)
- [ ] `user_info.json` 직접 수정 방법 숙지
- [ ] 변경사항 커밋 및 푸시 방법 숙지

### 🐛 문제 발생 시

- [ ] GitHub Actions 로그 확인 방법 숙지
  - Actions 탭 → 실패한 워크플로우 클릭 → 로그 확인
- [ ] Gemini API 사용량 및 비용 확인 방법 숙지
  - Google AI Studio에서 API 사용량 확인
- [ ] 이메일 발송 실패 시 확인 사항
  - SMTP 설정 확인
  - 앱 비밀번호 확인
  - 수신자 이메일 주소 확인

### 📚 추가 문서

- [ ] README.md 전체 내용 숙지
- [ ] 워크플로우 파일 이해 (`.github/workflows/`)
  - `daily-news.yml`: 정식 실행 워크플로우
  - `test-news.yml`: 테스트 워크플로우
