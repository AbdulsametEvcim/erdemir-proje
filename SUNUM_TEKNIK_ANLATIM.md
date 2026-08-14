# Envanter Sistemi — Baştan Sona Teknik Anlatım (Sunum Hazırlığı)

> Bu doküman yarınki antrenman/sunum için hazırlandı. Amaç: projenin her aşamasını "ne yaptık" değil "neden öyle yaptık" mantığıyla anlatabilmen. Sonda, bir mühendisin sorabileceği soruları ve cevaplarını bulacaksın.

---

## 1. Projenin amacı ve kapsam kararı

**Ne:** Bir fabrikada (Erdemir senaryosu) hammadde/malzeme stoklarını izleyen, stok hareketlerini kaydeden, geçmiş tüketime bakarak "bu malzeme kaç gün sonra biter" tahmini yapan ve kritik seviyedeki malzemeler için uyarı üreten bir web uygulaması.

**Neden bu kapsam seçildi:** Staj süresi ve tek kişilik geliştirme göz önüne alınarak, gerçek bir ERP modülünün *çekirdek değer önerisini* (stok görünürlüğü + tahmin + uyarı) hedef aldık; muhasebe entegrasyonu, çoklu depo, kullanıcı rolleri gibi genişletmeler kapsam dışı bırakıldı. Bu bilinçli bir MVP (Minimum Viable Product) kararı — "her şeyi yapmaya çalışıp hiçbirini bitirememek" yerine, 4 modülü uçtan uca sağlam çalışır hale getirmeyi tercih ettik.

---

## 2. Genel mimari — neden 3 katmanlı (frontend / backend / veritabanı)

```
React (frontend, tarayıcıda)  <-- HTTP/JSON -->  FastAPI (backend, Python)  <-- SQL -->  PostgreSQL (veritabanı)
```

- **Neden katmanları ayırdık (monolitik tek dosya değil):** Sorumlulukların ayrılması (separation of concerns). Frontend sadece görüntüleme/etkileşimden, backend iş kuralları ve hesaplamalardan (tahmin, CO2, PDF), veritabanı da kalıcı veriden sorumlu. Bu sayede örneğin ileride mobil uygulama eklense, aynı backend API'sini kullanabilir — arayüz değişse de iş mantığı tekrar yazılmaz.
- **Neden REST/JSON (GraphQL değil):** Proje küçük/orta ölçekli, sabit ve öngörülebilir veri ihtiyaçları var (dashboard, liste, detay). GraphQL'in esnek sorgu avantajı bu ölçekte gereksiz karmaşıklık katardı; REST + FastAPI'nin otomatik OpenAPI/Swagger dokümantasyonu geliştirmeyi hızlandırdı (`/docs` adresinden canlı test edilebiliyor).

---

## 3. Teknoloji seçimleri ve gerekçeleri

