import React, { useEffect } from 'react';
import { Flex, Spinner } from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';

import Sidebar from '../components/Common/Sidebar';
import UserMenu from '../components/Common/UserMenu';
import useAuth from '../hooks/useAuth';

const Layout: React.FC = () => {
    const { getUser, isLoading } = useAuth();

    useEffect(() => {
        getUser();
    }, []);

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