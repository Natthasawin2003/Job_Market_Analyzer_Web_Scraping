import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import plotly.express as px

plt.rcParams["font.family"] = "Tahoma"

st.set_page_config(layout="wide")

# ---------------- SIDEBAR ----------------
st.sidebar.title("FILTER")

keyword = st.sidebar.text_input("Search job")

use_salary = st.sidebar.checkbox("Filter by salary")
if use_salary :
    salary = st.sidebar.number_input(
        "Min salary",
        min_value=0,
        value=0,
        step=5000
    )

date_range = st.sidebar.date_input(
    "Posted date range",
    value=()   # ปล่อยว่างก่อน (สำคัญ)
)

# ---------------- LOAD DATA ----------------
# 👉 เปลี่ยน path เป็น CSV จริงของคุณ
df = pd.read_csv("Moss/Scraped_All/jobs_all_scraped.csv")

df["mid_salary"] = df[["min_salary","max_salary"]].mean(axis=1)
df_all = df.copy()

# DEMO structure (ลบทิ้งได้)
#np.random.seed(1)
#df = pd.DataFrame({
#    "title":["Data Analyst","Data Scientist","BI Analyst","ML Engineer"]*30,
#    "company":["ABC","XYZ","DATA","TECH"]*30,
#    "province":np.random.choice(["Bangkok","Remote","Chiang Mai"],120),
#    "salary":np.random.randint(18000,60000,120),
#    "web":np.random.choice(["Jobsdb","Jobbkk","Jobthai"],120),
#    "posted_date":pd.date_range("2026-01-01",periods=120),
#    "link":["https://example.com"]*120,
#    "description":["Example job"]*120
#})

# แปลงวันที่ (จำเป็นมาก)
df["posted_date"] = pd.to_datetime(df["posted_date"],errors="coerce")

# เติม province dropdown จากข้อมูลจริง
province_list = ["All"] + sorted(df["province_name"].dropna().unique().tolist())
province = st.sidebar.selectbox("province_name", province_list)

web_list = ["All"] + sorted(df["domain"].dropna().unique().tolist())
web = st.sidebar.selectbox("domain", web_list)

# ---------------- FILTER ----------------

if keyword:
    df = df[df["keyword"].str.contains(keyword, case=False, na=False)]

if province!="All":
    df = df[df["province_name"]==province]

if web!="All":
    df = df[df["domain"]==web]

if use_salary:
    df = df[(df["max_salary"].isna()) | 
        (df["max_salary"] >= salary)
    ]
    df_show = df[
        (df["max_salary"].notna()) &
        (df["max_salary"] >= salary)
    ]
else:
    df_show = df.copy()
    


# DATE FILTER (version กันพัง 100%)
if isinstance(date_range, tuple):
    if len(date_range)==2:
        start,end = pd.to_datetime(date_range[0]),pd.to_datetime(date_range[1])
        df = df[(df["posted_date"]>=start)&(df["posted_date"]<=end)]

elif isinstance(date_range, datetime.date):
    start = pd.to_datetime(date_range)
    df = df[df["posted_date"]>=start]
# ================= TITLE =================
st.title("📊 Job Market Dashboard")

# ================= KPI =================
c1,c2,c3,c4 = st.columns(4)

c1.metric("Total Jobs", len(df_show))
c2.metric("Avg Salary", int(df_show["mid_salary"].mean(skipna=True)) 
    if pd.notna(df["mid_salary"].mean(skipna=True)) else 0
)
c3.metric("Companies", df_show["company"].nunique())

if len(df)>0:
    percent = df_show["mid_salary"].notna().sum()/len(df)*100
else:
    percent = 0

c4.metric("Show Salary", "%.1f %%" % percent)

# ================= MAIN GRAPH AREA =================
big,side = st.columns([3,1])

