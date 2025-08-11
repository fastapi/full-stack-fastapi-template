import { IconButton } from "@chakra-ui/react";
import { BsThreeDotsVertical } from "react-icons/bs";
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu";

import type { DocumentPublic } from "@/client";
import DeleteDocument from "../Documents/DeleteDocument";
import EditDocument from "../Documents/EditDocument";

interface DocumentActionsMenuProps {
  document: DocumentPublic;
}

export const DocumentActionsMenu = ({ document }: DocumentActionsMenuProps) => {
  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit">
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <EditDocument document={document} />
        <DeleteDocument id={document.id} />
      </MenuContent>
    </MenuRoot>
  );
};
