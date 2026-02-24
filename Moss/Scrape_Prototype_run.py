# %% [markdown]
# ## Import Section

# %%
import pandas as pd
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse, urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCRAPED_EACH_DIR = BASE_DIR / "Scraped_Each"
SCRAPED_ALL_DIR = BASE_DIR / "Scraped_All"
SCRAPED_EACH_DIR.mkdir(parents=True, exist_ok=True)
SCRAPED_ALL_DIR.mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ## Initiate basic variables

# %%
JOBS_LIST = ['Data Scientist', 'Data Analyst', 'Data Engineer']
# JOBS_LIST = ['Data Scientist'] #FOR DEBUGGING
SKILLS = {
    # ---------------- Core Programming ----------------
    "python": ["python"],
    "r": [" r ", " r,", " r\n", " r/"],
    "java": ["java"],
    "scala": ["scala"],
    "c++": ["c++"],

    # ---------------- SQL & Databases ----------------
    "sql & database": [" sql ", "mysql", "postgres", "postgresql", "oracle", "sql server", "mssql", "sqlite"],
    "mongodb": ["mongodb", "mongo"],
    "elasticsearch": ["elasticsearch", "elastic search"],

    # ---------------- Data Libraries ----------------
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scipy": ["scipy"],
    "sklearn": ["scikit-learn", "sklearn"],

    # ---------------- Machine Learning ----------------
    "machine_learning": [
        "machine learning", "supervised", "unsupervised",
        "random forest", "xgboost", "lightgbm", "catboost"
    ],

    # ---------------- Deep Learning ----------------
    "deep_learning": [
        "deep learning", "neural network", "cnn", "rnn", "lstm", "transformer"
    ],

    # ---------------- GenAI / LLM ----------------
    "llm": ["llm", "large language model"],
    "rag": ["rag", "retrieval augmented generation"],
    "langchain": ["langchain"],
    "openai": ["openai"],
    "huggingface": ["huggingface"],
    "prompt_engineering": ["prompt engineering"],
    "vector_db": ["vector database", "pinecone", "faiss", "weaviate", "milvus"],

    # ---------------- Visualization / BI ----------------
    "excel": ["excel", "vlookup", "pivot table", "power query"],
    "powerbi": ["power bi", "powerbi", "dax"],
    "tableau": ["tableau"],
    "matplotlib": ["matplotlib"],
    "seaborn": ["seaborn"],
    "plotly": ["plotly"],

    # ---------------- Big Data ----------------
    "spark": ["spark", "pyspark"],
    "hadoop": ["hadoop"],
    "kafka": ["kafka"],

    # ---------------- Cloud ----------------
    "aws": ["aws", "amazon web services", "s3", "redshift", "athena", "glue", "lambda"],
    "gcp": ["gcp", "google cloud", "bigquery", "cloud storage"],
    "azure": ["azure", "synapse", "databricks"],

    # ---------------- Data Engineering ----------------
    "etl": ["etl", "elt", "data pipeline"],
    "airflow": ["airflow"],

    # ---------------- MLOps / Deployment ----------------
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "mlflow": ["mlflow"],
    "fastapi": ["fastapi"],
    "flask": ["flask"],
    "streamlit": ["streamlit"],

    # ---------------- Statistics ----------------
    "statistics": [
        "statistics", "statistical", "hypothesis testing",
        "regression", "anova", "probability"
    ],

    # ---------------- Version Control ----------------
    "git": ["git", "github", "gitlab"],

    # ---------------- APIs ----------------
    "api": ["api", "rest api"],

    # ---------------- Linux ----------------
    "linux": ["linux", "unix"],    
}

SEARCH_URLS = {
    # "JobThai": [[job_title,f"https://www.jobthai.com/th/jobs?keyword={job_title}&page=1&orderBy=RELEVANCE_SEARCH".replace(" ", "%20")] for job_title in JOBS_LIST],
    "JobsDB": [[job_title,f"https://th.jobsdb.com/th/{job_title}-jobs".replace(" ", "-")] for job_title in JOBS_LIST],
    # "JOBBKK": [[job_title,f"https://jobbkk.com/jobs/lists/1/หางาน,{job_title},ทุกจังหวัด,ทั้งหมด.html?keyword_type=3&sort=4".replace(" ", "%20")] for job_title in JOBS_LIST],
}

KEY_VARIANTS = {
    "data": ["data"],
    "scientist": ["scientist", "science", "scien", "scient"],
    "engineer": ["engineer", "engineering", "eng"],
    "analyst": ["analyst", "analytics", "analysis"],
    "developer": ["developer", "development", "dev"],
}

SKILL_COLUMNS = [f"skill_{name}" for name in SKILLS]

