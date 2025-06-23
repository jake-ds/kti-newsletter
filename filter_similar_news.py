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


def is_relevant(news, business_content):
    max_retries = 1
    wait_times = [5, 10, 15]  # seconds

    for attempt in range(max_retries):
        try:
            prompt = f"뉴스: {news}\n\n이 뉴스가 다음 사업 내용과 관련이 있나요?\n\n사업 내용: {business_content}\n\n관련이 있다면 'Yes', 관련이 없다면 'No'로 답변해 주세요."
            response = openai_client.Completion.create(
                model="text-davinci-003", prompt=prompt, max_tokens=10
            )
            answer = response.choices[0].text.strip().lower()
            if answer == "yes":
                return True
            elif answer == "no":
                return False
        except openai_client.error.RateLimitError:
            if attempt == max_retries - 1:
                print("Failed after all retries due to rate limits")
                return False
            time.sleep(wait_times[attempt])
        except Exception as e:
            print(f"Error checking relevance: {str(e)}")
            return False
    return False


def filter_news_by_company(news_data, company_info):
    filtered_news_data = {}
    for company, news_list in news_data.items():
        business_content = company_info.get(company, "")
        if business_content:
            filtered_news = [
                news for news in news_list if is_relevant(news, business_content)
            ]
            filtered_news_data[company] = filtered_news
    return filtered_news_data
