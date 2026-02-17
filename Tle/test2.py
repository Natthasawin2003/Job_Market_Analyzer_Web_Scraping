import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

# ================= SIDEBAR =================
st.sidebar.title("FILTER")

keyword = st.sidebar.text_input("Search job")

province = st.sidebar.selectbox(
    "Province",
    ["All","Bangkok","Chiang Mai","Remote"]
)

salary = st.sidebar.slider("Min salary",0,100000,0)

date_range = st.sidebar.date_input(
    "Posted date range",
    value=None
)

# ================= LOAD DATA =================
# ⭐ เปลี่ยนตรงนี้เป็น read_csv ของคุณได้

np.random.seed(1)

df = pd.DataFrame({
    "title":["Data Analyst","Data Scientist","BI Analyst","ML Engineer"]*30,
    "company":["ABC","XYZ","DATA","TECH"]*30,
    "province":np.random.choice(["Bangkok","Remote","Chiang Mai"],120),
    "salary":np.random.randint(18000,60000,120),

    # ⭐ สำคัญ: ต้องเป็น datetime
    "posted_date": pd.to_datetime("2025-01-01") +
                   pd.to_timedelta(np.random.randint(0,60,120), unit="D"),

    "link":["https://example.com/job"]*120,

    "description":[
        "Analyze business data and create reports"
    ]*120
})

# ================= FILTER =================

if keyword:
    df = df[df["title"].str.contains(keyword, case=False, na=False)]

if province!="All":
    df = df[df["province"]==province]

df = df[df["salary"]>=salary]

# DATE FILTER
if date_range and len(date_range)==2:
    start,end = pd.to_datetime(date_range[0]),pd.to_datetime(date_range[1])
    df = df[(df["posted_date"]>=start)&(df["posted_date"]<=end)]

# ================= TITLE =================

st.title("📊 Job Market Dashboard")

# ================= KPI =================

c1,c2,c3,c4 = st.columns(4)

c1.metric("Total Jobs", len(df))

c2.metric(
    "Avg Salary",
    int(df["salary"].mean()) if len(df)>0 else 0
)

c3.metric(
    "Companies",
    df["company"].nunique()
)

c4.metric(
    "Max Salary",
    df["salary"].max() if len(df)>0 else 0
)

# ================= BIG GRAPH + SIDE =================

big,side = st.columns([3,1])

with big:
    st.subheader("Salary Distribution")
    if len(df)>0:
        st.bar_chart(df["salary"])

with side:
    st.subheader("Province count")
    st.write(df["province"].value_counts())

# ================= TWO GRAPHS =================

g1,g2 = st.columns(2)

with g1:
    st.subheader("Jobs per company")
    st.bar_chart(df["company"].value_counts())

with g2:
    st.subheader("Jobs by posted date")
    if len(df)>0:
        trend = df.groupby("posted_date").size()
        st.line_chart(trend)

# ================= TABLE =================

st.subheader("Job Table")

# ⭐ ทำ link คลิกได้
df_display = df.copy()

df_display["link"] = df_display["link"].apply(
    lambda x: f'<a href="{x}" target="_blank">Open job</a>'
)

# ⭐ เรียงวันที่ใหม่สุดก่อน
df_display = df_display.sort_values("posted_date", ascending=False)

# ⭐ แสดง table
st.write(
    df_display.to_html(escape=False,index=False),
    unsafe_allow_html=True
)