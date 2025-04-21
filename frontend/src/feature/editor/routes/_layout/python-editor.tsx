import {
  Box,
  useColorModeValue,
} from "@chakra-ui/react"
import Monaco from "@monaco-editor/react";
import React from "react";

// export const _Route = createFileRoute("/_layout/python-editor")({
//   component: PythonEditor,
// });

function PythonEditor() {
  const defaultCode = `# Напишите ваш Python код здесь\nprint("Hello, World!")`;

  const handleCodeChange = (value: string | undefined) => {
    console.log("Текущий код:", value);
  };

  const bgColor = useColorModeValue("ui.light", "ui.dark")
  const textColor = useColorModeValue("ui.dark", "ui.light")

  return (
    <Box
      bg={bgColor} // Стили для совпадения с Sidebar
      color={textColor}
      border="1px solid" // Аналогичная граница
      borderColor="gray.700"
      borderRadius="12px" // Скругленные углы, как Sidebar
      p={4} // Внутренний отступ
      mt={{ base: 4, md: 0 }} // Отступ сверху аналогичный Sidebar
      boxShadow="lg" // Добавляем тень для объема, если нужно
      h="calc(50vh - 32px)" // Удерживаем высоту относительно экрана (минус небольшой отступ)
      width="100%" // Занимает доступную ширину
      overflow="hidden" // Для предотвращения выхода содержимого за пределы
    >
      <Monaco
        height="100%" // Растягиваем редактор по высоте контейнера
        defaultLanguage="python"
        defaultValue={defaultCode}
        onChange={handleCodeChange}
        options={{
          fontSize: 14,
          minimap: { enabled: false }, // Убираем мини-карту
          scrollBeyondLastLine: false, // Предотвращаем прокрутку вниз за конец
          wordWrap: "on", // Включаем перенос строк
          automaticLayout: true, // Автоматическое изменение размеров
          tabSize: 4, // Размер табуляции
        }}
      />
    </Box>
  );
};

export default PythonEditor;