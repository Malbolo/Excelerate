import { RouterProvider } from 'react-router-dom';

import './lib/i18n';
import router from './lib/router';

function App() {
  return <RouterProvider router={router} />;
}

export default App;
