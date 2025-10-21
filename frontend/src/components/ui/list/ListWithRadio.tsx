"use client";
import React, { useState } from "react";
import RadioSm from "../../form/input/RadioSm";

export default function ListWithRadio() {
  const [selectedValue, setSelectedValue] = useState<string>("option1");

  const handleChange = (value: string) => {
    setSelectedValue(value);
    console.log("Selected Value:", value);
  };
  return (
    <div className="rounded-lg border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] sm:w-fit">
      <ul className="flex flex-col">
        <li className="border-b border-gray-200 px-3 py-2.5 last:border-b-0 dark:border-gray-800">
          <RadioSm
            id="option1"
            name="example"
            value="option1"
            checked={selectedValue === "option1"}
            label="Lorem ipsum dolor sit amet"
            onChange={handleChange}
          />
        </li>
        <li className="border-b border-gray-200 px-3 py-2.5 last:border-b-0 dark:border-gray-800">
          <RadioSm
            id="option2"
            name="example"
            value="option2"
            checked={selectedValue === "option2"}
            label="It is a long established fact reader"
            onChange={handleChange}
          />
        </li>
        <li className="border-b border-gray-200 px-3 py-2.5 last:border-b-0 dark:border-gray-800">
          <RadioSm
            id="option3"
            name="example"
            value="option3"
            checked={selectedValue === "option3"}
            label="Lorem ipsum dolor sit amet"
            onChange={handleChange}
          />
        </li>
        <li className="border-b border-gray-200 px-3 py-2.5 last:border-b-0 dark:border-gray-800">
          <RadioSm
            id="option4"
            name="example"
            value="option4"
            checked={selectedValue === "option4"}
            label="Lorem ipsum dolor sit amet"
            onChange={handleChange}
          />
        </li>
        <li className="border-b border-gray-200 px-3 py-2.5 last:border-b-0 dark:border-gray-800">
          <RadioSm
            id="option5"
            name="example"
            value="option5"
            checked={selectedValue === "option5"}
            label="Lorem ipsum dolor sit amet"
            onChange={handleChange}
          />
        </li>
      </ul>
    </div>
  );
}
