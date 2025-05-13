import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Load file Excel kamu
df = pd.read_excel("data_gempa.xlsx")

# Inisialisasi geolocator
geolocator = Nominatim(user_agent="skripsi_geocoder")
geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)

# Fungsi untuk ambil nama kabupaten & kecamatan
def get_location_info(lat, lon):
    try:
        location = geocode((lat, lon), language='id')
        if location and location.raw.get('address'):
            address = location.raw['address']
            kabupaten = address.get('county') or address.get('state_district') or ''
            kecamatan = address.get('suburb') or address.get('city_district') or address.get('village') or ''
            return pd.Series([kabupaten, kecamatan])
    except:
        return pd.Series(['', ''])

# Terapkan ke semua baris
df[['Kabupaten', 'Kecamatan']] = df.apply(lambda row: get_location_info(row['LINTANG (°)'], row['BUJUR (°)']), axis=1)

# Simpan hasil ke file baru
df.to_excel("data_gempa_lengkap.xlsx", index=False)
