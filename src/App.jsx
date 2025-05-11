// src/App.jsx
import React from 'react';
// Import routing components and page components
import {Routes, Route, Link, useLocation} from 'react-router-dom';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import ProjectsPage from './pages/ProjectsPage';
import CreateTestScriptPage from './pages/CreateTestScriptPage';
import ContactPage from './pages/ContactPage';

import './App.css'; // Keep App specific styles (layout, header)

function App() {
  // Define navigation links with their corresponding paths
  const navLinks = [
    { text: "Home", path: "/" },
    { text: "About", path: "/about" },
    { text: "Projects", path: "/projects" },
    { text: "Create Test Script", path: "/create-test" },
    { text: "Contact", path: "/contact" },
  ];

    // --- Get current location to determine title ---
  const location = useLocation();
  // Find the navLink object matching the current pathname
  const currentNavLink = navLinks.find(link => link.path === location.pathname);
  // Set the banner title (use link text or a default)
  const bannerTitle = currentNavLink ? currentNavLink.text : "Testing Hub"; // Fallback title


  return (
    <div className="App">

      {/* Header - present on ALL pages */}
      <header className="App-header">
        <nav>
          {navLinks.map((link) => (
            <Link key={link.text} to={link.path} className="nav-item">
              {link.text}
            </Link>
          ))}
        </nav>
      </header>

      {/* Banner - NOW RENDERED HERE ON ALL PAGES */}
      <div className="intro-banner">
        {/* Use the dynamic title */}
        <h1>{bannerTitle}</h1>
      </div>

      {/* Route definition area - Content swaps based on URL */}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/create-test" element={<CreateTestScriptPage />} />
        <Route path="/contact" element={<ContactPage />} />
        {/* <Route path="*" element={<NotFoundPage />} /> */}
      </Routes>

      {/* Optional Footer could go here */}

    </div>
  );
}

export default App;
