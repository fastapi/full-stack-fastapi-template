import { IconButton } from "@chakra-ui/react";
import { BsThreeDotsVertical } from "react-icons/bs";
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu";

import type { DocumentPublic } from "@/client";
import DeleteDocument from "../Documents/DeleteDocument";

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
        <DeleteDocument id={document.id} />
      </MenuContent>
    </MenuRoot>
  );
};
