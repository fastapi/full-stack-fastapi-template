import { useEffect, useState } from "react";
import { getAccessToken } from "@/scripts/auth"; // adjust based on your token handling
import { API_URL } from "@/constants/config";

type PersonalBest = {
  metric: string;
  value: number;
  date: string;
};


export const usePersonalBests = () => {
  const [pbs, setPbs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchPBs = async () => {
    console.log("Fetching personal bests...");
    setLoading(true);
    try {
      const token = await getAccessToken();
      console.log("Token from getAccessToken: ", token);
      const res = await fetch(`http://localhost:8000/api/v1/personal-bests/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const text = await res.text();
      console.log("PB hook res: ", res);
      try {
        if (res.ok) {
          const data = await res.json();
          console.log("Fetched PBs:", data);
          setPbs(data.data);  // expected: array
        } else {
          const errData = await res.json();
          console.warn("PB hook res: ", errData);
          setPbs([]);  // fallback to empty array to avoid crash
        }
      } catch (parseErr) {
        console.error("Could not parse JSON:", text);
      }
    } catch (err) {
      console.error("Failed to fetch personal bests", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPBs();
  }, []);

  return { pbs, loading, refresh: fetchPBs };
};
