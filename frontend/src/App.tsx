import { Routes, Route, Navigate } from 'react-router-dom';
import { SearchPage } from './pages/Search';

export function App() {
  return (
    <Routes>
      <Route path="/" element={<SearchPage />} />
      <Route path="/search" element={<SearchPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}