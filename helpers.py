import numpy as np
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    """
    Menghitung jarak Haversine antara dua koordinat (latitude, longitude).
    Hasil dalam kilometer.
    """
    R = 6371  # Radius bumi dalam kilometer
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])  # Konversi ke radian
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

def match_donations(donasi_data, penerima_data):
    results = []

    for _, donasi in donasi_data.iterrows():
        donatur_lat, donatur_lon = map(float, donasi['lokasi_donatur'].split(', '))
        
        for _, penerima in penerima_data.iterrows():
            penerima_lat, penerima_lon = map(float, penerima['alamat_penerima'].split(', '))

            # Cek jenis makanan
            if donasi['jenis_makanan'].lower() == penerima['jenis_makanan_dibutuhkan'].lower():
                
                # Hitung jarak geografis dengan Haversine
                distance_km = haversine(donatur_lat, donatur_lon, penerima_lat, penerima_lon)

                # Normalisasi jarak agar bernilai antara 0-1 (semakin kecil jarak, semakin besar nilai)
                max_distance = 50  # Misalnya 50 km sebagai batas maksimum relevansi
                location_similarity = max(0, 1 - (distance_km / max_distance))

                # Similarity jumlah porsi
                jumlah_similarity = min(donasi['jumlah_porsi'], penerima['jumlah_kebutuhan']) / max(donasi['jumlah_porsi'], penerima['jumlah_kebutuhan'])

                # Hitung total skor kecocokan
                total_similarity = (0.5 * location_similarity) + (0.3 * jumlah_similarity) + 0.2

                results.append({
                    'nama_donatur': donasi['nama_donatur'],
                    'nama_penerima': penerima['nama_penerima'],
                    'jenis_makanan': donasi['jenis_makanan'],
                    'jumlah_porsi': donasi['jumlah_porsi'],
                    'jumlah_kebutuhan': penerima['jumlah_kebutuhan'],
                    'lokasi_donatur': donasi['lokasi_donatur'],
                    'alamat_penerima': penerima['alamat_penerima'],
                    'jarak_km': round(distance_km, 2),
                    'similarity': total_similarity
                })

    # Urutkan hasil berdasarkan similarity (dari yang paling cocok)
    results = sorted(results, key=lambda x: x['similarity'], reverse=True)
    return results
