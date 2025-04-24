import { Route, Routes } from 'react-router-dom';
import './App.css';
import { Home, Model } from './pages';
import { Toaster, ToasterComponent, ToasterProvider } from '@gravity-ui/uikit';

export const App = () => {

  const toaster = new Toaster();
  return (
    <div className='content'>
      <ToasterProvider toaster={toaster}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/model/*" element={<Model />} />
        </Routes>
        <ToasterComponent className="optional additional classes" hasPortal={true} />
      </ToasterProvider>
    </div>

  );
};
