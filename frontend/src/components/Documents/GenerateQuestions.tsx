import { Button } from "@chakra-ui/react";
import { FaPlus } from "react-icons/fa";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { DocumentPublic, ExamsService } from "@/client";
import type { ApiError } from "@/client/core/ApiError";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";

const GenerateQuestions = ({
  selectedDocuments,
}: {
  selectedDocuments: DocumentPublic[];
}) => {
  const queryClient = useQueryClient();
  const { showSuccessToast } = useCustomToast();

  const mutation = useMutation({
    mutationFn: async (documentIds: string[]) => {
      ExamsService.generateExam({ requestBody: { document_ids: documentIds } });
      console.log("Generating questions for documents:", documentIds);
    },
    onSuccess: (data) => {
      showSuccessToast("Questions generated successfully.");
      console.log("Questions generated successfully.");
      console.log("Generated questions:", data); // <- log the actual questions

      queryClient.invalidateQueries({ queryKey: ["questions"] });
    },
    onError: (err: ApiError) => {
      handleError(err);
    },
  });

  const handleClick = () => {
    mutation.mutate(selectedDocuments.map((doc) => doc.id));
  };

  return (
    <Button
      my={4}
      variant="solid"
      onClick={handleClick}
      disabled={selectedDocuments.length === 0}
      loading={mutation.isPending}
    >
      <FaPlus fontSize="16px" />
      Generate Questions from selected Documents
    </Button>
  );
};

export default GenerateQuestions;