EN_TO_THAI_PROVINCE = {
    "amnat charoen": "อำนาจเจริญ",
    "ang thong": "อ่างทอง",
    "bangkok": "กรุงเทพมหานคร",
    "bueng kan": "บึงกาฬ",
    "buri ram": "บุรีรัมย์",
    "chachoengsao": "ฉะเชิงเทรา",
    "chai nat": "ชัยนาท",
    "chaiyaphum": "ชัยภูมิ",
    "chanthaburi": "จันทบุรี",
    "chiang mai": "เชียงใหม่",
    "chiang rai": "เชียงราย",
    "chon buri": "ชลบุรี",
    "chonburi": "ชลบุรี",
    "chumphon": "ชุมพร",
    "kalasin": "กาฬสินธุ์",
    "kamphaeng phet": "กำแพงเพชร",
    "kanchanaburi": "กาญจนบุรี",
    "khon kaen": "ขอนแก่น",
    "krabi": "กระบี่",
    "lampang": "ลำปาง",
    "lamphun": "ลำพูน",
    "loei": "เลย",
    "lop buri": "ลพบุรี",
    "lopburi": "ลพบุรี",
    "mae hong son": "แม่ฮ่องสอน",
    "maha sarakham": "มหาสารคาม",
    "mukdahan": "มุกดาหาร",
    "nakhon nayok": "นครนายก",
    "nakhon pathom": "นครปฐม",
    "nakhon phanom": "นครพนม",
    "nakhon ratchasima": "นครราชสีมา",
    "korat": "นครราชสีมา",
    "nakhon sawan": "นครสวรรค์",
    "nakhon si thammarat": "นครศรีธรรมราช",
    "nan": "น่าน",
    "narathiwat": "นราธิวาส",
    "nong bua lamphu": "หนองบัวลำภู",
    "nong khai": "หนองคาย",
    "nonthaburi": "นนทบุรี",
    "pathum thani": "ปทุมธานี",
    "pattani": "ปัตตานี",
    "phang nga": "พังงา",
    "phatthalung": "พัทลุง",
    "phayao": "พะเยา",
    "phetchabun": "เพชรบูรณ์",
    "phetchaburi": "เพชรบุรี",
    "phichit": "พิจิตร",
    "phitsanulok": "พิษณุโลก",
    "phra nakhon si ayutthaya": "พระนครศรีอยุธยา",
    "ayutthaya": "พระนครศรีอยุธยา",
    "phrae": "แพร่",
    "phuket": "ภูเก็ต",
    "prachin buri": "ปราจีนบุรี",
    "prachinburi": "ปราจีนบุรี",
    "prachuap khiri khan": "ประจวบคีรีขันธ์",
    "ranong": "ระนอง",
    "ratchaburi": "ราชบุรี",
    "rayong": "ระยอง",
    "roi et": "ร้อยเอ็ด",
    "sa kaeo": "สระแก้ว",
    "sakaeo": "สระแก้ว",
    "sakon nakhon": "สกลนคร",
    "samut prakan": "สมุทรปราการ",
    "samut sakhon": "สมุทรสาคร",
    "samut songkhram": "สมุทรสงคราม",
    "sara buri": "สระบุรี",
    "saraburi": "สระบุรี",
    "satun": "สตูล",
    "sing buri": "สิงห์บุรี",
    "sisaket": "ศรีสะเกษ",
    "si sa ket": "ศรีสะเกษ",
    "songkhla": "สงขลา",
    "sukhothai": "สุโขทัย",
    "suphan buri": "สุพรรณบุรี",
    "surat thani": "สุราษฎร์ธานี",
    "surin": "สุรินทร์",
    "tak": "ตาก",
    "trang": "ตรัง",
    "trat": "ตราด",
    "ubon ratchathani": "อุบลราชธานี",
    "udon thani": "อุดรธานี",
    "uthai thani": "อุทัยธานี",
    "uttaradit": "อุตรดิตถ์",
    "yala": "ยะลา",
    "yasothon": "ยโสธร"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7",
}

JOBSDB_PROXIES = {
    "http": os.getenv("JOBSDB_PROXY_URL", "").strip(),
    "https": os.getenv("JOBSDB_PROXY_URL", "").strip(),
}
JOBSDB_PROXIES = {k: v for k, v in JOBSDB_PROXIES.items() if v}

# For Debugging Start
print("Search URLs:")
for platform, urls in SEARCH_URLS.items():
    print(f"{platform}:")
    for url in urls:
        print(f"  {url}")
# For Debugging End     

# %% [markdown]
# ## JobThai Scraper Function

# %%
def normalize_province_code(value) -> str:
    text = str(value).strip()
    if text.isdigit():
        number = int(text)
        if number <= 0:
            raise ValueError(f"Province must be positive, got: {value}")
        return f"{number:02d}"
    raise ValueError(f"Invalid province code: {value}")


