import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, Clock, Building2, Settings, History, Layers3 } from 'lucide-react';
import { useAPI } from '../contexts/APIContext';

const Sidebar = ({ onSettingsClick }) => {
  const { language } = useAPI();

  const getLanguageFlag = (code) => {
    const flags = {
      en: '🇬🇧', hi: '🇮🇳', fr: '🇫🇷', es: '🇪🇸', pt: '🇵🇹', ar: '🇸🇦',
      zh: '🇨🇳', ja: '🇯🇵', de: '🇩🇪', it: '🇮🇹', ru: '🇷🇺', ko: '🇰🇷'
    };
    return flags[code] || '🇬🇧';
  };

    const navItems = [
      { path: '/', icon: Home, label: 'Explore' },
      { path: '/search', icon: Layers3, label: 'Search' },
      { path: '/timeline', icon: Clock, label: 'Timeline' },
      { path: '/museums', icon: Building2, label: 'Museums' }
    ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="logo-icon">
            <Building2 size={28} />
          </div>
          <h1 className="logo-text">PastPortals</h1>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `sidebar-nav-item ${isActive ? 'active' : ''}`
              }
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <NavLink
          to="/history"
          className={({ isActive }) =>
            `sidebar-footer-link ${isActive ? 'active' : ''}`
          }
        >
          <History size={20} />
          <span>History</span>
        </NavLink>

        <button 
          className="sidebar-settings-btn"
          onClick={onSettingsClick}
        >
          <Settings size={20} />
          <span>Settings {getLanguageFlag(language)}</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
