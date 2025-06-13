import AsyncStorage from '@react-native-async-storage/async-storage';

export const getAccessToken = async (): Promise<string | null> => {
  try {
    const token = await AsyncStorage.getItem('access_token');
    console.log("Token from AsyncStorage:", token);
    return token;
  } catch (err) {
    console.error("Error getting token", err);
    return null;
  }
};
