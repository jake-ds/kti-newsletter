import json
import csv
import os

# 프로젝트 루트 (utils/ 기준 상위 디렉터리)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_json(file_path):
    """JSON 파일 로드. 상대 경로면 프로젝트 루트 기준."""
    if not os.path.isabs(file_path):
        file_path = os.path.join(_REPO_ROOT, file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def load_company_info_from_csv(csv_path="portfolio_news_data.csv"):
    """
    프로젝트 최상위의 CSV에서 회사 정보를 읽어 company_info와 동일한 구조의 dict를 반환합니다.
    반환 형태: { 회사명: { "keyword": [...], "comment": str, "manager": [...] } }
    csv_path는 기본값이면 프로젝트 루트의 portfolio_news_data.csv를 사용합니다.
    """
    if not os.path.isabs(csv_path):
        csv_path = os.path.join(_REPO_ROOT, csv_path)
    company_info = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("기업명", "").strip()
            if not name:
                continue
            comment = row.get("회사소개", "").strip()
            manager_str = row.get("담당자", "").strip()
            keyword_str = row.get("키워드", "").strip()
            managers = [m.strip() for m in manager_str.split("/") if m.strip()]
            keyword_for_list = keyword_str if keyword_str else name
            company_info[name] = {
                "keyword": [keyword_for_list],
                "comment": comment,
                "manager": managers,
            }
    return company_info
