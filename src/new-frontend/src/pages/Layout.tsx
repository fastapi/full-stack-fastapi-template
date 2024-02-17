import { useEffect } from 'react';

import { Outlet, useNavigate } from 'react-router-dom';
import Sidebar from '../components/Common/Sidebar';

import { Flex, useToast } from '@chakra-ui/react';
import { useUserStore } from '../store/user-store';
import UserMenu from '../components/Common/UserMenu';

const Layout: React.FC = () => {
    const toast = useToast();
    const navigate = useNavigate();
    const { getUser } = useUserStore();

    useEffect(() => {
        const fetchUser = async () => {
            const token = localStorage.getItem('access_token');
            if (token) {
                try {
                    await getUser();
                } catch (err) {
                    toast({
                        title: 'Something went wrong.',
                        description: 'Failed to fetch user. Please try again.',
                        status: 'error',
                        isClosable: true,
                    });
                }
            }

        }
        fetchUser();
    }, []);

    return (
        <Flex maxW="large" h="auto" position="relative">
            <Sidebar />
            <Outlet />
            <UserMenu />
        </Flex>
    );
};

export default Layout;