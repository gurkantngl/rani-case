import pandas as pd
import json
import re
from datetime import datetime
import html

def load_and_combine_data():
    """Veri setlerini yükle ve birleştir"""
    
    print("📊 Veri Setlerini Yüklüyor...")
    
    # İkinci dosyayı yükle (bu dosya düzgün görünüyor)
    df2 = pd.read_csv('5-12.csv')
    print(f"✅ 5-12.csv yüklendi: {df2.shape[0]} satır")
    
    # İlk dosyayı daha dikkatli yükle
    try:
        # İlk dosyada header problem var, manuel kontrol
        with open('1-5.csv', 'r', encoding='utf-8') as f:
            first_line = f.readline()
            print(f"İlk satır: {first_line[:100]}...")
        
        # Eğer ilk satır veri ise header=None kullan
        if 'conversation_id' not in first_line:
            df1 = pd.read_csv('1-5.csv', header=None)
            df1.columns = df2.columns
            print(f"✅ 1-5.csv yüklendi (header eklendi): {df1.shape[0]} satır")
        else:
            df1 = pd.read_csv('1-5.csv')
            print(f"✅ 1-5.csv yüklendi (header var): {df1.shape[0]} satır")
        
        # Dataframe'leri birleştir
        combined_df = pd.concat([df1, df2], ignore_index=True)
        print(f"✅ Veriler birleştirildi: {combined_df.shape[0]} satır")
        
    except Exception as e:
        print(f"⚠️  İlk dosya yüklenemedi, sadece ikinci dosya kullanılıyor: {e}")
        combined_df = df2
    
    return combined_df

def preprocess_data(df):
    """Veri ön işleme pipeline'ı"""
    
    print("\n🔧 VERİ ÖN İŞLEME BAŞLIYOR...")
    
    # 1. Zaman bilgilerini düzenle
    print("⏰ Zaman bilgileri işleniyor...")
    df['created_time'] = pd.to_datetime(df['created_time'], errors='coerce')
    df['date'] = df['created_time'].dt.date
    df['hour'] = df['created_time'].dt.hour
    df['day_of_week'] = df['created_time'].dt.day_name()
    
    # 2. Mesaj içeriklerini çıkar ve temizle
    print("💬 Mesaj içerikleri çıkarılıyor...")
    
    def extract_message_content(message_parts):
        """JSON mesaj parçalarından içeriği çıkar"""
        try:
            if pd.isna(message_parts):
                return ""
            
            parts = json.loads(message_parts)
            content = ""
            
            for part in parts:
                if 'text' in part and 'content' in part['text']:
                    content += part['text']['content'] + " "
            
            # HTML decode
            content = html.unescape(content)
            
            # Basit temizlik
            content = re.sub(r'<[^>]+>', '', content)  # HTML tagları kaldır
            content = re.sub(r'\s+', ' ', content)     # Fazla boşlukları temizle
            content = content.strip()
            
            return content
            
        except:
            return ""
    
    df['message_content'] = df['message_parts'].apply(extract_message_content)
    
    # 3. Kişisel bilgileri maskeleme (basit)
    print("🔒 Kişisel bilgiler maskeleniyor...")
    
    def mask_personal_info(text):
        """Temel kişisel bilgi maskeleme"""
        if not text:
            return text
        
        # Telefon numaralarını maskele
        text = re.sub(r'\+?90\s?5\d{2}\s?\d{3}\s?\d{4}', '[TELEFON]', text)
        text = re.sub(r'05\d{2}\s?\d{3}\s?\d{4}', '[TELEFON]', text)
        
        # Email maskele
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # IBAN/Kredi kartı (basit)
        text = re.sub(r'\d{4}\s?\d{4}\s?\d{4}\s?\d{4}', '[KART_NO]', text)
        
        return text
    
    df['message_content_masked'] = df['message_content'].apply(mask_personal_info)
    
    # 4. Konuşma rolleri belirle
    print("👥 Roller belirleniyor...")
    
    def determine_role(actor_type, actor_email):
        """Aktör tipine göre rol belirle"""
        if actor_type == 'user':
            return 'customer'
        elif actor_type == 'agent':
            return 'agent'
        elif actor_type == 'bot':
            return 'bot'
        else:
            return 'system'
    
    df['role'] = df.apply(lambda x: determine_role(x['actor_type'], x['actor_email']), axis=1)
    
    # 5. Boş ve gereksiz mesajları filtrele
    print("🧹 Gereksiz mesajlar filtreleniyor...")
    
    # Sadece normal mesajları ve content'i olan mesajları al
    filtered_df = df[
        (df['message_type'] == 'normal') & 
        (df['message_content_masked'].str.len() > 0) &
        (df['role'].isin(['customer', 'agent']))
    ].copy()
    
    print(f"✅ Filtreleme tamamlandı: {len(filtered_df)} mesaj kaldı ({len(df)} -> {len(filtered_df)})")
    
    return df, filtered_df

def analyze_conversations(df):
    """Konuşma bazlı analiz"""
    
    print("\n📊 KONUŞMA ANALİZİ")
    
    # Konuşma başına istatistikler
    conv_stats = df.groupby('conversation_id').agg({
        'message_id': 'count',
        'role': lambda x: list(x),
        'created_time': ['min', 'max'],
        'channel_name': 'first'
    }).reset_index()
    
    conv_stats.columns = ['conversation_id', 'message_count', 'roles', 'start_time', 'end_time', 'channel']
    
    # Konuşma süresini hesapla
    conv_stats['duration_minutes'] = (conv_stats['end_time'] - conv_stats['start_time']).dt.total_seconds() / 60
    
    print(f"Toplam konuşma sayısı: {len(conv_stats)}")
    print(f"Ortalama mesaj sayısı per konuşma: {conv_stats['message_count'].mean():.1f}")
    print(f"Ortalama konuşma süresi: {conv_stats['duration_minutes'].mean():.1f} dakika")
    
    # Kanal dağılımı
    print(f"\nKanal dağılımı:")
    print(conv_stats['channel'].value_counts())
    
    return conv_stats

def main():
    """Ana işlem pipeline'ı"""
    
    # 1. Veri yükleme
    df = load_and_combine_data()
    
    # 2. Ön işleme
    df_processed, df_filtered = preprocess_data(df)
    
    # 3. Konuşma analizi
    conv_stats = analyze_conversations(df_filtered)
    
    # 4. Dosyaları kaydet
    print("\n💾 İşlenmiş veri kaydediliyor...")
    df_filtered.to_csv('processed_chat_data.csv', index=False)
    conv_stats.to_csv('conversation_stats.csv', index=False)
    
    print("✅ İşlem tamamlandı!")
    print(f"📁 processed_chat_data.csv - {len(df_filtered)} mesaj")
    print(f"📁 conversation_stats.csv - {len(conv_stats)} konuşma")
    
    return df_filtered, conv_stats

if __name__ == "__main__":
    df_filtered, conv_stats = main() 