import pandas as pd

# İşlenmiş veriyi yükle
df = pd.read_csv('processed_chat_data.csv')
print(f"📊 İşlenmiş veri yüklendi: {len(df)} mesaj")
print(f"📋 Kolonlar: {list(df.columns)}")

print("\n🔍 VERİ ÖRNEKLERİ")

# Müşteri-agent konuşma örnekleri
print("\n👤 MÜŞTERİ MESAJLARI (İlk 5):")
customer_msgs = df[df['role'] == 'customer']['message_content_masked'].head(5)
for i, msg in enumerate(customer_msgs, 1):
    print(f"{i}. {msg[:150]}...")

print("\n🎧 AGENT MESAJLARI (İlk 5):")
agent_msgs = df[df['role'] == 'agent']['message_content_masked'].head(5)
for i, msg in enumerate(agent_msgs, 1):
    print(f"{i}. {msg[:150]}...")

print("\n📈 DETAYLI İSTATİSTİKLER")
print(f"Role dağılımı:")
print(df['role'].value_counts())

print(f"\nKarakter uzunluğu istatistikleri:")
print(df['message_content_masked'].str.len().describe())

print(f"\nKanal dağılımı:")
print(df['channel_name'].value_counts())

# Sık kullanılan kelimeler
print(f"\n📝 SIK KULLANILAN KELİMELER")
all_text = ' '.join(df['message_content_masked'].astype(str))
words = all_text.lower().split()
word_freq = {}
for word in words:
    if len(word) > 3:  # 3 karakterden uzun kelimeler
        word_freq[word] = word_freq.get(word, 0) + 1

# En sık 10 kelime
top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
for word, count in top_words:
    print(f"{word}: {count}")

# Örnek konuşma
print(f"\n💬 ÖRNEK KONUŞMA (İlk konuşmadan 10 mesaj):")
first_conv_id = df['conversation_id'].iloc[0]
conv_sample = df[df['conversation_id'] == first_conv_id].head(10)

for _, row in conv_sample.iterrows():
    print(f"{row['role'].upper()}: {row['message_content_masked'][:100]}...") 