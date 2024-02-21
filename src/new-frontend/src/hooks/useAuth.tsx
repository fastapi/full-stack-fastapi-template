import { useUserStore } from '../store/user-store';
import { Body_login_login_access_token as AccessToken, LoginService } from '../client';

const useAuth = () => {
    const user = useUserStore((state) => state.user);
    const getUser = useUserStore((state) => state.getUser);
    const resetUser = useUserStore((state) => state.resetUser);

    const login = async (data: AccessToken) => {
        const response = await LoginService.loginAccessToken({
            formData: data,
        });
        localStorage.setItem('access_token', response.access_token);
        await getUser();
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        resetUser();
    };

    const isLoggedIn = () => {
        return user !== null;
    };

    return { login, logout, isLoggedIn };
}

export default useAuth;