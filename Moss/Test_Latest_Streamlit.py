import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import plotly.express as px
import json
from pathlib import Path
import re

plt.rcParams["font.family"] = "Tahoma"


def get_latest_scrape_datetime_text(scraped_dir: Path) -> str:
    date_pattern = re.compile(r"(\d{8})(?:_(\d{6}))?")
    latest_dt = None

    for csv_path in scraped_dir.glob("*.csv"):
        match = date_pattern.search(csv_path.stem)
        if not match:
            continue

        date_part = match.group(1)
        time_part = match.group(2) or "000000"

        try:
            current_dt = datetime.datetime.strptime(
                f"{date_part}{time_part}", "%Y%m%d%H%M%S"
            )
        except ValueError:
            continue

        if latest_dt is None or current_dt > latest_dt:
            latest_dt = current_dt

    if latest_dt is None:
        return "Latest update: N/A"

    return f"Latest update: {latest_dt:%Y-%m-%d %H:%M}"

st.set_page_config(layout="wide")

st.markdown("""
<style>
            
.chart-card{
    background:#eef2ff;
    padding:18px;
    border-radius:14px;
    box-shadow:0 6px 18px rgba(15,23,42,0.08);
    margin-bottom:12px;
}
            
/* main background */
.stApp {
    background-color: #f8fafc;
}

/* sidebar */
[data-testid="stSidebar"]{
    background-color:#e2e8f0;
}

[data-testid="stMetric"]{
    background:#ffffff;
    padding:18px;
    border-radius:14px;
    box-shadow:0 6px 18px rgba(15,23,42,0.08);
    border:1px solid #e2e8f0;
}

h1, h2, h3 {
    color:#1e293b;
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

def reset_filters():
    st.session_state["keyword_filter"] = ""
    st.session_state["use_salary_filter"] = False
    st.session_state["min_salary_filter"] = 0
    st.session_state["date_range_filter"] = ()
    st.session_state["top_skill_n_filter"] = 12
    st.session_state["province_filter"] = "All"
    st.session_state["web_filter"] = "All"


st.sidebar.button(
    "Reset Filters",
    use_container_width=True,
    on_click=reset_filters,
)

keyword = st.sidebar.text_input("Search job", key="keyword_filter")

use_salary = st.sidebar.checkbox("Filter by salary", key="use_salary_filter")
if use_salary :
    salary = st.sidebar.number_input(
        "Min salary",
        min_value=0,
        value=0,
        step=5000,
        key="min_salary_filter",
    )

date_range = st.sidebar.date_input(
    "Posted date range",
    value=(),
    key="date_range_filter",
)

# ตัวดึงข้อมูลจากไฟล์ CSV
df = pd.read_csv("Moss\Scraped_All\jobs_all_scraped.csv")

df["mid_salary"] = df[["min_salary","max_salary"]].mean(axis=1)
df_all = df.copy()

df["posted_date"] = pd.to_datetime(df["posted_date"],errors="coerce")

skill_cols_all = [c for c in df.columns if c.startswith("skill_")]
skill_slider_max = max(5, len(skill_cols_all))

if "top_skill_n_filter" in st.session_state:
    st.session_state["top_skill_n_filter"] = max(
        5,
        min(st.session_state["top_skill_n_filter"], skill_slider_max)
    )

top_skill_n = st.sidebar.slider(
    "Top skills in treemap",
    min_value=5,
    max_value=skill_slider_max,
    value=min(12, skill_slider_max),
    step=1,
    key="top_skill_n_filter",
)

province_list = ["All"] + sorted(df["province_name"].dropna().unique().tolist())
province = st.sidebar.selectbox("Province", province_list, key="province_filter")

web_list = ["All"] + sorted(df["domain"].dropna().unique().tolist())
web = st.sidebar.selectbox("Website", web_list, key="web_filter")

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

latest_update_text = get_latest_scrape_datetime_text(Path("Moss/Scraped_All"))

#กราฟ 1
st.title(
    "Job Market Dashboard\n"
    "(Data Science & Data Engineer & Data Analyst)\n"
    f"{latest_update_text}"
)
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

if df_show.empty:
    st.warning("No jobs found for the current filters.")

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
    if counts.sum() > 0:
        st.bar_chart(counts, color="#4f46e5", height=420)
    else:
        st.info("No salary data for current filters")


#กราฟวงกลม
with f2:
    st.subheader("Job Per Web")

    web_keyword = df_show[["domain", "keyword"]].dropna().copy()

    if len(web_keyword) > 0:
        web_keyword.columns = ["Website", "Keyword"]
        web_keyword["Keyword"] = web_keyword["Keyword"].astype(str).str.strip()

        top_keywords = web_keyword["Keyword"].value_counts().head(8).index
        web_keyword["Keyword"] = np.where(
            web_keyword["Keyword"].isin(top_keywords),
            web_keyword["Keyword"],
            "Other"
        )

        web_keyword_counts = (
            web_keyword.groupby(["Website", "Keyword"], as_index=False)
            .size()
            .rename(columns={"size": "Jobs"})
        )

        fig_web = px.sunburst(
            web_keyword_counts,
            path=["Website", "Keyword"],
            values="Jobs",
            color="Website",
            color_discrete_sequence=["#4338ca", "#6366f1", "#818cf8", "#a5b4fc"],
            template="plotly_white",
        )

        fig_web.update_traces(
            textinfo="label+percent parent",
            marker_line_width=1,
            marker_line_color="#f8fafc",
            hovertemplate="<b>%{label}</b><br>Jobs: %{value:,}<br>Share in parent: %{percentParent:.1%}<extra></extra>",
        )

        fig_web.update_layout(
            height=420,
            margin=dict(l=0, r=0, t=8, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(
            fig_web,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "displaylogo": False,
                "scrollZoom": False,
            },
        )
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
    salary_role = salary_role.dropna()
    salary_role.index.name = "ตำแหน่ง"
    if len(salary_role) > 0:
        st.bar_chart(salary_role, color="#0f766e", height=420)
    else:
        st.info("No position salary data for current filters")


#graph3
g1,g2 = st.columns([1.2,1.8])
with g1:
    st.subheader("Job Per Province")
    max_val = province_counts["jobs"].quantile(0.95)
    max_val = float(max(max_val, 1))

    fig = px.choropleth(
        province_counts,
        geojson=geo,
        locations="province",
        featureidkey="properties.name",
        color="jobs",
        color_continuous_scale="PuBu",
        range_color=(0, max_val),
        labels={"jobs": "Jobs"},
        template="plotly_white",
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator",
        center={"lat": 15.5, "lon": 101.0},
        projection_scale=6.2,
        bgcolor="rgba(0,0,0,0)",
    )

    fig.update_traces(
        marker_line_width=1.4,
        marker_line_color="#475569",
        hovertemplate="<b>%{location}</b><br>Jobs: %{z:,.0f}<extra></extra>",
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=8, b=0),
        height=620,
        dragmode=False,
        coloraxis_colorbar=dict(
            title="Jobs",
            thickness=14,
            len=0.62,
            y=0.5,
            x=1.01,
            nticks=3,
            bgcolor="rgba(255,255,255,0.8)",
        ),
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": False,
            "modeBarButtonsToRemove": ["zoomInGeo", "zoomOutGeo", "resetGeo"],
        },
    )

with g2:
    st.subheader("Job Skill")
    skill_cols = [c for c in df_show.columns if c.startswith("skill_")]

    if len(skill_cols) == 0:
        st.info("No skill columns found")
    else:
        skill_counts = df_show[skill_cols].sum().sort_values(ascending=False)
        skill_counts = skill_counts[skill_counts > 0]

        if len(skill_counts) > top_skill_n:
            skill_counts = skill_counts.head(top_skill_n)

        if len(skill_counts) == 0:
            st.info("No skill data for current filters")
        else:
            nice = {
                "python":"Python",
                "sql & database":"SQL & Database",
                "c++":"C++",
                "mongodb":"MongoDB",
                "aws":"AWS",
                "etl":"ETL",
                "gcp":"GCP",
            }

            def format_skill_name(skill_name):
                cleaned = (
                    str(skill_name)
                    .replace("skill_", "")
                    .replace("_", " ")
                    .lower()
                )
                return nice.get(cleaned, cleaned.capitalize())

            skill_counts.index = [format_skill_name(name) for name in skill_counts.index]
            skill_df = skill_counts.reset_index()
            skill_df.columns = ["Skill","Count"]

            fig2 = px.treemap(
                skill_df,
                path=["Skill"],
                values="Count",
                color="Count",
                color_continuous_scale="PuBuGn",
                template="plotly_white",
            )

            fig2.update_traces(
                hovertemplate="<b>%{label}</b><br>จำนวน: %{value} คน<extra></extra>",
                marker_line_width=1,
                marker_line_color="#f8fafc",
                textfont_size=14,
            )

            fig2.update_layout(
                height=620,
                margin=dict(l=0, r=0, t=8, b=0),
                coloraxis_showscale=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )

            st.plotly_chart(
                fig2,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "displaylogo": False,
                    "scrollZoom": False,
                },
            )

# ================= TABLE =================
st.subheader("Job Table")

# แสดงตัวเลข
#for i, v in enumerate(skill_counts):
#    ax.text(v + 1, i, str(int(v)), va="center")
#
#ax.set_xlabel("Number of Jobs")
#ax.set_ylabel("")
#st.pyplot(fig)

# prepare url for clickable table column
if "job_url" in df.columns:
    df_show["job_url"] = df_show["job_url"].fillna("").astype(str)

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

table_df = df_show[show_cols].copy()

if "Posted Date" in table_df.columns:
    posted_dt = pd.to_datetime(table_df["Posted Date"], errors="coerce")
    table_df = (
        table_df.assign(_posted_sort=posted_dt)
        .sort_values("_posted_sort", ascending=False)
        .drop(columns=["_posted_sort"])
    )
    table_df["Posted Date"] = pd.to_datetime(
        table_df["Posted Date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

download_name = f"filtered_jobs_{datetime.datetime.now():%Y%m%d_%H%M%S}.csv"
st.download_button(
    "Download filtered data (CSV)",
    data=table_df.to_csv(index=False).encode("utf-8-sig"),
    file_name=download_name,
    mime="text/csv",
)

column_config = {}
if "Link" in table_df.columns:
    column_config["Link"] = st.column_config.LinkColumn(
        "Link",
        display_text="open job"
    )

if table_df.empty:
    st.info("No rows to show for current filters")
else:
    st.dataframe(
        table_df,
        use_container_width=True,
        height=420,
        hide_index=True,
        column_config=column_config,
    )