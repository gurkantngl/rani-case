#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rani Mobilya Çağrı Merkezi - Gelişmiş RAG Sistemi v2.0
Güncellenmiş dataset'ler ile RAG (Retrieval-Augmented Generation) sistemi
"""

import pandas as pd
import numpy as np
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple, Optional
import json
import logging
from datetime import datetime
import pickle

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedRAGSystem:
    def __init__(self, 
                 knowledge_base_path: str = "processed_datasets_v2/conversation_pairs.csv",
                 model_path: str = "rag_model_v2.pkl"):
        """
        Gelişmiş RAG Sistemi
        
        Args:
            knowledge_base_path: Konuşma çiftleri CSV dosyası
            model_path: Kaydedilmiş model dosyası
        """
        self.knowledge_base_path = knowledge_base_path
        self.model_path = model_path
        self.knowledge_base = pd.DataFrame()
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),
            stop_words=None,  # Türkçe için özel stop words eklenebilir
            lowercase=True,
            max_df=0.95,
            min_df=2
        )
        self.knowledge_vectors = None
        self.is_trained = False
        self.stats = {
            'total_entries': 0,
            'scenarios': {},
            'channels': {},
            'avg_similarity_threshold': 0.3
        }
        
    def load_knowledge_base(self) -> bool:
        """Bilgi tabanını yükle"""
        try:
            if not os.path.exists(self.knowledge_base_path):
                logger.error(f"Bilgi tabanı dosyası bulunamadı: {self.knowledge_base_path}")
                return False
            
            logger.info(f"Bilgi tabanı yükleniyor: {self.knowledge_base_path}")
            self.knowledge_base = pd.read_csv(self.knowledge_base_path, encoding='utf-8')
            
            # Veri temizleme
            self.knowledge_base = self.knowledge_base.dropna(subset=['customer', 'agent'])
            self.knowledge_base = self.knowledge_base[
                (self.knowledge_base['customer'].str.len() > 10) & 
                (self.knowledge_base['agent'].str.len() > 10)
            ]
            
            self.stats['total_entries'] = len(self.knowledge_base)
            self.stats['scenarios'] = self.knowledge_base['scenario'].value_counts().to_dict()
            self.stats['channels'] = self.knowledge_base['channel'].value_counts().to_dict()
            
            logger.info(f"✅ {self.stats['total_entries']} bilgi girdisi yüklendi")
            logger.info(f"Senaryolar: {list(self.stats['scenarios'].keys())}")
            logger.info(f"Kanallar: {list(self.stats['channels'].keys())}")
            
            return True
            
        except Exception as e:
            logger.error(f"Bilgi tabanı yüklenirken hata: {str(e)}")
            return False
    
    def preprocess_text(self, text: str) -> str:
        """Metni ön işleme"""
        if pd.isna(text):
            return ""
        
        text = str(text).lower()
        
        # Türkçe karakterleri normalize et (isteğe bağlı)
        turkish_chars = {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u'
        }
        
        # Noktalama işaretlerini temizle
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def train_vectorizer(self) -> bool:
        """TF-IDF vektörizeri eğit"""
        try:
            logger.info("TF-IDF vektörizeri eğitiliyor...")
            
            # Müşteri sorularını ön işleme
            customer_texts = self.knowledge_base['customer'].apply(self.preprocess_text).tolist()
            
            # Vektörizeri eğit
            self.knowledge_vectors = self.vectorizer.fit_transform(customer_texts)
            self.is_trained = True
            
            logger.info(f"✅ Vektörizasyon tamamlandı. Boyut: {self.knowledge_vectors.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Vektörizer eğitiminde hata: {str(e)}")
            return False
    
    def save_model(self) -> bool:
        """Modeli kaydet"""
        try:
            model_data = {
                'vectorizer': self.vectorizer,
                'knowledge_vectors': self.knowledge_vectors,
                'knowledge_base': self.knowledge_base,
                'stats': self.stats,
                'is_trained': self.is_trained
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"✅ Model kaydedildi: {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Model kaydedilirken hata: {str(e)}")
            return False
    
    def load_model(self) -> bool:
        """Modeli yükle"""
        try:
            if not os.path.exists(self.model_path):
                logger.warning(f"Model dosyası bulunamadı: {self.model_path}")
                return False
            
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.vectorizer = model_data['vectorizer']
            self.knowledge_vectors = model_data['knowledge_vectors']
            self.knowledge_base = model_data['knowledge_base']
            self.stats = model_data['stats']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"✅ Model yüklendi: {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Model yüklenirken hata: {str(e)}")
            return False
    
    def find_similar_conversations(self, 
                                 query: str, 
                                 top_k: int = 5,
                                 scenario_filter: Optional[str] = None,
                                 similarity_threshold: float = 0.1) -> List[Dict]:
        """Benzer konuşmaları bul"""
        
        if not self.is_trained:
            logger.error("Model henüz eğitilmemiş!")
            return []
        
        try:
            # Query'yi ön işleme
            processed_query = self.preprocess_text(query)
            
            # Query'yi vektörize et
            query_vector = self.vectorizer.transform([processed_query])
            
            # Benzerlik hesapla
            similarities = cosine_similarity(query_vector, self.knowledge_vectors).flatten()
            
            # En benzer indeksleri bul
            similar_indices = np.argsort(similarities)[::-1][:top_k * 2]  # Daha fazla al, sonra filtrele
            
            results = []
            for idx in similar_indices:
                similarity_score = similarities[idx]
                
                # Threshold kontrolü
                if similarity_score < similarity_threshold:
                    continue
                
                row = self.knowledge_base.iloc[idx]
                
                # Senaryo filtresi
                if scenario_filter and row['scenario'] != scenario_filter:
                    continue
                
                result = {
                    'customer_question': row['customer'],
                    'agent_response': row['agent'],
                    'scenario': row['scenario'],
                    'channel': row['channel'],
                    'similarity_score': float(similarity_score),
                    'conversation_id': row.get('conversation_id', ''),
                    'index': int(idx)
                }
                
                results.append(result)
                
                if len(results) >= top_k:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Benzer konuşma arama hatası: {str(e)}")
            return []
    
    def generate_response(self, 
                         query: str, 
                         scenario: Optional[str] = None,
                         use_context: bool = True) -> Dict:
        """RAG tabanlı yanıt üret"""
        
        # Benzer konuşmaları bul
        similar_conversations = self.find_similar_conversations(
            query, 
            top_k=3,
            scenario_filter=scenario,
            similarity_threshold=self.stats['avg_similarity_threshold']
        )
        
        if not similar_conversations:
            return {
                'answer': "Üzgünüm, bu konuda size yardımcı olacak bilgi bulamadım. Lütfen daha spesifik bir soru sorun veya müşteri temsilcimizle iletişime geçin.",
                'confidence': 0.1,
                'method': 'RAG_DEFAULT',
                'scenario': 'genel_destek',
                'sources': [],
                'similar_count': 0
            }
        
        # En iyi eşleşmeyi kullan
        best_match = similar_conversations[0]
        confidence = best_match['similarity_score']
        
        # Yanıtı uyarla
        if confidence > 0.8:
            # Çok yüksek benzerlik - direk yanıt
            answer = best_match['agent_response']
            method = 'RAG_DIRECT'
        elif confidence > 0.5:
            # Orta benzerlik - uyarlanmış yanıt
            answer = self._adapt_response(best_match['agent_response'], query)
            method = 'RAG_ADAPTED'
        else:
            # Düşük benzerlik - genel yanıt + benzer örnekler
            answer = self._generate_context_response(similar_conversations, query)
            method = 'RAG_CONTEXTUAL'
        
        return {
            'answer': answer,
            'confidence': confidence,
            'method': method,
            'scenario': best_match['scenario'],
            'sources': [
                {
                    'question': conv['customer_question'][:100] + "...",
                    'similarity': conv['similarity_score'],
                    'scenario': conv['scenario']
                }
                for conv in similar_conversations[:3]
            ],
            'similar_count': len(similar_conversations)
        }
    
    def _adapt_response(self, original_response: str, query: str) -> str:
        """Yanıtı query'ye göre uyarla"""
        # Basit uyarlama - gerçek uygulamada daha gelişmiş NLP teknikleri kullanılabilir
        adaptations = {
            'sipariş': 'siparişiniz',
            'ürün': 'ürününüz',
            'kargo': 'kargunuz',
            'iade': 'iade işleminiz',
            'fiyat': 'fiyat bilgisi'
        }
        
        adapted_response = original_response
        for key, value in adaptations.items():
            if key in query.lower():
                adapted_response = adapted_response.replace(key, value)
        
        return adapted_response
    
    def _generate_context_response(self, similar_conversations: List[Dict], query: str) -> str:
        """Kontekst tabanlı yanıt üret"""
        if not similar_conversations:
            return "Bu konuda size yardımcı olacak spesifik bilgi bulamadım."
        
        # Senaryoları grupla
        scenarios = {}
        for conv in similar_conversations:
            scenario = conv['scenario']
            if scenario not in scenarios:
                scenarios[scenario] = []
            scenarios[scenario].append(conv)
        
        # En sık görülen senaryoya göre yanıt
        main_scenario = max(scenarios.keys(), key=lambda k: len(scenarios[k]))
        
        context_templates = {
            'siparis_takip': "Sipariş takibi için size yardımcı olabilirim. Sipariş numaranızı paylaşırsanız detaylı bilgi verebilirim.",
            'urun_bilgisi': "Ürün bilgileri konusunda size yardımcı olabilirim. Hangi ürün hakkında bilgi almak istiyorsunuz?",
            'kargo_sorgulama': "Kargo durumu için size yardımcı olabilirim. Kargo takip numaranız var mı?",
            'iade_degisim': "İade ve değişim işlemleri için size yardımcı olabilirim. Hangi ürünü iade etmek istiyorsunuz?",
            'genel_destek': "Size nasıl yardımcı olabilirim? Daha spesifik sorular sorarsanız daha iyi yardımcı olabilirim."
        }
        
        return context_templates.get(main_scenario, context_templates['genel_destek'])
    
    def get_statistics(self) -> Dict:
        """Sistem istatistiklerini döndür"""
        return {
            'knowledge_base_size': self.stats['total_entries'],
            'scenarios': self.stats['scenarios'],
            'channels': self.stats['channels'],
            'is_trained': self.is_trained,
            'vector_dimensions': self.knowledge_vectors.shape[1] if self.knowledge_vectors is not None else 0,
            'avg_similarity_threshold': self.stats['avg_similarity_threshold']
        }
    
    def test_system(self, test_queries: List[str] = None) -> Dict:
        """Sistemi test et"""
        if test_queries is None:
            test_queries = [
                "Siparişim ne zaman gelir?",
                "Bu ürünün fiyatı nedir?",
                "Kargo durumunu öğrenebilir miyim?",
                "İade yapmak istiyorum",
                "Müşteri hizmetleri numarası"
            ]
        
        test_results = []
        total_confidence = 0
        
        for query in test_queries:
            result = self.generate_response(query)
            test_results.append({
                'query': query,
                'answer': result['answer'][:100] + "...",
                'confidence': result['confidence'],
                'method': result['method'],
                'scenario': result['scenario']
            })
            total_confidence += result['confidence']
        
        avg_confidence = total_confidence / len(test_queries) if test_queries else 0
        
        return {
            'test_results': test_results,
            'average_confidence': avg_confidence,
            'total_tests': len(test_queries)
        }

