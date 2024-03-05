import React from 'react';

import { Button, FormControl, FormLabel, Input, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay } from '@chakra-ui/react';
import { SubmitHandler, useForm } from 'react-hook-form';

import { useMutation, useQueryClient } from 'react-query';
import { ApiError, ItemUpdate, ItemsOut, ItemsService } from '../../client';
import useCustomToast from '../../hooks/useCustomToast';

interface EditItemProps {
    id: number;
    isOpen: boolean;
    onClose: () => void;
}

const EditItem: React.FC<EditItemProps> = ({ id, isOpen, onClose }) => {
    const queryClient = useQueryClient();
    const showToast = useCustomToast();

    const items = queryClient.getQueryData<ItemsOut>('items');
    const currentItem = items?.data.find((item) => item.id === id);

    const { register, handleSubmit, reset, formState: { isSubmitting }, } = useForm<ItemUpdate>({ defaultValues: { title: currentItem?.title, description: currentItem?.description } });

    const updateItem = async (data: ItemUpdate) => {
        await ItemsService.updateItem({ id, requestBody: data });
    }

    const mutation = useMutation(updateItem, {
        onSuccess: () => {
            showToast('Success!', 'Item updated successfully.', 'success');
            reset();
            onClose();
        },
        onError: (err: ApiError) => {
            const errDetail = err.body.detail;
            showToast('Something went wrong.', `${errDetail}`, 'error');
        },
        onSettled: () => {
            queryClient.invalidateQueries('items');
        }
    });

    const onSubmit: SubmitHandler<ItemUpdate> = async (data) => {
        mutation.mutate(data)
    }

    const onCancel = () => {
        reset();
        onClose();
    }

    return (
        <>
            <Modal
                isOpen={isOpen}
                onClose={onClose}
                size={{ base: 'sm', md: 'md' }}
                isCentered
            >
                <ModalOverlay />
                <ModalContent as='form' onSubmit={handleSubmit(onSubmit)}>
                    <ModalHeader>Edit Item</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody pb={6}>
                        <FormControl>
                            <FormLabel htmlFor='title'>Title</FormLabel>
                            <Input id='title' {...register('title')} type='text' />
                        </FormControl>
                        <FormControl mt={4}>
                            <FormLabel htmlFor='description'>Description</FormLabel>
                            <Input id='description' {...register('description')} placeholder='Description' type='text' />
                        </FormControl>
                    </ModalBody>
                    <ModalFooter gap={3}>
                        <Button bg='ui.main' color='white' _hover={{ opacity: 0.8 }} type='submit' isLoading={isSubmitting}>
                            Save
                        </Button>
                        <Button onClick={onCancel}>Cancel</Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    )
}

export default EditItem;