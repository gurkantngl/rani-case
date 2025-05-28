# 🎯 Rani Mobilya Çağrı Merkezi LLM Projesi

Bu proje, Rani Mobilya çağrı merkezi verilerini kullanarak üretici yapay zeka (LLM) teknolojilerini entegre eden çözümler geliştirmektedir.

## 📊 Proje Özeti

- **Veri**: 12 günlük çağrı merkezi chat verileri (~44K mesaj, 1862 konuşma)
- **Yaklaşımlar**: RAG, Prompt Engineering, Fine-Tuning Dataset Hazırlığı
- **Teknolojiler**: Python, Pandas, Scikit-learn, TF-IDF, JSON

## 🚀 Geliştirilen Sistemler

### 1. 📁 Veri Hazırlama Pipeline (`data_preprocessing.py`)

✅ **Tamamlanan Özellikler:**
- Kişisel bilgi maskeleme (telefon, email, kart numaraları)
- Müşteri/agent rol ayrımı
- HTML tag temizleme ve text normalizasyonu
- Konuşma bazlı analiz ve istatistikler
- Kaliteli veri filtreleme

```bash
python data_preprocessing.py
```

**Çıktılar:**
- `processed_chat_data.csv` - Temizlenmiş veri (22,926 mesaj)
- `conversation_stats.csv` - Konuşma istatistikleri

### 2. 🔍 RAG (Retrieval-Augmented Generation) Sistemi (`rag_system.py`)

✅ **Tamamlanan Özellikler:**
- TF-IDF tabanlı semantic search
- Konuşma bağlamı ile bilgi bankası oluşturma (~7K entry)
- Müşteri sorularına otomatik yanıt üretme
- Cosine similarity ile en relevan bilgileri bulma
- Sık sorulan konular analizi

```bash
python rag_system.py
```

**Test Sonuçları:**
- Kargo soruları: %51 güven skoru
- Ürün soruları: %63 güven skoru
- Teslimat soruları: %37 güven skoru

### 3. 🎭 Prompt Mühendisliği Sistemi (`prompt_engineering.py`)

✅ **Tamamlanan Özellikler:**
- 5 farklı senaryo şablonu (kargo, iade, ürün bilgisi, sipariş takip, genel destek)
- Otomatik senaryo tespiti
- Bağlam-aware prompt oluşturma
- Yanıt kalitesi değerlendirme sistemi
- Eğitim örneği oluşturma

```bash
python prompt_engineering.py
```

**Senaryolar:**
- `kargo_sorgulama`: Teslimat ve kargo durumu
- `iade_degisim`: İade/değişim süreçleri
- `urun_bilgisi`: Ürün özellikleri ve bilgileri
- `siparis_takip`: Sipariş durumu takibi
- `genel_destek`: Genel müşteri hizmetleri

### 4. 📚 Fine-Tuning Dataset Hazırlığı (`fine_tuning_dataset.py`)

✅ **Tamamlanan Özellikler:**
- Konuşma çiftlerinden input-output eşleşmeleri (~5.9K çift)
- Alpaca formatında eğitim verisi
- ChatML formatında eğitim verisi
- Senaryoya özel veri setleri
- Train/Validation/Test bölme (%80/%10/%10)
- Kalite filtreleme ve veri temizleme

```bash
python fine_tuning_dataset.py
```

**Çıktılar:**
- `alpaca_train.json` - Alpaca formatı eğitim verisi (4,304 örnek)
- `alpaca_val.json` - Validation verisi (538 örnek)
- `chatml_train.jsonl` - ChatML formatı (4,264 örnek)
- `scenario_*.json` - Senaryoya özel veri setleri

### 5. 📊 Model Değerlendirme Sistemi (`model_evaluation.py`)

✅ **Tamamlanan Özellikler:**
- Çok boyutlu performans değerlendirmesi
- Yanıt süresi, doğruluk, memnuniyet, tutarlılık, maliyet metrikleri
- RAG vs Prompt Engineering vs Fine-Tuning karşılaştırması
- Simülasyon tabanlı müşteri memnuniyet skoru
- Hibrit yaklaşım önerileri

```bash
python model_evaluation.py
```

## 📈 Analiz Sonuçları

