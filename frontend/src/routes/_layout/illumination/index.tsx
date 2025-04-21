import {
    Box,
    Button,
    Container,
    Flex,
    Heading,
    Icon,
    Stack,
    Text,
    useColorModeValue,
  } from '@chakra-ui/react';
import { ReactElement } from 'react';
import { FcAbout, FcCollaboration, FcCloseUpMode } from 'react-icons/fc';
import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/_layout/illumination/")({
    component: Illumination,
});

function Illumination() {
    interface CardProps {
        heading: string
        description: string
        icon: ReactElement
        href: string
        buttonPath: string
    };
    
    const bgColor = useColorModeValue("ui.light", "ui.dark");
    
    const Card = ({ heading, description, icon, buttonPath }: CardProps) => {
        return (
          <Box
            maxW={{ base: 'full', md: '275px' }}
            w={'full'}
            borderWidth="1px"
            borderRadius="lg"
            overflow="hidden"
            display="flex"
            p={5}>
            <Stack align={'start'} spacing={2}>
              <Flex
                w={16}
                h={16}
                align={'center'}
                justify={'center'}
                color={bgColor}
                rounded={'full'}
                bg={useColorModeValue('gray.100', 'gray.700')}>
                {icon}
              </Flex>
              <Box mt={2}>
                <Heading size="md">{heading}</Heading>
                <Text mt={1} fontSize={'sm'}>
                  {description}
                </Text>
              </Box>
              <Button as={Link} to={buttonPath} variant={'link'} colorScheme={'blue'} size={'sm'} mt={'auto'}>
                Открыть раздел
              </Button>
            </Stack>
          </Box>
        )
      }


    return (
        <Box p={4}>
        <Stack spacing={4} as={Container} maxW={'3xl'} textAlign={'center'}>
            <Heading fontSize={{ base: '2xl', sm: '4xl' }} fontWeight={'bold'}>
            Доступные разделы
            </Heading>
            <Text color={'gray.600'} fontSize={{ base: 'sm', sm: 'lg' }}>
            Выберите раздел, который наиболее подходит вашим целям
            </Text>
        </Stack>
        <Container maxW={'5xl'} mt={12}>
              <Flex flexWrap="wrap" gridGap={6} justify="center">
              <Card
                  heading={'Для собеседования'}
                  icon={<Icon as={FcCollaboration} w={10} h={10} />}
                  description={'Помощь в подготовке к собеседованию.'}
                  href={'#'}
                  buttonPath={'/illumination/interview/'}
              />
              <Card
                  heading={'Для детей'}
                  icon={<Icon as={FcCloseUpMode} w={10} h={10} />}
                  description={'Помощь в обучении детей.'}
                  href={'#'}
                  buttonPath={'/illumination/kids/'}
              />
              <Card
                  heading={'В разработке'}
                  icon={<Icon as={FcAbout} w={10} h={10} />}
                  description={'...'}
                  href={'#'}
                  buttonPath={'/illumination/unknown/'}
              />
              <Card
                  heading={'В разработке'}
                  icon={<Icon as={FcAbout} w={10} h={10} />}
                  description={'...'}
                  href={'#'}
                  buttonPath={'/illumination/unknown/'}
              />
              <Card
                  heading={'В разработке'}
                  icon={<Icon as={FcAbout} w={10} h={10} />}
                  description={'...'}
                  href={'#'}
                  buttonPath={'/illumination/unknown/'}
              />
              </Flex>
        </Container>
        </Box>
    )
};