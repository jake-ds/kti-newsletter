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


def check_news_relevance(news_title, news_description, business_content):
    """
    뉴스 기사가 회사 사업 내용과 얼마나 관련이 있는지 0-10 점수로 평가

    Args:
        news_title: 뉴스 제목
        news_description: 뉴스 설명/요약
        business_content: 회사 사업 내용

    Returns:
        int: 0-10 관련성 점수 (10이 가장 관련성 높음)
    """
    max_retries = 3
    wait_times = [2, 4, 8]  # seconds

    for attempt in range(max_retries):
        try:
            prompt = f"""다음 뉴스 기사가 회사의 사업 내용과 얼마나 관련이 있는지 0-10 점수로 평가해주세요.

뉴스 제목: {news_title}
뉴스 내용: {news_description}

회사 사업 내용: {business_content}

평가 기준:
- 10점: 회사의 핵심 사업/제품/서비스에 직접적으로 관련된 뉴스
- 7-9점: 회사의 사업 분야와 밀접하게 관련된 뉴스
- 4-6점: 회사가 속한 산업이나 시장과 간접적으로 관련된 뉴스
- 1-3점: 회사명은 언급되지만 사업과 거의 관련 없는 뉴스
- 0점: 완전히 관련 없는 뉴스 (동음이의어, 오타 등)

0-10 사이의 숫자만 답변해주세요."""

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 뉴스 기사와 회사 사업의 관련성을 평가하는 전문가입니다. 0-10 사이의 숫자로만 답변하세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.3
            )

            answer = response.choices[0].message.content.strip()

            # 숫자 추출
            try:
                score = int(answer)
                if 0 <= score <= 10:
                    return score
                else:
                    print(f"Warning: Score {score} out of range, defaulting to 0")
                    return 0
            except ValueError:
                print(f"Warning: Could not parse score '{answer}', defaulting to 0")
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


def filter_news_by_relevance(news_data, company_info, threshold=6):
    """
    AI 기반 관련성 점수로 뉴스 필터링

    Args:
        news_data: {회사명: [(제목, 설명, 링크), ...]} 형태의 뉴스 데이터
        company_info: {회사명: {"comment": "사업내용", ...}} 형태의 회사 정보
        threshold: 관련성 점수 임계값 (기본값 6, 0-10 범위)

    Returns:
        filtered_news_data: 필터링된 뉴스 데이터
    """
    filtered_news_data = {}
    total_news = 0
    filtered_news_count = 0

    for company, news_list in news_data.items():
        business_content = company_info.get(company, {}).get("comment", "")

        if not business_content:
            print(f"Warning: No business content for {company}, skipping relevance check")
            filtered_news_data[company] = news_list
            continue

        filtered_news = []
        for news_item in news_list:
            total_news += 1
            title, description, link = news_item

            # AI로 관련성 점수 평가
            score = check_news_relevance(title, description, business_content)

            print(f"  [{company}] Score: {score}/10 - {title[:50]}...")

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
    print(f"News after filtering: {filtered_news_count}")
    print(f"Filtered out: {total_news - filtered_news_count} ({(total_news - filtered_news_count) / total_news * 100:.1f}%)")

    return filtered_news_data
