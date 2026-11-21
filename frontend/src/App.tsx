import { Routes, Route, Navigate } from 'react-router-dom';
import { SearchPage } from './pages/Search';
import { DictionaryPage } from './pages/Dictionary';

export function App() {
  return (
    <Routes>
      <Route path="/" element={<SearchPage />} />
      <Route path="/search" element={<SearchPage />} />
      <Route path="/dictionary" element={<DictionaryPage />} />
      <Route path="*" element={<Navigate to="/dictionary" replace />} />
    </Routes>
  );
}
