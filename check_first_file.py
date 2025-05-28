import pandas as pd

# İlk dosyayı header olmadan yükle
df1 = pd.read_csv('1-5.csv', header=None)
print("1-5.csv dosyası:")
print(f"Boyut: {df1.shape}")
print("\nİlk 3 satır:")
print(df1.head(3))

# İkinci dosyanın kolonlarını ilk dosyaya uygula
df2_columns = ['conversation_id', 'conversation_url', 'interaction_raw_id', 'message_id', 'message_type', 
               'message_parts', 'created_time', 'message_source', 'actor_id', 'actor_type', 'actor_sub_entity', 
               'actor_email', 'actor_phone', 'actor_first_name', 'actor_last_name', 'reference_id', 'channel_id', 
               'channel_name', 'detailed_message_type', 'customer_id']

df1.columns = df2_columns
print(f"\nKolon isimleri atandıktan sonra:")
print(f"Actor types: {df1['actor_type'].value_counts()}")

# Tarihleri kontrol et
df1['created_time'] = pd.to_datetime(df1['created_time'])
df1['date'] = df1['created_time'].dt.date
print(f"\nTarih aralığı: {df1['date'].min()} - {df1['date'].max()}")
print(f"Günlük dağılım:")
print(df1.groupby('date').size()) 