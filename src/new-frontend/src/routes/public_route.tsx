import { Navigate } from 'react-router-dom';
import ErrorPage from '../pages/ErrorPage';
import Login from '../pages/Login';
import RecoverPassword from '../pages/RecoverPassword';
import ResetPassword from '../pages/ResetPassword';

export default function publicRoutes() {

    return [
        { path: 'login', element: <Login />, errorElement: <ErrorPage /> },
        { path: 'recover-password', element: <RecoverPassword />, errorElement: <ErrorPage /> },
        { path: 'reset-password', element: <ResetPassword />, errorElement: <ErrorPage /> },
        { path: '*', element: <Navigate to='login' replace /> },
    ];
}
