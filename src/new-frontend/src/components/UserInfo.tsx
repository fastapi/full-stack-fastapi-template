import React, { useEffect, useState } from 'react';

import { Avatar, Flex, Skeleton, Text } from '@chakra-ui/react';
import { FaUserAstronaut } from 'react-icons/fa';

import { UserOut, UsersService } from '../client';

const UserInfo: React.FC = () => {
    const [userData, setUserData] = useState<UserOut>();

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const userResponse = await UsersService.readUserMe();
                setUserData(userResponse);
            } catch (error) {
                console.error(error);
            }
        };
        fetchUserData();
    }, []);

    return (
        <>
            {userData ? (
                <Flex p={2} gap={3}>
                    <Avatar icon={<FaUserAstronaut fontSize="18px" />} size='sm' alignSelf="center" />
                    <Text color='gray' alignSelf={"center"}>{userData.email}</Text>
                </Flex>
            ) :
                <Skeleton height='20px' />
            }

        </>
    );

}

export default UserInfo;