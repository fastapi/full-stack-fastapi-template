import TakeExamForm from "@/components/exam/TakeExamForm";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Next.js TakeExam Page",
  description: "This is Next.js TakeExam Page",
};

export default function TakeExam() {
  return <TakeExamForm />;
}