# ----- SALARY HISTOGRAM PRO -----
with big:
    st.subheader("Salary Range")
    bins=[0,25000,50000,75000,100000,125000,150000,1000000]
    labels=["<25k","25-50k","50-75k","75-100k","100-125k","125-150k","150k+"]
    temp=df.copy()
    temp["range"]=pd.cut(temp["mid_salary"],bins=bins,labels=labels)
    st.bar_chart(temp["range"].value_counts().sort_index())

# ----- PROVINCE COUNT -----
with side:
    st.subheader("Job per Web")

    web_counts = df_show["domain"].value_counts()

    if len(web_counts) > 0:
        fig, ax = plt.subplots()

        ax.pie(
            web_counts,
            labels=web_counts.index,
            autopct=lambda p: f'{p:.1f}%\n({int(round(p/100*web_counts.sum()))})'
        )

        ax.axis("equal")   # ทำให้วงกลมไม่เบี้ยว
        st.pyplot(fig)
    else:
        st.write("No data")
# ================= SECOND ROW =================
g1,g2 = st.columns([2.5,1])

# ----- COMPANY GRAPH -----
with g1:
    st.subheader("Job Skill")
    skill_cols = [c for c in df_show.columns if c.startswith("skill_")]

    skill_counts = df_show[skill_cols].sum().sort_values(ascending=True)

    nice = {
        "python":"Python",
        "sql & database":"SQL & Database",
        "c++":"C++",
        "mongodb":"MongoDB",
        "aws":"AWS",
        "etl":"ETL",
        "gcp":"GCP",
    }

    skill_counts.index = (
        skill_counts.index
        .str.replace("skill_","",regex=False)
        .str.replace("_"," ")
        .str.lower()
        .map(lambda x: nice.get(x,x.capitalize()))
    )
    skill_df = skill_counts.reset_index()
    skill_df.columns = ["Skill","Count"]

    fig2 = px.treemap(
        skill_df,
        path=["Skill"],
        values="Count"
    )

    fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>จำนวน: %{value} คน<extra></extra>"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ----- SALARY BUCKET (IMPORTANT) -----
with g2:
    st.subheader("Jobs by province")
    counts = df_show["province_name"].value_counts()
    top = counts.head(6)
    others = counts.iloc[6:].sum()
    if others > 0:
        top["จังหวัดอื่นๆ"] = others
    top = top.sort_values()
    fig, ax = plt.subplots(figsize=(6,6))
    top.plot.barh(ax=ax)
    ax.set_ylabel("")   
    st.pyplot(fig)

h1,h2 = st.columns(2)

with h1:
    salary_role = (
    df_show.groupby("keyword")["mid_salary"]
    .mean()
    .sort_values()
    .tail(15)
    )
    st.bar_chart(salary_role)

with h2:
    skill_cols=[c for c in df_show.columns if c.startswith("skill_")]
    skill_salary={}
    for s in skill_cols:
        avg=df_show[df_show[s]==1]["mid_salary"].mean()
        if pd.notna(avg):
            skill_salary[s.replace("skill_","")]=avg
    skill_salary=pd.Series(skill_salary).sort_values()
    st.bar_chart(skill_salary)


# ================= TABLE =================
st.subheader("Job Table")

# แสดงตัวเลข
#for i, v in enumerate(skill_counts):
#    ax.text(v + 1, i, str(int(v)), va="center")
#
#ax.set_xlabel("Number of Jobs")
#ax.set_ylabel("")
#st.pyplot(fig)

# clickable link
def make_clickable(url):
    return f'<a target="_blank" href="{url}">open job</a>'

if "job_url" in df.columns:
    df_show["job_url"] = df_show["job_url"].apply(make_clickable)

#df = df.rename(columns={
#    "title":"Job",
#    "company":"Company",
#    "province":"Location",
#    "salary":"Salary",
#    "web":"Web",
 #   "posted_date":"Posted Date",
 #   "link":"Link"
#})

show_cols = [c for c in [
        "domain",
        "keyword",
        "province_name",
        "company",
        "posted_date",
        "matched_skill_count",
        "job_url"
    ] 
    if c in df.columns
]

st.write(
    df_show[show_cols].to_html(escape=False,index=False),
    unsafe_allow_html=True
)