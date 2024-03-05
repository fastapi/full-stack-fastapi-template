import { Flex, Spinner } from '@chakra-ui/react';
import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';

import Sidebar from '../components/Common/Sidebar';
import UserMenu from '../components/Common/UserMenu';
import useAuth, { isLoggedIn } from '../hooks/useAuth';

const Layout: React.FC = () => {
    const navigate = useNavigate();
    const { isLoading } = useAuth();

    if (!isLoggedIn()) {
        navigate('/login')
    }

    return (
        <Flex maxW='large' h='auto' position='relative'>
            <Sidebar />
            {isLoading ? (
                <Flex justify='center' align='center' height='100vh' width='full'>
                    <Spinner size='xl' color='ui.main' />
                </Flex>
            ) : (
                <Outlet />
            )}
            <UserMenu />
        </Flex>
    );
};

export default Layout;