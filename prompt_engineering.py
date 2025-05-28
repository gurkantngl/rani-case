import pandas as pd
import json
from datetime import datetime
from collections import defaultdict

class PromptEngineer:
    """Main Prompt Engineering class that main.py expects"""
    
    def __init__(self):
        """Initialize Prompt Engineer"""
        self.scenarios = {
            'siparis_takip': {
                'system': "Sen Rani Mobilya'nın sipariş takip uzmanısın. Nazik ve profesyonel yanıt ver.",
                'response': "Sipariş durumunuzu kontrol edebilmem için sipariş numaranızı paylaşabilir misiniz? Bu bilgi ile size güncel durumu ve tahmini teslimat tarihini verebilirim. 📦"
            },
            'iade_degisim': {
                'system': "Sen Rani Mobilya'nın iade süreçleri uzmanısın.",
                'response': "Tabii ki yardımcı olabilirim! İade sürecini başlatabilmek için ürünün hangi nedenle iade edilmek istendiğini öğrenebilir miyim? Ayrıca ürün orijinal ambalajında mı? 🔄"
            },
            'urun_bilgisi': {
                'system': "Sen Rani Mobilya'nın ürün uzmanısın.",
                'response': "Hangi ürünümüz hakkında bilgi almak istiyorsunuz? Ürün linkini veya adını paylaşırsanız size detaylı bilgileri verebilirim. 🛋️"
            },
            'kargo_sorgulama': {
                'system': "Sen Rani Mobilya'nın kargo uzmanısın.",
                'response': "Kargo durumunuzu kontrol edebilmem için sipariş numaranızı paylaşabilir misiniz? Bu şekilde size daha detaylı bilgi verebilirim. 🚚"
            },
            'genel_destek': {
                'system': "Sen Rani Mobilya'nın müşteri hizmetleri uzmanısın.",
                'response': "Merhaba! Rani Mobilya müşteri hizmetlerine hoş geldiniz. Size nasıl yardımcı olabilirim? Lütfen sorunuzu detaylı bir şekilde açıklayın. 😊"
            }
        }

    def detect_scenario(self, message: str) -> str:
        """Mesajdan senaryoyu tespit et"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['sipariş', 'order', 'takip', 'ne zaman', 'gelir']):
            return 'siparis_takip'
        elif any(word in message_lower for word in ['iade', 'return', 'değişim', 'geri']):
            return 'iade_degisim'
        elif any(word in message_lower for word in ['ürün', 'product', 'ölçü', 'boyut', 'fiyat', 'bilgi']):
            return 'urun_bilgisi'
        elif any(word in message_lower for word in ['kargo', 'cargo', 'teslimat', 'adres']):
            return 'kargo_sorgulama'
        else:
            return 'genel_destek'

    def generate_response(self, message: str) -> dict:
        """Prompt engineering ile yanıt üret"""
        scenario = self.detect_scenario(message)
        scenario_data = self.scenarios.get(scenario, self.scenarios['genel_destek'])
        
        return {
            "response": scenario_data['response'],
            "scenario": scenario,
            "confidence": 0.85,
            "method": "PROMPT_ENGINEERING"
        }

class CallCenterPromptEngine:
    """Çağrı Merkezi Prompt Mühendisliği Sistemi"""
    
    def __init__(self, data_file='processed_chat_data.csv'):
        try:
            self.df = pd.read_csv(data_file)
        except FileNotFoundError:
            self.df = pd.DataFrame()  # Empty dataframe if file not found
        self.scenario_templates = self._load_scenario_templates()
        self.system_prompts = self._create_system_prompts()
        
    def _load_scenario_templates(self):
        """Çağrı merkezi senaryoları için prompt şablonları"""
        
        templates = {
            'kargo_sorgulama': {
                'system_prompt': """Sen Rani Mobilya'nın profesyonel müşteri hizmetleri temsilcisisin.
Kargo durumu sorularını yanıtlarken:
- Nazik ve yardımcı ol
- Sipariş numarasını sor
- Kargo takip bilgisi ver
- Tahmini teslimat süresi belirt""",
                
                'user_template': "Müşteri: {customer_message}\nBağlam: {context}",
                
                'examples': [
                    {
                        'input': "Siparişim ne zaman gelir?",
                        'output': "Merhaba! Sipariş durumunuzu kontrol edebilmem için sipariş numaranızı paylaşabilir misiniz? Bu şekilde size daha detaylı bilgi verebilirim."
                    }
                ]
            },
            
            'iade_degisim': {
                'system_prompt': """Sen Rani Mobilya'nın iade süreçlerinde uzman müşteri hizmetleri temsilcisisin.
İade/değişim işlemlerinde:
- Ürünün durumunu sor
- İade nedenini öğren
- İade şartlarını açıkla
- Süreç adımlarını detaylandır""",
                
                'user_template': "Müşteri: {customer_message}\nÜrün: {product_info}\nSipariş tarihi: {order_date}",
                
                'examples': [
                    {
                        'input': "Bu ürünü iade etmek istiyorum",
                        'output': "Tabii ki yardımcı olabilirim. İade sürecini başlatabilmek için ürünün hangi nedenle iade edilmek istendiğini öğrenebilir miyim? Ayrıca ürün orijinal ambalajında mı?"
                    }
                ]
            },
            
            'urun_bilgisi': {
                'system_prompt': """Sen Rani Mobilya'nın ürün uzmanı müşteri hizmetleri temsilcisisin.
