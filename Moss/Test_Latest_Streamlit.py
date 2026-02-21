import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import plotly.express as px
import json

plt.rcParams["font.family"] = "Tahoma"

st.set_page_config(layout="wide")

st.markdown("""
<style>
            
.chart-card{
    background:#b3e5fc;
    padding:18px;
    border-radius:14px;
    box-shadow:0 4px 14px rgba(0,0,0,0.08);
    margin-bottom:12px;
}
            
/* main background */
.stApp {
    background-color: #e1f5fe;
}

/* sidebar */
[data-testid="stSidebar"]{
    background-color:#81d4fa;
}

[data-testid="stMetric"]{
    background:#b3e5fc;
    padding:18px;
    border-radius:14px;
    box-shadow:0 4px 14px rgba(0,0,0,0.08);
}

/* hover animation */
[data-testid="stMetric"]:hover{
    transform:translateY(-4px);
    transition:0.2s;
}

/* spacing */
.block-container{
    padding-top:2rem;
}

</style>
""", unsafe_allow_html=True)

#ฟิวเตอร์
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
    value=()
)

# ตัวดึงข้อมูลจากไฟล์ CSV
df = pd.read_csv("G:\\Users\\Moss\\Documents\\PYTHON_PROJECT\\Job_Market_Analyzer_Web_Scraping\\Moss\\Scraped_All\\jobs_all_scraped.csv")

df["mid_salary"] = df[["min_salary","max_salary"]].mean(axis=1)
df_all = df.copy()

df["posted_date"] = pd.to_datetime(df["posted_date"],errors="coerce")

province_list = ["All"] + sorted(df["province_name"].dropna().unique().tolist())
province = st.sidebar.selectbox("Province", province_list)

web_list = ["All"] + sorted(df["domain"].dropna().unique().tolist())
web = st.sidebar.selectbox("Website", web_list)

#ฟิวเตอร์เหมือนกันแค่ แค่นำข้อมูลมาใช้ด้วย
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

#เปลี่่ยนชื่อจังหวัดเป็นอังกฤษ
THAI_TO_ENGLISH_PROVINCE = {
	"กระบี่": "Krabi",
	"กรุงเทพมหานคร": "Bangkok Metropolis",
	"กรุงเทพฯ": "Bangkok Metropolis",
	"กาญจนบุรี": "Kanchanaburi",
	"กาฬสินธุ์": "Kalasin",
	"กำแพงเพชร": "Kamphaeng Phet",
	"ขอนแก่น": "Khon Kaen",
	"จันทบุรี": "Chanthaburi",
	"ฉะเชิงเทรา": "Chachoengsao",
	"ชลบุรี": "Chon Buri",
	"ชัยนาท": "Chai Nat",
	"ชัยภูมิ": "Chaiyaphum",
	"ชุมพร": "Chumphon",
	"เชียงราย": "Chiang Rai",
	"เชียงใหม่": "Chiang Mai",
	"ตรัง": "Trang",
	"ตราด": "Trat",
	"ตาก": "Tak",
	"นครนายก": "Nakhon Nayok",
	"นครปฐม": "Nakhon Pathom",
	"นครพนม": "Nakhon Phanom",
	"นครราชสีมา": "Nakhon Ratchasima",
	"นครศรีธรรมราช": "Nakhon Si Thammarat",
	"นครสวรรค์": "Nakhon Sawan",
	"นนทบุรี": "Nonthaburi",
	"นราธิวาส": "Narathiwat",
	"น่าน": "Nan",
	"บึงกาฬ": "Bueng Kan",
	"บุรีรัมย์": "Buri Ram",
	"ปทุมธานี": "Pathum Thani",
	"ประจวบคีรีขันธ์": "Prachuap Khiri Khan",
	"ปราจีนบุรี": "Prachin Buri",
	"ปัตตานี": "Pattani",
	"พระนครศรีอยุธยา": "Phra Nakhon Si Ayutthaya",
	"พะเยา": "Phayao",
	"พังงา": "Phangnga",
	"พัทลุง": "Phatthalung",
	"พิจิตร": "Phichit",
	"พิษณุโลก": "Phitsanulok",
	"เพชรบุรี": "Phetchaburi",
	"เพชรบูรณ์": "Phetchabun",
	"แพร่": "Phrae",
	"ภูเก็ต": "Phuket",
	"มหาสารคาม": "Maha Sarakham",
	"มุกดาหาร": "Mukdahan",
	"แม่ฮ่องสอน": "Mae Hong Son",
	"ยโสธร": "Yasothon",
	"ยะลา": "Yala",
	"ร้อยเอ็ด": "Roi Et",
	"ระนอง": "Ranong",
	"ระยอง": "Rayong",
	"ราชบุรี": "Ratchaburi",
	"ลพบุรี": "Lop Buri",
	"ลำปาง": "Lampang",
	"ลำพูน": "Lamphun",
	"เลย": "Loei",
	"ศรีสะเกษ": "Si Sa Ket",
	"สกลนคร": "Sakon Nakhon",
	"สงขลา": "Songkhla",
	"สตูล": "Satun",
	"สมุทรปราการ": "Samut Prakan",
	"สมุทรสงคราม": "Samut Songkhram",
	"สมุทรสาคร": "Samut Sakhon",
	"สระแก้ว": "Sa Kaeo",
	"สระบุรี": "Saraburi",
	"สิงห์บุรี": "Sing Buri",
	"สุโขทัย": "Sukhothai",
	"สุพรรณบุรี": "Suphan Buri",
	"สุราษฎร์ธานี": "Surat Thani",
	"สุรินทร์": "Surin",
	"หนองคาย": "Nong Khai",
	"หนองบัวลำภู": "Nong Bua Lamphu",
	"อ่างทอง": "Ang Thong",
	"อำนาจเจริญ": "Amnat Charoen",
	"อุดรธานี": "Udon Thani",
	"อุตรดิตถ์": "Uttaradit",
	"อุทัยธานี": "Uthai Thani",
	"อุบลราชธานี": "Ubon Ratchathani",
}

