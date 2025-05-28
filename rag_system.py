import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
from collections import defaultdict

class CallCenterRAG:
    """Çağrı Merkezi RAG (Retrieval-Augmented Generation) Sistemi"""
    
    def __init__(self, data_file='processed_chat_data.csv'):
        self.df = pd.read_csv(data_file)
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words=None  # Türkçe stop words eklenebilir
        )
        self.vectors = None
        self.knowledge_base = None
        self.build_knowledge_base()
        
    def build_knowledge_base(self):
        """Agent cevaplarından bilgi bankası oluştur"""
        print("🏗️ Bilgi bankası oluşturuluyor...")
        
        # Sadece agent mesajlarını al (çözüm içeren)
        agent_messages = self.df[self.df['role'] == 'agent'].copy()
        
        # Konuşma bağlamları ile birleştir
        knowledge_entries = []
        
        for conv_id in agent_messages['conversation_id'].unique():
            conv_data = self.df[self.df['conversation_id'] == conv_id].sort_values('created_time')
            
            customer_msgs = []
            agent_responses = []
            
            for _, row in conv_data.iterrows():
                if row['role'] == 'customer':
                    customer_msgs.append(row['message_content_masked'])
                elif row['role'] == 'agent':
                    if customer_msgs:  # Öncesinde müşteri mesajı varsa
                        # Bağlam: müşteri sorunu + agent çözümü
                        context = " ".join(customer_msgs[-3:])  # Son 3 müşteri mesajı
                        response = row['message_content_masked']
                        
                        knowledge_entries.append({
                            'conversation_id': conv_id,
                            'customer_context': context,
                            'agent_response': response,
                            'channel': row['channel_name'],
                            'combined_text': f"{context} {response}"
                        })
                        customer_msgs = []  # Reset
        
        self.knowledge_base = pd.DataFrame(knowledge_entries)
        print(f"✅ {len(self.knowledge_base)} bilgi girdisi oluşturuldu")
        
        # TF-IDF vektörlerini oluştur
        if len(self.knowledge_base) > 0:
            self.vectors = self.vectorizer.fit_transform(self.knowledge_base['combined_text'])
            print("✅ TF-IDF vektörleri hazır")
    
    def search_knowledge(self, query, top_k=5):
        """Sorguya en yakın bilgileri bul"""
        if self.vectors is None:
            return []
        
        # Sorguyu vektörize et
        query_vector = self.vectorizer.transform([query])
        
        # Cosine similarity hesapla
        similarities = cosine_similarity(query_vector, self.vectors).flatten()
        
        # En yüksek skorları al
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                results.append({
                    'score': similarities[idx],
                    'customer_context': self.knowledge_base.iloc[idx]['customer_context'],
                    'agent_response': self.knowledge_base.iloc[idx]['agent_response'],
                    'channel': self.knowledge_base.iloc[idx]['channel']
                })
        
        return results
    
    def generate_response(self, customer_query):
        """Müşteri sorusuna RAG ile yanıt üret"""
        print(f"🔍 Sorgu: {customer_query}")
        
        # 1. İlgili bilgileri bul
        relevant_knowledge = self.search_knowledge(customer_query, top_k=3)
        
        if not relevant_knowledge:
            return {
                'response': "Üzgünüm, bu konuda yeterli bilgim yok. Lütfen müşteri hizmetlerimizle iletişime geçin.",
                'confidence': 0.0,
                'sources': []
            }
        
        # 2. En iyi eşleşmeyi al
        best_match = relevant_knowledge[0]
        
        # 3. Yanıt şablonu oluştur
        response_template = self._create_response_template(customer_query, best_match)
        
        return {
            'response': response_template,
            'confidence': best_match['score'],
            'sources': relevant_knowledge[:2],  # En iyi 2 kaynak
            'channel_context': best_match['channel']
        }
    
    def _create_response_template(self, query, best_match):
        """Yanıt şablonu oluştur"""
        
        # Basit yanıt adaptasyonu
        response = best_match['agent_response']
        
        # Ortak yanıt kalıpları
        if any(keyword in query.lower() for keyword in ['kargo', 'teslimat', 'gönder']):
            prefix = "Kargo durumu ile ilgili: "
        elif any(keyword in query.lower() for keyword in ['iade', 'değişim', 'geri']):
            prefix = "İade işlemi için: "
        elif any(keyword in query.lower() for keyword in ['sipariş', 'sipariş']):
            prefix = "Sipariş durumunuz için: "
        elif any(keyword in query.lower() for keyword in ['ürün', 'ürün']):
            prefix = "Ürünümüz hakkında: "
        else:
            prefix = ""
        
        return f"{prefix}{response}"
    
    def get_common_queries(self):
        """Sık sorulan sorular analizi"""
        
        customer_msgs = self.df[self.df['role'] == 'customer']['message_content_masked']
        
        # Kelime analizi
        query_patterns = {
            'kargo': ['kargo', 'teslimat', 'gönder', 'ulaş'],
            'iade': ['iade', 'değişim', 'geri'],
            'sipariş': ['sipariş', 'sipariş', 'order'],
            'ürün': ['ürün', 'ürün', 'kalite', 'özellik'],
            'fiyat': ['fiyat', 'ücret', 'para', 'tl'],
            'adres': ['adres', 'konum', 'teslimat']
        }
        
        query_counts = defaultdict(int)
        
        for msg in customer_msgs:
            if isinstance(msg, str):
                msg_lower = msg.lower()
                for category, keywords in query_patterns.items():
                    if any(keyword in msg_lower for keyword in keywords):
                        query_counts[category] += 1
        
        return dict(query_counts)

def demo_rag_system():
    """RAG sistemi demo'su"""
    
    print("🚀 RAG SİSTEMİ DEMO'SU")
    print("=" * 50)
    
    # RAG sistemini başlat
    rag = CallCenterRAG()
    
    # Sık sorulan sorular analizi
    print("\n📊 SIK SORULAN KONULAR:")
    common_queries = rag.get_common_queries()
    for topic, count in sorted(common_queries.items(), key=lambda x: x[1], reverse=True):
        print(f"- {topic}: {count} mesaj")
    
    # Test soruları
    test_queries = [
        "Sipariş durumumu öğrenebilir miyim?",
        "Kargo ne zaman gelir?",
        "İade nasıl yapabilirim?",
        "Ürün fiyatı nedir?",
        "Teslimat adresi değiştirebilir miyim?"
    ]
    
    print("\n🎯 TEST SORULARI VE YANITLERI:")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n❓ Soru: {query}")
        result = rag.generate_response(query)
        print(f"🤖 Yanıt: {result['response']}")
        print(f"📊 Güven: {result['confidence']:.2f}")
        print(f"📱 Kanal: {result.get('channel_context', 'N/A')}")
        print("-" * 30)

if __name__ == "__main__":
    demo_rag_system() 