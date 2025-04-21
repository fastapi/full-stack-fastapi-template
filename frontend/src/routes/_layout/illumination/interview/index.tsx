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
    useColorModeValue,
    Collapse
} from '@chakra-ui/react';
import { IconType } from 'react-icons';
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { FaRegComment, FaRegHeart, FaRegEye } from 'react-icons/fa';
import { IlluminationsService, TaskPublic } from '../../../../client';
import { FaChevronDown, FaChevronRight } from "react-icons/fa";

export const Route = createFileRoute("/_layout/illumination/interview/")({
    component: Interview,
});

function Interview() {
    const [openCategoryId, setOpenCategoryId] = useState(null);

    const toggleList = (categoryId: any) => {
        setOpenCategoryId(prevState => (prevState === categoryId ? -1 : categoryId));
      };

    const IlluminationStat = ({ icon, value }: { icon: IconType; value: number }) => {
        return (
            <Flex p={1} alignItems="center">
                <Icon as={icon} w={5} h={5} mr={2} />
                <chakra.span> {value} </chakra.span>
            </Flex>
        );
    };

    const queryClient = useQueryClient();

    function getIlluminationsQueryOptions({ illuminationType }: { illuminationType: string }) {
        return {
            queryFn: () => IlluminationsService.readByIlluminationType({ illuminationType }),
            queryKey: ["illuminations", { illuminationType }],
        };
    };

    useEffect(() => {
        queryClient.prefetchQuery(getIlluminationsQueryOptions({ illuminationType: 'interview' }))
    }, [queryClient]
    );

    const {
        data: illumination_tasks,
        isPending
    } = useQuery({
        ...getIlluminationsQueryOptions({ illuminationType: 'interview' })
    });

    const groupTasksByCategory = (tasks: TaskPublic[]) => {
        let id = 0;
        return tasks.reduce<Record<string, {id: number, tasks: TaskPublic[]}>>((acc, task) => {
            if (!acc[task.category]) {
                acc[task.category] = {id: id, tasks: []};
                id += 1;
            }
            acc[task.category].tasks.push(task);
            return acc;
        }, {});
    };

    const groupedTasks = !isPending && illumination_tasks ? groupTasksByCategory(illumination_tasks.tasks) : { 'Загрузка': {id: 0, tasks: new Array<TaskPublic>} };

    console.log(illumination_tasks);
    console.log(groupedTasks);

    const IlluminationSettingLink = ({ label, href }: { label: string, href: string }) => {
        return (
            <chakra.p
                as={Link}
                href={href}
                _hover={{ bg: useColorModeValue('gray.400', 'gray.600') }}
                p={1}
                rounded="md"
            >
                {label}
            </chakra.p>
        );
    };

    return (
        <Container maxW="5xl" p={{ base: 5, md: 10 }}>
            <Flex justifyContent="left" mb={3}>
                <chakra.h2 fontSize="2xl" fontWeight="bold" textAlign="center">
                    Подготовка к собеседованию
                </chakra.h2>
            </Flex>
            {isPending ? (
                <Flex justifyContent="left" mb={3}></Flex>)
                :
                (<Container maxW="5xl" p={{ base: 5, md: 10 }} mb={25} m={25}>
                    {Object.entries(groupedTasks).map(([category, tasksMeta]) => (
                        <>
                            <Flex justifyContent="left" mb={3}>
                                <chakra.h3 fontSize="2xl" fontWeight="bold" textAlign="center" cursor="pointer" onClick={() => toggleList(tasksMeta.id)} _hover={{ color: "teal.500" }}>
                                    <Icon as={openCategoryId === tasksMeta.id ? FaChevronDown : FaChevronRight} mr={2} />
                                    {category}
                                </chakra.h3>

                            </Flex>

                            <Collapse in={openCategoryId === tasksMeta.id} animateOpacity>
                            <VStack border="1px solid" borderColor="gray.400" rounded="md" overflow="hidden" spacing={0} mb={25} m={25}>
                                {tasksMeta.tasks.map((task, index) => (
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
                                                <chakra.h3 as={Link} href={`/illumination/interview/task/${task.id}`} fontWeight="bold" fontSize="lg">
                                                    {task.title}
                                                </chakra.h3>
                                                <chakra.p
                                                    fontWeight="medium"
                                                    fontSize="sm"
                                                    color={useColorModeValue('gray.600', 'gray.300')}
                                                >
                                                    Published: {task.created_at}
                                                </chakra.p>
                                            </Box>
                                            <HStack
                                                spacing={{ base: 0, sm: 3 }}
                                                alignItems="center"
                                                fontWeight="medium"
                                                fontSize={{ base: 'xs', sm: 'sm' }}
                                                color={useColorModeValue('gray.600', 'gray.300')}
                                            >
                                                <IlluminationStat icon={FaRegComment} value={5} />
                                                <IlluminationStat icon={FaRegHeart} value={5} />
                                                <IlluminationStat icon={FaRegEye} value={5} />
                                            </HStack>
                                            <Stack
                                                spacing={2}
                                                direction="row"
                                                fontSize={{ base: 'sm', sm: 'md' }}
                                                justifySelf="flex-end"
                                                alignItems="center"
                                            >
                                                <IlluminationSettingLink key={0} label={'Перейти'} href={`/illumination/interview/task/${task.id}`}/>
                                            </Stack>
                                        </Grid>
                                        {tasksMeta.tasks.length - 1 !== index && <Divider m={0} />}
                                    </Fragment>
                                ))}
                            </VStack>
                            </Collapse>
                        </>
                    ))}
                </Container>
                )}
        </Container>
    );
};
