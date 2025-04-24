import React from 'react';
import ReactDOM from 'react-dom/client';
import '@gravity-ui/uikit/styles/fonts.css';
import '@gravity-ui/uikit/styles/styles.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { TextAreaPage } from './pages';
import App from './app/AppNew';
import Scene from './entities/Scene/SceneOld/SceneOld';

const rootEl = document.getElementById('root');
if (rootEl) {
  const root = ReactDOM.createRoot(rootEl);
  root.render(
    <React.StrictMode>
      <BrowserRouter basename='/' >
        <Routes>
          {/* <Route path="/"><TextAreaPage /></Route> */}
          {/* <Route path="/models"><App /></Route> */}
          <Scene />
        </Routes>
      </BrowserRouter>
    </React.StrictMode>
  );
}
