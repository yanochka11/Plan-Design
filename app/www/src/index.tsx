import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import { HashRouter } from 'react-router-dom';
import { ThemeProvider } from '@gravity-ui/uikit';
import '@gravity-ui/uikit/styles/fonts.css';
import '@gravity-ui/uikit/styles/styles.css';

const rootEl = document.getElementById('root');
if (rootEl) {
  const root = ReactDOM.createRoot(rootEl);
  root.render(
    <React.StrictMode>
      <ThemeProvider theme="light">
          <HashRouter>
            <App />
          </HashRouter>
      </ThemeProvider>
    </React.StrictMode>,
  );
}
