import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FaRobot, 
  FaComments, 
  FaChartBar, 
  FaFlask,
  FaBrain,
  FaCogs,
  FaDatabase,
  FaRocket,
  FaPlay,
  FaChevronRight
} from 'react-icons/fa';
import { apiService, utils } from '../services/api';

const HomePage = () => {
  const [stats, setStats] = useState(null);
  const [testResult, setTestResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await apiService.healthCheck();
      setStats(data);
    } catch (error) {
      console.error('Stats loading failed:', error);
    }
  };

  const runQuickTest = async (question) => {
    setIsLoading(true);
    try {
      const result = await apiService.askQuestion(question, 'prompt');
      setTestResult(result);
    } catch (error) {
      console.error('Quick test failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    {
      icon: FaComments,
      title: '💬 Canlı Chat',
      description: 'AI destekli sohbet arayüzü ile gerçek zamanlı müşteri desteği.',
      link: '/chat',
      color: 'from-blue-400 to-blue-600'
    },
    {
      icon: FaChartBar,
      title: '📊 Analytics Dashboard',
      description: 'Model performansı, veri istatistikleri ve sistem metrikleri.',
      link: '/dashboard',
      color: 'from-green-400 to-green-600'
    },
    {
      icon: FaFlask,
      title: '🧪 Model Testi',
      description: 'Farklı AI yaklaşımlarını karşılaştırın ve test edin.',
      link: '/test',
      color: 'from-purple-400 to-purple-600'
    }
  ];

  const systemFeatures = [
    { icon: FaBrain, label: 'RAG Sistemi', value: '9.6K+ Bilgi' },
    { icon: FaCogs, label: 'Prompt Engineering', value: '5 Senaryo' },
    { icon: FaDatabase, label: 'Eğitim Verisi', value: '23K+ Mesaj' },
    { icon: FaRocket, label: 'Doğruluk Oranı', value: '90%+' }
  ];

  const quickTests = [
    { question: 'Siparişim ne zaman gelir?', emoji: '📦', label: 'Sipariş Takip' },
    { question: 'Bu ürünü iade etmek istiyorum', emoji: '🔄', label: 'İade İşlemi' },
    { question: 'TV ünitesinin fiyatı nedir?', emoji: '💰', label: 'Fiyat Sorgusu' },
    { question: 'Kargo durumunu öğrenebilir miyim?', emoji: '🚚', label: 'Kargo Takip' }
  ];

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <motion.section 
        className="text-center py-16"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="bg-white rounded-3xl shadow-2xl p-12 gradient-primary text-white">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mb-8"
          >
            <FaRobot className="text-6xl mx-auto mb-6" />
            <h1 className="text-5xl font-bold mb-4">
              Rani AI Müşteri Hizmetleri
            </h1>
            <p className="text-xl opacity-90 mb-8">
              Yapay zeka destekli müşteri hizmetleri sistemi ile 7/24 destek
            </p>
          </motion.div>

          <div className="flex flex-wrap justify-center gap-4 mb-8">
            <span className="bg-white bg-opacity-20 px-4 py-2 rounded-full text-sm font-medium">
              🧠 RAG Sistemi
            </span>
            <span className="bg-white bg-opacity-20 px-4 py-2 rounded-full text-sm font-medium">
              ⚙️ Prompt Engineering
            </span>
            <span className="bg-white bg-opacity-20 px-4 py-2 rounded-full text-sm font-medium">
              🚀 Fine-Tuning Ready
            </span>
          </div>

          <Link
            to="/chat"
            className="inline-flex items-center space-x-2 bg-white text-blue-600 px-8 py-4 rounded-full font-bold text-lg hover:bg-gray-100 transition-all duration-200 transform hover:scale-105"
          >
            <FaPlay />
            <span>Hemen Başla</span>
            <FaChevronRight />
          </Link>
        </div>
      </motion.section>

      {/* Features */}
      <section>
        <h2 className="text-3xl font-bold text-center mb-8 text-gray-800">
          ✨ Ana Özellikler
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              className="bg-white rounded-2xl shadow-xl p-8 text-center hover:shadow-2xl transition-all duration-300"
            >
              <div className={`bg-gradient-to-r ${feature.color} text-white p-4 rounded-2xl w-16 h-16 mx-auto mb-6 flex items-center justify-center`}>
                <feature.icon className="text-2xl" />
              </div>
              <h3 className="text-xl font-bold mb-4 text-gray-800">
                {feature.title}
              </h3>
              <p className="text-gray-600 mb-6">
                {feature.description}
              </p>
              <Link
                to={feature.link}
                className="inline-flex items-center space-x-2 text-blue-600 font-semibold hover:text-blue-800 transition-colors"
              >
                <span>Keşfet</span>
                <FaChevronRight />
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      {/* System Stats */}
      <section className="bg-white rounded-2xl shadow-xl p-8">
        <h2 className="text-2xl font-bold text-center mb-8 text-gray-800">
          📊 Sistem Özellikleri
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {systemFeatures.map((item, index) => (
            <motion.div
              key={index}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="text-center p-4 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <item.icon className="text-3xl text-blue-500 mx-auto mb-3" />
              <h3 className="text-2xl font-bold text-gray-800 mb-1">
                {item.value}
              </h3>
              <p className="text-sm text-gray-600">
                {item.label}
              </p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Quick Test */}
      <section className="bg-white rounded-2xl shadow-xl p-8">
        <h2 className="text-2xl font-bold text-center mb-8 text-gray-800">
          🚀 Hızlı Test
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {quickTests.map((test, index) => (
            <motion.button
              key={index}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => runQuickTest(test.question)}
              disabled={isLoading}
              className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 hover:border-blue-400 rounded-xl p-4 text-center transition-all duration-200 disabled:opacity-50"
            >
              <div className="text-2xl mb-2">{test.emoji}</div>
              <div className="text-sm font-medium text-gray-800">
                {test.label}
              </div>
            </motion.button>
          ))}
        </div>

        {/* Test Result */}
        {isLoading && (
          <div className="text-center py-8">
            <div className="inline-flex items-center space-x-2 text-blue-600">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span>AI sistemi test ediliyor...</span>
            </div>
          </div>
        )}

        {testResult && !isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6"
          >
            <h3 className="font-bold text-gray-800 mb-2 flex items-center">
              <span className="text-green-500 mr-2">✅</span>
              Test Sonucu
            </h3>
            <p className="text-gray-700 mb-4">{testResult.answer}</p>
            <div className="flex flex-wrap gap-2">
              <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                {testResult.method}
              </span>
              <span className={`px-3 py-1 rounded-full text-sm ${utils.getConfidenceBadgeColor(testResult.confidence)}`}>
                {utils.formatConfidence(testResult.confidence)} güven
              </span>
            </div>
          </motion.div>
        )}
      </section>

      {/* System Status */}
      {stats && (
        <section className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-center mb-8 text-gray-800">
            💚 Sistem Durumu
          </h2>
          <div className="grid md:grid-cols-3 gap-6 text-center">
            <div className="p-4 bg-green-50 rounded-xl">
              <div className="text-green-500 text-2xl mb-2">✅</div>
              <h3 className="font-bold text-gray-800">API Durumu</h3>
              <p className="text-green-600 capitalize">{stats.status}</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-xl">
              <div className="text-blue-500 text-2xl mb-2">🧠</div>
              <h3 className="font-bold text-gray-800">RAG Sistemi</h3>
              <p className="text-blue-600">{stats.services?.knowledge_base_size} kayıt</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-xl">
              <div className="text-purple-500 text-2xl mb-2">💬</div>
              <h3 className="font-bold text-gray-800">Konuşmalar</h3>
              <p className="text-purple-600">{stats.services?.conversation_count} aktif</p>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};

export default HomePage; 