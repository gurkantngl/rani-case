from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import pandas as pd
from datetime import datetime
import os
import asyncio
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import Optional, List, Dict
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the enhanced systems
try:
    from rag_system_v2 import EnhancedRAGSystem
    from prompt_engineering import PromptEngineer
except ImportError as e:
    logger.warning(f"Could not import enhanced systems: {e}")
    EnhancedRAGSystem = None
    PromptEngineer = None

# FastAPI app instance
app = FastAPI(
    title="Rani AI Müşteri Hizmetleri",
    description="Yapay zeka destekli müşteri hizmetleri sistemi",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm originlere izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates setup
templates = Jinja2Templates(directory="templates")

# Global variables for models
rag_vectorizer = None
rag_vectors = None
knowledge_base = None
conversation_history = []

# Initialize systems
rag_system = None
prompt_engineer = None

def initialize_systems():
    """Initialize AI systems"""
    global rag_system, prompt_engineer
    
    try:
        # Initialize Enhanced RAG System
        logger.info("🚀 RAG Sistemi başlatılıyor...")
        rag_system = EnhancedRAGSystem()
        
        if rag_system.load_model():
            logger.info("✅ RAG Sistemi yüklendi")
        else:
            logger.warning("⚠️ RAG Sistemi eğitiliyor...")
            if rag_system.load_knowledge_base() and rag_system.train_vectorizer():
                rag_system.save_model()
                logger.info("✅ RAG Sistemi eğitildi ve kaydedildi")
            else:
                logger.error("❌ RAG Sistemi başlatılamadı")
                rag_system = None
        
        # Initialize Prompt Engineer
        logger.info("🧠 Prompt Engineer başlatılıyor...")
        prompt_engineer = PromptEngineer()
        logger.info("✅ Prompt Engineer hazır")
        
    except Exception as e:
        logger.error(f"Sistem başlatma hatası: {str(e)}")

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    approach: str = "prompt"  # rag, prompt, hybrid

class ChatResponse(BaseModel):
    message: str
    answer: str
    timestamp: str
    approach: str
    method: str
    confidence: float
    scenario: Optional[str] = None

class StatsResponse(BaseModel):
    model_performance: dict
    data_statistics: dict

async def load_rag_system():
    """RAG sistemini async olarak yükle"""
    global rag_vectorizer, rag_vectors, knowledge_base
    
    try:
        # İşlenmiş veriyi yükle - doğru dosya yolu
        df = pd.read_csv('processed_datasets_v2/conversation_pairs.csv')
        
        # Agent yanıtlarını knowledge base olarak kullan
        agent_messages = df['agent'].dropna()
        knowledge_base = agent_messages.tolist()
        
        # TF-IDF vektörizer
        rag_vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
        rag_vectors = rag_vectorizer.fit_transform(knowledge_base)
        
        print(f"✅ RAG sistemi yüklendi: {len(knowledge_base)} bilgi girdisi")
        return True
    except Exception as e:
        print(f"❌ RAG sistemi yüklenirken hata: {e}")
        return False

async def rag_search(query: str, top_k: int = 3) -> dict:
    """RAG sistemi ile async arama yap"""
    global rag_vectorizer, rag_vectors, knowledge_base
    
    if not rag_vectorizer or rag_vectors is None or not knowledge_base:
        return {"answer": "RAG sistemi henüz yüklenmedi.", "confidence": 0.0}
    
    try:
        # Query'yi vektörize et
        query_vector = rag_vectorizer.transform([query])
        
        # Benzerlik hesapla
        similarities = cosine_similarity(query_vector, rag_vectors).flatten()
        
        # En benzer sonuçları bul
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        if len(top_indices) > 0 and similarities[top_indices[0]] > 0.1:
            best_answer = knowledge_base[top_indices[0]]
            confidence = float(similarities[top_indices[0]])
            return {"answer": best_answer, "confidence": confidence}
        else:
            return {"answer": "Bu konuda yeterli bilgi bulunamadı.", "confidence": 0.0}
    except Exception as e:
        return {"answer": f"Arama hatası: {str(e)}", "confidence": 0.0}

def detect_scenario(message: str) -> str:
    """Mesajdan senaryoyu tespit et"""
    message_lower = message.lower()
    
    # Anahtar kelimeler
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

async def get_prompt_response(message: str, scenario: str) -> dict:
    """Prompt engineering ile async yanıt üret"""
    
    # Senaryo şablonları
    prompts = {
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
    
    prompt_data = prompts.get(scenario, prompts['genel_destek'])
    
    # Async simulation - gerçek LLM entegrasyonu için
    await asyncio.sleep(0.1)  # Simulate processing time
    
    return {
        "answer": prompt_data['response'],
        "scenario": scenario,
        "confidence": 0.85
    }

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Ana sayfa"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard sayfası"""
    try:
        # Veri istatistikleri - doğru dosya yolu
        df = pd.read_csv('processed_datasets_v2/conversation_pairs.csv')
        
        stats = {
            'total_messages': len(df) * 2,  # Customer + agent messages
            'total_conversations': df['conversation_id'].nunique(),
            'channels': df['channel'].value_counts().to_dict(),
            'scenarios': df['scenario'].value_counts().to_dict(),
            'daily_stats': {}  # Timestamp processing needed for this
        }
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request, 
            "stats": stats
        })
    except Exception as e:
        return templates.TemplateResponse("dashboard.html", {
            "request": request, 
            "stats": {}, 
            "error": str(e)
        })

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    """Chat arayüzü"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    """Test sayfası"""
    return templates.TemplateResponse("test.html", {"request": request})

@app.post("/api/ask")
async def ask_question(request: ChatRequest):
    """AI'dan soru sor"""
    try:
        start_time = datetime.now()
        message = request.message.strip()
        approach = request.approach.lower()
        
        if not message:
            raise HTTPException(status_code=400, detail="Mesaj boş olamaz")
        
        # Response structure
        response = {
            "answer": "",
            "confidence": 0.0,
            "method": approach.upper(),
            "scenario": "genel_destek",
            "response_time": 0,
            "sources": []
        }
        
        if approach == "rag":
            if rag_system and rag_system.is_trained:
                result = rag_system.generate_response(message)
                response.update({
                    "answer": result['answer'],
                    "confidence": result['confidence'],
                    "method": result['method'],
                    "scenario": result['scenario'],
                    "sources": result.get('sources', [])
                })
            else:
                response.update({
                    "answer": "RAG sistemi henüz hazır değil. Lütfen daha sonra tekrar deneyin.",
                    "confidence": 0.1,
                    "method": "RAG_ERROR"
                })
        
        elif approach == "prompt":
            if prompt_engineer:
                result = prompt_engineer.generate_response(message)
                response.update({
                    "answer": result['response'],
                    "confidence": result['confidence'],
                    "method": f"PROMPT_{result['scenario'].upper()}",
                    "scenario": result['scenario']
                })
            else:
                response.update({
                    "answer": "Prompt sistemi hazır değil. Lütfen daha sonra tekrar deneyin.",
                    "confidence": 0.1,
                    "method": "PROMPT_ERROR"
                })
        
        elif approach == "hybrid":
            # Hybrid approach: RAG + Prompt Engineering
            rag_result = None
            prompt_result = None
            
            if rag_system and rag_system.is_trained:
                rag_result = rag_system.generate_response(message)
            
            if prompt_engineer:
                prompt_result = prompt_engineer.generate_response(message)
            
            # Choose the best result based on confidence
            if rag_result and prompt_result:
                if rag_result['confidence'] > prompt_result['confidence']:
                    response.update({
                        "answer": rag_result['answer'],
                        "confidence": rag_result['confidence'],
                        "method": f"HYBRID_RAG_{rag_result['method']}",
                        "scenario": rag_result['scenario'],
                        "sources": rag_result.get('sources', [])
                    })
                else:
                    response.update({
                        "answer": prompt_result['response'],
                        "confidence": prompt_result['confidence'],
                        "method": f"HYBRID_PROMPT_{prompt_result['scenario'].upper()}",
                        "scenario": prompt_result['scenario']
                    })
            elif rag_result:
                response.update({
                    "answer": rag_result['answer'],
                    "confidence": rag_result['confidence'],
                    "method": f"HYBRID_RAG_{rag_result['method']}",
                    "scenario": rag_result['scenario']
                })
            elif prompt_result:
                response.update({
                    "answer": prompt_result['response'],
                    "confidence": prompt_result['confidence'],
                    "method": f"HYBRID_PROMPT_{prompt_result['scenario'].upper()}",
                    "scenario": prompt_result['scenario']
                })
            else:
                response.update({
                    "answer": "Üzgünüm, şu anda size yardımcı olamıyorum. Lütfen daha sonra tekrar deneyin.",
                    "confidence": 0.1,
                    "method": "HYBRID_ERROR"
                })
        
        else:
            raise HTTPException(status_code=400, detail="Geçersiz yaklaşım. Kullanılabilir: rag, prompt, hybrid")
        
        # Calculate response time
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        response["response_time"] = round(response_time, 2)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Soru yanıtlama hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=f"İç sunucu hatası: {str(e)}")

