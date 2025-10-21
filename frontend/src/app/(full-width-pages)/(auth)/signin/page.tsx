import SignInForm from "@/components/auth/SignInForm";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Next.js SignIn Page",
  description: "This is Next.js Signin Page",
};

export default function SignIn() {
  return <SignInForm />;
}