def normalize_for_match(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def normalize_for_skill_match(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def keyword_match_groups_from_query(keyword: str) -> list[list[str]]:
    tokens = [token for token in normalize_for_match(keyword).split() if token]
    groups = []

    for token in tokens:
        if token in KEY_VARIANTS:
            groups.append(KEY_VARIANTS[token])
        else:
            groups.append([token])

    return groups


def title_matches_keyword(title: str, keyword_groups: list[list[str]]) -> bool:
    if not keyword_groups:
        return True

    title_norm = normalize_for_match(title)
    search_from = 0

    for group in keyword_groups:
        best_pos = None
        best_variant = ""

        for variant in group:
            variant_norm = normalize_for_match(variant)
            if not variant_norm:
                continue

            pos = title_norm.find(variant_norm, search_from)
            if pos != -1 and (best_pos is None or pos < best_pos):
                best_pos = pos
                best_variant = variant_norm

        if best_pos is None:
            return False

        search_from = best_pos + len(best_variant)

    return True


def variant_matches_text(variant: str, normalized_text: str) -> bool:
    variant_norm = normalize_for_skill_match(variant)
    if not variant_norm:
        return False
    pattern = rf"(?<![a-z0-9]){re.escape(variant_norm).replace(r'\\ ', r'\\s+')}(?![a-z0-9])"
    return re.search(pattern, normalized_text) is not None


def extract_skills(text: str) -> dict:
    normalized_text = normalize_for_skill_match(text)
    matched = []

    for skill_name, variants in SKILLS.items():
        if any(variant_matches_text(variant, normalized_text) for variant in variants):
            matched.append(skill_name)

    skill_flags = {f"skill_{name}": int(name in matched) for name in SKILLS}

    return {
        "matched_skills": "|".join(matched),
        "matched_skill_count": len(matched),
        **skill_flags,
    }


def normalize_jobthai_detail_url(job_url: str) -> str:
    if not job_url:
        return ""

    parsed = urlparse(job_url)
    path = parsed.path

    path = path.replace("/th/company/job/", "/th/job/")
    path = path.replace("/company/job/", "/job/")

    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def clean_text(text: str) -> str:
    return " ".join((text or "").split())


def extract_salary(text: str) -> str:
    patterns = [
        r"\d[\d,\s]*\s*-\s*\d[\d,\s]*\s*บาท",
        r"\d[\d,\s]*\s*บาท",
        r"ตามโครงสร้างบริษัทฯ",
        r"ตามประสบการณ์",
        r"ตามตกลง",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return clean_text(match.group(0))
    return ""


def extract_posted_date(text: str) -> str:
    match = re.search(r"\b\d{1,2}\s+[ก-๙A-Za-z\.]+\s+\d{2}\b", text)
    return clean_text(match.group(0)) if match else ""


def pick_text(parent, selectors: list[str]) -> str:
    for selector in selectors:
        element = parent.select_one(selector)
        if element:
            text = clean_text(element.get_text(" ", strip=True))
            if text:
                return text
    return ""


def guess_location(lines: list[str], title: str, company: str, salary: str) -> str:
    priority_keywords = ["เขต", "กรุงเทพ", "จังหวัด", "อำเภอ", "อ.", "ต."]
    transit_keywords = ["BTS", "MRT", "SRT", "BRT", "Airport Rail Link"]

    for line in lines:
        if line in {title, company, salary}:
            continue
        if any(keyword in line for keyword in priority_keywords):
            return line

    for line in lines:
        if line in {title, company, salary}:
            continue
        if any(keyword in line for keyword in transit_keywords):
            return line

    if salary and salary in lines:
        salary_idx = lines.index(salary)
        for idx in range(salary_idx - 1, -1, -1):
            candidate = lines[idx]
            if candidate not in {title, company}:
                return candidate

    return ""


def parse_card_from_title(title_node, page_num: int, keyword: str) -> dict:
    title = clean_text(title_node.get_text(" ", strip=True))

    anchor = title_node.find_parent("a", href=True)
    href = anchor.get("href", "") if anchor else ""
    job_url = href if href.startswith("http") else f"https://www.jobthai.com{href}"
    job_url = normalize_jobthai_detail_url(job_url)

    card = anchor if anchor is not None else title_node

    company = pick_text(card, [
        'span[id^="job-list-company-name-"]',
        'h2.ohgq7e-0.enAWkF',
    ])

    location = pick_text(card, [
        "h3#location-text",
        "h3.location-text",
    ])

    salary = pick_text(card, [
        "span.salary-text",
        "div.msklqa-20",
        "div.msklqa-17",
    ])

    posted_date = pick_text(card, [
        "span.msklqa-9",
    ])

    raw_lines = [clean_text(x) for x in card.get_text("\n", strip=True).splitlines() if clean_text(x)]
    raw_text = clean_text(" ".join(raw_lines))

    if not salary:
        salary = extract_salary(raw_text)
    if not posted_date:
        posted_date = extract_posted_date(raw_text)
    if not location:
        location = guess_location(raw_lines, title=title, company=company, salary=salary)

    return {
        "keyword": keyword,
        "page": page_num,
        "job_title": title,
        "company": company,
        "location": location,
        "salary": salary,
        "posted_date": posted_date,
        "job_url": job_url,
        "raw_text": raw_text,
    }


def extract_detail_from_job_page(job_url: str, headers: dict) -> dict:
    base_detail = {
        "province_code": "",
        "province_name": "",
        "job_detail_text": "",
        "job_qualification_text": "",
        "matched_skills": "",
        "matched_skill_count": 0,
        **{column: 0 for column in SKILL_COLUMNS},
    }

    try:
        response = requests.get(job_url, headers=headers, timeout=30)
        response.raise_for_status()
    except Exception:
        return base_detail

    soup = BeautifulSoup(response.text, "html.parser")

    province_code = ""
    province_name = ""
    for anchor in soup.select('a[href*="province="]'):
        tag = anchor.select_one('h3[id^="job-detail-tag-"]')
        if not tag:
            continue

        href = anchor.get("href", "")
        name = clean_text(tag.get_text(" ", strip=True))
        if not href or not name:
            continue

        province_value = parse_qs(urlparse(href).query).get("province", [""])[0]
        if not province_value or not province_value.isdigit():
            continue

        try:
            province_code = normalize_province_code(province_value)
        except ValueError:
            continue

        province_name = name
        break

    jd_node = soup.select_one("span#job-detail")
    job_detail_text = clean_text(jd_node.get_text("\n", strip=True)) if jd_node else ""

    qualification_node = soup.select_one("#job-properties-wrapper")
    job_qualification_text = clean_text(qualification_node.get_text(" ", strip=True)) if qualification_node else ""

    combined_text = " ".join([text for text in [job_detail_text, job_qualification_text] if text])
    skill_info = extract_skills(combined_text)

    return {
        "province_code": province_code,
        "province_name": province_name,
        "job_detail_text": job_detail_text,
        "job_qualification_text": job_qualification_text,
        **skill_info,
    }


def scrape_job_jobthai(
    SEARCH_URLS: dict[str, list[str]],
    SLEEP_SEC: float = 0.5,
) -> pd.DataFrame:

    collected_frames = []

    try:
        for job in SEARCH_URLS["JobThai"]:
            keyword = job[0]
            search_url = job[1]

            keyword_groups = keyword_match_groups_from_query(keyword)
            print(f"Scraping JobThai for '{keyword}'")

            all_rows = []
            seen_urls = set()

            for page_no in range(1, 50):
                page_url = search_url.replace("page=1", f"page={page_no}")
                print(f"\tFetching page {page_no}")

                response = requests.get(page_url, headers=headers, timeout=30)
                response.raise_for_status()

                if "nodata=true" in response.url.lower():
                    print("No data found for this keyword.")
                    break

                soup = BeautifulSoup(response.text, "html.parser")
                title_cards_html = soup.select('h2[id^="job-card-item-"]')

                page_rows = []
                for title_card_html in title_cards_html:
                    row = parse_card_from_title(
                        title_card_html,
                        page_num=page_no,
                        keyword=keyword,
                    )

                    if not row["job_url"]:
                        continue
                    if not title_matches_keyword(row["job_title"], keyword_groups):
                        continue
                    if row["job_url"] in seen_urls:
                        continue

                    seen_urls.add(row["job_url"])
                    page_rows.append(row)

                if not page_rows:
                    break

                all_rows.extend(page_rows)

                if SLEEP_SEC > 0:
                    time.sleep(SLEEP_SEC)

            total_details = len(all_rows)
            print(f"[Detail] Starting detail extraction for {total_details} jobs")

            for row in all_rows:
                detail_info = extract_detail_from_job_page(row["job_url"], headers=headers)
                row.update(detail_info)

                if SLEEP_SEC > 0:
                    time.sleep(SLEEP_SEC)

            job_df = pd.DataFrame(all_rows)
            if job_df.empty:
                continue
            job_df["domain"] = "JobThai"
            job_df["min_salary"] = None
            job_df["max_salary"] = None

            ordered_columns = [
                "domain",
                "keyword",
                "province_name",
                "job_title",
                "company",
                "location",
                "salary",
                "min_salary",
                "max_salary",
                "posted_date",
                "job_url",
                "matched_skills",
                "matched_skill_count",
                *SKILL_COLUMNS,
            ]
            for column in ordered_columns:
                if column not in job_df.columns:
                    job_df[column] = "" if column not in {"matched_skill_count", *SKILL_COLUMNS} else 0

            job_df = job_df[ordered_columns].drop_duplicates(subset=["job_url"])
            collected_frames.append(job_df)
            print(f"[Done] Collected {len(job_df)} rows for '{keyword}' job search in JobThai")

    except Exception as e:
        print(f"Error occurred on JobThai scraping: {e}")
        print("Skipping JobThai and returning collected data so far.")

    if not collected_frames:
        return pd.DataFrame()

    final_df = pd.concat(collected_frames, ignore_index=True)
    final_df = final_df.drop_duplicates(subset=["job_url"])
    return final_df

# %% [markdown]
# ## JobThai Scraper Run

# %%
jobthai_scraped_df = scrape_job_jobthai(SEARCH_URLS)

# %% [markdown]
# ## Clean Data JobThai Function

# %%
THAI_MONTHS = {
    "ม.ค.": 1,
    "ก.พ.": 2,
    "มี.ค.": 3,
    "เม.ย.": 4,
    "พ.ค.": 5,
    "มิ.ย.": 6,
    "ก.ค.": 7,
    "ส.ค.": 8,
    "ก.ย.": 9,
    "ต.ค.": 10,
    "พ.ย.": 11,
    "ธ.ค.": 12,
}

def parse_thai_short_date(value: str) -> str:
    text = str(value).strip()
    if not text:
        return ""

    match = re.match(r"^(\d{1,2})\s+([ก-๙\.]+)\s+(\d{2})$", text)
    if not match:
        return ""

    day = int(match.group(1))
    month_text = match.group(2)
    yy_be = int(match.group(3))  # e.g. 69 -> 2569 (B.E.)
    month = THAI_MONTHS.get(month_text)
    if month is None:
        return ""

    year_ad = (2500 + yy_be) - 543
    try:
        parsed = pd.Timestamp(year=year_ad, month=month, day=day)
    except Exception:
        return ""

    return parsed.strftime("%m/%d/%Y")


def clean_data_jobthai(job_df: pd.DataFrame) -> pd.DataFrame:

    # province_name: remove "จ." prefix
    job_df["province_name"] = (
        job_df["province_name"]
        .fillna("")
        .astype(str)
        .str.replace(r"^\s*จ\.\s*", "", regex=True)
        .str.strip()
    )

    # salary: extract min/max
    salary_pattern = re.compile(
        r"^\s*(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)(?:\s*บาท)?\s*$"
    )

    salary_parts = job_df["salary"].fillna("").astype(str).str.extract(salary_pattern)
    job_df["min_salary"] = salary_parts[0].fillna("").str.replace(",", "", regex=False)
    job_df["max_salary"] = salary_parts[1].fillna("").str.replace(",", "", regex=False)

    # 3) posted_date: convert Thai short date like to MM/DD/YYYY format
    job_df["posted_date"] = (
        job_df["posted_date"]
        .fillna("")
        .astype(str)
        .apply(parse_thai_short_date)
    )
    return job_df

# %% [markdown]
# ## Clean & Export Scraped JobThai Run

# %%
jobthai_scraped_df = clean_data_jobthai(jobthai_scraped_df)
jobthai_scraped_df.to_csv(SCRAPED_EACH_DIR / "jobthai_jobs.csv", index=False, encoding="utf-8-sig")

# %% [markdown]
# ## JobsDB Scraper Function

# %%
def update_query_in_url(url: str, **params) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    for key, value in params.items():
        query[key] = [str(value)]
    new_query = urlencode(query, doseq=True)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()

def normalize_for_match(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()

def keyword_match_groups_from_query(search_keyword: str) -> list[list[str]]:

    tokens = [token for token in normalize_for_match(search_keyword).split() if token]
    groups = []

    for token in tokens:
        groups.append(KEY_VARIANTS.get(token, [token]))

    return groups

def title_matches_keyword(title: str, keyword_groups: list[list[str]]) -> bool:
    if not keyword_groups:
        return True
    title_norm = normalize_for_match(title)
    return all(any(variant in title_norm for variant in group) for group in keyword_groups)

def extract_salary(text: str) -> str:
    patterns = [
        r"THB\s*[\d,]+\s*[-–]\s*THB\s*[\d,]+",
        r"THB\s*[\d,]+",
        r"[\d,]+\s*[-–]\s*[\d,]+\s*บาท",
        r"[\d,]+\s*บาท",
        r"Negotiable|ไม่ระบุเงินเดือน|ตามตกลง|ตามประสบการณ์",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return clean_text(match.group(0))
    return ""

def is_probable_salary(text: str) -> bool:
    if not text:
        return False
    text_norm = text.lower()
    salary_keywords = ["thb", "บาท", "salary", "negotiable", "ตามตกลง", "ตามประสบการณ์"]
    if any(key in text_norm for key in salary_keywords):
        return True
    return bool(re.search(r"\d", text_norm) and re.search(r"[-–]", text_norm))

def guess_province_name(location_text: str) -> str:
    location_clean = clean_text(location_text)
    if not location_clean:
        return ""

    for province in EN_TO_THAI_PROVINCE.values():
        if province in location_clean:
            return province

    location_lower = location_clean.lower()
    for english_name, thai_name in EN_TO_THAI_PROVINCE.items():
        if re.search(rf"\b{re.escape(english_name)}\b", location_lower):
            return thai_name

    parts = [clean_text(part) for part in re.split(r",|\||/", location_clean) if clean_text(part)]
    if not parts:
        return ""

    tail = parts[-1]
    tail = re.sub(r"^(เขต|อ\.|อำเภอ|จ\.|จังหวัด)\s*", "", tail).strip()
    return tail


def create_retry_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1,
        status_forcelist=[403, 429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET", "HEAD"]),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def jobsdb_headers(referer: str = "https://th.jobsdb.com/") -> dict:
    return {
        "User-Agent": headers["User-Agent"],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": headers["Accept-Language"],
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": referer,
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }


def jobsdb_get(session: requests.Session, url: str, referer: str = "https://th.jobsdb.com/") -> requests.Response:
    last_response = None

    for attempt in range(1, 4):
        response = session.get(
            url,
            headers=jobsdb_headers(referer=referer),
            timeout=30,
            proxies=JOBSDB_PROXIES or None,
        )
        last_response = response

        if response.status_code != 403:
            response.raise_for_status()
            return response

        if attempt < 3:
            try:
                session.get(
                    "https://th.jobsdb.com/",
                    headers=jobsdb_headers(),
                    timeout=30,
                    proxies=JOBSDB_PROXIES or None,
                )
            except Exception:
                pass
            time.sleep(1.0 * attempt)

    if last_response is not None:
        last_response.raise_for_status()
    raise requests.HTTPError("JobsDB request failed without response")


def extract_job_detail_text(job_url: str, session: requests.Session | None = None) -> str:
    active_session = session or create_retry_session()
    try:
        response = jobsdb_get(active_session, job_url, referer="https://th.jobsdb.com/")
    except Exception:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    detail_el = soup.select_one("[data-automation='jobAdDetails']")
    if detail_el:
        return clean_text(detail_el.get_text("\n", strip=True))

    section_el = soup.select_one("section")
    if section_el:
        return clean_text(section_el.get_text("\n", strip=True))

    return ""

def variant_matches_text(variant: str, normalized_text: str) -> bool:
    variant_norm = normalize_for_match(variant)
    if not variant_norm:
        return False

    pattern = re.escape(variant_norm)
    pattern = pattern.replace(r"\ ", r"\s+")
    regex = rf"(?<![a-z0-9]){pattern}(?![a-z0-9])"
    return re.search(regex, normalized_text) is not None


def extract_skills(detail_text: str) -> dict:
    text_norm = normalize_for_match(detail_text)
    found = []
    flags = {}

    for skill_key, variants in SKILLS.items():
        matched = any(variant_matches_text(variant, text_norm) for variant in variants)
        flags[f"skill_{skill_key}"] = int(matched)
        if matched:
            found.append(skill_key)

    flags["matched_skills"] = "|".join(found)
    flags["matched_skill_count"] = len(found)
    return flags

def parse_card(card, page_num: int, search_keyword: str) -> dict:
    title_el = card.select_one("a[data-automation='jobTitle']")
    company_el = card.select_one("a[data-automation='jobCompany'], [data-automation='jobCompany']")
    location_el = card.select_one("a[data-automation='jobLocation'], [data-automation='jobCardLocation']")
    date_el = card.select_one("[data-automation='jobListingDate']")
    salary_el = card.select_one("[data-automation='jobSalary']")
    overlay_link_el = card.select_one("a[data-automation='job-list-item-link-overlay'][href]")

    title = clean_text(title_el.get_text(" ", strip=True) if title_el else "")
    company = clean_text(company_el.get_text(" ", strip=True) if company_el else "")
    location_name = clean_text(location_el.get_text(" ", strip=True) if location_el else "")
    posted_date = clean_text(date_el.get_text(" ", strip=True) if date_el else "")

    salary_candidate = clean_text(salary_el.get_text(" ", strip=True) if salary_el else "")
    salary = salary_candidate if is_probable_salary(salary_candidate) else ""

    href = ""
    if overlay_link_el:
        href = overlay_link_el.get("href", "")
    elif title_el and title_el.get("href"):
        href = title_el.get("href", "")
    job_url = urljoin("https://th.jobsdb.com", href) if href else ""

    raw_text = clean_text(card.get_text("\n", strip=True))
    if not salary:
        salary = extract_salary(raw_text)

    province_name = guess_province_name(location_name)

    return {
        "keyword": search_keyword,
        "province_code": "",
        "province_name": province_name,
        "page": page_num,
        "job_title": title,
        "company": company,
        "location": location_name,
        "salary": salary,
        "posted_date": posted_date,
        "job_url": job_url,
        "raw_text": raw_text,
    }

def scrape_job_jobsdb(search_url: str = "", search_location: str = "", max_pages: int = 50, sleep_seconds: float = 0.5) -> pd.DataFrame:
    collected_frames = []
    session = create_retry_session()

    try:
        for job in SEARCH_URLS["JobsDB"]:
            keyword = job[0]
            search_url = job[1]
            keyword_groups = keyword_match_groups_from_query(keyword)

            all_rows = []
            seen_urls = set()

            print(f"[Search] Starting JobsDB crawl: max_pages={max_pages}")

            for page_num in range(1, max_pages + 1):
                page_url = update_query_in_url(search_url, page=page_num)
                if search_location.strip():
                    page_url = update_query_in_url(page_url, where=search_location.strip())

                print(f"[Search] Page {page_num}/{max_pages} -> request")
                try:
                    response = jobsdb_get(session, page_url, referer=search_url)
                except requests.HTTPError as http_err:
                    status_code = http_err.response.status_code if http_err.response is not None else None
                    if status_code == 403:
                        print("[Warn] JobsDB returned 403 (Forbidden).")
                        print("[Warn] This is commonly IP-based blocking on cloud runners (e.g., GitHub Actions).")
                        print("[Warn] Tip: set JOBSDB_PROXY_URL or run JobsDB scraping from a residential/local IP.")
                        break
                    raise

                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.select("article[data-testid='job-card'], article[data-automation='normalJob']")
                print(f"[Search] Page {page_num}/{max_pages} -> found cards: {len(cards)}")

                if not cards:
                    print(f"[Search] Page {page_num}/{max_pages} -> no cards, stopping")
                    break

                page_rows = []
                for card in cards:
                    row = parse_card(card, page_num=page_num, search_keyword=keyword)
                    if not row["job_title"] or not row["job_url"]:
                        continue
                    if not title_matches_keyword(row["job_title"], keyword_groups):
                        continue
                    if row["job_url"] in seen_urls:
                        continue

                    seen_urls.add(row["job_url"])
                    page_rows.append(row)

                if not page_rows:
                    print(f"[Search] Page {page_num}/{max_pages} -> no keyword matches, stopping")
                    break

                all_rows.extend(page_rows)
                print(f"[Search] Page {page_num}/{max_pages} -> kept {len(page_rows)} | cumulative={len(all_rows)}")

                if sleep_seconds > 0:
                    time.sleep(sleep_seconds)

            print(f"[Detail] Start detail scrape for {len(all_rows)} jobs")

            for idx, row in enumerate(all_rows, start=1):
                detail_text = extract_job_detail_text(row["job_url"], session=session)
                row["job_detail_text"] = detail_text

                skill_result = extract_skills(detail_text)
                row.update(skill_result)

                if len(all_rows) <= 50 or idx % 10 == 0 or idx == len(all_rows):
                    percent = (idx / len(all_rows)) * 100 if all_rows else 100
                    print(f"[Detail] {idx}/{len(all_rows)} ({percent:.1f}%)")

                if  sleep_seconds > 0:
                    time.sleep(sleep_seconds)

            job_df = pd.DataFrame(all_rows)

            if job_df.empty:
                continue

            job_df["domain"] = "JobsDB"
            job_df["min_salary"] = None
            job_df["max_salary"] = None

            ordered_cols = [
            "domain",
            "keyword",
            "province_name",
            "job_title",
            "company",
            "location",
            "salary",
            "min_salary",
            "max_salary",
            "posted_date",
            "job_url",
            "matched_skills",
            "matched_skill_count",
            *SKILL_COLUMNS,
            ]

            for col in ordered_cols:
                if col not in job_df.columns:
                    job_df[col] = "" if not col.startswith("skill_") and col != "matched_skill_count" else 0

            job_df = job_df[ordered_cols].drop_duplicates(subset=["job_url"])
            collected_frames.append(job_df)
            print(f"[Done] Collected {len(job_df)} rows for '{keyword}' job search in JobsDB")
    except Exception as e:
        print(f"Error occurred on JobsDB scraping: {e}")
        print("Skipping JobsDB and returning collected data so far.")

    if not collected_frames:
        return pd.DataFrame()
    
    final_df = pd.concat(collected_frames, ignore_index=True)
    final_df = final_df.drop_duplicates(subset=["job_url"])
    return final_df



# %% [markdown]
# ## JobsDB Scraper Run

# %%
jobsdb_scraped_df = scrape_job_jobsdb(SEARCH_URLS)

# %% [markdown]
# ## JobsDB Clean Function

# %%
def extract_jobsdb_salary_range(salary_text: str) -> tuple[str, str]:
    text = clean_text(str(salary_text or ""))
    if not text:
        return "", ""

    pattern = r"฿?\s*([\d,]+)\s*[-–]\s*฿?\s*([\d,]+)"
    match = re.search(pattern, text)
    if not match:
        return "", ""

    min_salary = match.group(1).replace(",", "")
    max_salary = match.group(2).replace(",", "")
    return min_salary, max_salary


def parse_jobsdb_relative_posted_date(value: str, now_dt: datetime | None = None) -> str:
    text = clean_text(str(value or ""))
    if not text:
        return ""

    current = now_dt or datetime.now()

    hour_match = re.search(r"(\d+)\s*ชั่วโมงที่ผ่านมา", text)
    if hour_match:
        dt = current - timedelta(hours=int(hour_match.group(1)))
        return dt.strftime("%m/%d/%Y")

    day_match = re.search(r"(\d+)\s*วันที่ผ่านมา", text)
    if day_match:
        dt = current - timedelta(days=int(day_match.group(1)))
        return dt.strftime("%m/%d/%Y")

    minute_match = re.search(r"(\d+)\s*นาทีที่ผ่านมา", text)
    if minute_match:
        dt = current - timedelta(minutes=int(minute_match.group(1)))
        return dt.strftime("%m/%d/%Y")

    week_match = re.search(r"(\d+)\s*สัปดาห์ที่ผ่านมา", text)
    if week_match:
        dt = current - timedelta(days=7 * int(week_match.group(1)))
        return dt.strftime("%m/%d/%Y")

    month_match = re.search(r"(\d+)\s*เดือนที่ผ่านมา", text)
    if month_match:
        dt = current - timedelta(days=30 * int(month_match.group(1)))
        return dt.strftime("%m/%d/%Y")

    return ""


def clean_data_jobsdb(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    output = df.copy()

    salary_pairs = output["salary"].apply(extract_jobsdb_salary_range)
    output["min_salary"] = salary_pairs.apply(lambda pair: pair[0])
    output["max_salary"] = salary_pairs.apply(lambda pair: pair[1])

    output["posted_date"] = output["posted_date"].apply(parse_jobsdb_relative_posted_date)

    return output

# %% [markdown]
# ## JobsDB Clean & Export Run

# %%
jobsdb_scraped_df = clean_data_jobsdb(jobsdb_scraped_df)
jobsdb_scraped_df.to_csv(SCRAPED_EACH_DIR / "jobsdb_jobs.csv", index=False, encoding="utf-8-sig")

# %% [markdown]
# ## JOBBKK Scraper Function

# %%
def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def normalize_for_match(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def normalize_for_skill_match(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()

def keyword_match_groups_from_query(search_keyword: str) -> list[list[str]]:

    tokens = [token for token in normalize_for_match(search_keyword).split() if token]
    groups = []

    for token in tokens:
        groups.append(KEY_VARIANTS.get(token, [token]))

    return groups

def title_matches_keyword(title: str, keyword_groups: list[list[str]]) -> bool:
    if not keyword_groups:
        return True
    title_norm = normalize_for_match(title)
    return all(any(variant in title_norm for variant in group) for group in keyword_groups)

def variant_matches_text(variant: str, normalized_text: str) -> bool:
    variant_norm = normalize_for_skill_match(variant)
    if not variant_norm:
        return False
    pattern = rf"(?<![a-z0-9]){re.escape(variant_norm).replace(r'\\ ', r'\\s+')}(?![a-z0-9])"
    return re.search(pattern, normalized_text) is not None


def extract_skills(text: str) -> dict:
    normalized_text = normalize_for_skill_match(text)
    matched = []

    for skill_name, variants in SKILLS.items():
        if any(variant_matches_text(variant, normalized_text) for variant in variants):
            matched.append(skill_name)

    skill_flags = {f"skill_{name}": int(name in matched) for name in SKILLS}

    return {
        "matched_skills": "|".join(matched),
        "matched_skill_count": len(matched),
        **skill_flags,
    }

def extract_salary(text: str) -> str:
    patterns = [
        r"\d[\d,\s]*\s*[-–]\s*\d[\d,\s]*\s*บาท",
        r"\d[\d,\s]*\s*บาท",
        r"ตามตกลง|ตามประสบการณ์|ไม่ระบุเงินเดือน",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return clean_text(match.group(0))
    return ""

def update_page_in_search_url(url: str, page_num: int) -> str:
    return re.sub(r"/jobs/lists/\d+/", f"/jobs/lists/{page_num}/", url)


def extract_keyword_from_url(url: str) -> str:
    path = url.split("?")[0]
    parts = path.split(",")
    if len(parts) >= 2:
        return parts[1].replace("%20", " ")
    return ""


def guess_province_name(location_text: str) -> str:
    location_text = clean_text(location_text)
    if not location_text:
        return ""
    for province in EN_TO_THAI_PROVINCE.values():
        if province in location_text:
            return province
    return ""

def parse_jobbkk_card(card, page_num: int, keyword: str) -> dict:
    title_el = card.select_one(".joblist-name-urgent a[href*='/jobs/detail']")
    company_el = card.select_one(".joblist-company-name a")
    location_el = card.select_one(".position-location span:last-child")
    salary_el = card.select_one(".position-salary span:last-child")
    updated_el = card.select_one(".joblist-updatetime-md-upper a")

    title = clean_text(title_el.get_text(" ", strip=True) if title_el else "")
    company = clean_text(company_el.get_text(" ", strip=True) if company_el else "")
    location = clean_text(location_el.get_text(" ", strip=True) if location_el else "")
    salary = clean_text(salary_el.get_text(" ", strip=True) if salary_el else "")
    posted_date = clean_text(updated_el.get("title") if updated_el and updated_el.get("title") else "")

    href = title_el.get("href", "") if title_el else ""
    job_url = href if href.startswith("http") else f"https://jobbkk.com{href}" if href else ""

    if not job_url:
        company_id = card.get("data-com-id", "")
        job_id = card.get("data-job-id", "")
        if company_id and job_id:
            job_url = f"https://jobbkk.com/jobs/detailurgent/{company_id}/{job_id}"

    raw_text = clean_text(card.get_text("\n", strip=True))
    if not salary:
        salary = extract_salary(raw_text)
    if not posted_date and updated_el:
        posted_date = clean_text(updated_el.get_text(" ", strip=True))

    province_name = guess_province_name(location)

    return {
        "keyword": keyword,
        "province_code": "",
        "province_name": province_name,
        "page": page_num,
        "job_title": title,
        "company": company,
        "location": location,
        "salary": salary,
        "posted_date": posted_date,
        "job_url": job_url,
        "raw_text": raw_text,
    }

def collect_list_items_text(container) -> str:
    if container is None:
        return ""
    items = [clean_text(li.get_text(" ", strip=True)) for li in container.select("li")]
    items = [item for item in items if item]
    if items:
        return "\n".join(items)
    return clean_text(container.get_text("\n", strip=True))

def find_section_by_heading(root, heading_pattern: str):
    heading_regex = re.compile(heading_pattern)
    heading = root.find(
        lambda tag: tag.name in ["p", "span", "h2", "h3", "strong"]
        and heading_regex.search(clean_text(tag.get_text(" ", strip=True)))
    )
    if not heading:
        return None

    for container in [heading.find_parent("section"), heading.find_parent("div")]:
        if container and container.select("li"):
            return container

    next_ul = heading.find_next("ul")
    if next_ul:
        return next_ul

    return heading.find_parent("section") or heading.find_parent("div")

def extract_jobbkk_detail(job_url: str, headers: dict) -> dict:
    base_detail = {
        "job_detail_full_text": "",
        "matched_skills": "",
        "matched_skill_count": 0,
        **{column: 0 for column in SKILL_COLUMNS},
    }

    try:
        response = requests.get(job_url, headers=headers, timeout=30)
        response.raise_for_status()
    except Exception:
        return base_detail

    soup = BeautifulSoup(response.text, "html.parser")

    detail_root = soup.select_one("article.row") or soup
    job_detail_full_text = clean_text(detail_root.get_text("\n", strip=True))

    skill_info = extract_skills(job_detail_full_text)

    return {
        "job_detail_full_text": job_detail_full_text,
        **skill_info,
    }

def scrape_job_jobbkk(
    search_url: str = "",
    max_pages: int = 50,
    sleep_seconds: float = 0.5,
) -> pd.DataFrame:
    
    collected_frames = []
    try:
        for job in SEARCH_URLS["JOBBKK"]:
            keyword = job[0]
            search_url = job[1]
            keyword_groups = keyword_match_groups_from_query(keyword)

            all_rows = []
            seen_urls = set()

            print(f"[Search] Starting JobBKK crawl: max_pages={max_pages}")

            for page_num in range(1, max_pages + 1):
                page_url = update_page_in_search_url(search_url, page_num)
                print(f"[Search] Page {page_num}/{max_pages} -> request")

                response = requests.get(page_url, headers=headers, timeout=30)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.select("div.joblist-pos.jobbkk-list-company")
                print(f"[Search] Page {page_num}/{max_pages} -> found cards: {len(cards)}")

                if not cards:
                    print(f"[Search] Page {page_num}/{max_pages} -> no cards, stopping")
                    break

                page_rows = []
                for card in cards:
                    row = parse_jobbkk_card(card, page_num=page_num, keyword=keyword)

                    if not row["job_title"] or not row["job_url"]:
                        continue
                    if not title_matches_keyword(row["job_title"], keyword_groups):
                        continue
                    if row["job_url"] in seen_urls:
                        continue

                    seen_urls.add(row["job_url"])
                    page_rows.append(row)

                if not page_rows:
                    print(f"[Search] Page {page_num}/{max_pages} -> no keyword matches, stopping")
                    break

                all_rows.extend(page_rows)
                print(f"[Search] Page {page_num}/{max_pages} -> kept {len(page_rows)} | cumulative={len(all_rows)}")

                if sleep_seconds > 0:
                    time.sleep(sleep_seconds)

            total_details = len(all_rows)
            print(f"[Detail] Starting detail extraction for {total_details} jobs")

            for index, row in enumerate(all_rows, start=1):
                detail_info = extract_jobbkk_detail(row["job_url"], headers=headers)
                row.update(detail_info)

                if total_details <= 50 or index % 10 == 0 or index == total_details:
                    percent = (index / total_details) * 100 if total_details else 100
                    print(f"[Detail] {index}/{total_details} ({percent:.1f}%)")

                if sleep_seconds > 0:
                    time.sleep(sleep_seconds)

            job_df = pd.DataFrame(all_rows)

            if job_df.empty:
                continue

            job_df["domain"] = "JOBBKK"
            job_df["min_salary"] = None
            job_df["max_salary"] = None            

            ordered_cols = [
            "domain",
            "keyword",
            "province_name",
            "job_title",
            "company",
            "location",
            "salary",
            "min_salary",
            "max_salary",
            "posted_date",
            "job_url",
            "matched_skills",
            "matched_skill_count",
            *SKILL_COLUMNS,
            ]

            for column in ordered_cols:
                if column not in job_df.columns:
                    job_df[column] = "" if column not in {"matched_skill_count", *SKILL_COLUMNS} else 0

            job_df = job_df[ordered_cols].drop_duplicates(subset=["job_url"])
            collected_frames.append(job_df)
            print(f"[Done] Collected {len(job_df)} rows for '{keyword}' job search in JobBKK")
    except Exception as e:
        print(f"Error occurred on JobBKK scraping: {e}")
        print("Skipping JobBKK and returning collected data so far.")
    
    if not collected_frames:
        return pd.DataFrame()
    
    final_df = pd.concat(collected_frames, ignore_index=True)
    final_df = final_df.drop_duplicates(subset=["job_url"])
    
    return final_df

# %% [markdown]
# ## JOBBKK Scraper Run

# %%
jobbkk_scraped_df = scrape_job_jobbkk(SEARCH_URLS)

# %% [markdown]
# ## JOBBKK Clean Function

# %%
def clean_jobbkk_data(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()

    salary_parts = out["salary"].fillna("").astype(str).str.extract(
        r"(?P<min>\d{1,3}(?:,\d{3})*)\s*[-–]\s*(?P<max>\d{1,3}(?:,\d{3})*)\s*บาท?",
        expand=True,
    )
    out["min_salary"] = salary_parts["min"].fillna("").str.replace(",", "", regex=False)
    out["max_salary"] = salary_parts["max"].fillna("").str.replace(",", "", regex=False)

    parsed_dates = pd.to_datetime(
        out["posted_date"].fillna("").astype(str),
        format="%d/%m/%Y %H:%M",
        errors="coerce",
    )
    out["posted_date"] = parsed_dates.dt.strftime("%m/%d/%Y").fillna("")

    return out

# %% [markdown]
# ## JOBBKK Clean & Export Run

# %%
jobbkk_scraped_df = clean_jobbkk_data(jobbkk_scraped_df)
jobbkk_scraped_df.to_csv(SCRAPED_EACH_DIR / "jobbkk_jobs.csv", index=False, encoding="utf-8-sig")

# %% [markdown]
# ## Final output run (Concat all domain data)

# %%
csv_files = sorted(SCRAPED_EACH_DIR.glob("*.csv"))

if not csv_files:
    print(f"No CSV files found in: {SCRAPED_EACH_DIR.resolve()}")
    job_all_df = pd.DataFrame()
else:
    dataframes = []

    for file in csv_files:
        if file.stat().st_size > 0:   # check file size
            try:
                df = pd.read_csv(file)
                if not df.empty:
                    dataframes.append(df)
                else:
                    print(f"{file.name} has header but no rows.")
            except Exception as e:
                print(f"Error reading {file.name}: {e}")
        else:
            print(f"{file.name} is empty (0 bytes). Skipping.")   

    if dataframes:
        job_all_df = pd.concat(dataframes, ignore_index=True)
    else:
        job_all_df = pd.DataFrame()

    output_static = SCRAPED_ALL_DIR / "jobs_all_scraped.csv"
    output_timestamped = SCRAPED_ALL_DIR / f"jobs_all_scraped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    job_all_df.to_csv(output_static, index=False, encoding="utf-8-sig")
    job_all_df.to_csv(output_timestamped, index=False, encoding="utf-8-sig")

    print(f"Concatenated {len(csv_files)} files -> {len(job_all_df)} rows")


