import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Baca data
df = pd.read_excel("data_gempa.xlsx")

# Bersihkan data (hapus baris yang kosong atau radius tidak valid)
df = df.dropna(subset=["LINTANG (°)", "BUJUR (°)", "RADIUS (KM)", "KEDALAMAN (KM)", "MAGNITUDO (M)"])
df = df[df["RADIUS (KM)"] > 0]

# Buat GeoDataFrame titik gempa
df["geometry"] = [Point(xy) for xy in zip(df["BUJUR (°)"], df["LINTANG (°)"])]
gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
gdf = gdf.to_crs(epsg=32750)

# Buat buffer dari radius
gdf["buffer"] = gdf.buffer(gdf["RADIUS (KM)"] * 1000)  # dari km ke meter
gdf_buffer = gpd.GeoDataFrame(gdf.drop("geometry", axis=1), geometry=gdf["buffer"], crs=gdf.crs)

# Baca data kecamatan
gdf_kecamatan = gpd.read_file("gadm36_IDN_3.shp")
gdf_kecamatan = gdf_kecamatan.to_crs(epsg=32750)

# Filter hanya kecamatan di Pulau Lombok
kabupaten_lombok = ["Lombok Barat", "Lombok Tengah", "Lombok Timur", "Kota Mataram"]
gdf_lombok = gdf_kecamatan[gdf_kecamatan["NAME_2"].isin(kabupaten_lombok)]

# Cek kecamatan yang terdampak setiap gempa
hasil = []

for i, gempa in gdf_buffer.iterrows():
    if gempa.geometry is None:
        continue  # Lewati jika geometry kosong
    dampak = gdf_lombok[gdf_lombok.intersects(gempa.geometry)]
    for _, kec in dampak.iterrows():
        hasil.append({
            "Data ke-": i+1,
            "Tahun": pd.to_datetime(gempa["DATE (GMT)"]).year,
            "Kabupaten/Kota": kec["NAME_2"],
            "Kecamatan": kec["NAME_3"],
            "Kedalaman (km)": gempa["KEDALAMAN (KM)"],
            "Magnitudo": gempa["MAGNITUDO (M)"],
            "Radius (km)": gempa["RADIUS (KM)"]
        })

# Simpan ke Excel
df_hasil = pd.DataFrame(hasil)
df_hasil.to_excel("kecamatan_terdampak_lombok.xlsx", index=False)
print("✅ Data berhasil disimpan ke 'kecamatan_terdampak_lombok.xlsx'")
