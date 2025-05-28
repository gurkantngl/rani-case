import pandas as pd
import json
from collections import Counter
import re
from datetime import datetime

def load_and_analyze_data():
    """Veri setlerini yükle ve analiz et"""
    
    print("📊 Veri Setlerini Yüklüyor...")
    
    # İlk dosyayı yükle (header yok gibi görünüyor)
    try:
        df1 = pd.read_csv('1-5.csv', header=None)
        print(f"✅ 1-5.csv yüklendi: {df1.shape[0]} satır, {df1.shape[1]} kolon")
    except Exception as e:
        print(f"❌ 1-5.csv yüklenirken hata: {e}")
        df1 = None
    
    # İkinci dosyayı yükle (header var)
    try:
        df2 = pd.read_csv('5-12.csv')
        print(f"✅ 5-12.csv yüklendi: {df2.shape[0]} satır, {df2.shape[1]} kolon")
        print(f"📋 Kolonlar: {list(df2.columns)}")
    except Exception as e:
        print(f"❌ 5-12.csv yüklenirken hata: {e}")
        df2 = None
        return
    
    # Temel istatistikler
    print("\n📈 TEMEL İSTATİSTİKLER")
    print(f"Toplam konuşma sayısı: {df2['conversation_id'].nunique()}")
    print(f"Toplam mesaj sayısı: {len(df2)}")
    print(f"Benzersiz aktör sayısı: {df2['actor_id'].nunique()}")
    
    # Aktör tipleri analizi
    print("\n👥 AKTÖR TİPLERİ")
    actor_types = df2['actor_type'].value_counts()
    print(actor_types)
    
    # Mesaj tipleri analizi
    print("\n💬 MESAJ TİPLERİ")
    message_types = df2['message_type'].value_counts()
    print(message_types)
    
    # Kanal analizi
    print("\n📱 KANAL DAĞILIMI")
    channels = df2['channel_name'].value_counts()
    print(channels)
    
    # Zaman analizi
    print("\n⏰ ZAMAN ANALİZİ")
    df2['created_time'] = pd.to_datetime(df2['created_time'])
    df2['date'] = df2['created_time'].dt.date
    daily_counts = df2.groupby('date').size()
    print("Günlük mesaj sayıları:")
    print(daily_counts)
    
    # Örnek mesajlar
    print("\n💭 ÖRNEK MESAJLAR")
    normal_messages = df2[df2['message_type'] == 'normal']
    if len(normal_messages) > 0:
        print("Normal mesaj örnekleri:")
        for i, row in normal_messages.head(3).iterrows():
            try:
                message_parts = json.loads(row['message_parts'])
                if message_parts and 'text' in message_parts[0]:
                    content = message_parts[0]['text']['content']
                    print(f"- {row['actor_type']}: {content[:100]}...")
            except:
                print(f"- {row['actor_type']}: [Mesaj parse edilemedi]")
    
    return df2

if __name__ == "__main__":
    df = load_and_analyze_data() 