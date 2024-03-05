import Admin from '../pages/Admin';
import Dashboard from '../pages/Dashboard';
import ErrorPage from '../pages/ErrorPage';
import Items from '../pages/Items';
import Layout from '../pages/Layout';
import Login from '../pages/Login';
import NotFound from '../pages/NotFound';
import RecoverPassword from '../pages/RecoverPassword';
import ResetPassword from '../pages/ResetPassword';
import UserSettings from '../pages/UserSettings';

export default function routes() {

    return [
        {
            path: '/',
            element: <Layout />,
            errorElement: <ErrorPage />,
            children: [
                { path: '/', element: <Dashboard /> },
                { path: 'items', element: <Items /> },
                { path: 'admin', element: <Admin /> },
                { path: 'settings', element: <UserSettings /> },
            ],
        },
        { path: 'login', element: <Login />, errorElement: <ErrorPage /> },
        { path: 'recover-password', element: <RecoverPassword />, errorElement: <ErrorPage /> },
        { path: 'reset-password', element: <ResetPassword />, errorElement: <ErrorPage /> },
        {
            path: '*',
            element: <NotFound />
        }
    ]
}
