import React from 'react';
import { usePredictorStore } from '../store/usePredictorStore';
import { Swords, LayoutGrid, Award, Star, Compass, Cpu } from 'lucide-react';

const TABS = [
  { id: 'predictor', label: '2-Leg Match Predictor', icon: Swords },
  { id: 'squads', label: 'Squads & EA FC27 Tactical Pitch', icon: LayoutGrid },
  { id: 'standings', label: 'Season Standings & Title Race', icon: Award },
  { id: 'players', label: 'POTS & Golden Boot', icon: Star },
  { id: 'transfers', label: 'Darkhorse & Transfer Market', icon: Compass },
  { id: 'improvisation', label: 'AI Self-Improvisation Rate', icon: Cpu },
];

export const Navbar: React.FC = () => {
  const { activeTab, setActiveTab } = usePredictorStore();

  return (
    <nav className="nav-tabs">
      {TABS.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            className={`tab-btn ${isActive ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <Icon size={16} className="tab-icon" />
            <span>{tab.label}</span>
          </button>
        );
      })}
    </nav>
  );
};
