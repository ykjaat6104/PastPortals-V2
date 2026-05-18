import React, { useState } from 'react';
import { Building2, MapPin, Globe, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import VoiceSearchBar from './VoiceSearchBar';
import { navigateToSearch } from '../utils/searchNavigation';

const MuseumsPageNew = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMuseum, setSelectedMuseum] = useState(null);

  const featuredMuseums = [
    {
      id: 1,
      name: 'The Louvre',
      location: 'Paris, France',
      flag: '🇫🇷',
      description: 'World\'s largest art museum and historic monument. Home to the Mona Lisa and Venus de Milo.',
      established: '1793',
      highlights: ['Mona Lisa', 'Venus de Milo', 'Winged Victory', 'Egyptian Antiquities'],
      gradient: 'from-blue-600 to-purple-600',
      website: 'https://www.louvre.fr/en'
    },
    {
      id: 2,
      name: 'British Museum',
      location: 'London, United Kingdom',
      flag: '🇬🇧',
      description: 'Dedicated to human history, art and culture with 8 million works spanning 2 million years.',
      established: '1753',
      highlights: ['Rosetta Stone', 'Egyptian Mummies', 'Parthenon Sculptures', 'Assyrian Lions'],
      gradient: 'from-red-600 to-blue-700',
      website: 'https://www.britishmuseum.org'
    },
    {
      id: 3,
      name: 'National Museum',
      location: 'New Delhi, India',
      flag: '🇮🇳',
      description: 'Premier museum of India showcasing over 200,000 works of Indian and foreign origin.',
      established: '1949',
      highlights: ['Harappan Artifacts', 'Buddhist Relics', 'Miniature Paintings', 'Central Asian Antiquities'],
      gradient: 'from-orange-600 to-green-600',
      website: 'https://www.nationalmuseumindia.gov.in'
    },
    {
      id: 4,
      name: 'Egyptian Museum',
      location: 'Cairo, Egypt',
      flag: '🇪🇬',
      description: 'Houses the world\'s largest collection of Pharaonic antiquities spanning 5000 years.',
      established: '1902',
      highlights: ['Tutankhamun Treasures', 'Royal Mummies', 'Ancient Jewelry', 'Papyrus Collection'],
      gradient: 'from-yellow-600 to-orange-700',
      website: 'https://nmec.gov.eg/en'
    },
    {
      id: 5,
      name: 'Smithsonian National Museum',
      location: 'Washington D.C., USA',
      flag: '🇺🇸',
      description: 'Natural history museum with 145 million specimens of plants, animals, fossils, and minerals.',
      established: '1910',
      highlights: ['Hope Diamond', 'Dinosaur Fossils', 'Human Origins', 'Butterfly Pavilion'],
      gradient: 'from-blue-700 to-red-600',
      website: 'https://naturalhistory.si.edu'
    },
    {
      id: 6,
      name: 'Palace Museum',
      location: 'Beijing, China',
      flag: '🇨🇳',
      description: 'Located in the Forbidden City, housing imperial collections from Ming and Qing dynasties.',
      established: '1925',
      highlights: ['Imperial Treasures', 'Chinese Ceramics', 'Calligraphy', 'Court Paintings'],
      gradient: 'from-red-700 to-yellow-600',
      website: 'https://en.dpm.org.cn'
    }
  ];

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    navigateToSearch(navigate, `${searchQuery} museum`, '/museums');
  };

  const handleMuseumSearch = (museumName) => {
    navigateToSearch(navigate, `${museumName} museum`, '/museums');
  };

  return (
    <div className="museums-page">
      <div className="museums-header">
        <h1 className="page-title">
          <Building2 size={36} />
          World Museums
        </h1>
        <p className="page-subtitle">
          Explore renowned museums and their incredible collections from around the globe
        </p>
      </div>

      <div className="museum-search-container">
        <VoiceSearchBar
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onSubmit={handleSearch}
          placeholder="Search for museums by name or location..."
          className="museums-search-bar"
        />
      </div>

      <div className="museums-grid">
        {featuredMuseums.map((museum) => (
          <div
            key={museum.id}
            className="museum-card"
            onClick={() => setSelectedMuseum(museum.id === selectedMuseum ? null : museum.id)}
          >
            <div className={`museum-header bg-gradient-to-br ${museum.gradient}`}>
              <span className="museum-flag">{museum.flag}</span>
              <div className="museum-location">
                <MapPin size={16} />
                <span>{museum.location}</span>
              </div>
            </div>

            <div className="museum-body">
              <h3 className="museum-name">{museum.name}</h3>
              <p className="museum-established">Established {museum.established}</p>
              <p className="museum-description">{museum.description}</p>

              <button
                className="visit-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  handleMuseumSearch(museum.name);
                }}
              >
                <Globe size={16} />
                Search This Museum
              </button>

              {selectedMuseum === museum.id && (
                <div className="museum-details">
                  <h4 className="highlights-title">Must-See Highlights</h4>
                  <ul className="highlights-list">
                    {museum.highlights.map((highlight, idx) => (
                      <li key={idx} className="highlight-item">
                        <span className="highlight-dot"></span>
                        <button
                          type="button"
                          className="highlight-link-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigateToSearch(navigate, `${highlight} ${museum.name}`, '/museums');
                          }}
                        >
                          {highlight}
                        </button>
                      </li>
                    ))}
                  </ul>
                  <button 
                    className="visit-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      window.open(museum.website, '_blank');
                    }}
                  >
                    <Globe size={16} />
                    Learn More
                    <ExternalLink size={16} />
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="museums-stats">
        <div className="stat-card">
          <span className="stat-number">100,000+</span>
          <span className="stat-label">Museums Worldwide</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">195</span>
          <span className="stat-label">Countries Represented</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">1B+</span>
          <span className="stat-label">Annual Visitors</span>
        </div>
      </div>
    </div>
  );
};

export default MuseumsPageNew;
