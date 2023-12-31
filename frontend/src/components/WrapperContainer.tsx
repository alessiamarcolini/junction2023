import { ReactNode } from "react";
import { Heading } from "./Heading";

interface WrapperContainerProps {
  children: ReactNode;
}

export const WrapperContainer = ({ children }: WrapperContainerProps) => {
  return (
    <div className="grid w-full justify-items-center">
      <div className="flex flex-col w-full max-w-2xl h-screen max-h-screen text-secondary-300 bg-secondary-300 overflow-hidden">
        <Heading />
        <div className="text-secondary-300 bg-secondary-300 w-full grid justify-items-center h-full overflow-hidden">
          {children}
        </div>
      </div>
    </div>
  );
};
