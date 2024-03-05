import { RouterProvider, createBrowserRouter } from 'react-router-dom';

import { isLoggedIn } from './hooks/useAuth';
import privateRoutes from './routes/private_route';
import publicRoutes from './routes/public_route';

const router = createBrowserRouter([
    ...(isLoggedIn() ? privateRoutes() : []),
    ...publicRoutes(),
]);

function App() {
    return (
        <RouterProvider router={router} />
    );
}

export default App;