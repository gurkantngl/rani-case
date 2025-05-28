import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  FaFlask, 
  FaPlay, 
  FaTrash,
  FaCogs,
  FaDatabase,
  FaLayerGroup
} from 'react-icons/fa';
import { apiService, utils } from '../services/api';

const TestPage = () => {
  const [testQuestion, setTestQuestion] = useState('');
  const [testResults, setTestResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [testHistory, setTestHistory] = useState([]);

  const runAllTests = async () => {
    if (!testQuestion.trim()) {
      alert('Lütfen bir test sorusu girin!');
      return;
    }

    setIsLoading(true);
    setTestResults(null);

    try {
      const results = await apiService.testAllApproaches(testQuestion);
      setTestResults(results);
      
      // Add to history
      const historyItem = {
        id: Date.now(),
        question: testQuestion,
        results,
        timestamp: new Date()
      };
      setTestHistory(prev => [historyItem, ...prev.slice(0, 9)]); // Keep last 10
      
    } catch (error) {
      console.error('Test failed:', error);
      alert('Test sırasında bir hata oluştu.');
    } finally {
      setIsLoading(false);
    }
  };

  const setQuickTest = (question) => {
    setTestQuestion(question);
  };

  const clearHistory = () => {
    if (window.confirm('Test geçmişini temizlemek istediğinizden emin misiniz?')) {
      setTestHistory([]);
    }
  };

  const quickTests = [
    { question: 'Siparişim ne zaman gelir?', emoji: '📦', label: 'Sipariş Takip' },
    { question: 'Bu ürünü iade etmek istiyorum, nasıl yapabilirim?', emoji: '🔄', label: 'İade Süreci' },
    { question: 'TV ünitesinin ölçüleri ve fiyatı nedir?', emoji: '📏', label: 'Ürün Bilgisi' },
    { question: 'Kargo adresimi değiştirebilir miyim?', emoji: '🚚', label: 'Kargo İşlemleri' },
    { question: 'Montaj hizmeti veriyor musunuz? Fiyatı ne kadar?', emoji: '🔧', label: 'Genel Destek' }
  ];

  const approaches = [
    { key: 'rag', label: 'RAG Sistemi', color: 'border-blue-500 bg-blue-50', icon: FaDatabase },
    { key: 'prompt', label: 'Prompt Engineering', color: 'border-green-500 bg-green-50', icon: FaCogs },
    { key: 'hybrid', label: 'Hibrit Mod', color: 'border-purple-500 bg-purple-50', icon: FaLayerGroup }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl shadow-xl p-8"
      >
        <div className="bg-gradient-warning text-white rounded-2xl p-8 text-center">
          <FaFlask className="text-4xl mx-auto mb-4" />
          <h1 className="text-3xl font-bold mb-2">Model Test Laboratuvarı</h1>
          <p className="opacity-90">Farklı AI yaklaşımlarını karşılaştırın ve test edin</p>
        </div>
      </motion.div>

      {/* Test Input */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-2xl shadow-xl p-8"
      >
        <h2 className="text-xl font-bold mb-6 text-gray-800">✏️ Test Sorusu Girin</h2>
        
        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <textarea
              value={testQuestion}
              onChange={(e) => setTestQuestion(e.target.value)}
              placeholder="Test etmek istediğiniz müşteri sorusunu yazın..."
              className="w-full h-32 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>
          
          <div className="space-y-4">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={runAllTests}
              disabled={isLoading || !testQuestion.trim()}
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 rounded-xl font-bold text-lg flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Test Ediliyor...</span>
                </>
              ) : (
                <>
                  <FaPlay />
                  <span>Tüm Modelleri Test Et</span>
                </>
              )}
            </motion.button>
            
            <div className="flex items-center">
              <input type="checkbox" id="detailed" className="mr-2" defaultChecked />
              <label htmlFor="detailed" className="text-sm text-gray-600">
                Detaylı metrikler göster
              </label>
            </div>
          </div>
        </div>

        {/* Quick Test Buttons */}
        <div className="mt-6">
          <h3 className="font-semibold mb-3 text-gray-700">Hızlı Test Örnekleri:</h3>
          <div className="flex flex-wrap gap-3">
            {quickTests.map((test, index) => (
              <motion.button
                key={index}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setQuickTest(test.question)}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-full text-sm font-medium transition-colors flex items-center space-x-2"
              >
                <span>{test.emoji}</span>
                <span>{test.label}</span>
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Test Results */}
      {testResults && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid md:grid-cols-3 gap-6"
        >
          {approaches.map((approach, index) => {
            const result = testResults.find(r => r.approach === approach.key);
            const Icon = approach.icon;

            return (
              <motion.div
                key={approach.key}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className={`bg-white rounded-2xl shadow-xl border-2 ${approach.color} overflow-hidden`}
              >
                <div className={`p-4 ${approach.color} border-b`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Icon className="text-xl" />
                      <h3 className="font-bold">{approach.label}</h3>
                    </div>
                    {result && !result.error && (
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${utils.getConfidenceBadgeColor(result.confidence)}`}>
                        {utils.formatConfidence(result.confidence)}
                      </span>
                    )}
                  </div>
                </div>

                <div className="p-6">
                  {result?.error ? (
                    <div className="text-center py-4">
                      <div className="text-red-500 text-2xl mb-2">❌</div>
                      <p className="text-red-600 text-sm">Test başarısız: {result.error}</p>
                    </div>
                  ) : result ? (
                    <div>
                      <p className="text-gray-700 mb-4">{result.answer}</p>
                      
                      <div className="space-y-2 text-sm text-gray-600">
                        <div className="flex justify-between">
                          <span>Metod:</span>
                          <span className="font-medium">{result.method}</span>
                        </div>
                        {result.scenario && (
                          <div className="flex justify-between">
                            <span>Senaryo:</span>
                            <span className="font-medium">
                              {utils.getScenarioIcon(result.scenario)} {result.scenario}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <div className="animate-pulse">
                        <div className="bg-gray-200 h-4 rounded mb-2"></div>
                        <div className="bg-gray-200 h-4 rounded mb-2"></div>
                        <div className="bg-gray-200 h-4 rounded w-3/4"></div>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      )}

      {/* Comparison Chart */}
      {testResults && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-2xl shadow-xl p-8"
        >
          <h2 className="text-xl font-bold mb-6 text-gray-800">📊 Karşılaştırma Analizi</h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="font-semibold mb-4">Güven Skorları</h3>
              <div className="space-y-3">
                {testResults.filter(r => !r.error).map((result, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm font-medium capitalize">{result.approach}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${utils.getApproachColor(result.approach)}`}
                          style={{ width: `${result.confidence * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-bold">
                        {utils.formatConfidence(result.confidence)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Sonuç Özeti</h3>
              <div className="space-y-3">
                {testResults.filter(r => !r.error).length > 0 && (
                  <>
                    <div className="p-3 bg-green-50 rounded-lg">
                      <h4 className="font-medium text-green-800">🏆 En Yüksek Güven:</h4>
                      <p className="text-sm text-green-700">
                        {testResults.filter(r => !r.error).reduce((best, current) => 
                          current.confidence > best.confidence ? current : best
                        ).approach.toUpperCase()}
                      </p>
                    </div>
                    
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-blue-800">📊 Ortalama Performans:</h4>
                      <p className="text-sm text-blue-700">
                        {utils.formatConfidence(
                          testResults.filter(r => !r.error).reduce((sum, r) => sum + r.confidence, 0) /
                          testResults.filter(r => !r.error).length
                        )}
                      </p>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Test History */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-white rounded-2xl shadow-xl p-8"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-800">📜 Test Geçmişi</h2>
          {testHistory.length > 0 && (
            <button
              onClick={clearHistory}
              className="flex items-center space-x-2 text-red-600 hover:text-red-800 transition-colors"
            >
              <FaTrash />
              <span>Temizle</span>
            </button>
          )}
        </div>

        {testHistory.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <FaFlask className="text-4xl mx-auto mb-4 opacity-50" />
            <p>Henüz test yapılmadı. Yukarıdan bir test başlatın.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {testHistory.map((item) => {
              const bestResult = item.results.filter(r => !r.error).reduce((best, current) => 
                current.confidence > best.confidence ? current : best, { confidence: 0 }
              );

              return (
                <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-medium text-gray-800 mb-1">
                        {item.question.length > 50 ? `${item.question.substring(0, 50)}...` : item.question}
                      </p>
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span>{item.timestamp.toLocaleString('tr-TR')}</span>
                        {bestResult.confidence > 0 && (
                          <span className={`px-2 py-1 rounded-full ${utils.getConfidenceBadgeColor(bestResult.confidence)}`}>
                            En iyi: {bestResult.approach.toUpperCase()} - {utils.formatConfidence(bestResult.confidence)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default TestPage; 