### Veri İstatistikleri
- **Toplam Mesaj**: 22,926 (filtrelenmiş)
- **Konuşma Sayısı**: 1,862
- **Ortalama Mesaj/Konuşma**: 12.3
- **Kanal Dağılımı**: 
  - WhatsApp: %69 (15,793 mesaj)
  - Web Sohbeti: %26 (5,935 mesaj)
  - Instagram: %1.6 (371 mesaj)

### Sık Sorulan Konular
1. **Ürün**: 1,326 mesaj (%34%)
2. **Kargo**: 1,026 mesaj (%26%)
3. **Sipariş**: 901 mesaj (%23%)
4. **Fiyat**: 818 mesaj (%21%)
5. **İade**: 147 mesaj (%4%)

## 🛠️ Teknik Detaylar

### Kullanılan Kütüphaneler
```txt
pandas>=1.5.0
scikit-learn>=1.2.0
numpy>=1.21.0
```

### Veri İşleme Pipeline
1. **Veri Yükleme**: CSV dosyalarının birleştirilmesi
2. **Temizleme**: HTML tagları, fazla boşluklar
3. **Maskeleme**: Kişisel bilgilerin anonimleştirilmesi
4. **Filtreleme**: Kaliteli mesajların seçilmesi
5. **Analiz**: İstatistiksel özet çıkarma

### RAG Sistemi Mimarisi
```
Müşteri Sorusu -> TF-IDF Vektörizasyon -> Cosine Similarity -> 
En İyi Eşleşmeler -> Yanıt Şablonu -> Final Yanıt
```

## 🎯 Kullanım Önerileri

### Hızlı Başlangıç (RAG)
1. Mevcut veri ile RAG sistemi kurun
2. Temel sorulara otomatik yanıt vermek için kullanın
3. Agent'lar için yanıt önerileri sağlayın

### Orta Vadeli Gelişim (Prompt Engineering)
1. Spesifik senaryolar için prompt'ları optimize edin
2. A/B test ile en etkili prompt'ları belirleyin
3. Few-shot örneklerini artırın

### Uzun Vadeli Hedef (Fine-Tuning)
1. Daha fazla kaliteli veri toplayın (50K+ örnek)
2. Domain-specific model eğitin
3. Production'da sürekli öğrenme sistemini kurun

## 📋 Sonuç ve Öneriler

### 🥇 En İyi Yaklaşım: RAG Sistemi
**Avantajları:**
- Hızlı implementasyon
- Mevcut veri ile çalışma
- Düşük maliyet
- Sürekli güncelleme imkanı

**İyileştirme Alanları:**
- Semantic search algoritması
- Daha fazla veri ile knowledge base genişletme
- Response template optimizasyonu

### 🔄 Hibrit Yaklaşım Önerisi
1. **Phase 1**: RAG sistemi ile başlayın (1-2 ay)
2. **Phase 2**: Prompt Engineering optimizasyonu (2-3 ay)
3. **Phase 3**: Fine-tuning için veri toplama (6+ ay)
4. **Phase 4**: Production A/B testing

### 📊 Beklenen İyileştirmeler
- **Yanıt Süresi**: %40 azalma (5-6 saniye -> 3 saniye)
- **Doğruluk**: %25 artış (%60 -> %75)
- **Agent Verimliliği**: %30 artış
- **Müşteri Memnuniyeti**: %15 artış

## 🔧 Geliştirme Notları

### Gelecek Güncellemeler
- [ ] Türkçe BERT modeli entegrasyonu
- [ ] Real-time learning sistemi
- [ ] Multi-modal destek (resim, dosya)
- [ ] Sentiment analizi entegrasyonu
- [ ] Advanced metrik sistemleri

### Bilinen Limitasyonlar
- Veri seti boyutu (12 gün, 3 aylık hedefin %13'ü)
- Kişisel bilgi maskeleme basit regex tabanlı
- Müşteri memnuniyet simülasyonu (gerçek feedback gerekli)
- Prompt Engineering manuel senaryo tespiti

## 📞 İletişim

Bu proje Rani Mobilya çağrı merkezi verimliliğini artırmak amacıyla geliştirilmiştir. Teknik sorular ve geliştirme önerileri için ilgili ekip ile iletişime geçebilirsiniz.

---
*Son güncelleme: 2025-01-05* 