import Image from "next/image";
import React from "react";

export default function TwoColumnImageGrid() {
  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
      <div>
        <Image
          src="/images/grid-image/image-02.png"
          alt=" grid"
          className="w-full border border-gray-200 rounded-xl dark:border-gray-800"
          width={517}
          height={295}
        />
      </div>

      <div>
        <Image
          src="/images/grid-image/image-03.png"
          alt=" grid"
          className="w-full border border-gray-200 rounded-xl dark:border-gray-800"
          width={517}
          height={295}
        />
      </div>
    </div>
  );
}
