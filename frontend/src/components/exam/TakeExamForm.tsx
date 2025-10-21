"use client";
import React from "react";
import Button from "../ui/button/Button";
import Form from "../form/Form";
import ComponentCard from "../common/ComponentCard";
import QuestionInput from "./QuestionInput";

export default function TakeExamForm() {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Form submitted:");
  };
  return (
    <ComponentCard title="Exam Form">
      <Form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">


        {Array.from({ length: 5 }).map((_, i) => (
          <QuestionInput key={i} />
        ))}


          <div className="col-span-full">
            <Button className="w-full" size="sm">
              Submit
            </Button>
          </div>
        </div>
      </Form>
    </ComponentCard>
  );
}
