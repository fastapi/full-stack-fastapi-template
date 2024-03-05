import React from 'react';

import { Container, Text } from '@chakra-ui/react';
import { useQueryClient } from 'react-query';

import { UserOut } from '../client';



const Dashboard: React.FC = () => {
    const queryClient = useQueryClient();
    const currentUser = queryClient.getQueryData<UserOut>('currentUser');

    return (
        <>
            <Container maxW='full' pt={12}>
                <Text fontSize='2xl'>Hi, {currentUser?.full_name || currentUser?.email} 👋🏼</Text>
                <Text>Welcome back, nice to see you again!</Text>
            </Container>
        </>

    )
}

export default Dashboard;