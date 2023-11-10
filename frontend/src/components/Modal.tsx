import { ReactNode } from "react";

interface OverlayProps {
  children: ReactNode;
  callback: Function;
}

export const Modal = ({ children, callback }: OverlayProps) => {
  return (
    <div
      className="fixed top-0 left-0 right-0 bottom-0 backdrop-blur-md flex justify-center items-center z-[999]"
      onClick={() => callback()}
    >
      <div
        className="w-full max-w-xl h-[80%] bg-secondary-100 flex flex-col gap-4 rounded-xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="bg-secondary-300 flex w-full p-4 justify-end">
          <button
            onClick={() => callback()}
            className="p-2 bg-secondary-100 rounded-xl"
          >
            Close
          </button>
        </div>
        <div className="p-8">
          {children}
        </div>
      </div>
    </div>
  );
};
