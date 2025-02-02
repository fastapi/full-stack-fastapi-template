import React, { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';

interface PathActionsMenuProps {
  pathId: string;
}

const PathActionsMenu: React.FC<PathActionsMenuProps> = ({ pathId }) => {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleEdit = () => {
    navigate({ to: `/paths/${pathId}` });
  };

  const handleDelete = () => {
    // Placeholder for delete functionality
    console.log('Delete action for path:', pathId);
  };

  return (
    <div className="relative inline-block">
      <button
        onClick={() => setMenuOpen(!menuOpen)}
        className="p-2 hover:bg-gray-200 rounded-full"
        aria-label="Actions"
      >
        <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
          <circle cx="3" cy="10" r="2" />
          <circle cx="10" cy="10" r="2" />
          <circle cx="17" cy="10" r="2" />
        </svg>
      </button>
      {menuOpen && (
        <div className="absolute right-0 mt-2 w-32 bg-white border rounded shadow-md z-10">
          <div
            onClick={() => {
              handleEdit();
              setMenuOpen(false);
            }}
            className="cursor-pointer px-4 py-2 hover:bg-gray-100"
          >
            Edit Path
          </div>
          <div
            onClick={() => {
              handleDelete();
              setMenuOpen(false);
            }}
            className="cursor-pointer px-4 py-2 hover:bg-gray-100"
          >
            Delete Path
          </div>
        </div>
      )}
    </div>
  );
};

export default PathActionsMenu;
