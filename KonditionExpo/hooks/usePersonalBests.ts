import { useEffect, useState } from "react";
import { getAccessToken } from "@/scripts/auth"; // adjust based on your token handling

export const usePersonalBests = () => {
  const [pbs, setPbs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log("🔁 usePersonalBests hook loaded");
  
    const fetchPBs = async () => {
      console.log("📡 Fetching personal bests...");
      setLoading(true);
      try {
        console.log("🔑 Attempting to get token...");
        const token = await getAccessToken();
        console.log("Got token:", token);
  
        const res = await fetch("http://localhost:8000/api/v1/personal-bests", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
  
        const data = await res.json();
        console.log("📬 Fetched PBs:", data);
        setPbs(data.data); // Adjust if shape differs
      } catch (err) {
        console.error("Failed to fetch personal bests", err);
      } finally {
        setLoading(false);
      }
    };
  
    fetchPBs();
  }, []);
  
  

  return { pbs, loading };
};
