import { createFileRoute } from "@tanstack/react-router";
import { Fragment } from 'react';
import {
    Container,
    Box,
    chakra,
    Flex,
    Stack,
    VStack,
    HStack,
    Grid,
    Icon,
    Divider,
    Link,
    useColorModeValue
} from '@chakra-ui/react';
import { IconType } from 'react-icons';
import { FaRegComment, FaRegHeart, FaRegEye } from 'react-icons/fa';

export const Route = createFileRoute("/_layout/illumination/kids/")({
    component: Kids,
});

function Kids() {
    const ArticleStat = ({ icon, value }: { icon: IconType; value: number }) => {
        return (
            <Flex p={1} alignItems="center">
                <Icon as={icon} w={5} h={5} mr={2} />
                <chakra.span> {value} </chakra.span>
            </Flex>
        );
    };

    const ArticleSettingLink = ({ label }: { label: string }) => {
        return (
            <chakra.p
                as={Link}
                _hover={{ bg: useColorModeValue('gray.400', 'gray.600') }}
                p={1}
                rounded="md"
            >
                {label}
            </chakra.p>
        );
    };

    interface ArticleAttributes {
        title: string;
        link: string;
        created_at: string;
        meta: {
            reactions: number;
            comments: number;
            views: number;
        };
    }

    const articles: ArticleAttributes[] = [
        {
            title: 'Started 2022 by updating portfolio website',
            link: 'https://mahmad.me/blog/started-2022-by-updating-portfolio-website-1jde-temp-slug-4553258',
            created_at: '21 Jan 2022',
            meta: {
                reactions: 225,
                comments: 20,
                views: 500
            }
        },
        {
            title: 'Create professional portfolio website with Nextjs and ChakraUI',
            link: 'https://mahmad.me/blog/create-professional-portfolio-website-with-nextjs-and-chakraui-4lkn',
            created_at: '20 Jun 2021',
            meta: {
                reactions: 400,
                comments: 25,
                views: 300
            }
        },
        {
            title: `Find out what's new in my portfolio website`,
            link: 'https://mahmad.me/blog/what-s-new-in-my-portfolio-websitea',
            created_at: '31 Sept 2022',
            meta: {
                reactions: 5,
                comments: 15,
                views: 150
            }
        }
    ];

    return (
        <Container maxW="5xl" p={{ base: 5, md: 10 }}>
            <Flex justifyContent="left" mb={3}>
                <chakra.h3 fontSize="2xl" fontWeight="bold" textAlign="center">
                    Articles
                </chakra.h3>
            </Flex>
            <VStack border="1px solid" borderColor="gray.400" rounded="md" overflow="hidden" spacing={0}>
                {articles.map((article, index) => (
                    <Fragment key={index}>
                        <Grid
                            templateRows={{ base: 'auto auto', md: 'auto' }}
                            w="100%"
                            templateColumns={{ base: 'unset', md: '4fr 2fr 2fr' }}
                            p={{ base: 2, sm: 4 }}
                            gap={3}
                            alignItems="center"
                            _hover={{ bg: useColorModeValue('gray.200', 'gray.700') }}
                        >
                            <Box gridColumnEnd={{ base: 'span 2', md: 'unset' }}>
                                <chakra.h3 as={Link} href={article.link} isExternal fontWeight="bold" fontSize="lg">
                                    {article.title}
                                </chakra.h3>
                                <chakra.p
                                    fontWeight="medium"
                                    fontSize="sm"
                                    color={useColorModeValue('gray.600', 'gray.300')}
                                >
                                    Published: {article.created_at}
                                </chakra.p>
                            </Box>
                            <HStack
                                spacing={{ base: 0, sm: 3 }}
                                alignItems="center"
                                fontWeight="medium"
                                fontSize={{ base: 'xs', sm: 'sm' }}
                                color={useColorModeValue('gray.600', 'gray.300')}
                            >
                                <ArticleStat icon={FaRegComment} value={article.meta.comments} />
                                <ArticleStat icon={FaRegHeart} value={article.meta.reactions} />
                                <ArticleStat icon={FaRegEye} value={article.meta.views} />
                            </HStack>
                            <Stack
                                spacing={2}
                                direction="row"
                                fontSize={{ base: 'sm', sm: 'md' }}
                                justifySelf="flex-end"
                                alignItems="center"
                            >
                                {['Manage', 'Edit'].map((label, index) => (
                                    <ArticleSettingLink key={index} label={label} />
                                ))}
                            </Stack>
                        </Grid>
                        {articles.length - 1 !== index && <Divider m={0} />}
                    </Fragment>
                ))}
            </VStack>
        </Container>
    );
};
