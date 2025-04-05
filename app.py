import streamlit as st
import pandas as pd
import json
import altair as alt
from cryptography.fernet import Fernet

st.set_page_config(
    page_title="StatProb - PDF & CDF Soal No. 1",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="auto"
)

fernet_key = st.secrets["encryption"]["key"]
fernet = Fernet(fernet_key.encode())

with open("data.encrypted", "rb") as f:
    encrypted_data = f.read()

decrypted_data = fernet.decrypt(encrypted_data)
json_data = json.loads(decrypted_data.decode())

students = pd.DataFrame(json_data['students'])
shows   = pd.DataFrame(json_data['shows'])
students = students.merge(shows, left_on='most_like_show', right_on='id', suffixes=('','_show'))

def get_freq_df(df):
    freq = df['name_show'].value_counts().reset_index()
    freq.columns = ['Show','Frequency']
    return freq

male_freq    = get_freq_df(students[students.gender=='male'])
female_freq  = get_freq_df(students[students.gender=='female'])
overall_freq = get_freq_df(students)

male_total    = len(students[students.gender=='male'])
female_total  = len(students[students.gender=='female'])
overall_total = len(students)

def add_pdf_cdf(df, total):
    df = df.copy()
    df['PDF_numeric'] = df['Frequency'] / total
    df['PDF'] = df.apply(lambda r: f"{r.Frequency}/{total} = {r.PDF_numeric:.4f}", axis=1)
    df['CDF_numeric'] = df['PDF_numeric'].cumsum()

    cdf_strings = []
    running = 0
    for p in df['PDF_numeric']:
        prev = running
        running += p
        if prev == 0:
            cdf_strings.append(f"{p:.4f} = {running:.4f}")
        else:
            cdf_strings.append(f"{prev:.4f} + {p:.4f} = {running:.4f}")
    df['CDF'] = cdf_strings
    df['Persentase'] = (df['PDF_numeric'] * 100).round(2)
    return df

male_freq    = add_pdf_cdf(male_freq, male_total)
female_freq  = add_pdf_cdf(female_freq, female_total)
overall_freq = add_pdf_cdf(overall_freq, overall_total)

st.markdown(
    "<h3>Analisis Survei Acara TV yang Paling Disukai Mahasiswa Teknik Komputer A 2023</h3>",
    unsafe_allow_html=True
)
st.write("""
**Tugas No. 1**

Anda lakukan survey terhadap 20 orang teman anda yang dipilih secara acak.
Tanyakan jenis acara TV yang PALING DISUKAI oleh mereka dari acara-acara TV berikut ini:
**Olahraga**, **Infotainment** (berita Selebriti, dll), **Berita politik dan/atau ekonomi**, **Film Action**, **Film Kartun**, **Film Drama**, **Sinetron**.

- Buatlah *Distribusi frekuensi*, *PDF*, dan *CDF* dari hasil survey tersebut.
- Gambar grafik PDF dan CDF-nya.
- Didasarkan pada segmen mahasiswa yang anda pilih (**jenis kelamin**), buatlah analisa:
    - Berapa % mahasiswa laki-laki pada masing-masing acara TV yang PALING DISUKAI tersebut.
    - Demikian juga untuk mahasiswa perempuan.
""")

df_survei = students[['id', 'name', 'gender', 'name_show']]

df_survei.loc[:, 'gender'] = df_survei['gender'].map({
    'male': 'Laki-laki',
    'female': 'Perempuan'
})

df_survei = df_survei.rename(columns={
    'id': 'NRP',
    'name': 'Nama',
    'gender': 'Jenis Kelamin',
    'name_show': 'Acara TV'
})

st.header("Data Survei")
st.dataframe(df_survei.set_index('NRP'))

choice = st.selectbox("Pilih Jenis Kelamin", ["Keseluruhan", "Laki-laki","Perempuan"])
if choice=="Laki-laki":
    df = male_freq; total = male_total; label="Laki-laki"
elif choice=="Perempuan":
    df = female_freq; total = female_total; label="Perempuan"
else:
    df = overall_freq; total = overall_total; label="Semua"

st.header(f"Distribusi untuk: {label}")
st.dataframe(df[['Show','Frequency','PDF','CDF','Persentase']].set_index('Show'))

st.subheader("Grafik Frekuensi")
freq_chart = df[['Show','Frequency']].set_index('Show')

st.markdown("**Bar Chart**")
st.bar_chart(freq_chart)

st.markdown("**Line Chart**")
st.line_chart(freq_chart)

st.subheader("Grafik PDF (Probability Density Function)")
pdf_chart = (
    alt.Chart(df)
    .mark_line(point=True, color='#d62728')
    .encode(
        x=alt.X('Show', sort='-y', title='Acara TV'),
        y=alt.Y('PDF_numeric', title='Probabilitas'),
        tooltip=['Show','PDF']
    )
)
st.altair_chart(pdf_chart, use_container_width=True)

st.subheader("Grafik CDF (Cumulative Distribution Function)")
cdf_chart = (
    alt.Chart(df)
    .mark_line(point=True, color='#1f77b4')
    .encode(
        x=alt.X('Show', sort='-y', title='Acara TV'),
        y=alt.Y('CDF_numeric', title='CDF'),
        tooltip=['Show','CDF']
    )
)
st.altair_chart(cdf_chart, use_container_width=True)

st.header("Persentase (%)")
st.dataframe(df.set_index('Show')[['Persentase']])

st.markdown("""---""")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Made with 愛 in Streamlit"
    "</div>",
    unsafe_allow_html=True
)