df_show["province_eng"] = (
    df_show["province_name"]
    .map(THAI_TO_ENGLISH_PROVINCE)
    .fillna(df_show["province_name"])
)

#ตัวดึงข้อมูล Heatmapประเทศไทย
with open("Tle/thailand.json",encoding="utf-8") as f:
    geo = json.load(f)

geo_names = [f["properties"]["name"] for f in geo["features"]]

province_counts = (
    df_show["province_eng"]
    .value_counts()
    .rename_axis("province")
    .reset_index(name="jobs")
)

province_counts = (
    pd.DataFrame({"province": geo_names})
    .merge(province_counts, on="province", how="left")
    .fillna(0)
)

province_counts.columns=["province","jobs"]

    


#ฟิวเตอของ date
if isinstance(date_range, tuple):
    if len(date_range)==2:
        start,end = pd.to_datetime(date_range[0]),pd.to_datetime(date_range[1])
        df_show = df_show[(df_show["posted_date"]>=start)&(df_show["posted_date"]<=end)]

elif isinstance(date_range, datetime.date):
    start = pd.to_datetime(date_range)
    df_show = df_show[df_show["posted_date"]>=start]

#กราฟ 1
st.title("📊 Job Market Dashboard") 
c1,c2,c3,c4 = st.columns(4)

#จำนวนงานทั้งหมด
c1.metric("Total Jobs", len(df_show))

#ค่าเฉลี่ยเงินเดือน
avg = df_show["mid_salary"].mean()

c2.metric(
    "Avg Salary",
    f"{int(avg):,}" if pd.notna(avg) else "0"
)

#จำนวนบริษัท
c3.metric("Companies", df_show["company"].nunique())

#จำนวนงานที่บอกเงินเดือน
if len(df_show)>0:
    percent = df_show["mid_salary"].notna().sum()/len(df_show)*100
else:
    percent = 0
c4.metric("Show Salary", "%.1f %%" % percent)

#กราฟ 2
f1,f2,f3 = st.columns([1,1,1])

#กราฟแท่งเงินเดือน
with f1:
    st.subheader("Salary Range")
    bins=[0,25000,50000,75000,100000,125000,150000,1000000]
    labels=["<25k","25-50k","50-75k","75-100k","100-125k","125-150k","150k+"]
    temp=df_show.copy()
    temp["ช่วงเงินเดือน"]=pd.cut(temp["mid_salary"],bins=bins,labels=labels)
    counts = (
    temp["ช่วงเงินเดือน"]
    .value_counts()
    .sort_index()
    .rename("จำนวนงาน")   
    )
    st.bar_chart(counts,color="#2563EB")


#กราฟวงกลม
with f2:
    st.subheader("Job Per Web")

    web_counts = df_show["domain"].value_counts()

    if len(web_counts) > 0:
        fig, ax = plt.subplots()

        ax.pie(
            web_counts,
            labels=web_counts.index,
            autopct=lambda p: f'{p:.1f}%\n({int(round(p/100*web_counts.sum()))})'
        )

        ax.axis("equal")   
        st.pyplot(fig)
    else:
        st.write("No data")

#กราฟแท่งค่าเฉลี่ยเงินเดือนต่อตำแหน่ง
with f3:
    st.subheader("AvG Salary For Each Position.")
    salary_role = (
    df_show.groupby("keyword")["mid_salary"]
    .mean()
    .round()
    .sort_values()
    .tail(15)
    .rename("ค่าเฉลี่ยเงินเดือน")
    )
    salary_role.index.name = "ตำแหน่ง"
    st.bar_chart(salary_role,color="#10B981")


#graph3
g1,g2 = st.columns([1,2])
with g1:
    st.subheader("Job Per Province")
    max_val = province_counts["jobs"].quantile(0.95)

    fig = px.choropleth(
    province_counts,
    geojson=geo,
    locations="province",
    featureidkey="properties.name",   # <-- สำคัญ
    color="jobs",
    color_continuous_scale="Reds",
    range_color=(0,max_val)
)

    fig.update_geos(fitbounds="locations", visible=False)

    fig.update_traces(
    hovertemplate="<b>%{location}</b><br>จำนวนงาน %{z} ตำแหน่ง<extra></extra>"
)

    st.plotly_chart(fig, use_container_width=True)

with g2:
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

df_show = df_show.rename(columns={
    "domain":"Website",
    "job_title":"Job",
    "province_name":"Province",
    "company":"Company",
    "posted_date":"Posted Date",
    "job_url":"Link",
})

show_cols = [c for c in [
        "Website",
        "Job",
        "Province",
        "Company",
        "Posted Date",
        "Link"
    ] 
    if c in df_show.columns
]

st.markdown("""
<style>
table th, table td {
    text-align: left !important;
}
</style>
""", unsafe_allow_html=True)

st.write(
    df_show[show_cols].to_html(escape=False,index=False),
    unsafe_allow_html=True
)