Ürün sorularında:
- Teknik özellikleri detaylandır
- Ölçü bilgilerini ver
- Renk/materyal seçeneklerini belirt
- Montaj bilgisi ver""",
                
                'user_template': "Müşteri: {customer_message}\nÜrün kategori: {category}",
                
                'examples': [
                    {
                        'input': "Bu ürünün ölçüleri nedir?",
                        'output': "Hangi ürünümüz hakkında bilgi almak istiyorsunuz? Ürün linkini veya adını paylaşırsanız size detaylı ölçü bilgilerini verebilirim."
                    }
                ]
            },
            
            'siparis_takip': {
                'system_prompt': """Sen Rani Mobilya'nın sipariş takip uzmanı müşteri hizmetleri temsilcisisin.
Sipariş durumu sorularında:
- Sipariş numarasını doğrula
- Mevcut durumu açıkla
- Sonraki adımları belirt
- Tahmini zaman ver""",
                
                'user_template': "Müşteri: {customer_message}\nSipariş No: {order_number}\nDurum: {status}",
                
                'examples': [
                    {
                        'input': "Siparişim nerede?",
                        'output': "Sipariş durumunuzu kontrol edebilmem için sipariş numaranızı paylaşabilir misiniz? Bu bilgi ile size güncel durumu ve tahmini teslimat tarihini verebilirim."
                    }
                ]
            },
            
            'genel_destek': {
                'system_prompt': """Sen Rani Mobilya'nın deneyimli müşteri hizmetleri temsilcisisin.
Genel müşteri hizmetlerinde:
- Sıcak ve samimi ol
- Sorunları dinle
- Çözüm odaklı yaklaş
- Gerekirse ilgili departmana yönlendir""",
                
                'user_template': "Müşteri: {customer_message}\nKanal: {channel}\nSaat: {time}",
                
                'examples': [
                    {
                        'input': "Merhabalar, yardım istiyorum",
                        'output': "Merhaba! Rani Mobilya müşteri hizmetlerine hoş geldiniz. Size nasıl yardımcı olabilirim? Lütfen sorunuzu detaylı bir şekilde açıklayın."
                    }
                ]
            }
        }
        
        return templates
    
    def _create_system_prompts(self):
        """Genel sistem prompt'ları"""
        
        return {
            'base_agent': """Sen Rani Mobilya'nın profesyonel müşteri hizmetleri temsilcisisin.

TEMEL KURALLAR:
- Her zaman nazik, yardımsever ve profesyonel ol
- Türkçe konuş, resmi ama samimi dil kullan
- Müşterinin sorununu tamamen anlayıp çöz
- Bilmediğin konularda tahmin yapma, uzman arkadaşlara yönlendir
- Her yanıtta müşteri memnuniyetini ön planda tut

RANI MOBİLYA HAKKINDA:
- Kaliteli ve modern mobilya üreticisi
- Hızlı teslimat ve montaj hizmeti
- 14 gün iade garantisi
- Whatsapp, web sitesi ve Instagram'dan destek
- Mesai saatleri: Hafta içi ve Cumartesi 09:00-23:30

YANIT STİLİ:
- Kısa ve anlaşılır cümleler
- Müşterinin ismini kullan (varsa)
- Emojiler kullanarak sıcaklık kat
- Sonraki adımları net belirt""",

            'escalation_manager': """Sen Rani Mobilya'nın müşteri hizmetleri süpervizörüsün.
Karmaşık durumlarda devreye giriyorsun.

YAKLAŞIMIN:
- Empati ile yaklaş
- Sorunu köküne kadar anla
- Hızlı çözüm öner
- Müşteriyi elde tutmaya odaklan
- Gerekirse özel indirim/avantaj öner

SÜREÇLERİN:
- Acil durumlar için özel kargo
- İade/değişimlerde esneklik
- Mağduriyet durumlarında kompanzasyon
- Üst yönetim onayı alabilme""",

            'quality_checker': """Sen Rani Mobilya müşteri hizmetleri kalite kontrol uzmanısın.
Agent yanıtlarını değerlendiriyorsun.

DEĞERLENDİRME KRİTERLERİ:
1. Yanıt süresi (2 dakika hedef)
2. Ton ve üslup (nazik/profesyonel)
3. Çözüm odaklılık
4. Bilgi doğruluğu
5. Müşteri memnuniyeti

SCORING:
- Mükemmel (9-10): Tüm kriterleri karşılıyor
- İyi (7-8): Çoğu kriteri karşılıyor
- Geliştirilmeli (5-6): Bazı eksiklikler var
- Yetersiz (<5): Ciddi problemler var"""
        }
    
    def detect_scenario(self, message):
        """Mesajdan senaryoyu tespit et"""
        
        message_lower = message.lower()
        
        # Anahtar kelime bazlı tespit
        if any(word in message_lower for word in ['kargo', 'teslimat', 'gönder', 'ulaş']):
            return 'kargo_sorgulama'
        elif any(word in message_lower for word in ['iade', 'değişim', 'geri']):
            return 'iade_degisim'
        elif any(word in message_lower for word in ['ürün', 'ölçü', 'renk', 'özellik']):
            return 'urun_bilgisi'
        elif any(word in message_lower for word in ['sipariş', 'order', 'takip']):
            return 'siparis_takip'
        else:
            return 'genel_destek'
    
    def generate_prompt(self, customer_message, context=None):
        """Müşteri mesajı için uygun prompt oluştur"""
        
        scenario = self.detect_scenario(customer_message)
        template = self.scenario_templates[scenario]
        
        # Sistem prompt'ı
        system_prompt = template['system_prompt']
        
        # Kullanıcı prompt'ı
        user_vars = {
            'customer_message': customer_message,
            'context': context or "İlk iletişim",
            'category': "Genel",
            'order_number': "Belirtilmedi",
            'status': "Sorgulanıyor",
            'product_info': "Belirtilmedi",
            'order_date': "Belirtilmedi",
            'channel': "Whatsapp",
            'time': datetime.now().strftime("%H:%M")
        }
        
        user_prompt = template['user_template'].format(**user_vars)
        
        return {
            'scenario': scenario,
            'system_prompt': system_prompt,
            'user_prompt': user_prompt,
            'examples': template['examples'],
            'base_system': self.system_prompts['base_agent']
        }
    
    def evaluate_response(self, response, criteria=['tone', 'helpfulness', 'accuracy']):
        """Yanıtı değerlendir"""
        
        scores = {}
        
        # Basit kural bazlı değerlendirme
        if 'tone' in criteria:
            # Naziklik kontrolü
            polite_words = ['lütfen', 'teşekkür', 'merhaba', 'iyi günler', 'yardımcı']
            tone_score = sum(1 for word in polite_words if word in response.lower()) * 2
            scores['tone'] = min(10, tone_score)
        
        if 'helpfulness' in criteria:
            # Yardımcılık kontrolü
            helpful_phrases = ['yardımcı olabilirim', 'kontrol ede', 'bilgi ver', 'çözüm']
            help_score = sum(1 for phrase in helpful_phrases if phrase in response.lower()) * 2.5
            scores['helpfulness'] = min(10, help_score)
        
        if 'accuracy' in criteria:
            # Doğruluk (basit uzunluk kontrolü)
            if len(response) > 20 and len(response) < 300:
                scores['accuracy'] = 8
            else:
                scores['accuracy'] = 5
        
        # Genel skor
        scores['overall'] = sum(scores.values()) / len(scores)
        
        return scores
    
    def create_training_examples(self):
        """Eğitim örnekleri oluştur"""
        
        training_data = []
        
        # Her senaryo için örnekler
        for scenario, template in self.scenario_templates.items():
            for example in template['examples']:
                training_data.append({
                    'scenario': scenario,
                    'system': template['system_prompt'],
                    'user': example['input'],
                    'assistant': example['output']
                })
        
        return training_data

