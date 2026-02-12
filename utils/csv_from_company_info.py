"""
일회성: company_info.json → portfolio_news_data.csv 변환.
출력 CSV는 프로젝트 최상위(portfolio_news_data.csv)에 씁니다.
"""
import json
import csv
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPANY_INFO_PATH = os.path.join(REPO_ROOT, "company_info.json")
CSV_PATH = os.path.join(REPO_ROOT, "portfolio_news_data.csv")

with open(COMPANY_INFO_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

rows = []
for company, info in data.items():
    comment = info.get("comment", "")
    keywords = info.get("keyword", [])
    managers = info.get("manager", [])
    keyword_str = " / ".join(keywords) if keywords else ""
    manager_str = " / ".join(managers) if managers else ""
    rows.append({
        "기업명": company,
        "회사소개": comment,
        "담당자": manager_str,
        "키워드": keyword_str,
    })

with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["기업명", "회사소개", "담당자", "키워드"])
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {len(rows)} rows to {CSV_PATH}")
