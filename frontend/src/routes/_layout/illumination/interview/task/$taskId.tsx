import { createFileRoute } from "@tanstack/react-router";
import { Box, Flex, Heading, Text, Divider, useColorModeValue } from '@chakra-ui/react';
import Editor from '@monaco-editor/react';
import { useState, useCallback } from "react";


export const Route = createFileRoute("/_layout/illumination/interview/task/$taskId")({
  component: InterViewTask,
});

function InterViewTask() {
  const editorTheme = useColorModeValue('vs', 'vs-dark');
  const problemTextColor = useColorModeValue('gray.700', 'gray.300');

  const [editorHeight, setEditorHeight] = useState('30%');
  const [isDragging, setIsDragging] = useState(false);

  const handleMouseDown = useCallback(() => {
    setIsDragging(true);
  }, []);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent | MouseEvent) => {
      if (isDragging) {
        const newHeight = `calc(${(e.clientY / window.innerHeight) * 100}% - 8px)`;
        setEditorHeight(newHeight);
      }
    },
    [isDragging]
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);


  const problemDescription = `
      ## Two Sum
      
      Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.
      
      You may assume that each input would have exactly one solution, and you may not use the same element twice.
      
      **Example 1:**
      
      \`\`\`
      Input: nums = [2,7,11,15], target = 9
      Output: [0,1]
      Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
      \`\`\`
      
      **Constraints:**
      - 2 <= nums.length <= 10^4
      - -10^9 <= nums[i] <= 10^9
      - -10^9 <= target <= 10^9
      `;


  return (
    <Flex
      height="100vh"
      width="100%"
      direction="row" // Меняем направление на горизонтальное
    >

      <Flex
        height="100vh"
        width="50%"
        direction="column"
        mt={4}
        onMouseMove={handleMouseMove as any}
        onMouseUp={handleMouseUp}
        position="relative"
      >
        {/* Редактор кода */}
        <Box
          flexShrink={0}
          height={editorHeight}
          borderBottomWidth={1}
          overflow="hidden"
          position="relative"
        >
          <Editor
            height="100%"
            defaultLanguage="python"
            theme={editorTheme}
            defaultValue="// Write your code here"
            options={{
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              automaticLayout: true,
            }}
          />
        </Box>

        {/* Разделитель */}
        <Divider
          orientation="horizontal"
          cursor="row-resize"
          borderColor="gray.400"
          borderWidth={2}
          _hover={{ borderWidth: 3, borderColor: 'blue.400' }}
          position="relative"
          zIndex={1}
          width="98%"
          onMouseDown={handleMouseDown}
        />


        {/* Описание задачи */}
        <Box
          flex={1}
          overflowY="auto"
          p={6}
          bg={useColorModeValue('gray.50', 'gray.800')}
          color={problemTextColor}
        >
          <Box maxW="800px" mx="auto">
            <Heading mb={4} fontSize="2xl">Two Sum</Heading>
            <Divider mb={6} />
            <Text
              whiteSpace="pre-wrap"
              fontFamily="monospace"
              lineHeight="tall"
              fontSize="md"
            >
              {problemDescription}
            </Text>
          </Box>
        </Box>
      </Flex>

      <Box
        flex={1} // Занимает все оставшееся пространство
        p={6}
        bg={useColorModeValue('gray.50', 'gray.800')}
        borderLeftWidth={1}
        borderColor={useColorModeValue('gray.200', 'gray.600')}
        overflowY="auto"
      >
        <Heading mb={4} fontSize="xl">Анализ кода</Heading>
        <Divider mb={6} />, 

        <Text mb={4} color="gray.500">
          Здесь будет отображаться анализ вашего кода в реальном времени.
          Пример вывода переменных и подсказок:
        </Text>

        <Box
          p={4}
          bg={useColorModeValue('gray.50', 'gray.800')}
          borderRadius="md"
        >
          <Text fontFamily="monospace" fontSize="sm">
        // Пример вывода переменных:\n
            nums = [2, 7, 11, 15]\n
            target = 9\n
            hashmap = {'{'} 2: 0 {'}'}\n
            current index = 1\n
            complement = 2\n
          </Text>
        </Box>

        <Text mt={6} color="gray.500">
          Советы от системы:\n
          1. Попробуйте использовать хеш-таблицу для оптимизации\n
          2. Проверьте граничные случаи для пустого массива\n
          3. Убедитесь в правильности возвращаемых индексов
        </Text>
      </Box>

    </Flex>
  );
};