def demo_prompt_engineering():
    """Prompt mühendisliği demo'su"""
    
    print("🚀 PROMPT MÜHENDİSLİĞİ DEMO'SU")
    print("=" * 60)
    
    # Prompt engine'i başlat
    engine = CallCenterPromptEngine()
    
    # Test mesajları
    test_messages = [
        "Merhaba, siparişim ne zaman gelir?",
        "Bu ürünü iade etmek istiyorum, nasıl yapabilirim?",
        "TV ünitesinin ölçüleri nedir?",
        "Kargo durumumu öğrenebilir miyim?",
        "Yardım istiyorum"
    ]
    
    print("\n🎯 SENARYO TESPİTİ VE PROMPT ÜRETİMİ:")
    print("=" * 60)
    
    for msg in test_messages:
        print(f"\n📱 Müşteri: {msg}")
        
        prompt_data = engine.generate_prompt(msg)
        
        print(f"🎭 Senaryo: {prompt_data['scenario']}")
        print(f"🤖 Sistem Prompt: {prompt_data['system_prompt'][:100]}...")
        print(f"👤 Kullanıcı Prompt: {prompt_data['user_prompt']}")
        print(f"💡 Örnek Yanıt: {prompt_data['examples'][0]['output']}")
        
        # Örnek yanıtı değerlendir
        scores = engine.evaluate_response(prompt_data['examples'][0]['output'])
        print(f"📊 Değerlendirme: {scores}")
        print("-" * 40)
    
    # Eğitim verisi oluştur
    print(f"\n📚 EĞİTİM VERİSİ:")
    training_data = engine.create_training_examples()
    print(f"Toplam {len(training_data)} eğitim örneği oluşturuldu")
    
    # JSON formatında kaydet
    with open('training_prompts.json', 'w', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
    
    print("✅ training_prompts.json dosyası oluşturuldu")

if __name__ == "__main__":
    demo_prompt_engineering() 