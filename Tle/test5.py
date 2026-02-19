import streamlit as st
import pandas as pd
import json
import plotly.express as px
import random

st.title("Thailand Job Heatmap (Mock Data)")

# -----------------
# 1️⃣ MOCK JOB DATA
# -----------------

provinces = [
    "Bangkok","Chiang Mai","Chon Buri","Phuket",
    "Nonthaburi","Pathum Thani","Rayong",
    "Khon Kaen","Songkhla","Nakhon Ratchasima"
]

data = []

for p in provinces:
    for i in range(random.randint(5,40)):
        data.append({
            "company": f"Company_{random.randint(1,100)}",
            "province": p,
            "salary": random.randint(20000,90000)
        })

df = pd.DataFrame(data)

st.write("Mock jobs", df.head())

# -----------------
# 2️⃣ COUNT JOBS / PROVINCE
# -----------------

prov = df["province"].value_counts().reset_index()
prov.columns = ["province","job_count"]

# -----------------
# 3️⃣ LOAD GEOJSON
# -----------------
# ⭐ IMPORTANT: โหลด geojson จังหวัดไทย
# โหลดจาก github แล้วใส่ path

with open("Tle/thailand-provinces.geojson", encoding="utf-8") as f:
    geo = json.load(f)

# -----------------
# 4️⃣ PLOT MAP
# -----------------

fig = px.choropleth(
    prov,
    geojson=geo,
    locations="province",
    featureidkey="properties.name",
    color="job_count",
    color_continuous_scale="Reds"
)

fig.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig, use_container_width=True)
