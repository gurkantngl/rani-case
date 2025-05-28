import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';

// Components
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import DashboardPage from './pages/DashboardPage';
import TestPage from './pages/TestPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Navbar />
        
        <motion.main 
          className="container mx-auto px-4 py-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/test" element={<TestPage />} />
          </Routes>
        </motion.main>
        
        {/* Footer */}
        <footer className="bg-gray-800 text-white py-8 mt-12">
          <div className="container mx-auto px-4 text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <span className="text-red-400">♥</span>
              <span>Rani Mobilya AI Müşteri Hizmetleri Sistemi</span>
              <span className="text-blue-400">🤖</span>
            </div>
            <p className="text-gray-400 text-sm">
              Powered by FastAPI & React - Machine Learning & Natural Language Processing
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
