import SignUpForm from "@/components/auth/SignUpForm";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Next.js SignUp Page",
  description: "This is Next.js SignUp Page",
  // other metadata
};

export default function SignUp() {
  return <SignUpForm />;
}