| Katman | Seçilen | Neden bu, alternatif ne olurdu |
|---|---|---|
| Backend framework | **FastAPI** | Python'da veri işleme (Pandas, Scikit-learn) ile aynı dilde backend yazmak entegrasyonu kolaylaştırdı. FastAPI; Flask'a göre otomatik veri doğrulama (Pydantic) ve otomatik Swagger dokümantasyonu sunuyor, Django'ya göre ise çok daha hafif — bize tam bir CMS/admin panel gerekmiyordu, sadece API. |
| Veri doğrulama | **Pydantic** | Gelen isteklerin (örn. yeni malzeme eklerken `current_stock` sayısal mı, `unit` boş mu) tip güvenliğini FastAPI ile birlikte otomatik sağlıyor — elle `if` kontrolü yazmak yerine şema tanımlamak yeterli. |
| Veritabanı | **PostgreSQL** | İlişkisel veri (malzeme ↔ hareketler, bire-çok ilişki), tutarlılık (bir hareket eklenince stok güncellenmesi gibi işlemler) ve endüstri standardı olması nedeniyle. NoSQL (MongoDB vb.) burada gereksiz olurdu çünkü veri zaten satır/tablo yapısına çok uygun ve ilişkisel sorgular (filtreleme, gruplama, toplama) SQL'de doğal. |
| ORM | **SQLAlchemy 2.0** | Ham SQL yazmak yerine Python nesneleriyle veritabanı işlemi yapmayı sağlıyor; ayrıca **SQL injection riskini** otomatik olarak ortadan kaldırıyor çünkü tüm sorgular parametreli/hazırlanmış (prepared statement) şekilde üretiliyor. |
| Veri analizi | **Pandas** | Excel'e aktarma ve tüketim verisini gün bazında gruplama/toplama işlemlerinde kullanıldı — elle döngü yazmaktan çok daha az hata riskli ve hızlı. |
| Tahmin | **Scikit-learn (Lineer Regresyon)** | Aşağıda ayrı bölümde detaylı anlatılıyor (bölüm 6). |
| Frontend framework | **React + Vite** | React'ın component tabanlı yapısı, tekrar eden UI parçalarını (kart, tablo satırı, grafik) yeniden kullanılabilir hale getiriyor. Vite, Create-React-App'e göre çok daha hızlı başlatma/yenileme (hot reload) sağlıyor — geliştirme sırasında saniyeler içinde değişiklik görebiliyoruz. |
| Grafikler | **Recharts** | React ile doğal entegre olan, SVG tabanlı, az kod ile responsive grafik üreten bir kütüphane. |
| PDF üretimi | **ReportLab + Matplotlib** | ReportLab PDF'in düzenini (tablo, başlık, sayfa) kod ile tam kontrol ederek oluşturur; Matplotlib ise grafikleri PNG olarak üretip PDF'e gömer. Alternatif olan "HTML'i PDF'e çevir" (wkhtmltopdf/weasyprint) yerine bunu seçtik çünkü PDF içeriği tablo+grafik ağırlıklı ve programatik/deterministik üretim istiyorduk. |

---

## 4. Veritabanı tasarımı

İki tablo var:

**`materials`** (malzemeler): id, name (benzersiz), unit (ton/m³/adet), current_stock, critical_threshold, co2_factor, created_at

