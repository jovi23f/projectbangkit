import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

#Load data
def load_data():
    # lokasi file
    data_day = pd.read_csv("day.csv")
    data_hour = pd.read_csv("hour.csv")
    data_all = pd.read_csv("all_data.csv")
    return data_day, data_hour, data_all

data_day, data_hour, data_all = load_data()

# Mengubah tipe data dateday menjadi datetime dan diurutkan
data_all.sort_values(by="dateday", inplace=True)
data_all.reset_index(inplace=True)
data_all['dateday'] = pd.to_datetime(data_all['dateday'])
                                     
min_date = data_all["dateday"].min() # nilai minimal dateday
max_date = data_all["dateday"].max() # nilai maksimal dateday

#menyiapkan dataframe yang dibutuhkan
def create_month(df): 
    month_df = df.groupby(by=['year', 'month'])[['count']].mean().reset_index()
    return month_df

def create_hour(df):
    hour_df = df.groupby(by=['year', 'hour'])[['count']].mean().reset_index()
    return hour_df

def create_weather(df):
    weather_df = df.groupby(by = 'weather')[['count']].sum().reset_index()
    return weather_df


def create_rfm(df):
    rfm_df = df.groupby(by="instant", as_index=False).agg({
    "dateday": "max",       # Mengambil tanggal terakhir penyewaan sepeda dilakukan
    "weekday": "max",      # Mengambil hari dengan penyewaan terbanyak
    "count": "sum"           # Menghitung jumlah penyewaan yang telah dilakukan
    })

# Rename the columns for clarity
    rfm_df.columns = [
        "instant",
        "recent_date",  # Diganti menjadi recent_date agar lebih jelas
        "frequency",  
        "monetary"  
    ]

    # Menghitung kapan terakhir pelanggan melakukan transaksi (tanggal)
    recent_date = rfm_df['recent_date'].max()
    rfm_df["recency"] = (recent_date - rfm_df["recent_date"]).dt.days

    # Menghapus kolom 'recent_date' karena sudah tidak diperlukan lagi
    rfm_df.drop("recent_date", axis=1, inplace=True)
    return rfm_df

with st.sidebar:
    st.sidebar.title("YourBike Rental")
    st.sidebar.markdown("**Ride Everyday!**")
    # Menambahkan logo perusahaan
    st.image("https://previews.123rf.com/images/butenkow/butenkow1905/butenkow190505958/122912299-logo-for-bicycle-rental-vector-illustration-on-white-background.jpg")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = data_all[(data_all['dateday'] >= str(start_date)) & (data_all['dateday'] <= str(end_date))]

month_df = create_month(main_df)
hour_df = create_hour(main_df)
weather_df = create_weather(main_df)
rfm_df = create_rfm(main_df)

#Dashboard
st.title("Bike Sharing Information System")

#subheader pertanyaan 1
st.subheader('Bike Rentals Performance ')

fig, ax = plt.subplots(figsize=(12, 6))
                       
sns.lineplot(x="month", y="count", hue="year", data=month_df, palette="husl")
ax.set_xlabel("Month")
ax.set_ylabel("Average Bike Rentals")
ax.set_xticks(ticks=range(1, 13), labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
ax.grid(True, alpha =0.5)
ax.set_title("Average of Bike Rentals by Month", loc="center", fontsize=15)

st.pyplot(fig)

#subheader pertanyaan 2
st.subheader('Average Users based on Holiday and Working Day')
col1, col2, col3 = st.columns(3)
with col1:
# Menghitung total pengguna berdasarkan kondisi libur (holiday)
    users_holiday = data_day[data_day['holiday'] == 1]['cnt'].mean()
    st.metric("Holiday Users:", users_holiday)
with col2:
# Menghitung jumlah total pengguna berdasarkan hari kerja (workingday)
    users_workingday = data_day[data_day['workingday'] == 1]['cnt'].mean()
    st.metric("Workingday Users:", users_workingday)
with col3:
# Menghitung jumlah total pengguna berdasarkan hari kerja (weekday)
    total_users = round(data_day[data_day['weekday'] < 5]['cnt'].mean(), 2)
    st.metric("Average Users:", total_users)

#subheader pertanyaan 2
st.subheader('Total Users based on Weather ')

fig, ax = plt.subplots(figsize=(12, 6))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="weather", y="count", data=weather_df.sort_values(by="count", ascending=False), palette=colors, ax=ax)
ax.set_ylabel("User count") 
ax.set_xlabel("Weather") 
ax.set_title("Best Performing Weather to Rent", loc="center", fontsize=15)  # Set title
ax.tick_params(axis ='y', labelsize=12)  # Set y-axis tick label size
st.pyplot(fig)

#subheader rfm
st.subheader("Most Valuable Users Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (hours)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = round(rfm_df.monetary.mean(), 2) 
    st.metric("Average Duration (hours)", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="instant", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("user", fontsize=30)
ax[0].set_title("By Recency (hours)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="frequency", x="instant", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("user", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="monetary", x="instant", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("user", fontsize=30)
ax[2].set_title("By Duration (hours)", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)

st.caption('Copyright (c) Fidela Jovita Kanedi 2024')