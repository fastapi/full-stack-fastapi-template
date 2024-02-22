import React from 'react';

import { Container, Heading, Tab, TabList, TabPanel, TabPanels, Tabs } from '@chakra-ui/react';
import Appearance from '../components/UserSettings/Appearance';
import ChangePassword from '../components/UserSettings/ChangePassword';
import DeleteAccount from '../components/UserSettings/DeleteAccount';
import UserInformation from '../components/UserSettings/UserInformation';

const tabsConfig = [
    { title: 'My profile', component: UserInformation },
    { title: 'Password', component: ChangePassword },
    { title: 'Appearance', component: Appearance },
    { title: 'Danger zone', component: DeleteAccount },
];

const UserSettings: React.FC = () => {
    return (
        <Container maxW='full'>
            <Heading size='lg' textAlign={{ base: 'center', md: 'left' }} py={12}>
                User Settings
            </Heading>
            <Tabs variant='enclosed'>
                <TabList>
                    {tabsConfig.map((tab, index) => (
                        <Tab key={index}>{tab.title}</Tab>
                    ))}
                </TabList>
                <TabPanels>
                    {tabsConfig.map((tab, index) => (
                        <TabPanel key={index}>
                            <tab.component />
                        </TabPanel>
                    ))}
                </TabPanels>
            </Tabs>
        </Container>
    );
};

export default UserSettings;