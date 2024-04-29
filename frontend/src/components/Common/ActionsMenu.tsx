import {
  Button,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  useDisclosure,
} from "@chakra-ui/react";
import { BsThreeDotsVertical } from "react-icons/bs";
import { FiEdit, FiTrash } from "react-icons/fi";

import type { ItemPublic, StorePublic, UserPublic } from "../../client";
import EditUser from "../Admin/EditUser";
import EditItem from "../Items/EditItem";
import Delete from "./DeleteAlert";
import EditStore from "../Stores/EditStore";
import EditStoreInventory from "./Inventory/EditInventoryStore";
import PurchaseStoreInventory from "./Inventory/PurchaseInventory";

interface ActionsMenuProps {
  type: string;
  value: ItemPublic | UserPublic | StorePublic;
  disabled?: boolean;
}

const ActionsMenu = ({ type, value, disabled }: ActionsMenuProps) => {
  const editUserModal = useDisclosure();
  const deleteModal = useDisclosure();
  const purchaseModal = useDisclosure();

  const getAction = (type: string) => {
    switch (type) {
      case "User":
        return (
          <EditUser
            user={value as UserPublic}
            isOpen={editUserModal.isOpen}
            onClose={editUserModal.onClose}
          />
        );
      case "Store":
        return (
          <EditStore
            store={value as StorePublic}
            isOpen={editUserModal.isOpen}
            onClose={editUserModal.onClose}
          />
        );
      case "StoreInventory":
        return (
          <>
            <EditStoreInventory
              item={value as ItemPublic}
              isOpen={editUserModal.isOpen}
              onClose={editUserModal.onClose}
            />
            <PurchaseStoreInventory
              item={value as ItemPublic}
              isOpen={purchaseModal.isOpen}
              onClose={purchaseModal.onClose}
            />
          </>
        );
      case "Items":
        return (
          <EditItem
            item={value as ItemPublic}
            isOpen={editUserModal.isOpen}
            onClose={editUserModal.onClose}
          />
        );
      default:
        return;
    }
  };

  return (
    <>
      <Menu>
        <MenuButton
          isDisabled={disabled}
          as={Button}
          rightIcon={<BsThreeDotsVertical />}
          variant="unstyled"
        />
        <MenuList>
          <MenuItem
            onClick={editUserModal.onOpen}
            icon={<FiEdit fontSize="16px" />}
          >
            Edit {type}
          </MenuItem>

          {type === "StoreInventory" && (
            <MenuItem
              onClick={purchaseModal.onOpen}
            >
              Purchase this item
            </MenuItem>
            
          )}
                    <MenuItem
            onClick={deleteModal.onOpen}
            icon={<FiTrash fontSize="16px" />}
            color="ui.danger"
          >
            Delete {type}
            </MenuItem>
        </MenuList>
        {getAction(type)}
        <Delete
          type={type}
          id={value.id}
          isOpen={deleteModal.isOpen}
          onClose={deleteModal.onClose}
        />
      </Menu>
    </>
  );
};

export default ActionsMenu;
