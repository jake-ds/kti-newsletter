from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
import time
import os

# Load environment variables
load_dotenv()
openai_client = OpenAI()

# Set OpenAI API key from environment variable
openai_client.api_key = os.environ.get("OPENAI_API_KEY")
if not openai_client.api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable is not set")


def get_embedding(text, model="text-embedding-ada-002"):
    response = openai_client.embeddings.create(input=text, model=model)

    return response.data[0].embedding


def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def filter_similar_titles(titles, threshold=0.85):
    embeddings = []
    for title in titles:
        try:
            embedding = get_embedding(title)
            embeddings.append(embedding)
            time.sleep(0.4)  # Rate limiting
        except Exception as e:
            print(f"Error processing title '{title}': {str(e)}")
            continue

    if not embeddings:
        return []

    unique_titles = []
    for i, embedding in enumerate(embeddings):
        is_unique = True
        for unique_embedding in unique_titles:
            if cosine_similarity(embedding, unique_embedding[1]) > threshold:
                is_unique = False
                break
        if is_unique:
            unique_titles.append((titles[i], embedding, i))
    return [idx for _, _, idx in unique_titles]


def check_news_relevance(news_title, news_description, company_name, business_content, keywords):
    """
    뉴스 기사가 회사 사업 내용과 얼마나 관련이 있는지 0-10 점수로 평가

    Args:
        news_title: 뉴스 제목
        news_description: 뉴스 설명/요약
        company_name: 회사명
        business_content: 회사 사업 내용
        keywords: 검색에 사용된 키워드 리스트

    Returns:
        int: 0-10 관련성 점수 (10이 가장 관련성 높음)
    """
    max_retries = 3
    wait_times = [2, 4, 8]  # seconds

    for attempt in range(max_retries):
        try:
            keywords_str = ', '.join(keywords) if isinstance(keywords, list) else str(keywords)

            prompt = f"""다음 뉴스가 회사와 얼마나 관련이 있는지 0-10으로 평가해주세요.

**회사 정보:**
- 회사명: {company_name}
- 사업 내용: {business_content}
- 검색 키워드: {keywords_str}

**뉴스 정보:**
- 제목: {news_title}
- 내용: {news_description}

**평가 순서:**
1. 먼저 회사명이나 검색 키워드가 뉴스에 직접 언급되는지 확인
2. 검색 키워드가 회사와 무관한 맥락으로 사용되었는지 확인 (예: "파운트" 회사인데 "어마운트", "마운트" 같은 다른 단어)
3. 뉴스 내용이 회사 사업과 관련 있는지 평가

**점수 기준:**
- 10점: 회사명 직접 언급 + 핵심 사업/제품/서비스 직접 관련
- 7-9점: 회사명 직접 언급 + 일반 사업 활동 관련
- 4-6점: 회사명 언급 없지만 산업/시장과 관련, 또는 파트너사/경쟁사 관련
- 1-3점: 키워드만 일치하나 사업과 거의 무관, 또는 간접 언급
- 0점: 동음이의어/오타/완전 무관 (키워드가 다른 의미로 사용됨)

**특별 주의사항:**
- 회사명이 뉴스에 전혀 언급되지 않으면 일반적으로 5점 이하
- 검색 키워드가 다른 단어의 일부로 포함된 경우 (예: "~마운트"는 "파운트"와 무관) 0-1점
- 단순 키워드 일치보다 의미적 관련성을 우선 평가

먼저 판단 근거를 한 문장으로 간단히 설명하고, 마지막 줄에 "점수: X" 형식으로 점수를 출력하세요.
예시: 회사명이 직접 언급되고 신규 서비스 출시 내용이므로 핵심 사업 관련 | 점수: 9"""

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 뉴스 기사와 회사 사업의 관련성을 평가하는 전문가입니다. 판단 근거를 간단히 설명하고 마지막에 '점수: X' 형식으로 0-10 사이의 점수를 제시하세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.2
            )

            answer = response.choices[0].message.content.strip()

            # 판단 근거와 점수 분리
            reasoning = ""
            score_str = ""

            # "점수: X" 패턴 찾기
            if "점수:" in answer or "점수 :" in answer:
                parts = answer.split("|")
                if len(parts) == 2:
                    reasoning = parts[0].strip()
                    score_part = parts[1].strip()
                else:
                    score_part = answer

                # 점수 추출
                import re
                score_match = re.search(r'점수\s*:\s*(\d+)', score_part)
                if score_match:
                    score_str = score_match.group(1)
            else:
                # "점수:" 패턴이 없으면 숫자만 추출 시도
                import re
                score_match = re.search(r'\b(\d+)\b', answer)
                if score_match:
                    score_str = score_match.group(1)

            # 숫자 변환 및 검증
            try:
                score = int(score_str)
                if 0 <= score <= 10:
                    if reasoning:
                        print(f"    Reasoning: {reasoning[:100]}...")
                    return score
                else:
                    print(f"Warning: Score {score} out of range, defaulting to 0")
                    return 0
            except (ValueError, AttributeError):
                print(f"Warning: Could not parse score from '{answer}', defaulting to 0")
                return 0

        except Exception as e:
            if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                print(f"Rate limit hit, retrying in {wait_times[attempt]}s...")
                time.sleep(wait_times[attempt])
            elif attempt == max_retries - 1:
                print(f"Error checking relevance after {max_retries} attempts: {str(e)}")
                return 0  # 에러 시 보수적으로 0점 반환
            else:
                print(f"Error checking relevance: {str(e)}")
                return 0

    return 0


