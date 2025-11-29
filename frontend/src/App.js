import React from 'react'
import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from './Component/Home';
import Chatbot from './Component/Chatbot.jsx';

const App = () => {
  return (
    <>

      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/Chat" element={<Chatbot />} />
        </Routes>
      </Router>
    </>
  )
}

export default App
