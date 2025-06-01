import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# === 1. Baca file Excel ===
df = pd.read_excel("data_gempa.xlsx")

# === 2. Konversi ke GeoDataFrame ===
gdf_points = gpd.GeoDataFrame(
    df,
    geometry=[Point(xy) for xy in zip(df["BUJUR (°)"], df["LINTANG (°)"])],
    crs="EPSG:4326"
)

# === 3. Baca shapefile kecamatan (level 3) ===
gdf_kec = gpd.read_file("gadm36_IDN_3.shp")  # File SHP harus satu folder dengan .dbf, .shx, .prj

# === 4. Pastikan sistem koordinat sama ===
gdf_kec = gdf_kec.to_crs(gdf_points.crs)

# === 5. Gabungkan titik ke wilayah administratif ===
gdf_joined = gpd.sjoin(gdf_points, gdf_kec, how="left", predicate="within")

# === 6. Tampilkan kolom yang tersedia ===
print("Kolom yang tersedia di data hasil join:")
print(gdf_joined.columns)

# === 7. Pilih kolom yang ada dari data Excel (untuk menghindari error) ===
kolom_utama = [col for col in [
    "Tanggal", "Jam", "LINTANG (°)", "BUJUR (°)", "KEDALAMAN (km)", "MAGNITUDO", "RADIUS (KM)"
] if col in gdf_joined.columns]

# === 8. Tambahkan kolom lokasi: Provinsi, Kabupaten/Kota, Kecamatan ===
kolom_lengkap = kolom_utama + ["NAME_1", "NAME_2", "NAME_3"]

# === 9. Simpan ke file Excel ===
gdf_joined[kolom_lengkap].rename(columns={
    "NAME_1": "Provinsi",
    "NAME_2": "Kabupaten/Kota",
    "NAME_3": "Kecamatan"
}).to_excel("data_gempa_dengan_lokasi 2.xlsx", index=False)

# Baris yang gagal dikenali wilayah administratif
gdf_tidak_terbaca = gdf_joined[gdf_joined["NAME_1"].isna()]

# Lihat berapa banyak yang gagal
print("Jumlah titik yang tidak terbaca wilayahnya:", len(gdf_tidak_terbaca))

print("✅ File berhasil disimpan sebagai: data_gempa_dengan_lokasi 2.xlsx")
