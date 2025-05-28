import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaRobot, 
  FaUser, 
  FaPaperPlane, 
  FaTrash, 
  FaDownload,
  FaCircle
} from 'react-icons/fa';
import { apiService, utils } from '../services/api';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedApproach, setSelectedApproach] = useState('prompt');
  const [stats, setStats] = useState({ messageCount: 0, avgConfidence: 0, avgResponseTime: 0 });
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    // Add welcome message
    setMessages([{
      id: Date.now(),
      type: 'assistant',
      content: 'Merhaba! Rani Mobilya AI asistanıyım. 😊\n\nSize nasıl yardımcı olabilirim?\n\n**Yapabileceklerim:**\n📦 Sipariş takibi\n🔄 İade işlemleri\n🛋️ Ürün bilgileri\n🚚 Kargo sorguları\n💬 Genel destek',
      timestamp: new Date(),
      method: 'Sistem Mesajı',
      confidence: 1.0
    }]);
    
    // Focus input
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const startTime = Date.now();
      const response = await apiService.askQuestion(inputValue, selectedApproach);
      const responseTime = Date.now() - startTime;

      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        method: response.method,
        confidence: response.confidence,
        scenario: response.scenario,
        responseTime
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Update stats
      setStats(prev => {
        const newMessageCount = prev.messageCount + 1;
        const newAvgConfidence = ((prev.avgConfidence * prev.messageCount) + response.confidence) / newMessageCount;
        const newAvgResponseTime = ((prev.avgResponseTime * prev.messageCount) + responseTime) / newMessageCount;
        
        return {
          messageCount: newMessageCount,
          avgConfidence: newAvgConfidence,
          avgResponseTime: newAvgResponseTime
        };
      });

    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: 'Üzgünüm, şu an yanıt veremiyorum. Lütfen tekrar deneyin.',
        timestamp: new Date(),
        method: 'Hata',
        confidence: 0,
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    if (window.confirm('Tüm sohbet geçmişini silmek istediğinizden emin misiniz?')) {
      setMessages(messages.slice(0, 1)); // Keep welcome message
      setStats({ messageCount: 0, avgConfidence: 0, avgResponseTime: 0 });
    }
  };

  const sendQuickReply = (message) => {
    setInputValue(message);
    setTimeout(() => handleSendMessage(), 100);
  };

  const approaches = [
    { value: 'prompt', label: '🎯 Prompt Engineering', color: 'bg-green-500' },
    { value: 'rag', label: '📚 RAG Sistemi', color: 'bg-blue-500' },
    { value: 'hybrid', label: '🔄 Hibrit Mod', color: 'bg-purple-500' }
  ];

  const quickReplies = [
    { text: 'Siparişim ne zaman gelir?', emoji: '📦' },
    { text: 'Bu ürünü iade edebilir miyim?', emoji: '🔄' },
    { text: 'Ürün fiyatı nedir?', emoji: '💰' },
    { text: 'Kargo ne zaman gelir?', emoji: '🚚' }
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <div className="grid lg:grid-cols-4 gap-6">
        {/* Chat Area */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden h-[700px] flex flex-col">
            {/* Chat Header */}
            <div className="bg-gradient-primary text-white p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <div className="bg-white bg-opacity-20 p-3 rounded-full">
                      <FaRobot className="text-2xl" />
                    </div>
                    <div className="absolute bottom-0 right-0 bg-green-400 w-4 h-4 rounded-full border-2 border-white"></div>
                  </div>
                  <div>
                    <h3 className="font-bold text-lg">Rani AI Asistan</h3>
                    <div className="flex items-center space-x-1 text-sm opacity-90">
                      <FaCircle className="text-green-400 text-xs" />
                      <span>Çevrimiçi</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <select
                    value={selectedApproach}
                    onChange={(e) => setSelectedApproach(e.target.value)}
                    className="bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50"
                  >
                    {approaches.map(approach => (
                      <option key={approach.value} value={approach.value} className="text-gray-800">
                        {approach.label}
                      </option>
                    ))}
                  </select>

                  <button
                    onClick={clearChat}
                    className="bg-white bg-opacity-20 hover:bg-opacity-30 p-2 rounded-lg transition-colors"
                  >
                    <FaTrash />
                  </button>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className={`flex mb-6 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex items-start space-x-3 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                      {/* Avatar */}
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white ${
                        message.type === 'user' ? 'bg-blue-500' : 'bg-green-500'
                      }`}>
                        {message.type === 'user' ? <FaUser /> : <FaRobot />}
                      </div>

                      {/* Message Bubble */}
                      <div className={`rounded-2xl p-4 ${
                        message.type === 'user' 
                          ? 'bg-blue-500 text-white rounded-br-md' 
                          : `bg-white text-gray-800 rounded-bl-md shadow-md ${message.isError ? 'border border-red-200' : ''}`
                      }`}>
                        <div className="whitespace-pre-wrap">{message.content}</div>
                        
                        {/* Message metadata */}
                        <div className={`mt-2 text-xs ${message.type === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                          <div className="flex items-center justify-between">
                            <span>{message.timestamp.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}</span>
                            {message.method && (
                              <span className="ml-2">{message.method}</span>
                            )}
                          </div>
                          
                          {message.confidence !== undefined && message.type === 'assistant' && (
                            <div className="flex items-center space-x-2 mt-1">
                              <span className={`px-2 py-1 rounded-full text-xs ${utils.getConfidenceBadgeColor(message.confidence)}`}>
                                {utils.formatConfidence(message.confidence)} güven
                              </span>
                              {message.responseTime && (
                                <span className="text-xs opacity-75">
                                  {utils.formatResponseTime(message.responseTime)}
                                </span>
                              )}
                              {message.scenario && (
                                <span className="text-xs opacity-75">
                                  {utils.getScenarioIcon(message.scenario)} {message.scenario}
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Typing Indicator */}
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-start space-x-3 mb-6"
                >
                  <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center text-white">
                    <FaRobot />
                  </div>
                  <div className="bg-white rounded-2xl rounded-bl-md p-4 shadow-md">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-6 bg-white border-t">
              {/* Quick Replies */}
              <div className="flex flex-wrap gap-2 mb-4">
                {quickReplies.map((reply, index) => (
                  <motion.button
                    key={index}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => sendQuickReply(reply.text)}
                    disabled={isLoading}
                    className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-full text-sm font-medium transition-colors disabled:opacity-50"
                  >
                    {reply.emoji} {reply.text}
                  </motion.button>
                ))}
              </div>

              {/* Input */}
              <div className="flex items-end space-x-4">
                <div className="flex-1">
                  <textarea
                    ref={inputRef}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Mesajınızı yazın..."
                    disabled={isLoading}
                    className="w-full px-4 py-3 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:opacity-50"
                    rows="1"
                    style={{ minHeight: '44px', maxHeight: '120px' }}
                  />
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  className="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-2xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <FaPaperPlane />
                </motion.button>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar Stats */}
        <div className="space-y-6">
          {/* Chat Stats */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h3 className="font-bold text-lg mb-4 text-gray-800">💬 Chat İstatistikleri</h3>
            
            <div className="space-y-4">
              <div className="text-center p-4 bg-blue-50 rounded-xl">
                <div className="text-2xl font-bold text-blue-600">{stats.messageCount}</div>
                <div className="text-sm text-gray-600">Gönderilen Mesaj</div>
              </div>
              
              <div className="text-center p-4 bg-green-50 rounded-xl">
                <div className="text-2xl font-bold text-green-600">
                  {stats.avgConfidence > 0 ? utils.formatConfidence(stats.avgConfidence) : '-%'}
                </div>
                <div className="text-sm text-gray-600">Ortalama Güven</div>
              </div>
              
              <div className="text-center p-4 bg-purple-50 rounded-xl">
                <div className="text-2xl font-bold text-purple-600">
                  {stats.avgResponseTime > 0 ? utils.formatResponseTime(stats.avgResponseTime) : '-ms'}
                </div>
                <div className="text-sm text-gray-600">Ortalama Yanıt Süresi</div>
              </div>
            </div>
          </div>

          {/* Model Info */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h3 className="font-bold text-lg mb-4 text-gray-800">🤖 Aktif Model</h3>
            
            <div className="space-y-3">
              {approaches.map(approach => (
                <div
                  key={approach.value}
                  className={`p-3 rounded-xl border-2 transition-all ${
                    selectedApproach === approach.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${approach.color}`}></div>
                    <span className="text-sm font-medium">{approach.label}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h3 className="font-bold text-lg mb-4 text-gray-800">⚙️ İşlemler</h3>
            
            <div className="space-y-3">
              <button
                onClick={clearChat}
                className="w-full flex items-center justify-center space-x-2 bg-red-50 hover:bg-red-100 text-red-600 py-3 rounded-xl transition-colors"
              >
                <FaTrash />
                <span>Sohbeti Temizle</span>
              </button>
              
              <button
                onClick={() => {/* Export functionality */}}
                className="w-full flex items-center justify-center space-x-2 bg-gray-50 hover:bg-gray-100 text-gray-600 py-3 rounded-xl transition-colors"
              >
                <FaDownload />
                <span>Dışa Aktar</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage; 