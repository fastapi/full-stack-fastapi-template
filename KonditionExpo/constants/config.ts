const LOCAL_IP = "http://192.168.1.119"; //replace with *your* machine's IP
const PRODUCTION_URL = "https://your-deployed-backend.com"; // if you have one

// Smart switcher for dev vs prod
export const API_URL =
  process.env.NODE_ENV === "production" ? PRODUCTION_URL : LOCAL_IP;