**`stock_movements`** (stok hareketleri): id, material_id (materials'a FK), movement_type ("giris"/"cikis"), quantity, note, supplier, created_by, created_at

**Neden bu şekilde ayrıldı (2 tablo, tek tablo değil):** Bu klasik bir **muhasebe defteri (ledger) deseni**. `current_stock`'u sadece bir sayı olarak tutup üzerine ekleyip çıkarabilirdik, ama o zaman *geçmişi* kaybederdik — "ne zaman, ne kadar, kim tarafından, hangi tedarikçiden" bilgisi olmazdı. Her hareketi ayrı bir satır olarak tutmak sayesinde:
1. Tahmin algoritması geçmiş tüketim eğilimine bakabiliyor,
2. Denetlenebilirlik var (kim ne zaman ne yaptı),
3. `current_stock` alanı yine de var — her sorguda tüm hareketleri toplamak yerine (performans), güncel stok ayrı bir alanda tutulup her hareket sonrası güncelleniyor (denormalizasyon, bilinçli bir performans/basitlik tercihi).

**Neden `unit` alanı serbest metin (ton/m³/adet) ve neden bu önemli bir hata kaynağı oldu:** Farklı malzemeler farklı birimlerle ölçülüyor (demir cevheri ton, doğalgaz m³, yedek parça adet). Toplam tüketim hesaplarken (`/api/summary`, karşılaştırma grafiği, PDF rapor) birimleri karıştırıp toplamak anlamsız sonuç veriyordu (örn. "4181 ton" görünen sayı aslında ton+m³+adet karışımıydı). Bunu `Material.unit == "ton"` filtresiyle üç ayrı yerde düzelttik ve regresyon testleri (pytest) ekledik ki bu hata bir daha sessizce geri gelmesin.

---

## 5. Kimlik doğrulama (Auth) — bilinçli basitleştirme

Sistemde tek bir sabit kullanıcı var (`.env` dosyasında tanımlı kullanıcı adı/şifre), giriş başarılı olunca sabit bir "Bearer token" dönülüyor ve sonraki tüm istekler bu token'ı `Authorization` header'ında taşıyor.

**Neden JWT/OAuth değil:** Bu bir üretim (production) sistemi değil, tek kullanıcılı bir staj demosu. Gerçek bir kullanıcı yönetimi (kayıt, şifre sıfırlama, roller, oturum süresi) kapsam dışı bırakıldı çünkü projenin değeri stok takibi/tahmin kısmında; auth karmaşıklığı buraya harcanacak zamanı asıl işlevden çalardı. **Bu net bir sınır — sunumda sorulursa "gerçek bir üretime taşınırken JWT + rol bazlı yetkilendirme eklenir" diye cevaplanabilir.**

---

## 6. Tahmin (Forecasting) — Regresyon neden ve nasıl kullanıldı (en kritik teknik kısım)

### Ne yapıyor?

`backend/app/forecast.py` içindeki `forecast_days_remaining()` fonksiyonu şunu yapıyor:

1. Son 90 günün her günü için toplam **çıkış** miktarını hesaplıyor (`compute_daily_consumption`) → gün bazlı bir seri elde ediyoruz: `[gün1: 12 ton, gün2: 0 ton, gün3: 8 ton, ...]`
2. Bu günlük değerlerin **kümülatif toplamını** (cumulative sum) alıyoruz → `[12, 12, 20, ...]` — yani "o güne kadar toplam ne kadar tüketildi".
3. X ekseni = gün indeksi (0, 1, 2, ... 89), Y ekseni = kümülatif tüketim olacak şekilde **basit lineer regresyon** (`sklearn.linear_model.LinearRegression`) uyguluyoruz: `y = m·x + b`
4. Bulunan eğim (**m**, `model.coef_[0]`) = **günlük ortalama tüketim hızı**.
5. `kalan_gün = mevcut_stok / günlük_tüketim_hızı`

### Neden ham günlük veriler yerine kümülatif toplam kullanıldı?

Günlük tüketim çok dalgalı/gürültülü (bazı gün 0, bazı gün yüksek sevkiyat). Kümülatif toplam **monoton artan ve düzgün (smooth)** bir çizgi oluşturuyor; bu çizginin eğimi = ortalama tüketim hızı. Bu, gürültülü günlük verilerin ortalamasını almanın matematiksel olarak temiz bir yolu — aynı zamanda tek bir "kaç gün sonra biter" çizgisi elde etmeyi kolaylaştırıyor (regresyon doğrusunu ileri uzatınca stokun 0'a ineceği nokta = tahmini bitiş günü mantığıyla aynı).

### Neden Lineer Regresyon seçildi, ARIMA/LSTM/Prophet gibi daha "gelişmiş" yöntemler değil?

- **Veri miktarı sınırlı:** 90 günlük veri, mevsimsellik veya karmaşık örüntü yakalamak için yeterli değil. ARIMA veya LSTM gibi yöntemler çok daha fazla veri ve hiperparametre ayarı gerektirir; bu veri hacminde **aşırı öğrenme (overfitting)** riski yüksek olur ve sonuç daha kötü olabilir.
- **Yorumlanabilirlik:** Lineer regresyonun çıktısı (eğim = günlük tüketim hızı) hem koda hem kullanıcıya (rapora) doğrudan anlamlı bir sayı olarak yansıyor. LSTM gibi kara kutu modellerde "neden bu tahmin çıktı" sorusuna cevap vermek zor.
- **Gerçek zamanlı/hafif hesaplama:** Her API isteğinde anında hesaplanabiliyor (milisaniyeler), ayrı bir model eğitme/saklama altyapısı gerekmiyor.
- **Problemin doğası zaten "trend":** Sorulan soru "tüketim ne zaman biter" — bu temelde bir trend ekstrapolasyonu, mevsimsel döngü tahmini değil. Lineer regresyon bu iş için doğru araç ölçeği.

**Kısacası: karmaşık model = daha iyi model değil. Veri miktarına ve soruya uygun en basit, en anlaşılır, en test edilebilir yöntemi seçmek mühendislik açısından doğru tercih.**

### Ek mantık — trend ve ortalamaya geri dönüş

- `daily_rate <= 0` ise (yani regresyon negatif/durgun eğim buluyorsa — örn. çok az hareket varsa), sistem basit ortalamaya (`avg_daily`) geri dönüyor. Bu bir **fallback (yedek plan)** — regresyon anlamsız bir sonuç verirse (örn. negatif tüketim hızı, ki bu mantıksız), daha basit ve güvenli bir tahmine geçiliyor.
- Ayrıca `compute_trend()` diye ayrı, daha basit bir fonksiyon var: son 7 günü, önceki 7 günle karşılaştırıp "artıyor/azalıyor/sabit" etiketi üretiyor (%5 eşik payı ile). Bu regresyondan bağımsız, dashboard'daki hızlı görsel trend ok işaretleri için kullanılıyor — regresyon "ne zaman biter" sorusuna, bu basit karşılaştırma da "yön ne" sorusuna cevap veriyor.

### Modelin sınırlamaları (dürüstçe bilinmesi gereken noktalar)

- Mevsimsellik yok (örn. kışın daha çok doğalgaz tüketimi gibi döngüsel etkiler modellenmiyor).
- Dışsal faktörler yok (üretim planı değişikliği, planlı bakım, arıza gibi olaylar tahmine yansımıyor).
- Ani sıçramalar (örn. büyük bir tek seferlik sevkiyat) ortalamayı geçici olarak bozabilir.
- Bu bilinçli bir kapsam kararı: **basit ve açıklanabilir bir taban çizgisi (baseline)** kurduk; gerçek üretimde zaman serisi mevsimsellik modelleri (SARIMA, Prophet) veya harici sinyallerle zenginleştirme bir sonraki adım olurdu.

---

## 7. Diğer modüller — ne, neden

### 7.1 Dashboard / Özet
Kritik malzeme sayısı, toplam malzeme sayısı, son 7 günlük toplam tüketim (ton bazlı, birim karışıklığı düzeltmesiyle) kart olarak gösteriliyor. **Neden:** Bir depo/üretim sorumlusunun sabah ilk bakacağı ekran — "bugün acil bir şey var mı" sorusuna 3 saniyede cevap vermeli. Bu yüzden detay değil, özet + uyarı önde.

### 7.2 Karşılaştırma grafiği
Malzemeler arası son N günlük tüketimi bar chart ile karşılaştırıyor — **sadece ton birimli malzemeler dahil** (yukarıdaki birim-karışıklığı hatasından sonra bilinçli bir filtre + kullanıcıya açıklayan bir alt yazı eklendi: "m³, adet birimli malzemeler farklı ölçekte olduğu için dahil edilmemiştir"). Bu şeffaflık önemli — veri neden eksik gösteriliyor, kullanıcıya açıkça söyleniyor.

### 7.3 Stok Hareketleri + Tedarikçi takibi
Her giriş hareketinde tedarikçi bilgisi tutuluyor (`supplier` alanı). Tedarikçi özeti endpoint'i, her tedarikçiden ne kadar/hangi malzeme geldiğini grupluyor. **Neden:** Gerçek bir stok sisteminde "bu malzeme kimden geliyor, en çok kimden alım yapıyoruz" sorusu tedarik zinciri kararları için önemli — basit ama gerçekçi bir ERP özelliği.

### 7.4 Çevresel Etki (CO2)
Her malzemenin bir `co2_factor` değeri var (kg CO2 / birim tüketim, sektör ortalamalarına dayalı kaba katsayı). Tüketim × faktör = tahmini emisyon. **Neden:** Stajın adı "ERP ve Çevresel Uygulamalar" — bu modül, stok verisinin çevresel etki analizine nasıl köprü kurabileceğini gösteren bir kavram kanıtı (proof of concept). **Önemli dürüstlük noktası:** Bu ölçülmüş gerçek bir emisyon değeri değil, kaba bir yaklaşım — arayüzde ve raporlarda bu açıkça belirtiliyor.

### 7.5 PDF Raporlama
Hem tek malzeme hem sistem geneli için PDF üretiliyor (tablo + trend grafiği). **Neden PDF:** Fabrika ortamında yöneticiye/vardiya raporunda paylaşılabilecek, ekran dışında da kullanılabilir somut bir çıktı formatı — dashboard'daki canlı veriyi "dondurup" paylaşılabilir hale getiriyor.

**Teknik not — Türkçe karakter sorunu:** PDF kütüphanesinin varsayılan fontu (Helvetica) ş/ğ/ı/ç/ö/ü karakterlerini düzgün basamıyordu (kutucuk/bozuk çıkıyordu). Çözüm: Matplotlib'in kendi paketiyle gelen DejaVu Sans fontunu PDF motoruna (ReportLab) manuel kayıt ettirdik. Ayrıca Türkçe dosya adlarının (örn. "Genel_Rapor_Ağustos.pdf") HTTP header'a konulması Latin-1 kodlama hatası veriyordu — RFC 5987 standardına uygun `filename*=UTF-8''...` header formatıyla çözüldü.

### 7.6 Otomatik veri tazeleme
Backend her başlatıldığında, `top_up_movements()` son kayıtlı hareketten bugüne kadarki boşluğu geçmiş ortalama tüketim hızına göre otomatik dolduruyor. **Neden:** Demo/sunum verisinin her zaman "güncel/canlı" görünmesi için — kullanıcı bir hafta sonra sisteme girdiğinde veri bir hafta önce donmuş kalmıyor, sanki gerçek zamanlı işliyormuş gibi görünüyor.

---

## 8. Test stratejisi

- **41 pytest testi**, API uç noktaları (materials, movements, alerts/summary, forecast, report, environmental, auth) ve tahmin mantığını kapsıyor.
- **İzole in-memory SQLite** kullanılıyor — gerçek PostgreSQL veritabanına asla dokunmuyor (`conftest.py`'de `DATABASE_URL` test başlamadan önce sqlite'a çevriliyor, `database.py` bu durumda `StaticPool` kullanıyor).
- **Neden gerçek DB değil sqlite ile test:** Testler hızlı çalışsın (disk/network yok, RAM'de), her test öncesi tablo sıfırlansın (`reset_db` fixture, `autouse=True`) ve **hiçbir demo veri riske girmesin** diye. Bu ayrım bir yerde pahalıya mal oldu: geliştirme sırasında bir ara test verisiyle gerçek veri karışıp gerçek bir stok hareketi kazayla silinmişti — bu tecrübeden sonra test/gerçek veri ayrımına daha da dikkat edildi.
- Regresyon (birim karışıklığı) hatası bulunduğunda, sadece kodu düzeltmekle kalmayıp **aynı hatayı bir daha yakalayacak testler** eklendi (`test_summary_consumption_7d_ignores_non_ton_units`, `test_consumption_comparison_excludes_non_ton_units`).

---

## 9. Bilinçli sınırlamalar (sunumda dürüstçe söylenebilecek noktalar — bunları saklamak yerine "bildiğimi" göstermek güven verir)

- Tek kullanıcılı, basit auth — çoklu kullanıcı/rol sistemi yok.
- Tahmin modeli mevsimsellik/dış faktör görmüyor, sadece geçmiş trend ekstrapolasyonu.
- CO2 faktörleri gerçek ölçüm değil, kaba sektör ortalaması yaklaşımı.
- Tek depo/lokasyon varsayımı — çoklu depo/transfer yok.
- Veritabanı yerel (local) — bulut/yüksek erişilebilirlik (HA) kurulumu yok.

---

## 10. Muhtemel mühendis soruları ve cevapları (Q&A)

**S: Neden lineer regresyon, neden ARIMA veya makine öğrenmesi tabanlı (LSTM vb.) bir zaman serisi modeli kullanmadınız?**
C: 90 günlük, tek değişkenli ve nispeten düzensiz veri hacmiyle ARIMA/LSTM gibi modeller hem aşırı öğrenmeye (overfitting) hem de gereksiz karmaşıklığa yol açardı. Sorunun doğası "genel eğilim ne" — bu bir trend ekstrapolasyon problemi, mevsimsel döngü tahmini değil. Lineer regresyon hem yeterli hem yorumlanabilir hem de anlık hesaplanabilir.

**S: Model negatif ya da anlamsız bir eğim bulursa ne oluyor?**
C: Kod bunu kontrol ediyor (`daily_rate <= 0`) ve o durumda basit aritmetik ortalamaya düşüyor (fallback); veri hiç yoksa "tahmin yapılamıyor" mesajı dönüyor, hata fırlatmıyor.

**S: Birden fazla kullanıcı aynı anda stok hareketi girerse veri tutarlılığı nasıl korunuyor?**
C: PostgreSQL işlemleri (transaction) SQLAlchemy session üzerinden atomik şekilde yürütülüyor; şu anki ölçekte (tek kullanıcı demo) yarış durumu (race condition) pratik bir risk değil, ama üretime taşınırken satır kilitleme (`SELECT ... FOR UPDATE`) veya optimistic locking eklenmesi gerekir.

**S: SQL injection'a karşı korumalı mı?**
C: Evet — tüm sorgular SQLAlchemy ORM üzerinden parametreli olarak üretiliyor, hiçbir yerde ham string birleştirmesiyle SQL yazılmıyor.

**S: Auth neden JWT değil?**
C: Kapsam bilinçli olarak sınırlı tutuldu — bu bir üretim kimlik doğrulama sistemi değil, demo amaçlı sabit token. Gerçek dağıtımda JWT + rol bazlı yetkilendirme + şifre hash'leme (bcrypt) eklenir.

**S: Veri kaybı riski var mı, yedekleme var mı?**
C: Yerel PostgreSQL kurulumu bu haliyle otomatik yedekleme içermiyor — bu bir demo/staj ortamı. Üretimde düzenli pg_dump/point-in-time recovery eklenir.

**S: Neden ORM (SQLAlchemy), neden ham SQL değil?**
C: Geliştirme hızı, tip güvenliği, SQL injection'a karşı doğal koruma ve veritabanı motoru değişse bile (örn. testte SQLite, gerçekte PostgreSQL) aynı kodun çalışabilmesi için.

**S: CO2 hesaplaması bilimsel olarak doğru mu?**
C: Hayır, gerçek ölçüm değil — malzeme başına kaba bir katsayı (kg CO2/birim) ile tüketim çarpılıyor. Amacı kesin karbon muhasebesi değil, stok verisinin çevresel etki analiziyle nasıl ilişkilendirilebileceğini göstermek (kavram kanıtı).

**S: Test kapsamı ne kadar, neyi test etmediniz?**
C: 41 test; tüm API uç noktaları, auth, tahmin mantığı, birim tutarlılığı (regresyon testleri) kapsanıyor. Frontend tarafında otomatik test yok (manuel/görsel test yapıldı) — zaman kısıtı nedeniyle backend'e öncelik verildi çünkü iş mantığının (hesaplamalar, veri bütünlüğü) kritik kısmı orada.

**S: Sistem kaç malzeme/kaç hareketle test edildi, büyük veri hacminde performans nasıl?**
C: Demo verisi 9 malzeme × 90 günlük hareket geçmişi ölçeğinde — bu ölçekte gecikme yok. Çok daha büyük hacimde (milyonlarca hareket) tahmin sorgusundaki `SELECT` + Python tarafı toplama işlemleri veritabanı tarafında indeksleme ve/veya materialized view ile optimize edilmesi gerekir; şu an `created_at` üzerinde aralık sorgusu yapılıyor ama ayrı bir indeks tanımlanmadı.

**S: Neden React, neden Vue/Angular değil?**
C: Ekosistem büyüklüğü (Recharts gibi kütüphaneler), component tabanlı düşünmenin dashboard/liste/form ağırlıklı bu projeye uygunluğu ve kişisel/sektörel yaygınlık nedeniyle tercih edildi — bu ölçekte üç framework de teknik olarak yeterli olurdu, bu bir ekosistem/tercih kararıydı.

**S: Stok miktarı negatife düşebilir mi (aşırı çıkış girilirse)?**
C: Şu anki haliyle giriş formunda ekstra bir üst sınır kontrolü yok — bu bilinen bir geliştirme alanı; üretimde çıkış miktarının mevcut stoktan büyük olmasını engelleyen bir doğrulama eklenmesi gerekir.

---

## Hızlı özet (30 saniyelik anlatım için)

"Erdemir'de kullanılabilecek bir stok takip ve tahmin sistemi geliştirdim: FastAPI + PostgreSQL backend, React frontend. Sistem sadece anlık stok göstermiyor, geçmiş tüketim verisine lineer regresyon uygulayarak 'bu malzeme kaç gün sonra biter' tahmini yapıyor ve kritik seviyeye düşen malzemeler için otomatik uyarı üretiyor. Ayrıca tedarikçi takibi, CO2 emisyon tahmini ve PDF raporlama gibi ek modüller ekledim. Regresyonu bilinçli seçtim — veri hacmi ve problemin 'trend tahmini' doğası için en basit, en yorumlanabilir yöntem buydu; daha karmaşık modeller bu ölçekte overfitting riski taşırdı."
