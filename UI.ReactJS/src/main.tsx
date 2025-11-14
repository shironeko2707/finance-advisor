import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Set document title from environment variable
const appTitle = import.meta.env.VITE_APP_TITLE || 'Smart Reports System';
document.title = appTitle;

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
