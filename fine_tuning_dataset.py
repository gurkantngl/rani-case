import pandas as pd
import json
import re
from collections import defaultdict
from datetime import datetime

class FineTuningDatasetGenerator:
    """Fine-tuning için dataset hazırlama sistemi"""
    
    def __init__(self, data_file='processed_chat_data.csv'):
        self.df = pd.read_csv(data_file)
        # Zaman formatı problemini çöz
        try:
            self.df['created_time'] = pd.to_datetime(self.df['created_time'], errors='coerce')
        except:
            # Eğer hala problem varsa, stringe çevir
            self.df['created_time'] = self.df['created_time'].astype(str)
        
    def extract_conversation_pairs(self):
        """Konuşmalardan input-output çiftleri çıkar"""
        
        print("🔄 Konuşma çiftleri çıkarılıyor...")
        
        conversation_pairs = []
        
        for conv_id in self.df['conversation_id'].unique():
            try:
                conv_data = self.df[self.df['conversation_id'] == conv_id].copy()
                
                # Zaman sıralamasını kullan (eğer mümkünse)
                if self.df['created_time'].dtype != 'object':
                    conv_data = conv_data.sort_values('created_time')
                
                messages = []
                for _, row in conv_data.iterrows():
                    if pd.notna(row['message_content_masked']) and len(str(row['message_content_masked'])) > 5:
                        messages.append({
                            'role': row['role'],
                            'content': str(row['message_content_masked']),
                            'timestamp': row.get('created_time', '')
                        })
                
                # Müşteri-agent çiftlerini bul
                for i in range(len(messages) - 1):
                    current_msg = messages[i]
                    next_msg = messages[i + 1]
                    
                    # Müşteri mesajından sonra agent yanıtı varsa
                    if (current_msg['role'] == 'customer' and 
                        next_msg['role'] == 'agent' and
                        len(current_msg['content']) > 10 and
                        len(next_msg['content']) > 10):
                        
                        # Bağlam oluştur (önceki 2 mesaj)
                        context_messages = messages[max(0, i-2):i]
                        context = ""
                        for ctx_msg in context_messages:
                            context += f"{ctx_msg['role']}: {ctx_msg['content']}\n"
                        
                        conversation_pairs.append({
                            'conversation_id': conv_id,
                            'context': context.strip(),
                            'customer_input': current_msg['content'],
                            'agent_response': next_msg['content'],
                            'channel': conv_data['channel_name'].iloc[0] if 'channel_name' in conv_data.columns else 'Unknown'
                        })
            except Exception as e:
                # Bu konuşmayı atla
                continue
        
        print(f"✅ {len(conversation_pairs)} konuşma çifti çıkarıldı")
        return conversation_pairs
    
    def create_alpaca_format(self, conversation_pairs):
        """Alpaca formatında eğitim verisi oluştur"""
        
        print("📝 Alpaca formatı oluşturuluyor...")
        
        alpaca_data = []
        
        for pair in conversation_pairs:
            # Instruction - görevin açıklaması
            instruction = "Sen Rani Mobilya'nın profesyonel müşteri hizmetleri temsilcisisin. Müşterinin sorusunu nazik ve yardımcı bir şekilde yanıtla."
            
            # Input - müşteri mesajı ve bağlam
            input_text = ""
            if pair['context']:
                input_text += f"Konuşma geçmişi:\n{pair['context']}\n\n"
            input_text += f"Müşteri: {pair['customer_input']}"
            
            # Output - agent yanıtı
            output_text = pair['agent_response']
            
            # Veri kalitesi kontrolü
            if (len(input_text) > 20 and len(output_text) > 20 and
                len(output_text) < 500 and
                not any(skip_word in output_text.lower() for skip_word in ['test', 'deneme', 'aaa'])):
                
                alpaca_data.append({
                    "instruction": instruction,
                    "input": input_text,
                    "output": output_text,
                    "metadata": {
                        "conversation_id": pair['conversation_id'],
                        "channel": pair['channel']
                    }
                })
        
        print(f"✅ {len(alpaca_data)} Alpaca formatı örneği oluşturuldu")
        return alpaca_data
    
    def create_chatml_format(self, conversation_pairs):
        """ChatML formatında eğitim verisi oluştur"""
        
        print("💬 ChatML formatı oluşturuluyor...")
        
        chatml_data = []
        
        for pair in conversation_pairs:
            # ChatML formatı: sistem, kullanıcı, asistan mesajları
            messages = [
                {
                    "role": "system",
                    "content": "Sen Rani Mobilya'nın profesyonel müşteri hizmetleri temsilcisisin. Nazik, yardımcı ve çözüm odaklı yanıtlar ver."
                }
            ]
            
            # Eğer bağlam varsa ekle
            if pair['context']:
                messages.append({
                    "role": "user",
                    "content": f"Önceki konuşma:\n{pair['context']}\n\nYeni mesaj: {pair['customer_input']}"
                })
            else:
                messages.append({
                    "role": "user",
                    "content": pair['customer_input']
                })
            
            messages.append({
                "role": "assistant",
                "content": pair['agent_response']
            })
            
            chatml_data.append({
                "messages": messages,
                "metadata": {
                    "conversation_id": pair['conversation_id'],
                    "channel": pair['channel']
                }
            })
        
        print(f"✅ {len(chatml_data)} ChatML formatı örneği oluşturuldu")
        return chatml_data
    
    def create_scenario_specific_datasets(self, conversation_pairs):
        """Senaryoya özel veri setleri oluştur"""
        
        print("🎭 Senaryoya özel veri setleri oluşturuluyor...")
        
        scenario_patterns = {
            'kargo_tracking': ['kargo', 'teslimat', 'gönder', 'ulaş', 'gelir'],
            'product_info': ['ürün', 'özellik', 'ölçü', 'renk', 'malzeme'],
            'order_status': ['sipariş', 'order', 'durum', 'takip'],
            'return_exchange': ['iade', 'değişim', 'geri'],
            'support_general': ['yardım', 'problem', 'sorun', 'memnun']
        }
        
        scenario_datasets = defaultdict(list)
        
        for pair in conversation_pairs:
            customer_text = pair['customer_input'].lower()
            
            # Hangi senaryoya ait olduğunu belirle
            scenarios = []
            for scenario, keywords in scenario_patterns.items():
                if any(keyword in customer_text for keyword in keywords):
                    scenarios.append(scenario)
            
            # Eğer hiç senaryo bulunamazsa genel desteğe ekle
            if not scenarios:
                scenarios = ['support_general']
            
            # Her senaryoya ekle
            for scenario in scenarios:
                scenario_datasets[scenario].append({
                    "instruction": f"Sen Rani Mobilya'nın {scenario} konusunda uzman müşteri hizmetleri temsilcisisin.",
                    "input": pair['customer_input'],
                    "output": pair['agent_response'],
                    "scenario": scenario,
                    "channel": pair['channel']
                })
        
        # İstatistikleri yazdır
        for scenario, data in scenario_datasets.items():
            print(f"- {scenario}: {len(data)} örnek")
        
        return dict(scenario_datasets)
    
    def quality_filter(self, dataset, min_length=20, max_length=500):
        """Veri kalitesi filtresi"""
        
        print("🔍 Veri kalitesi filtreleniyor...")
        
        original_count = len(dataset)
        
        filtered_data = []
        for item in dataset:
            # Alpaca formatı için
            if 'input' in item and 'output' in item:
                input_len = len(item['input'])
                output_len = len(item['output'])
                
                if (min_length <= input_len <= max_length * 2 and
                    min_length <= output_len <= max_length and
                    not self._contains_problematic_content(item['output'])):
                    filtered_data.append(item)
            
            # ChatML formatı için
            elif 'messages' in item:
                user_msg = next((msg['content'] for msg in item['messages'] if msg['role'] == 'user'), "")
                assistant_msg = next((msg['content'] for msg in item['messages'] if msg['role'] == 'assistant'), "")
                
                if (min_length <= len(user_msg) <= max_length * 2 and
                    min_length <= len(assistant_msg) <= max_length and
                    not self._contains_problematic_content(assistant_msg)):
                    filtered_data.append(item)
        
        print(f"✅ {original_count} -> {len(filtered_data)} örnek kaldı (kalite filtresi)")
        return filtered_data
    
    def _contains_problematic_content(self, text):
        """Problemli içerik kontrolü"""
        
        problematic_patterns = [
            r'test\s*test',
            r'deneme\s*deneme',
            r'aaa+',
            r'xxx+',
            r'\d{11,}',  # Çok uzun sayılar (kişisel bilgi olabilir)
        ]
        
        text_lower = text.lower()
        
        # Çok kısa veya anlamsız yanıtlar
        if len(text.strip()) < 10 or text_lower in ['ok', 'tamam', 'evet', 'hayır']:
            return True
        
        # Regex kontrolleri
        for pattern in problematic_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def split_train_val_test(self, dataset, train_ratio=0.8, val_ratio=0.1):
        """Veri setini train/validation/test olarak böl"""
        
        import random
        random.seed(42)
        
        shuffled = dataset.copy()
        random.shuffle(shuffled)
        
        total = len(shuffled)
        train_end = int(total * train_ratio)
        val_end = int(total * (train_ratio + val_ratio))
        
        splits = {
            'train': shuffled[:train_end],
            'validation': shuffled[train_end:val_end],
            'test': shuffled[val_end:]
        }
        
        print(f"📊 Veri seti bölündü:")
        for split_name, split_data in splits.items():
            print(f"- {split_name}: {len(split_data)} örnek")
        
        return splits
    
    def generate_all_formats(self):
        """Tüm formatları oluştur ve kaydet"""
        
        print("🚀 FINE-TUNING DATASET OLUŞTURUCU")
        print("=" * 60)
        
        # 1. Konuşma çiftlerini çıkar
        conversation_pairs = self.extract_conversation_pairs()
        
        # 2. Alpaca formatı
        alpaca_data = self.create_alpaca_format(conversation_pairs)
        alpaca_filtered = self.quality_filter(alpaca_data)
        
        # 3. ChatML formatı
        chatml_data = self.create_chatml_format(conversation_pairs)
        chatml_filtered = self.quality_filter(chatml_data)
        
        # 4. Senaryoya özel veri setleri
        scenario_datasets = self.create_scenario_specific_datasets(conversation_pairs)
        
        # 5. Train/Val/Test bölme
        alpaca_splits = self.split_train_val_test(alpaca_filtered)
        chatml_splits = self.split_train_val_test(chatml_filtered)
        
        # 6. Dosyaları kaydet
        print("\n💾 Dosyalar kaydediliyor...")
        
        # Alpaca formatı
        with open('alpaca_train.json', 'w', encoding='utf-8') as f:
            json.dump(alpaca_splits['train'], f, ensure_ascii=False, indent=2)
        
        with open('alpaca_val.json', 'w', encoding='utf-8') as f:
            json.dump(alpaca_splits['validation'], f, ensure_ascii=False, indent=2)
        
        # ChatML formatı
        with open('chatml_train.jsonl', 'w', encoding='utf-8') as f:
            for item in chatml_splits['train']:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        
        # Senaryoya özel veri setleri
        for scenario, data in scenario_datasets.items():
            with open(f'scenario_{scenario}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("✅ Tüm dosyalar kaydedildi!")
        
        # İstatistik özeti
        print(f"\n📈 ÖZET:")
        print(f"- Alpaca Train: {len(alpaca_splits['train'])} örnek")
        print(f"- Alpaca Val: {len(alpaca_splits['validation'])} örnek")
        print(f"- ChatML Train: {len(chatml_splits['train'])} örnek")
        print(f"- Senaryo veri setleri: {len(scenario_datasets)} farklı senaryo")
        
        return {
            'alpaca_splits': alpaca_splits,
            'chatml_splits': chatml_splits,
            'scenario_datasets': scenario_datasets
        }

def demo_dataset_generation():
    """Dataset oluşturma demo'su"""
    
    generator = FineTuningDatasetGenerator()
    results = generator.generate_all_formats()
    
    # Örnek verileri göster
    print("\n🔍 ÖRNEK VERİLER:")
    print("=" * 40)
    
    # Alpaca örneği
    alpaca_example = results['alpaca_splits']['train'][0]
    print("📝 ALPACA ÖRNEĞİ:")
    print(f"Instruction: {alpaca_example['instruction'][:100]}...")
    print(f"Input: {alpaca_example['input'][:100]}...")
    print(f"Output: {alpaca_example['output'][:100]}...")
    
    # ChatML örneği
    chatml_example = results['chatml_splits']['train'][0]
    print(f"\n💬 CHATTML ÖRNEĞİ:")
    for msg in chatml_example['messages']:
        print(f"{msg['role']}: {msg['content'][:50]}...")

if __name__ == "__main__":
    demo_dataset_generation() 