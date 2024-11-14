import React from "react";
import { Select, Box } from "@chakra-ui/react";

// Define the expected props for the ModelSelector component
interface ModelSelectorProps {
  models: string[]; // Array of model names to display in the dropdown
  onSelectModel: (model: string) => void; // Callback function to handle the selected model
}

// ModelSelector component
const ModelSelector: React.FC<ModelSelectorProps> = ({ models, onSelectModel }) => {
  // handleChange function: Called when a new model is selected from the dropdown.
  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    onSelectModel(event.target.value); // Pass the selected model value to the onSelectModel callback
  };

  return (
    // Box component for layout styling, used to wrap the Select component
    <Box>
      {/* Chakra UI's Select component for the dropdown menu */}
      <Select placeholder="Select a model" onChange={handleChange}>
        {/* Map over the models array to create an <option> for each model */}
        {models.map((model) => (
          <option key={model} value={model}>
            {model} {/* Display the model name */}
          </option>
        ))}
      </Select>
    </Box>
  );
};

export default ModelSelector;