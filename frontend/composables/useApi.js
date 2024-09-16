export const useApi = () => {
  const config = useRuntimeConfig();
  const apiUrl = config.public.apiUrl;

  // Function to fetch a specific item by ID
  const getItem = async (id) => await useFetch(`${apiUrl}/api/v1/items/test/`, {
    method: 'GET'
  });

  return {
    getItem
  };
};
