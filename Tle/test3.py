import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ================= LOAD DATA =================
#df = pd.read_csv("yourfile.csv")
np.random.seed(1)
df = pd.DataFrame({
    "title":["Data Analyst","Data Scientist","BI Analyst","ML Engineer"]*30,
    "company":["ABC","XYZ","DATA","TECH"]*30,
    "province":np.random.choice(["Bangkok","Remote","Chiang Mai"],120),
    "salary":np.random.randint(18000,60000,120),
    "posted_date":pd.date_range("2026-01-01",periods=120),
    "link":["https://example.com"]*120,
    "description":["Example job"]*120
})

# ===== แปลง posted date =====
if "posted_date" in df.columns:
    df["posted_date"] = pd.to_datetime(df["posted_date"], errors="coerce")

# ================= SIDEBAR =================
st.sidebar.title("FILTER")

keyword = st.sidebar.text_input("Search job")

province = st.sidebar.selectbox(
    "Province",
    ["All"] + sorted(df["province"].dropna().unique().tolist())
)

min_salary = st.sidebar.slider("Min salary",0,100000,0)

date_range = st.sidebar.date_input("Posted date range")

# ================= FILTER =================
if keyword:
    df = df[df["title"].str.contains(keyword,case=False,na=False)]

if province!="All":
    df = df[df["province"]==province]

df = df[df["salary"]>=min_salary]

# ----- DATE FILTER FIX -----
if isinstance(date_range, tuple) and len(date_range)==2:
    start,end = date_range
    df = df[
        (df["posted_date"]>=pd.to_datetime(start)) &
        (df["posted_date"]<=pd.to_datetime(end))
    ]

# ================= TITLE =================
st.title("📊 Job Market Dashboard")

# ================= KPI =================
c1,c2,c3,c4 = st.columns(4)

c1.metric("Total Jobs", len(df))
c2.metric("Avg Salary", int(df["salary"].mean()) if len(df)>0 else 0)
c3.metric("Companies", df["company"].nunique())
c4.metric("Max Salary", df["salary"].max() if len(df)>0 else 0)

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
    st.subheader("Jobs per Province")
    st.bar_chart(df["province"].value_counts())

# ================= SECOND ROW =================
g1,g2 = st.columns(2)

# ----- COMPANY GRAPH -----
with g1:
    st.subheader("Top Companies Hiring")
    st.bar_chart(df["company"].value_counts().head(10))

# ----- SALARY BUCKET (IMPORTANT) -----
with g2:
    st.subheader("Salary Range")

    bins=[0,20000,30000,40000,50000,60000,100000]
    labels=["<20k","20-30k","30-40k","40-50k","50-60k","60k+"]

    temp=df.copy()
    temp["range"]=pd.cut(temp["salary"],bins=bins,labels=labels)

    st.bar_chart(temp["range"].value_counts().sort_index())

# ================= TABLE =================
st.subheader("Job Table")

# clickable link
if "link" in df.columns:
    df["link"]=df["link"].apply(lambda x: f"[open]({x})")

st.dataframe(df,use_container_width=True)