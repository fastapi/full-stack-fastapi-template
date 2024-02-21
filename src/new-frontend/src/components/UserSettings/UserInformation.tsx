import React, { useState } from 'react';

import { Button, Container, Flex, FormControl, FormLabel, Heading, Input, Text, useColorModeValue } from '@chakra-ui/react';

import { useUserStore } from '../../store/user-store';

const UserInformation: React.FC = () => {
    const color = useColorModeValue('gray.700', 'white');
    const [editMode, setEditMode] = useState(false);
    const { user } = useUserStore();


    const toggleEditMode = () => {
        setEditMode(!editMode);
    };

    return (
        <>
            <Container maxW='full'>
                <Heading size='sm' py={4}>
                    User Information
                </Heading>
                <FormControl>
                    <FormLabel color={color}>Full name</FormLabel>
                    {
                        editMode ?
                            <Input placeholder={user?.full_name || 'Full name'} type='text' size='md' /> :
                            <Text size='md' py={2}>
                                {user?.full_name || 'N/A'}
                            </Text>
                    }
                </FormControl>
                <FormControl mt={4}>
                    <FormLabel color={color}>Email</FormLabel>
                    {
                        editMode ?
                            <Input placeholder={user?.email} type='text' size='md' /> :
                            <Text size='md' py={2}>
                                {user?.email || 'N/A'}
                            </Text>
                    }
                </FormControl>
                <Flex mt={4} gap={3}>
                    <Button bg='ui.main' color='white' _hover={{ opacity: 0.8 }} onClick={toggleEditMode}>
                        {editMode ? 'Save' : 'Edit'}
                    </Button>
                    {editMode &&
                        <Button onClick={() => setEditMode(false)}>
                            Cancel
                        </Button>}
                </Flex>
            </ Container>
        </>
    );
}
export default UserInformation;