def filter_news_by_relevance(news_data, company_info, threshold=6, beta_mode=False):
    """
    AI 기반 관련성 점수로 뉴스 필터링

    Args:
        news_data: {회사명: [(제목, 설명, 링크), ...]} 형태의 뉴스 데이터
        company_info: {회사명: {"comment": "사업내용", ...}} 형태의 회사 정보
        threshold: 관련성 점수 임계값 (기본값 6, 0-10 범위)
        beta_mode: 베타 테스트 모드 (True면 필터링하지 않고 점수만 추가)

    Returns:
        filtered_news_data: 필터링된 뉴스 데이터
        - 일반 모드: {회사명: [(제목, 설명, 링크), ...]}
        - 베타 모드: {회사명: [(제목, 설명, 링크, 점수), ...]}
    """
    filtered_news_data = {}
    total_news = 0
    filtered_news_count = 0
    low_relevance_count = 0

    for company, news_list in news_data.items():
        business_content = company_info.get(company, {}).get("comment", "")
        keywords = company_info.get(company, {}).get("keyword", [])

        if not business_content:
            print(f"Warning: No business content for {company}, skipping relevance check")
            filtered_news_data[company] = news_list
            continue

        filtered_news = []
        for news_item in news_list:
            total_news += 1
            title, description, link = news_item

            # AI로 관련성 점수 평가
            score = check_news_relevance(title, description, company, business_content, keywords)

            print(f"  [{company}] Score: {score}/10 - {title[:50]}...")

            if beta_mode:
                # 베타 모드: 모든 뉴스를 포함하되 점수를 추가
                filtered_news.append((title, description, link, score))
                filtered_news_count += 1
                if score < threshold:
                    low_relevance_count += 1
                    print(f"    → Low relevance (score {score} < threshold {threshold}) - Will be shown with warning")
            else:
                # 일반 모드: 임계값 이상만 포함
                if score >= threshold:
                    filtered_news.append(news_item)
                    filtered_news_count += 1
                else:
                    print(f"    → Filtered out (score {score} < threshold {threshold})")

            # Rate limiting
            time.sleep(0.5)

        if filtered_news:
            filtered_news_data[company] = filtered_news

    print(f"\n=== Relevance Filtering Summary ===")
    print(f"Total news before filtering: {total_news}")
    if beta_mode:
        print(f"BETA MODE: All news included with relevance scores")
        print(f"News with high relevance (>= {threshold}): {filtered_news_count - low_relevance_count}")
        print(f"News with low relevance (< {threshold}): {low_relevance_count}")
        print(f"  → These will be marked as '[관련성 낮음 - 필터링 예정]'")
    else:
        print(f"News after filtering: {filtered_news_count}")
        print(f"Filtered out: {total_news - filtered_news_count} ({(total_news - filtered_news_count) / total_news * 100:.1f}%)")

    return filtered_news_data
