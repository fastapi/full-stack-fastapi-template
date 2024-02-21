import React, { useState } from 'react';

import { Button, FormControl, FormLabel, Input, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay } from '@chakra-ui/react';
import { SubmitHandler, useForm } from 'react-hook-form';

import { ItemCreate } from '../../client';
import useCustomToast from '../../hooks/useCustomToast';
import { useItemsStore } from '../../store/items-store';

interface AddItemProps {
    isOpen: boolean;
    onClose: () => void;
}

const AddItem: React.FC<AddItemProps> = ({ isOpen, onClose }) => {
    const showToast = useCustomToast();
    const [isLoading, setIsLoading] = useState(false);
    const { register, handleSubmit, reset } = useForm<ItemCreate>();
    const { addItem } = useItemsStore();

    const onSubmit: SubmitHandler<ItemCreate> = async (data) => {
        setIsLoading(true);
        try {
            await addItem(data);
            showToast('Success!', 'Item created successfully.', 'success');
            reset();
            onClose();
        } catch (err) {
            showToast('Something went wrong.', 'Failed to create item. Please try again.', 'error');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            <Modal
                isOpen={isOpen}
                onClose={onClose}
                size={{ base: 'sm', md: 'md' }}
                isCentered
            >
                <ModalOverlay />
                <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
                    <ModalHeader>Add Item</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody pb={6}>
                        <FormControl>
                            <FormLabel>Title</FormLabel>
                            <Input
                                {...register('title')}
                                placeholder="Title"
                                type="text"
                            />
                        </FormControl>
                        <FormControl mt={4}>
                            <FormLabel>Description</FormLabel>
                            <Input
                                {...register('description')}
                                placeholder="Description"
                                type="text"
                            />
                        </FormControl>
                    </ModalBody>

                    <ModalFooter gap={3}>
                        <Button bg="ui.main" color="white" _hover={{ opacity: 0.8 }} type="submit" isLoading={isLoading}>
                            Save
                        </Button>
                        <Button onClick={onClose} isDisabled={isLoading}>
                            Cancel
                        </Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    );
};

export default AddItem;
