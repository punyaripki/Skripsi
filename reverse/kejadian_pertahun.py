import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 1. Baca data gempa
df = pd.read_excel("total semua gempa.xlsx", skiprows=1)

# 2. Konversi tipe kolom
df["LINTANG (°)"] = df["LINTANG (°)"].astype(float)
df["BUJUR (°)"] = df["BUJUR (°)"].astype(float)
df["Radius (KM)"] = df["Radius (KM)"].astype(float)
df["DATE (GMT)"] = pd.to_datetime(df["DATE (GMT)"])
df["Tahun"] = df["DATE (GMT)"].dt.year

# 3. Buat GeoDataFrame dari data gempa
geometry = [Point(xy) for xy in zip(df["BUJUR (°)"], df["LINTANG (°)"])]
gdf_quakes = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
gdf_quakes = gdf_quakes.to_crs(epsg=32750)

# 4. Buat buffer area berdasarkan radius
gdf_quakes["geometry"] = gdf_quakes.buffer(gdf_quakes["Radius (KM)"] * 1000)

# 5. Load shapefile kecamatan seluruh Indonesia dan filter Lombok saja
gdf_kecamatan = gpd.read_file("gadm36_IDN_3.shp").to_crs(epsg=32750)

# Nama kabupaten yang ingin difilter
kabupaten_lombok = ["Lombok Barat", "Lombok Timur", "Lombok Tengah", "Mataram"]
gdf_lombok = gdf_kecamatan[gdf_kecamatan["NAME_2"].isin(kabupaten_lombok)].copy()

# 6. Join buffer gempa dengan kecamatan di Lombok
gdf_join = gpd.sjoin(gdf_lombok, gdf_quakes, how="inner", predicate="intersects")

# 7. Hitung frekuensi kejadian gempa per tahun per kecamatan
result = gdf_join.groupby(["Tahun", "NAME_2", "NAME_3"]).size().reset_index(name="Frekuensi")

# 8. Simpan ke Excel
result.to_excel("frekuensi_gempa_lombok.xlsx", index=False)
