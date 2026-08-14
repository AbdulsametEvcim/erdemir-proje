# Envanter/Stok Takip ve Tahmin Sistemi

Erdemir ERP ve Çevresel Uygulamalar stajı kapsamında geliştirilen stok takip ve tahmin sistemi.

Stack: FastAPI + Pandas + Scikit-learn (backend), React + Vite (frontend), PostgreSQL (veritabanı).

## Modüller

- **Ana Sayfa** — özet kartları, kritik uyarı bandı, malzemeler arası tüketim karşılaştırma grafiği, aranabilir/sıralanabilir malzeme listesi, malzeme ekleme, Excel'e aktarma, genel durum PDF raporu
- **Stok Hareketleri** — giriş/çıkış hareketi girme (girişte tedarikçi bilgisi), malzeme/tipe göre filtrelenebilir son hareketler listesi, tedarikçi özeti paneli
- **Malzeme Detayı** — 90 günlük tüketim grafiği, istatistiksel tahmin ("X gün sonra tükenir"), malzeme düzenleme/silme, tek malzeme için PDF raporu
- **Çevresel Etki** — malzeme tüketimine bağlı tahmini CO₂ emisyonu (sektör ortalamalarına dayalı kaba yaklaşım, ölçülmüş değer değildir)

Ek özellikler: manuel karanlık/aydınlık tema, toast bildirimleri, otomatik veri tazeleme (backend her açıldığında son hareketten bugüne kadarki boşluğu geçmiş tüketim hızına göre doldurur).

## Çalıştırma

PostgreSQL servisi Windows'ta arka planda otomatik çalışır (`postgresql-x64-18`).

**En kolay yol:** proje klasöründeki `baslat.bat` dosyasına çift tıkla — backend ve frontend'i otomatik başlatır, tarayıcıyı açar.

**Manuel (VS Code terminalinden):**
```bash
cd backend
venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
```bash
cd frontend
npm run dev
```

Tarayıcıda [http://localhost:5173](http://localhost:5173) adresini aç.

## Giriş bilgileri

- Kullanıcı adı: `samo`
- Şifre: `fener1907`

(`backend/.env` dosyasında tanımlı, gerçek güvenlik değil — sadece sunum için basit bir kapı.)

## Örnek veri

Sistemde 9 malzeme var: Demir Cevheri, Taşkömürü, Kok Kömürü, Kireçtaşı, Ferrokrom, Hurda Çelik, Dolomit, Doğalgaz, Haddehane Merdanesi (yedek parça). Her biri 90 günlük gerçekçi hareket geçmişiyle geliyor.

`python -m app.seed` komutu, `MATERIAL_DEFS` listesinde olup veritabanında henüz olmayan malzemeleri ekler — var olanlara dokunmaz, tekrar çalıştırmak güvenlidir.

## API dokümantasyonu

Backend çalışırken [http://localhost:8000/docs](http://localhost:8000/docs) adresinden Swagger arayüzüne erişilebilir.

## Testleri çalıştırma

```bash
cd backend
venv\Scripts\python.exe -m pytest -v
```

41 test var (API uç noktaları + tahmin mantığı). Testler gerçek veritabanına dokunmaz — izole bir in-memory (RAM'de) test veritabanı kullanır, bu yüzden demo verisini bozma riski yoktur.