def setup_rag_system() -> EnhancedRAGSystem:
    """RAG sistemini kur ve eğit"""
    logger.info("🚀 Gelişmiş RAG Sistemi başlatılıyor...")
    
    rag = EnhancedRAGSystem()
    
    # Model varsa yükle, yoksa eğit
    if rag.load_model():
        logger.info("✅ Önceden eğitilmiş model yüklendi")
    else:
        logger.info("📚 Yeni model eğitiliyor...")
        
        # Bilgi tabanını yükle
        if not rag.load_knowledge_base():
            logger.error("❌ Bilgi tabanı yüklenemedi!")
            return None
        
        # Vektörizeri eğit
        if not rag.train_vectorizer():
            logger.error("❌ Vektörizer eğitilemedi!")
            return None
        
        # Modeli kaydet
        rag.save_model()
    
    # Test et
    test_results = rag.test_system()
    logger.info(f"🧪 Test tamamlandı. Ortalama güven skoru: {test_results['average_confidence']:.3f}")
    
    return rag

def main():
    """Ana fonksiyon"""
    print("🎯 Rani Mobilya - Gelişmiş RAG Sistemi v2.0")
    print("=" * 50)
    
    # RAG sistemini kur
    rag_system = setup_rag_system()
    
    if rag_system:
        # İstatistikleri göster
        stats = rag_system.get_statistics()
        print(f"\n📊 Sistem İstatistikleri:")
        print(f"   Bilgi tabanı boyutu: {stats['knowledge_base_size']:,}")
        print(f"   Vektör boyutu: {stats['vector_dimensions']:,}")
        print(f"   Senaryolar: {list(stats['scenarios'].keys())}")
        
        # Test sorguları
        print(f"\n🧪 Test Sonuçları:")
        test_results = rag_system.test_system()
        for result in test_results['test_results']:
            print(f"   ❓ {result['query']}")
            print(f"   ✅ {result['answer']}")
            print(f"   📈 Güven: {result['confidence']:.3f} | Senaryo: {result['scenario']}")
            print()
        
        print("✅ RAG Sistemi hazır!")
    else:
        print("❌ RAG Sistemi kurulamadı!")

if __name__ == "__main__":
    main() 