@app.get("/api/history")
async def get_history():
    """Konuşma geçmişini getir"""
    return conversation_history[-10:]  # Son 10 mesaj

@app.get("/api/stats")
async def get_stats():
    """Sistem istatistiklerini getir"""
    try:
        # RAG system stats
        rag_stats = {}
        if rag_system:
            rag_stats = rag_system.get_statistics()
        
        # General stats
        stats = {
            "total_conversations": rag_stats.get('knowledge_base_size', 0),
            "scenarios": rag_stats.get('scenarios', {}),
            "channels": rag_stats.get('channels', {}),
            "rag_system": {
                "is_trained": rag_stats.get('is_trained', False),
                "vector_dimensions": rag_stats.get('vector_dimensions', 0),
                "knowledge_base_size": rag_stats.get('knowledge_base_size', 0)
            },
            "prompt_system": {
                "is_ready": prompt_engineer is not None,
                "scenarios": ["siparis_takip", "iade_degisim", "urun_bilgisi", "kargo_sorgulama", "genel_destek"]
            },
            "processing_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"İstatistik hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=f"İstatistik getirilemedi: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Sistem sağlık kontrolü"""
    
    # System status
    rag_status = "healthy" if (rag_system and rag_system.is_trained) else "unhealthy"
    prompt_status = "healthy" if prompt_engineer else "unhealthy"
    
    # Service details
    services = {
        "rag_system": {
            "status": rag_status,
            "knowledge_base_size": rag_system.get_statistics()['knowledge_base_size'] if rag_system else 0,
            "is_trained": rag_system.is_trained if rag_system else False
        },
        "prompt_system": {
            "status": prompt_status,
            "scenario_count": 5 if prompt_engineer else 0
        }
    }
    
    # Overall health
    overall_status = "healthy" if (rag_status == "healthy" and prompt_status == "healthy") else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "services": services,
        "version": "2.0",
        "conversation_count": services["rag_system"]["knowledge_base_size"]
    }

@app.on_event("startup")
async def startup_event():
    """Uygulama başlangıcında çalışacak işlemler"""
    print("🚀 Rani AI Müşteri Hizmetleri (FastAPI) Başlatılıyor...")
    
    # RAG sistemini yükle
    success = await load_rag_system()
    if success:
        print("✅ RAG sistemi başarıyla yüklendi")
    else:
        print("⚠️ RAG sistemi yüklenemedi")
    
    print("🌐 FastAPI Server: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("📚 ReDoc: http://localhost:8000/redoc")

    # Initialize systems
    initialize_systems()

@app.on_event("shutdown")
async def shutdown_event():
    """Uygulama kapatılırken çalışacak işlemler"""
    print("🔄 Sistem kapatılıyor...")
    print("✅ Temizlik işlemleri tamamlandı")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 