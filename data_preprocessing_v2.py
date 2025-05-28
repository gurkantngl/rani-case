#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rani Mobilya Çağrı Merkezi - Gelişmiş Veri Ön İşleme Sistemi v2.0
Güncellenmiş dataset'ler için kapsamlı veri hazırlama ve temizleme
"""

import pandas as pd
import numpy as np
import re
import os
import glob
from datetime import datetime
import hashlib
import logging
from typing import List, Dict, Tuple
import json

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_preprocessing_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    def __init__(self, dataset_dir: str = "datasets"):
        """
        Gelişmiş veri ön işleme sınıfı
        
        Args:
            dataset_dir: Dataset dosyalarının bulunduğu klasör
        """
        self.dataset_dir = dataset_dir
        self.raw_data = []
        self.processed_data = []
        self.stats = {
            'total_files': 0,
            'total_raw_messages': 0,
            'total_processed_messages': 0,
            'total_conversations': 0,
            'channels': {},
            'date_range': {},
            'processing_time': 0
        }
        
    def load_datasets(self) -> None:
        """Tüm CSV dosyalarını yükle"""
        logger.info("📁 Dataset dosyaları yükleniyor...")
        
        csv_files = glob.glob(os.path.join(self.dataset_dir, "*.csv"))
        self.stats['total_files'] = len(csv_files)
        
        logger.info(f"Toplam {len(csv_files)} CSV dosyası bulundu")
        
        all_data = []
        
        for i, file_path in enumerate(csv_files, 1):
            logger.info(f"📄 Dosya {i}/{len(csv_files)}: {os.path.basename(file_path)}")
            
            try:
                # Dosya boyutunu kontrol et
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                logger.info(f"   📊 Dosya boyutu: {file_size:.1f} MB")
                
                # CSV'yi chunk'lar halinde oku (memory efficiency için)
                chunk_size = 10000
                chunks = []
                
                for chunk in pd.read_csv(file_path, chunksize=chunk_size, encoding='utf-8', on_bad_lines='skip'):
                    chunks.append(chunk)
                
                df = pd.concat(chunks, ignore_index=True)
                logger.info(f"   ✅ {len(df)} satır yüklendi")
                
                # Dosya bilgisini ekle
                df['source_file'] = os.path.basename(file_path)
                all_data.append(df)
                
            except Exception as e:
                logger.error(f"   ❌ Dosya yüklenemedi: {str(e)}")
                continue
        
        if all_data:
            self.raw_data = pd.concat(all_data, ignore_index=True)
            self.stats['total_raw_messages'] = len(self.raw_data)
            logger.info(f"🎉 Toplam {self.stats['total_raw_messages']} mesaj yüklendi")
        else:
            logger.error("❌ Hiç veri yüklenemedi!")
            
    def analyze_data_structure(self) -> Dict:
        """Veri yapısını analiz et"""
        logger.info("🔍 Veri yapısı analiz ediliyor...")
        
        analysis = {
            'columns': list(self.raw_data.columns),
            'data_types': self.raw_data.dtypes.to_dict(),
            'null_counts': self.raw_data.isnull().sum().to_dict(),
            'unique_values': {},
            'sample_data': {}
        }
        
        # Her sütun için benzersiz değer sayıları
        for col in self.raw_data.columns:
            analysis['unique_values'][col] = self.raw_data[col].nunique()
            
            # Örnek veriler (ilk 5 benzersiz değer)
            sample_values = self.raw_data[col].dropna().unique()[:5].tolist()
            analysis['sample_data'][col] = sample_values
            
        logger.info(f"📊 Sütunlar: {analysis['columns']}")
        logger.info(f"📈 Veri boyutu: {self.raw_data.shape}")
        
        return analysis
    
    def clean_text(self, text: str) -> str:
        """Metni temizle"""
        if pd.isna(text) or text == '':
            return ''
        
        text = str(text)
        
        # HTML etiketlerini temizle
        text = re.sub(r'<[^>]+>', '', text)
        
        # Kişisel bilgileri maskele
        # Telefon numaraları
        text = re.sub(r'\b0?5\d{2}\s?\d{3}\s?\d{2}\s?\d{2}\b', '[TELEFON]', text)
        text = re.sub(r'\b0?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}\b', '[TELEFON]', text)
        
        # Email adresleri
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # IBAN/Kart numaraları
        text = re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b', '[KART]', text)
        
        # TC Kimlik No
        text = re.sub(r'\b\d{11}\b', '[KIMLIK]', text)
        
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def identify_user_type(self, message: str, sender: str = None) -> str:
        """Mesajın müşteri mi agent mi olduğunu belirle"""
        if pd.isna(message):
            return 'unknown'
        
        message = str(message).lower()
        
        # Agent belirteçleri
        agent_patterns = [
            r'rani\s*mobilya',
            r'müşteri\s*hizmetleri',
            r'size\s*yardımcı',
            r'teşekkür\s*ederiz',
            r'iyi\s*günler',
            r'yönlendir',
            r'departman',
            r'sistem',
            r'işleminizi',
            r'tarafımıza'
        ]
        
        for pattern in agent_patterns:
            if re.search(pattern, message):
                return 'agent'
        
        # Müşteri belirteçleri
        customer_patterns = [
            r'sipariş\s*ver',
            r'ürün\s*sor',
            r'ne\s*zaman\s*gel',
            r'iade\s*et',
            r'param',
            r'fiyat\s*ne',
            r'memnun\s*değil'
        ]
        
        for pattern in customer_patterns:
            if re.search(pattern, message):
                return 'customer'
        
        return 'unknown'
    
    def extract_conversation_pairs(self) -> List[Dict]:
        """Konuşma çiftlerini çıkar"""
        logger.info("💬 Konuşma çiftleri çıkarılıyor...")
        
        conversation_pairs = []
        
        # Konuşma ID'sine göre grupla
        if 'conversation_id' in self.raw_data.columns:
            conv_col = 'conversation_id'
        elif 'session_id' in self.raw_data.columns:
            conv_col = 'session_id'
        else:
            # Timestamp ve kanal bazında grupla
            self.raw_data['conversation_group'] = (
                self.raw_data['timestamp'].astype(str) + '_' + 
                self.raw_data.get('channel', 'unknown').astype(str)
            )
            conv_col = 'conversation_group'
        
        grouped = self.raw_data.groupby(conv_col)
        
        for conv_id, group in grouped:
            messages = group.sort_values('timestamp' if 'timestamp' in group.columns else group.index)
            
            # User type'ları belirle
            messages['user_type'] = messages.apply(
                lambda row: self.identify_user_type(
                    row.get('message', ''), 
                    row.get('sender', '')
                ), axis=1
            )
            
            # Customer-Agent çiftlerini bul
            prev_customer_msg = None
            
            for _, msg in messages.iterrows():
                if msg['user_type'] == 'customer':
                    prev_customer_msg = msg
                elif msg['user_type'] == 'agent' and prev_customer_msg is not None:
                    pair = {
                        'conversation_id': conv_id,
                        'customer_message': self.clean_text(prev_customer_msg.get('message', '')),
                        'agent_response': self.clean_text(msg.get('message', '')),
                        'channel': msg.get('channel', 'unknown'),
                        'timestamp': msg.get('timestamp', ''),
                        'source_file': msg.get('source_file', '')
                    }
                    
                    # Boş mesajları filtreleme
                    if pair['customer_message'] and pair['agent_response']:
                        conversation_pairs.append(pair)
                    
                    prev_customer_msg = None
        
        logger.info(f"✅ {len(conversation_pairs)} konuşma çifti çıkarıldı")
        return conversation_pairs
    
    def detect_scenario(self, customer_message: str) -> str:
        """Müşteri mesajından senaryoyu tespit et"""
        message = customer_message.lower()
        
        # Sipariş takip
        if any(word in message for word in ['sipariş', 'takip', 'nerede', 'geldi mi', 'teslim']):
            return 'siparis_takip'
        
        # İade/değişim
        elif any(word in message for word in ['iade', 'değişim', 'geri ver', 'beğenmedim', 'kusur']):
            return 'iade_degisim'
        
        # Ürün bilgisi
        elif any(word in message for word in ['ürün', 'fiyat', 'özellik', 'renk', 'boyut', 'ölçü']):
            return 'urun_bilgisi'
        
        # Kargo sorgulama
        elif any(word in message for word in ['kargo', 'teslimat', 'adres', 'gönder']):
            return 'kargo_sorgulama'
        
        # Genel destek
        else:
            return 'genel_destek'
    
    def create_training_datasets(self, conversation_pairs: List[Dict]) -> Dict:
        """Eğitim dataset'lerini oluştur"""
        logger.info("📚 Eğitim dataset'leri oluşturuluyor...")
        
        datasets = {
            'alpaca_format': [],
            'chatml_format': [],
            'conversation_format': [],
            'scenario_datasets': {
                'siparis_takip': [],
                'iade_degisim': [],
                'urun_bilgisi': [],
                'kargo_sorgulama': [],
                'genel_destek': []
            }
        }
        
        for pair in conversation_pairs:
            # Senaryo tespiti
            scenario = self.detect_scenario(pair['customer_message'])
            
            # Alpaca format
            alpaca_entry = {
                "instruction": "Rani Mobilya müşteri hizmetleri temsilcisi olarak aşağıdaki müşteri sorusuna yardımcı ve profesyonel bir şekilde yanıt verin:",
                "input": pair['customer_message'],
                "output": pair['agent_response'],
                "scenario": scenario,
                "channel": pair['channel'],
                "metadata": {
                    "conversation_id": pair['conversation_id'],
                    "timestamp": pair['timestamp'],
                    "source_file": pair['source_file']
                }
            }
            datasets['alpaca_format'].append(alpaca_entry)
            
            # ChatML format
            chatml_entry = {
                "messages": [
                    {
                        "role": "system",
                        "content": "Sen Rani Mobilya'nın AI müşteri hizmetleri asistanısın. Müşterilere yardımcı, anlayışlı ve profesyonel bir şekilde destek ol."
                    },
                    {
                        "role": "user", 
                        "content": pair['customer_message']
                    },
                    {
                        "role": "assistant",
                        "content": pair['agent_response']
                    }
                ],
                "scenario": scenario,
                "channel": pair['channel']
            }
            datasets['chatml_format'].append(chatml_entry)
            
            # Conversation format
            conv_entry = {
                "customer": pair['customer_message'],
                "agent": pair['agent_response'],
                "scenario": scenario,
                "channel": pair['channel'],
                "conversation_id": pair['conversation_id']
            }
            datasets['conversation_format'].append(conv_entry)
            
            # Scenario-specific datasets
            datasets['scenario_datasets'][scenario].append(conv_entry)
        
        logger.info(f"📊 Dataset istatistikleri:")
        logger.info(f"   Alpaca format: {len(datasets['alpaca_format'])} örnek")
        logger.info(f"   ChatML format: {len(datasets['chatml_format'])} örnek") 
        logger.info(f"   Konuşma format: {len(datasets['conversation_format'])} örnek")
        
        for scenario, data in datasets['scenario_datasets'].items():
            logger.info(f"   {scenario}: {len(data)} örnek")
        
        return datasets
    
    def save_datasets(self, datasets: Dict, output_dir: str = "processed_datasets_v2") -> None:
        """Dataset'leri kaydet"""
        logger.info(f"💾 Dataset'ler kaydediliyor: {output_dir}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Ana dataset'leri kaydet
        pd.DataFrame(datasets['alpaca_format']).to_json(
            os.path.join(output_dir, 'alpaca_format.json'), 
            orient='records', 
            force_ascii=False, 
            indent=2
        )
        
        pd.DataFrame(datasets['chatml_format']).to_json(
            os.path.join(output_dir, 'chatml_format.json'), 
            orient='records', 
            force_ascii=False, 
            indent=2
        )
        
        pd.DataFrame(datasets['conversation_format']).to_csv(
            os.path.join(output_dir, 'conversation_pairs.csv'), 
            index=False, 
            encoding='utf-8'
        )
        
        # Senaryo-specific dataset'leri kaydet
        scenario_dir = os.path.join(output_dir, 'scenarios')
        os.makedirs(scenario_dir, exist_ok=True)
        
        for scenario, data in datasets['scenario_datasets'].items():
            if data:  # Boş değilse kaydet
                pd.DataFrame(data).to_csv(
                    os.path.join(scenario_dir, f'{scenario}.csv'),
                    index=False,
                    encoding='utf-8'
                )
        
        # Train/validation/test split'leri oluştur
        self.create_train_splits(datasets['conversation_format'], output_dir)
        
        logger.info("✅ Tüm dataset'ler başarıyla kaydedildi")
    
    def create_train_splits(self, conversation_data: List[Dict], output_dir: str) -> None:
        """Train/validation/test bölümlemesi yap"""
        logger.info("🔄 Train/validation/test bölümlemesi yapılıyor...")
        
        df = pd.DataFrame(conversation_data)
        
        # Karıştır
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        total_size = len(df)
        train_size = int(0.8 * total_size)
        val_size = int(0.1 * total_size)
        
        train_df = df[:train_size]
        val_df = df[train_size:train_size + val_size]
        test_df = df[train_size + val_size:]
        
        # Kaydet
        splits_dir = os.path.join(output_dir, 'splits')
        os.makedirs(splits_dir, exist_ok=True)
        
        train_df.to_csv(os.path.join(splits_dir, 'train.csv'), index=False, encoding='utf-8')
        val_df.to_csv(os.path.join(splits_dir, 'validation.csv'), index=False, encoding='utf-8')
        test_df.to_csv(os.path.join(splits_dir, 'test.csv'), index=False, encoding='utf-8')
        
        logger.info(f"📊 Bölümleme tamamlandı:")
        logger.info(f"   Train: {len(train_df)} örnek (%80)")
        logger.info(f"   Validation: {len(val_df)} örnek (%10)")
        logger.info(f"   Test: {len(test_df)} örnek (%10)")
    
    def generate_statistics_report(self, datasets: Dict) -> Dict:
        """İstatistik raporu oluştur"""
        logger.info("📈 İstatistik raporu oluşturuluyor...")
        
        conv_df = pd.DataFrame(datasets['conversation_format'])
        
        stats = {
            'total_conversations': len(conv_df),
            'unique_conversation_ids': conv_df['conversation_id'].nunique(),
            'channel_distribution': conv_df['channel'].value_counts().to_dict(),
            'scenario_distribution': conv_df['scenario'].value_counts().to_dict(),
            'avg_customer_message_length': conv_df['customer'].str.len().mean(),
            'avg_agent_message_length': conv_df['agent'].str.len().mean(),
            'processing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return stats
    
    def run_full_pipeline(self) -> None:
        """Tam işleme pipeline'ını çalıştır"""
        start_time = datetime.now()
        logger.info("🚀 Gelişmiş veri işleme pipeline'ı başlatılıyor...")
        
        try:
            # 1. Dataset'leri yükle
            self.load_datasets()
            
            # 2. Veri yapısını analiz et
            structure_analysis = self.analyze_data_structure()
            
            # 3. Konuşma çiftlerini çıkar
            conversation_pairs = self.extract_conversation_pairs()
            
            # 4. Eğitim dataset'lerini oluştur
            datasets = self.create_training_datasets(conversation_pairs)
            
            # 5. Dataset'leri kaydet
            self.save_datasets(datasets)
            
            # 6. İstatistik raporu oluştur
            stats = self.generate_statistics_report(datasets)
            
            # Raporu kaydet
            with open('processed_datasets_v2/processing_report.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'structure_analysis': structure_analysis,
                    'processing_stats': stats,
                    'file_stats': self.stats
                }, f, ensure_ascii=False, indent=2, default=str)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            logger.info("🎉 Pipeline başarıyla tamamlandı!")
            logger.info(f"⏱️  Toplam işleme süresi: {processing_time:.2f} saniye")
            logger.info(f"📊 Toplam konuşma çifti: {len(conversation_pairs)}")
            logger.info(f"📁 Çıktı klasörü: processed_datasets_v2/")
            
        except Exception as e:
            logger.error(f"❌ Pipeline hatası: {str(e)}")
            raise

def main():
    """Ana fonksiyon"""
    print("🎯 Rani Mobilya - Gelişmiş Veri Ön İşleme Sistemi v2.0")
    print("=" * 60)
    
    processor = DataPreprocessor()
    processor.run_full_pipeline()
    
    print("\n✅ İşlem tamamlandı! Çıktıları kontrol edin:")
    print("📁 processed_datasets_v2/")
    print("📄 data_preprocessing_v2.log")

if __name__ == "__main__":
    main() 