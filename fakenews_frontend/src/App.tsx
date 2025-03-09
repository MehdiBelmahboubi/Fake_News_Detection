import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { ThemeProvider } from './shared-theme/ThemeContext';
import { useTheme } from './shared-theme/ThemeContext';
import NavBar from './components/NavBar';
import HomePage from './components/HomePage';
import Choser from './components/choser/choser';

export default function App() {
  const { muiTheme } = useTheme();
  return (
    <ThemeProvider>
      <Router>
        <NavBar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          {/* <Route path="/news-papers" element={<NewsPapersPage />} /> */}
          <Route path="/news-analyzer" element={<Choser />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}