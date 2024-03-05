import { useQuery } from 'react-query';
import { useNavigate } from 'react-router-dom';

import { Body_login_login_access_token as AccessToken, UserOut, UsersService, LoginService } from '../client';

const isLoggedIn = () => {
    return localStorage.getItem('access_token') !== null;
};

async function fetchUser() {
    return await UsersService.readUserMe();
}

const useAuth = () => {
    const navigate = useNavigate();
    const { refetch: getUser, isLoading } = useQuery<UserOut | null, Error>('currentUser', fetchUser, {
        enabled: isLoggedIn(),
    });

    const login = async (data: AccessToken) => {
        const response = await LoginService.loginAccessToken({
            formData: data,
        });
        localStorage.setItem('access_token', response.access_token);
        await getUser();
        navigate('/');
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        navigate('/login');
    };


    return { login, logout, getUser, isLoading };
}

export { isLoggedIn };
export default useAuth;