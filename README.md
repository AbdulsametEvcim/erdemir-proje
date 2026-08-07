# Envanter/Stok Takip ve Tahmin Sistemi

Erdemir ERP ve Çevresel Uygulamalar stajı kapsamında geliştirilen stok takip ve tahmin sistemi.

Stack: FastAPI + Pandas + Scikit-learn (backend), React + Vite (frontend), PostgreSQL (veritabanı).

## Çalıştırma

PostgreSQL servisi Windows'ta arka planda otomatik çalışır (`postgresql-x64-18`).

**Backend:**
```bash
cd backend
./venv/Scripts/activate
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

Tarayıcıda [http://localhost:5173](http://localhost:5173) adresini aç.

## Giriş bilgileri

- Kullanıcı adı: `admin`
- Şifre: `admin123`

(`backend/.env` dosyasında tanımlı, gerçek güvenlik değil — sadece sunum için basit bir kapı.)

## Örnek veriyi yeniden oluşturma

Veritabanı boşsa `python -m app.seed` komutu 5 malzeme ve 90 günlük hareket geçmişi üretir. Zaten veri varsa dokunmaz.

## API dokümantasyonu

Backend çalışırken [http://localhost:8000/docs](http://localhost:8000/docs) adresinden Swagger arayüzüne erişilebilir.
