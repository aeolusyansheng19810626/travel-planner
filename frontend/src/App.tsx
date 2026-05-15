import './App.css';
import { useQueryStream } from './hooks/useQueryStream';
import BrandBar from './components/BrandBar';
import LeftRail from './components/LeftRail';
import ChatColumn from './components/ChatColumn';
import ResultPanel from './components/ResultPanel';
import TweaksPanel from './components/TweaksPanel';

export default function App() {
  useQueryStream();
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <BrandBar />
      <div style={{
        display: 'grid',
        gridTemplateColumns: '232px minmax(280px, 1fr) 380px',
        flex: 1,
        minWidth: '892px',
        overflow: 'hidden',
      }}
        className="app-grid"
      >
        <LeftRail />
        <ChatColumn />
        <ResultPanel />
      </div>
      <TweaksPanel />
    </div>
  );
}
