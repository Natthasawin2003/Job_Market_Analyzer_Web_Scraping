from __future__ import annotations

from pathlib import Path
import re
from typing import Iterable

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


st.set_page_config(page_title="Thailand Job Openings Geo Map", layout="wide")


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


def normalize_thai_province(text: str) -> str:
	cleaned = str(text).strip()
	cleaned = re.sub(r"^จังหวัด", "", cleaned)
	cleaned = re.sub(r"^จ\.?", "", cleaned)
	cleaned = re.sub(r"\s+", "", cleaned)
	return cleaned


def find_province_column(df: pd.DataFrame) -> str | None:
	candidates = ["province_name", "province", "จังหวัด"]
	lower_map = {col.lower(): col for col in df.columns}
	for name in candidates:
		if name.lower() in lower_map:
			return lower_map[name.lower()]
	return None


def extract_province_from_location(location: str) -> str | None:
	if not isinstance(location, str):
		return None
	compact = location.replace(" ", "")
	for thai_name in THAI_TO_ENGLISH_PROVINCE:
		if thai_name in compact:
			return thai_name
	return None


@st.cache_data(show_spinner=False)
def load_csvs(paths: tuple[str, ...]) -> pd.DataFrame:
	frames: list[pd.DataFrame] = []
	for p in paths:
		try:
			frames.append(pd.read_csv(p))
		except Exception:
			continue
	if not frames:
		return pd.DataFrame()
	return pd.concat(frames, ignore_index=True)


@st.cache_data(show_spinner=False)
def load_thailand_geojson() -> dict:
	url = "https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json"
	res = requests.get(url, timeout=30)
	res.raise_for_status()
	return res.json()


def to_province_counts(df: pd.DataFrame) -> pd.DataFrame:
	province_col = find_province_column(df)

	if province_col is not None:
		provinces = df[province_col].fillna("").map(normalize_thai_province)
	elif "location" in df.columns:
		provinces = (
			df["location"]
			.fillna("")
			.map(extract_province_from_location)
			.fillna("")
			.map(normalize_thai_province)
		)
	else:
		return pd.DataFrame(columns=["province_th", "province_en", "job_openings"])

	counts = (
		pd.DataFrame({"province_th": provinces})
		.query("province_th != ''")
		.value_counts("province_th")
		.reset_index(name="job_openings")
	)
	counts["province_en"] = counts["province_th"].map(THAI_TO_ENGLISH_PROVINCE)
	return counts


st.title("Thailand Province Job Openings (Geo Map)")
st.caption("Color intensity shows number of job openings in each province.")

base_dir = Path(__file__).resolve().parent
csv_files = sorted(base_dir.glob("*.csv"))

if not csv_files:
	st.warning("No CSV files found in this folder.")
	st.stop()

default_select = [str(p) for p in csv_files[: min(5, len(csv_files))]]
selected_files = st.multiselect(
	"Select CSV files",
	options=[str(p) for p in csv_files],
	default=default_select,
)

if not selected_files:
	st.info("Please select at least one CSV file.")
	st.stop()

raw_df = load_csvs(tuple(selected_files))
if raw_df.empty:
	st.error("Could not read selected files.")
	st.stop()

province_counts = to_province_counts(raw_df)
if province_counts.empty:
	st.error("No province data found. Need a province column or location column.")
	st.stop()

geojson = load_thailand_geojson()
feature_names = {
	f.get("properties", {}).get("name", "")
	for f in geojson.get("features", [])
}

map_df = province_counts.dropna(subset=["province_en"]).copy()
map_df = map_df[map_df["province_en"].isin(feature_names)]

left, right = st.columns([2, 1])

with left:
	fig = px.choropleth_mapbox(
		map_df,
		geojson=geojson,
		locations="province_en",
		featureidkey="properties.name",
		color="job_openings",
		hover_name="province_th",
		hover_data={"province_en": True, "job_openings": True},
		color_continuous_scale="YlOrRd",
		mapbox_style="carto-positron",
		center={"lat": 13.736717, "lon": 100.523186},
		zoom=4.8,
		opacity=0.7,
	)
	fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
	st.plotly_chart(fig, use_container_width=True)

with right:
	st.subheader("Top Provinces")
	st.dataframe(
		province_counts.sort_values("job_openings", ascending=False).head(20),
		use_container_width=True,
		hide_index=True,
	)

unmapped = province_counts[province_counts["province_en"].isna()]
if not unmapped.empty:
	st.warning(
		"Some province names are not mapped yet: "
		+ ", ".join(unmapped["province_th"].sort_values().unique()[:20])
	)

