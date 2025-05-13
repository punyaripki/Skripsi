import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Baca data gempa
df = pd.read_excel("data_gempa.xlsx")

# Standarisasi nama kolom
df.columns = df.columns.str.strip().str.upper()
df = df.rename(columns={
    "DATE (GMT)": "TANGGAL",
    "LINTANG (°)": "LAT",
    "BUJUR (°)": "LON",
    "KEDALAMAN (KM)": "KEDALAMAN",
    "MAGNITUDO (M)": "MAGNITUDO",
    "RADIUS (KM)": "RADIUS"
})

# Konversi ke GeoDataFrame dan ubah CRS ke meter
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["LON"], df["LAT"]), crs="EPSG:4326")
gdf = gdf.to_crs(epsg=3857)

# Buat buffer radius gempa
gdf["geometry"] = gdf.buffer(gdf["RADIUS"] * 1000)

# Baca shapefile kecamatan
kecamatan = gpd.read_file("gadm36_IDN_3.shp").to_crs(epsg=3857)

# Gabungkan untuk menemukan kecamatan terdampak
terdampak = gpd.sjoin(kecamatan, gdf, how="inner", predicate="intersects")

# Hitung berapa kali kecamatan terdampak
jumlah_terdampak = terdampak.groupby("NAME_3").size().reset_index(name="JUMLAH_TERDAMPAK")

# Gabungkan kembali ke peta kecamatan
kecamatan_terdampak = kecamatan.merge(jumlah_terdampak, on="NAME_3", how="left").fillna(0)

# Simpan ke Excel
kecamatan_terdampak[["NAME_1", "NAME_2", "NAME_3", "JUMLAH_TERDAMPAK"]].to_excel("kecamatan_terdampak.xlsx", index=False)

print("Selesai! File 'kecamatan_terdampak.xlsx' telah dibuat.")
