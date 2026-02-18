import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

st.set_page_config(layout="wide")

# ---------------- SIDEBAR ----------------
st.sidebar.title("FILTER")

keyword = st.sidebar.text_input("Search job")

salary = st.sidebar.slider("Min salary",0,100000,0)

date_range = st.sidebar.date_input(
    "Posted date range",
    value=()   # ปล่อยว่างก่อน (สำคัญ)
)

# ---------------- LOAD DATA ----------------
# 👉 เปลี่ยน path เป็น CSV จริงของคุณ
# df = pd.read_csv("yourfile.csv")

# DEMO structure (ลบทิ้งได้)
np.random.seed(1)
df = pd.DataFrame({
    "title":["Data Analyst","Data Scientist","BI Analyst","ML Engineer"]*30,
    "company":["ABC","XYZ","DATA","TECH"]*30,
    "province":np.random.choice(["Bangkok","Remote","Chiang Mai"],120),
    "salary":np.random.randint(18000,60000,120),
    "web":np.random.choice(["Jobsdb","Jobbkk","Jobthai"],120),
    "posted_date":pd.date_range("2026-01-01",periods=120),
    "link":["https://example.com"]*120,
    "description":["Example job"]*120
})

# แปลงวันที่ (จำเป็นมาก)
df["posted_date"] = pd.to_datetime(df["posted_date"],errors="coerce")

# เติม province dropdown จากข้อมูลจริง
province_list = ["All"] + sorted(df["province"].dropna().unique().tolist())
province = st.sidebar.selectbox("Province", province_list)

web_list = ["All"] + sorted(df["web"].dropna().unique().tolist())
web = st.sidebar.selectbox("web", web_list)

# ---------------- FILTER ----------------

if keyword:
    df = df[df["title"].str.contains(keyword, case=False, na=False)]

if province!="All":
    df = df[df["province"]==province]

if web!="All":
    df = df[df["web"]==web]

df = df[df["salary"]>=salary]

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

c1.metric("Total Jobs", len(df))
c2.metric("Avg Salary", int(df["salary"].mean()) if len(df)>0 else 0)
c3.metric("Companies", df["company"].nunique())

if len(df)>0:
    percent = df["salary"].notna().sum()/len(df)*100
else:
    percent = 0

c4.metric("Show Salary", "%.1f %%" % percent)

# ================= MAIN GRAPH AREA =================
big,side = st.columns([3,1])

# ----- SALARY HISTOGRAM PRO -----
with big:
    st.subheader("Salary Range")
    bins=[0,25000,50000,75000,100000,125000,150000,175000,200000,1000000]
    labels=["<25k","25-50k","50-75k","75-100k","100-125k","125-150k","150-175k","175-200k","200k+"]
    temp=df.copy()
    temp["range"]=pd.cut(temp["salary"],bins=bins,labels=labels)
    st.bar_chart(temp["range"].value_counts().sort_index())

# ----- PROVINCE COUNT -----
with side:
    st.subheader("Job per Web")
    st.bar_chart(df["web"].value_counts())

# ================= SECOND ROW =================
g1,g2 = st.columns(2)

# ----- COMPANY GRAPH -----
with g1:
    st.subheader("Top Companies Hiring")
    st.bar_chart(df["company"].value_counts().head(10))

# ----- SALARY BUCKET (IMPORTANT) -----
with g2:
    st.subheader("Jobs by province")
    st.bar_chart(df["province"].value_counts())

# ================= TABLE =================
st.subheader("Job Table")

# clickable link
def make_clickable(url):
    return f'<a target="_blank" href="{url}">open job</a>'

if "link" in df.columns:
    df["link"] = df["link"].apply(make_clickable)

df = df.rename(columns={
    "title":"Job",
    "company":"Company",
    "province":"Location",
    "salary":"Salary",
    "web":"Web",
    "posted_date":"Posted Date",
    "link":"Link"
})

show_cols = [c for c in ["Job","Company","Location","Salary","Web","Posted Date","Link"] if c in df.columns]

st.write(
    df[show_cols].to_html(escape=False,index=False),
    unsafe_allow_html=True
)