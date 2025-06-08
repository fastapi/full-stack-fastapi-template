import { useEffect, useState } from "react";
import { getAccessToken } from "@/scripts/auth";

type PersonalBest = {
  id: string;
  user_id: string;
  exercise_name: string;
  metric_type: string;
  metric_value: number;
  date_achieved: string | null;
};
  
export const usePersonalBests = () => {
  const [pbs, setPbs] = useState<PersonalBest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPBs = async () => {
      setLoading(true);
      try {
        const token = await getAccessToken();
        const res = await fetch("http://localhost:8000/api/v1/personal-bests", {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (!res.ok) {
          throw new Error(`Failed to fetch: ${res.status} ${res.statusText}`);
        }

        const data = await res.json();

        // Confirm if data is directly a list or wrapped in { data: [...] }
        const pbsList = Array.isArray(data) ? data : data.data;
        setPbs(pbsList ?? []);
      } catch (err) {
        console.error("Failed to fetch personal bests", err);
        setPbs([]);
      } finally {
        setLoading(false);
      }
    };

    fetchPBs();
  }, []);

  return { pbs, loading };
};
