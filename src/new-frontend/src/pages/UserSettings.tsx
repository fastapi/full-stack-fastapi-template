import React from 'react';

import { Container, Heading, Tab, TabList, TabPanel, TabPanels, Tabs } from '@chakra-ui/react';

import Appearance from '../components/UserSettings/Appearance';
import ChangePassword from '../components/UserSettings/ChangePassword';
import DeleteAccount from '../components/UserSettings/DeleteAccount';
import UserInformation from '../components/UserSettings/UserInformation';



const UserSettings: React.FC = () => {

    return (
        <>
            <Container maxW='full'>
                <Heading size='lg' textAlign={{ base: 'center', md: 'left' }} py={12}>
                    User Settings
                </Heading>
                <Tabs variant='enclosed' >
                    <TabList>
                        <Tab>My profile</Tab>
                        <Tab>Password</Tab>
                        <Tab>Appearance</Tab>
                        <Tab>Danger zone</Tab>
                    </TabList>
                    <TabPanels>
                        <TabPanel>
                            <UserInformation />
                        </TabPanel>
                        <TabPanel>
                            <ChangePassword />
                        </TabPanel>
                        <TabPanel>
                            <Appearance />
                        </TabPanel>
                        <TabPanel>
                            <DeleteAccount />
                        </TabPanel>

                    </TabPanels>
                </Tabs>
            </Container>
        </>
    );
};

export default UserSettings;

