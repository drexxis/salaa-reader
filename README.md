# Salaa Reader — Ezan Takip Sistemi

Diyanet esaslı namaz vakitlerini otomatik çekip, vakit öncesi anons ve vakit başında ezanı
sesli olarak çalan bir Python + Arduino projesi. Ses çıkışı PC hoparlörlerinden verilir,
Arduino ise her anons öncesi hoparlörde kısa bir uyarı bipi üretir.

## Özellikler

- Diyanet metoduna (method 13) göre günlük vakitleri otomatik çeker
- Her vakit için **45 dakika önce** ve **5 dakika önce** otomatik anons çalar
- Vakit başında giriş anonsu + ezan çalar
- Gece 00:01'de vakitleri yeniler, aynı gün tekrar çalmaz
- Vakitler API'den alınamazsa mevcut program çalışmaya devam eder
- Arduino bağlı değilse sistem PC üzerinden sessiz çalışmaya devam eder

## Gereksinimler

- Python 3.9+
- Arduino (USB bağlantılı, isteğe bağlı)
- Hoparlör / ses kartı
- İnternet bağlantısı

## Kurulum

```bash
pip install -r requirements.txt
```

## Ses Dosyaları

`.mp3` dosyaları binary ve toplam ~3 MB olduğu için **bu repoya dahil edilmemıştir**
(`.gitignore` içinde). Program bu dosyaları çalıştığı dizinde arar, ses dosyası
bulunamazsa ilgili anonsu atlar ve konsolda uyarı basar.

Projeyi çalıştırmak için aşağıdaki 17 dosyayı proje dizinine koymanız gerekir:

| Dosya | Kullanım |
| --- | --- |
| `ezan.mp3` | Vakit başında çalan ezan |
| `dingdong.mp3` | Her anonsun başında çalan uyarı sesi |
| `giris_sabah.mp3` `giris_ogle.mp3` `giris_ikindi.mp3` `giris_aksam.mp3` `giris_yatsi.mp3` | Vakit başındaki giriş anonsları |
| `anons45_sabah.mp3` … `anons45_yatsi.mp3` | Vakitten 45 dakika önce çalan anonslar |
| `anons5_sabah.mp3` … `anons5_yatsi.mp3` | Vakitten 5 dakika önce çalan anonslar |

## Ayarlar

`system.py` üstündeki sabitlerden değiştirilir:

| Sabit | Varsayılan | Açıklama |
| --- | --- | --- |
| `ARDUINO_PORT` | `COM3` | Arduino'nun seri portu (Linux/macOS'ta `/dev/ttyUSB0` gibi) |
| `CITY` | `Canakkale` | Vakitlerin çekileceği şehir |
| `COUNTRY` | `Turkey` | Ülke |
| seri hızı | `9600` | Arduino ile baud rate (baud hızı) |

## Çalıştırma

```bash
python system.py
```

Program başladığında vakitleri çeker, Arduino'ya bağlanmayı dener ve çalışmaya başlar.

### Test modu

Tüm vakit akışını (45 dk anonsu → 5 dk anonsu → giriş + ezan) öğle vakti için
denemek üzere iki şekilde tetiklenebilir:

- Konsolda `test` yazıp Enter'a basmak
- Arduino'dan seri porttan `test` satırı göndermek

## Arduino Haberleşmesi

| Yön | Mesaj | Zaman |
| --- | --- | --- |
| PC → Arduino | `BEEP\n` | Her anons ve ezan öncesi |
| Arduino → PC | `test\n` | Test modunu tetikler |

## Dosya Yapısı

```
.
├── system.py           # Ana program
├── requirements.txt    # Python bağımlılıkları
├── .gitignore
└── *.mp3               # Ses dosyaları (repodan hariç, yerelde bulunmalı)
```

## Güvenlik Notları

- Vakitler **HTTPS** üzerinden çekilir (`api.aladhan.com`). Düz metin HTTP kullanmak,
  ağdaki bir saldırganın vakitleri değiştirmesine (ve dolayısıyla yanlış vakit
  bildirilmesine) yol açardı.
- API'den gelen veri hiçbir yerde dosya yolu olarak kullanılmaz; çalınan ses dosyasının
  adı sabit bir sözlükten seçilir.
- Kod içinde hiçbir API anahtarı, şifre veya token bulunmaz.

## Sorumluluk Notu

Bu proje bir **yardımcı programdır**; vakit hesaplamasını harici bir servisten alır.
Kendi başına kullanıldığında doğruluk garantisi vermez. Cami vb. yerlerde kullanım
öncesi ayet/giriş anonslarının içeriği yetkili kurumlarca kontrol edilmelidir.