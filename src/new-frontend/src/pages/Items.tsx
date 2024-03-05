import React from 'react';

import { Container, Flex, Heading, Spinner, Table, TableContainer, Tbody, Td, Th, Thead, Tr } from '@chakra-ui/react';
import { useQuery } from 'react-query';

import { ApiError, ItemsService } from '../client';
import ActionsMenu from '../components/Common/ActionsMenu';
import Navbar from '../components/Common/Navbar';
import useCustomToast from '../hooks/useCustomToast';

const getItems = async () => {
    const response = await ItemsService.readItems({ skip: 0, limit: 10 });
    return response.data;
}

const Items: React.FC = () => {
    const showToast = useCustomToast();
    const { data: items, isLoading, isError, error } = useQuery('items', getItems)

    if (isError) {
        const errDetail = (error as ApiError).body?.detail;
        showToast('Something went wrong.', `${errDetail}`, 'error');
    }

    return (
        <>
            {isLoading ? (
                // TODO: Add skeleton
                <Flex justify='center' align='center' height='100vh' width='full'>
                    <Spinner size='xl' color='ui.main' />
                </Flex>
            ) : (
                items &&
                <Container maxW='full'>
                    <Heading size='lg' textAlign={{ base: 'center', md: 'left' }} pt={12}>
                        Items Management
                    </Heading>
                    <Navbar type={'Item'} />
                    <TableContainer>
                        <Table size={{ base: 'sm', md: 'md' }}>
                            <Thead>
                                <Tr>
                                    <Th>ID</Th>
                                    <Th>Title</Th>
                                    <Th>Description</Th>
                                    <Th>Actions</Th>
                                </Tr>
                            </Thead>
                            <Tbody>
                                {items.map((item) => (
                                    <Tr key={item.id}>
                                        <Td>{item.id}</Td>
                                        <Td>{item.title}</Td>
                                        <Td color={!item.description ? 'gray.600' : 'inherit'}>{item.description || 'N/A'}</Td>
                                        <Td>
                                            <ActionsMenu type={'Item'} id={item.id} />
                                        </Td>
                                    </Tr>
                                ))}
                            </Tbody>
                        </Table>
                    </TableContainer>
                </Container>
            )}
        </>
    )
}

export default Items;