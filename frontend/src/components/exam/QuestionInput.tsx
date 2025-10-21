import { useState } from "react";
import ListWithRadio from "../ui/list/ListWithRadio";

export default function QuestionInput() {
    const [selectedOption, setSelectedOption] = useState<string | null>(null);

    return (
               <div className="col-span-full">

              <ListWithRadio
                value={selectedOption} // controlled
                onChange={(val: React.SetStateAction<string | null>) => setSelectedOption(val)}
              />
            </div>)
}
