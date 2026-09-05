import React, { useEffect } from 'react';
import { usePredictorStore } from './store/usePredictorStore';
import { Header } from './components/Header';
import { Navbar } from './components/Navbar';
import { MatchPredictor } from './components/MatchPredictor/MatchPredictor';
import { TacticalPitch } from './components/TacticalPitch/TacticalPitch';
import { Standings } from './components/Standings/Standings';
import { PlayerAnalytics } from './components/PlayerAnalytics/PlayerAnalytics';
import { Transfers } from './components/Transfers/Transfers';
import { Improvisation } from './components/Improvisation/Improvisation';
import { Loader2, AlertCircle } from 'lucide-react';

export const App: React.FC = () => {
  const { activeTab, loading, error, initApp } = usePredictorStore();

  useEffect(() => {
    initApp();
  }, [initApp]);

  if (loading) {
    return (
      <div className="loading-screen">
        <Loader2 size={48} className="spinner" />
        <h2>Loading Premier League AI Prediction Engine...</h2>
        <p>Ingesting 10,000 Monte Carlo simulations and player ratings</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-screen">
        <AlertCircle size={48} className="error-icon" />
        <h2>Failed to Load Application</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      <Header />
      <Navbar />

      <main className="main-content">
        {activeTab === 'predictor' && <MatchPredictor />}
        {activeTab === 'squads' && <TacticalPitch />}
        {activeTab === 'standings' && <Standings />}
        {activeTab === 'players' && <PlayerAnalytics />}
        {activeTab === 'transfers' && <Transfers />}
        {activeTab === 'improvisation' && <Improvisation />}
      </main>

      <footer className="footer-bar">
        <p>Premier League AI Predictor Hub • Powered by React, Vite, Zustand, Recharts & Machine Learning</p>
      </footer>
    </div>
  );
};
