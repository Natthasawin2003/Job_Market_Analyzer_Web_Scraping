import streamlit as st
import pandas as pd

st.title("My First Dashboard")

name = st.text_input("ชื่อ")

if st.button("submit"):
    st.write("Hello", name)

data = pd.DataFrame({
    "Month":["Jan","Feb","Mar"],
    "Sales":[100,200,150]
})

st.bar_chart(data.set_index("Month"))