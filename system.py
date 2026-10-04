import datetime
import time
import serial
import pygame
import requests
import os
import threading

pygame.mixer.init()

ARDUINO_PORT = 'COM3'
CITY = "Canakkale"
COUNTRY = "Turkey"

ANONS_SESLERI = {}
EZAN_GIRIS_SESLERI = {}

def vakitleri_diyanetten_cek():
    global ANONS_SESLERI, EZAN_GIRIS_SESLERI
    print(f">> Diyanet'ten bugunun {CITY} ezan vakitleri cekiliyor...")
    
    # Diyanet İşleri Başkanlığı Servisi (Method 13)
    url = f"https://api.aladhan.com/v1/timingsByCity?city={CITY}&country={COUNTRY}&method=13"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 200:
            timings = data["data"]["timings"]
            
            ezan_saatleri = {
                "sabah":  timings["Fajr"],
                "ogle":   timings["Dhuhr"],
                "ikindi": timings["Asr"],
                "aksam":  timings["Maghrib"],
                "yatsi":  timings["Isha"]
            }
            
            ANONS_SESLERI.clear()
            EZAN_GIRIS_SESLERI.clear()
            
            print(f"\n--- BUGUNUN DIYANET EZAN VAKITLERI ({CITY.upper()}) ---")
            for vakit_adi, ezan_saat_str in ezan_saatleri.items():
                ezan_dt = datetime.datetime.strptime(ezan_saat_str, "%H:%M")
                
                anons45_dt = ezan_dt - datetime.timedelta(minutes=45)
                anons5_dt  = ezan_dt - datetime.timedelta(minutes=5)
                
                s_45 = anons45_dt.strftime("%H:%M")
                s_5  = anons5_dt.strftime("%H:%M")
                s_ezan = ezan_saat_str
                
                print(f"[{vakit_adi.upper()}] -> 45 Dk Kala: {s_45} | 5 Dk Kala: {s_5} | Ezan: {s_ezan}")
                
                ANONS_SESLERI[s_45] = f"anons45_{vakit_adi}.mp3"
                ANONS_SESLERI[s_5]  = f"anons5_{vakit_adi}.mp3"
                EZAN_GIRIS_SESLERI[s_ezan] = f"giris_{vakit_adi}.mp3"
                
            print("------------------------------------\n")
            return True
        else:
            print(">> HATA: API yaniti basarisiz oldu.")
            return False
            
    except Exception as e:
        print(f">> HATA: Diyanet vakitleri cekilemedi! ({e})")
        return False

# Vakitleri Çek
vakitleri_diyanetten_cek()

# Arduino Bağlantısı
arduino = None
try:
    arduino = serial.Serial(ARDUINO_PORT, 9600, timeout=0.1)
    time.sleep(2)
    print(f">> Arduino'ya baglanildi! ({ARDUINO_PORT})")
except Exception as e:
    print(f">> UYARI: Arduino baglanamadi ({e}). Sadece PC'den ses calinacak.")

calinan_vakitler = set()
test_tetiklendi = False

# Güvenli Ses Çalma Fonksiyonu
def ses_cal_ve_bekle(dosya_adi):
    if os.path.exists(dosya_adi):
        pygame.mixer.music.load(dosya_adi)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.5)
    else:
        print(f">> UYARI: '{dosya_adi}' bulunamadi!")

# TEST FONKSİYONU
def tam_ogle_testi_yap():
    global test_tetiklendi
    print("\n--- TEST MODU BASLATILDI (OGLE VAKTI) ---")
    
    # 1. 45 Dk Kala Anonsu
    print("1/3: 45 Dk Anonsu Caliniyor...")
    if arduino: 
        try: arduino.write(b"BEEP\n")
        except Exception: pass
        
    ses_cal_ve_bekle("dingdong.mp3")
    ses_cal_ve_bekle("anons45_ogle.mp3")
    
    print(">> 5 Saniye Bekleniyor...")
    time.sleep(5)

    # 2. 5 Dk Kala Anonsu
    print("2/3: 5 Dk Anonsu Caliniyor...")
    if arduino: 
        try: arduino.write(b"BEEP\n")
        except Exception: pass
        
    ses_cal_ve_bekle("dingdong.mp3")
    ses_cal_ve_bekle("anons5_ogle.mp3")

    print(">> 5 Saniye Bekleniyor...")
    time.sleep(5)

    # 3. Giriş Anonsu + Ezan
    print("3/3: Ezan Giriş Anonsu ve Ezan Caliniyor...")
    if arduino: 
        try: arduino.write(b"BEEP\n")
        except Exception: pass
    
    ses_cal_ve_bekle("giris_ogle.mp3")
    time.sleep(1)
    ses_cal_ve_bekle("ezan.mp3")

    print("--- TEST TAMAMLANDI ---\n")
    test_tetiklendi = False

# Konsol Dinleyici
def konsol_dinle():
    global test_tetiklendi
    while True:
        try:
            girdi = input()
            if girdi.strip().lower() == "test":
                test_tetiklendi = True
        except (EOFError, KeyboardInterrupt):
            break

threading.Thread(target=konsol_dinle, daemon=True).start()

print(">> Ezan Takip Sistemi Calisiyor...")
print(">> TEST ETMEK İÇİN: Bu ekrana 'test' yazip ENTER'a basabilirsin!\n")

while True:
    # Serial Kontrolü
    if arduino and arduino.in_waiting > 0:
        try:
            gelen_veri = arduino.readline().decode('utf-8', errors='ignore').strip()
            if gelen_veri.lower() == "test":
                test_tetiklendi = True
        except Exception:
            pass

    if test_tetiklendi:
        tam_ogle_testi_yap()

    # Normal Takip
    simdi = datetime.datetime.now()
    su_anki_zaman = simdi.strftime("%H:%M")
    saniye = simdi.second

    if saniye == 0 and su_anki_zaman not in calinan_vakitler:

        if su_anki_zaman in ANONS_SESLERI:
            calinacak_dosya = ANONS_SESLERI[su_anki_zaman]
            print(f"[{su_anki_zaman}] Anons caliniyor: {calinacak_dosya}")
            if arduino: 
                try: arduino.write(b"BEEP\n")
                except: pass
            
            ses_cal_ve_bekle("dingdong.mp3")
            ses_cal_ve_bekle(calinacak_dosya)
            calinan_vakitler.add(su_anki_zaman)

        elif su_anki_zaman in EZAN_GIRIS_SESLERI:
            giris_dosyasi = EZAN_GIRIS_SESLERI[su_anki_zaman]
            print(f"[{su_anki_zaman}] Ezan vakti geldi!")
            if arduino: 
                try: arduino.write(b"BEEP\n")
                except: pass

            ses_cal_ve_bekle(giris_dosyasi)
            time.sleep(1)
            ses_cal_ve_bekle("ezan.mp3")
            
            calinan_vakitler.add(su_anki_zaman)

    if su_anki_zaman == "00:01" and saniye == 0:
        calinan_vakitler.clear()
        vakitleri_diyanetten_cek()
        time.sleep(2)

    time.sleep(0.2)