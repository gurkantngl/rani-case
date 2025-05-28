import pandas as pd
import json
import numpy as np
from collections import defaultdict
import time
import random

class ModelEvaluationSystem:
    """Model Seçimi ve Değerlendirme Sistemi"""
    
    def __init__(self):
        self.evaluation_metrics = {}
        self.test_scenarios = self._create_test_scenarios()
        
    def _create_test_scenarios(self):
        """Test senaryoları oluştur"""
        
        return {
            'response_time': {
                'description': 'Yanıt süresi performansı',
                'target_time': 2.0,  # 2 saniye hedef
                'weight': 0.2
            },
            'accuracy': {
                'description': 'Doğru bilgi verme oranı',
                'target_score': 0.85,  # %85 doğruluk hedefi
                'weight': 0.3
            },
            'customer_satisfaction': {
                'description': 'Müşteri memnuniyet simülasyonu',
                'target_score': 0.80,  # %80 memnuniyet hedefi
                'weight': 0.25
            },
            'consistency': {
                'description': 'Tutarlı yanıt verme',
                'target_score': 0.90,  # %90 tutarlılık hedefi
                'weight': 0.15
            },
            'cost_efficiency': {
                'description': 'Maliyet etkinliği',
                'target_score': 0.75,  # %75 verimlilik hedefi
                'weight': 0.1
            }
        }
    
    def evaluate_rag_approach(self):
        """RAG yaklaşımını değerlendir"""
        
        print("🔍 RAG Yaklaşımı Değerlendiriliyor...")
        
        # RAG sistemini import et
        from rag_system import CallCenterRAG
        
        rag_system = CallCenterRAG()
        
        # Test soruları
        test_queries = [
            "Sipariş durumumu öğrenebilir miyim?",
            "Kargo ne zaman gelir?",
            "İade nasıl yapabilirim?",
            "Ürün fiyatı nedir?",
            "Teslimat adresi değiştirebilir miyim?",
            "Montaj hizmeti var mı?",
            "Garanti süresi ne kadar?",
            "İndirim var mı?",
            "Stok durumu nedir?",
            "Ödeme seçenekleri neler?"
        ]
        
        rag_metrics = {
            'response_times': [],
            'accuracy_scores': [],
            'satisfaction_scores': [],
            'consistency_scores': [],
            'responses': []
        }
        
        for query in test_queries:
            start_time = time.time()
            
            try:
                result = rag_system.generate_response(query)
                response_time = time.time() - start_time
                
                # Metrikleri hesapla
                rag_metrics['response_times'].append(response_time)
                rag_metrics['accuracy_scores'].append(result['confidence'])
                rag_metrics['satisfaction_scores'].append(self._simulate_satisfaction(result['response']))
                rag_metrics['responses'].append(result)
                
            except Exception as e:
                print(f"Hata: {e}")
                rag_metrics['response_times'].append(10.0)  # Timeout
                rag_metrics['accuracy_scores'].append(0.0)
                rag_metrics['satisfaction_scores'].append(0.0)
        
        # Tutarlılık skorunu hesapla
        rag_metrics['consistency_scores'] = self._calculate_consistency(rag_metrics['responses'])
        
        return self._calculate_final_scores('RAG', rag_metrics)
    
    def evaluate_prompt_engineering(self):
        """Prompt Engineering yaklaşımını değerlendir"""
        
        print("🎭 Prompt Engineering Değerlendiriliyor...")
        
        from prompt_engineering import CallCenterPromptEngine
        
        prompt_engine = CallCenterPromptEngine()
        
        test_messages = [
            "Merhaba, siparişim ne zaman gelir?",
            "Bu ürünü iade etmek istiyorum",
            "TV ünitesinin ölçüleri nedir?",
            "Kargo durumumu öğrenebilir miyim?",
            "Yardım istiyorum",
            "Fiyat bilgisi alabilir miyim?",
            "Montaj yapıyor musunuz?",
            "Garanti var mı?",
            "İndirim var mı?",
            "Ne zaman teslim edilir?"
        ]
        
        prompt_metrics = {
            'response_times': [],
            'accuracy_scores': [],
            'satisfaction_scores': [],
            'consistency_scores': [],
            'prompts': []
        }
        
        for msg in test_messages:
            start_time = time.time()
            
            try:
                prompt_data = prompt_engine.generate_prompt(msg)
                response_time = time.time() - start_time
                
                # Simulated LLM response time (prompt engineering genelde daha hızlı)
                response_time += random.uniform(0.5, 1.5)
                
                # Metrikleri hesapla
                prompt_metrics['response_times'].append(response_time)
                prompt_metrics['accuracy_scores'].append(0.75 + random.uniform(0, 0.2))  # Simulated
                prompt_metrics['satisfaction_scores'].append(self._simulate_satisfaction(prompt_data['examples'][0]['output']))
                prompt_metrics['prompts'].append(prompt_data)
                
            except Exception as e:
                print(f"Hata: {e}")
                prompt_metrics['response_times'].append(5.0)
                prompt_metrics['accuracy_scores'].append(0.0)
                prompt_metrics['satisfaction_scores'].append(0.0)
        
        # Tutarlılık skorunu hesapla
        prompt_metrics['consistency_scores'] = [0.85 + random.uniform(-0.1, 0.1) for _ in test_messages]
        
        return self._calculate_final_scores('Prompt Engineering', prompt_metrics)
    
    def evaluate_fine_tuning_potential(self):
        """Fine-tuning potansiyelini değerlendir"""
        
        print("🎯 Fine-Tuning Potansiyeli Değerlendiriliyor...")
        
        # Dataset kalitesini analiz et
        try:
            with open('alpaca_train.json', 'r', encoding='utf-8') as f:
                training_data = json.load(f)
            
            dataset_quality = self._analyze_dataset_quality(training_data)
            
            # Fine-tuning metrikleri (tahmin edilen)
            ft_metrics = {
                'response_times': [0.8 + random.uniform(0, 0.4) for _ in range(10)],  # Fine-tuned models daha hızlı
                'accuracy_scores': [0.85 + random.uniform(0, 0.1) for _ in range(10)],  # Yüksek doğruluk
                'satisfaction_scores': [0.80 + random.uniform(0, 0.15) for _ in range(10)],
                'consistency_scores': [0.90 + random.uniform(-0.05, 0.05) for _ in range(10)],  # Çok tutarlı
                'dataset_quality': dataset_quality
            }
            
            return self._calculate_final_scores('Fine-Tuning', ft_metrics)
            
        except Exception as e:
            print(f"Fine-tuning dataset'i bulunamadı: {e}")
            return None
    
    def _simulate_satisfaction(self, response):
        """Müşteri memnuniyetini simüle et"""
        
        if not response or len(response) < 10:
            return 0.2
        
        satisfaction_factors = {
            'politeness': 0 if not any(word in response.lower() for word in ['merhaba', 'lütfen', 'teşekkür']) else 0.2,
            'helpfulness': 0.2 if any(phrase in response.lower() for phrase in ['yardımcı', 'çözüm', 'destek']) else 0.1,
            'clarity': 0.2 if len(response.split()) > 5 and len(response) < 300 else 0.1,
            'completeness': 0.2 if len(response) > 50 else 0.1,
            'professional': 0.2 if not any(word in response.lower() for word in ['bilmiyorum', 'emin değilim']) else 0.1
        }
        
        base_score = sum(satisfaction_factors.values())
        noise = random.uniform(-0.1, 0.1)  # Gerçekçi varyasyon
        
        return min(1.0, max(0.0, base_score + noise))
    
    def _calculate_consistency(self, responses):
        """Yanıtların tutarlılığını hesapla"""
        
        if not responses:
            return [0.0]
        
        # Basit tutarlılık simülasyonu
        base_consistency = 0.8
        consistency_scores = []
        
        for response in responses:
            if isinstance(response, dict) and 'response' in response:
                response_text = response['response']
                # Yanıt kalitesine göre tutarlılık skoru
                if len(response_text) > 20 and not any(word in response_text.lower() for word in ['bilmiyorum', 'emin değilim']):
                    score = base_consistency + random.uniform(0, 0.15)
                else:
                    score = base_consistency - random.uniform(0, 0.2)
                consistency_scores.append(min(1.0, max(0.0, score)))
            else:
                consistency_scores.append(base_consistency)
        
        return consistency_scores
    
    def _analyze_dataset_quality(self, training_data):
        """Dataset kalitesini analiz et"""
        
        quality_metrics = {
            'size': len(training_data),
            'avg_input_length': np.mean([len(item['input']) for item in training_data]),
            'avg_output_length': np.mean([len(item['output']) for item in training_data]),
            'diversity_score': len(set(item['output'][:50] for item in training_data)) / len(training_data)
        }
        
        # Kalite skoru hesapla
        size_score = min(1.0, quality_metrics['size'] / 5000)  # 5000 örnek ideal
        length_score = 1.0 if 50 <= quality_metrics['avg_output_length'] <= 200 else 0.7
        diversity_score = quality_metrics['diversity_score']
        
        overall_quality = (size_score * 0.4 + length_score * 0.3 + diversity_score * 0.3)
        
        quality_metrics['overall_score'] = overall_quality
        
        return quality_metrics
    
    def _calculate_final_scores(self, approach_name, metrics):
        """Final skorları hesapla"""
        
        scores = {}
        
        # Her metrik için ortalama al
        if 'response_times' in metrics:
            avg_response_time = np.mean(metrics['response_times'])
            # Yanıt süresi skoru (2 saniye hedef)
            scores['response_time'] = max(0, 1 - (avg_response_time - 2.0) / 3.0) if avg_response_time > 2.0 else 1.0
        
        if 'accuracy_scores' in metrics:
            scores['accuracy'] = np.mean(metrics['accuracy_scores'])
        
        if 'satisfaction_scores' in metrics:
            scores['customer_satisfaction'] = np.mean(metrics['satisfaction_scores'])
        
        if 'consistency_scores' in metrics:
            scores['consistency'] = np.mean(metrics['consistency_scores'])
        
        # Maliyet etkinliği (yaklaşım türüne göre)
        cost_efficiency = {
            'RAG': 0.85,  # Orta maliyet, iyi performans
            'Prompt Engineering': 0.90,  # Düşük maliyet
            'Fine-Tuning': 0.70  # Yüksek maliyet, en iyi performans
        }
        scores['cost_efficiency'] = cost_efficiency.get(approach_name, 0.75)
        
        # Ağırlıklı final skor
        final_score = 0
        for metric, weight in [(k, v['weight']) for k, v in self.test_scenarios.items()]:
            if metric in scores:
                final_score += scores[metric] * weight
        
        return {
            'approach': approach_name,
            'individual_scores': scores,
            'final_score': final_score,
            'raw_metrics': metrics
        }
    
    def compare_approaches(self):
        """Tüm yaklaşımları karşılaştır"""
        
        print("🏆 MODEL YAKLAŞIMLARI KARŞILAŞTIRMASI")
        print("=" * 60)
        
        results = []
        
        # RAG değerlendirmesi
        try:
            rag_result = self.evaluate_rag_approach()
            results.append(rag_result)
        except Exception as e:
            print(f"RAG değerlendirme hatası: {e}")
        
        # Prompt Engineering değerlendirmesi
        try:
            prompt_result = self.evaluate_prompt_engineering()
            results.append(prompt_result)
        except Exception as e:
            print(f"Prompt Engineering değerlendirme hatası: {e}")
        
        # Fine-tuning değerlendirmesi
        ft_result = self.evaluate_fine_tuning_potential()
        if ft_result:
            results.append(ft_result)
        
        # Sonuçları sırala
        results.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Sonuçları göster
        print("\n📊 SONUÇLAR:")
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['approach']}")
            print(f"   Final Skor: {result['final_score']:.3f}")
            print(f"   Detay Skorlar:")
            for metric, score in result['individual_scores'].items():
                print(f"   - {metric}: {score:.3f}")
        
        # Öneriler
        self._generate_recommendations(results)
        
        return results
    
    def _generate_recommendations(self, results):
        """Sonuçlara göre öneriler oluştur"""
        
        print(f"\n💡 ÖNERİLER:")
        print("=" * 30)
        
        if not results:
            print("Değerlendirme yapılamadı.")
            return
        
        best_approach = results[0]
        
        print(f"🥇 En İyi Yaklaşım: {best_approach['approach']}")
        print(f"   Skor: {best_approach['final_score']:.3f}")
        
        # Yaklaşım özel öneriler
        if best_approach['approach'] == 'RAG':
            print("\n📋 RAG İyileştirme Önerileri:")
            print("- Daha fazla veri ile knowledge base'i genişletin")
            print("- Semantic search algoritmasını optimize edin")
            print("- Response template'lerini iyileştirin")
            
        elif best_approach['approach'] == 'Prompt Engineering':
            print("\n📋 Prompt Engineering İyileştirme Önerileri:")
            print("- Daha spesifik senaryo prompt'ları ekleyin")
            print("- Few-shot örnekleri çoğaltın")
            print("- Model seçimini optimize edin")
            
        elif best_approach['approach'] == 'Fine-Tuning':
            print("\n📋 Fine-Tuning İyileştirme Önerileri:")
            print("- Daha fazla kaliteli training verisi toplayın")
            print("- Hyperparameter tuning yapın")
            print("- Model monitoringi kurun")
        
        # Hibrit yaklaşım önerisi
        print(f"\n🔄 Hibrit Yaklaşım Önerisi:")
        print("1. Başlangıç için RAG sistemi kurun (hızlı deployment)")
        print("2. Prompt Engineering ile optimize edin")
        print("3. Uzun vadede Fine-Tuning için veri toplayın")
        print("4. A/B test ile performansları karşılaştırın")

def main():
    """Ana değerlendirme fonksiyonu"""
    
    evaluator = ModelEvaluationSystem()
    results = evaluator.compare_approaches()
    
    # Sonuçları JSON'a kaydet
    with open('model_evaluation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Sonuçlar 'model_evaluation_results.json' dosyasına kaydedildi")

if __name__ == "__main__":
    main() 