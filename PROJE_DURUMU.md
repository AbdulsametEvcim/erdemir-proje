# Envanter Sistemi — Proje Durumu Özeti

> Yeni bir sohbette bu dosyayı gösterirsen (veya içeriğini yapıştırırsan) kaldığımız yerden devam edebilirim.

## Ne yaptık

Erdemir "ERP ve Çevresel Uygulamalar" stajı için **Envanter/Stok Takip ve Tahmin Sistemi** kurduk.
- Backend: Python (FastAPI, Pandas, Scikit-learn) + PostgreSQL 18 (yerel, şifre `fener1907`)
- Frontend: React 18 + Vite + recharts + axios
- Konum: `C:\Users\Lenovo\Desktop\envanter-sistem\`
- Çalıştırma: proje klasöründeki `baslat.bat` dosyasına çift tıkla
- Giriş: kullanıcı `samo` / şifre `fener1907` (gerçek güvenlik değil, sadece demo)

## 4 modül

1. **Ana Sayfa** — özet kartları, kritik uyarı bandı, karşılaştırma grafiği, malzeme listesi/ekleme, Excel'e aktarma, genel PDF rapor
2. **Stok Hareketleri** — giriş/çıkış girme (girişte tedarikçi), filtrelenebilir hareket listesi, tedarikçi özeti
3. **Malzeme Detayı** — 90 günlük tüketim grafiği, istatistiksel tahmin, düzenleme/silme, PDF rapor
4. **Çevresel Etki** — tüketime bağlı tahmini CO₂ emisyonu

Ekstra: karanlık/aydınlık tema, toast bildirimler, onay modalları, sidebar ikonları, gerçek Erdemir logosu ve gerçek tesis fotoğrafı (login sayfası), otomatik veri tazeleme, 41 testlik pytest paketi.

## Önemli tercihler / kararlar (tekrar sorulmasın diye)

- Ana renk **mavi** (`#2563eb`) — kurumsal kırmızı (`#ed1c2e`) denendi, **reddedildi**, maviye dönüldü.
- Login arka planı **gerçek Erdemir tesis fotoğrafı** — özel SVG illüstrasyon reddedilmişti.
- 9 gerçekçi malzeme var: Demir Cevheri, Taşkömürü, Kok Kömürü, Kireçtaşı, Ferrokrom, Hurda Çelik, Dolomit, Doğalgaz, Haddehane Merdanesi.
- Tüketim toplamlarında ton/m³/adet karışmaması için `Material.unit == "ton"` filtresi 3 farklı yerde düzeltildi (özet, karşılaştırma, PDF rapor).

## Sunum (PowerPoint)

Kullanıcının verdiği kurumsal şablon içine (`Erdemir Sunum Formatı (TR) 16-9.pptx`) işlendi. Şu an **v4** teslim edildi: `C:\Users\Lenovo\Desktop\Envanter_Sistemi_Sunum_v4.pptx`
- v2→v3: başlık slaydındaki metin üst üste binme hatası düzeltildi, modül/özet maddeleri detaylandırıldı
- v3→v4: Proje Özeti'ndeki teknoloji satırına eksik olan "Python" kelimesi eklendi
- **Bekleyen:** v4 hakkında henüz onay/geri bildirim gelmedi.

## Bitmemiş / ertelenmiş iş

- `README.md` güncel değil (hâlâ "5 malzeme" yazıyor, PDF rapor/çevresel sayfa/tedarikçi takibi/tema anlatılmamış). Daha önce işaret edildi ama ertelendi — istenirse güncellenecek.

## Bilinmesi gereken teknik notlar

- Bu Windows makinede LibreOffice/soffice yok, bu yüzden sunumun görsel önizlemesi/PDF'i alınamadı — değişiklikler XML seviyesinde yapıldı ve `validate.py` ile şema doğrulaması yapıldı, ama ekran görüntüsüyle doğrulanmadı. Sunumu PowerPoint'te açıp göz atman iyi olur.
- v2 ve v3 dosyaları hâlâ Desktop'ta duruyor olabilir (bazıları PowerPoint'te açık kaldığı için silinemedi) — istersen temizleyebilirim.
