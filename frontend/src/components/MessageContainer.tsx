import { useState } from "react";
import { Message } from "../Messages";
import { Overlay } from "./Overlay";

interface MessageContainerProps {
  message: Message;
}

export const MessageContainer = ({ message }: MessageContainerProps) => {
  const [currentOverlay, setCurrentOverlay] = useState<string>("");
  const [showOverlay, setShowOverlay] = useState<boolean>(false);
  return (
    <div
      className={`${
        message.owner === "bot" ? "justify-items-start" : "justify-items-end"
      } grid  h-fit w-full`}
    >
      <div className="flex items-end">
        {message.owner === "bot" && (
          <img
            className="w-10 h-10 aspect-square"
            src="https://ia.leadoo.com/upload/images/bot_icon/WTYxNb0TNUeTcKL9.png"
            alt=""
          />
        )}
        <div
          className={`${
            message.owner === "bot"
              ? "bg-secondary-100 shadow-secondary-200 text-secondary-300 mr-16"
              : "bg-secondary-200 shadow-secondary-300 text-secondary-100 ml-16"
          } rounded-xl p-4 m-4 shadow-lg`}
        >
          {message.fragments.map((fragment, fragmentIdx) =>
            fragment.type === "text" ? (
              <div key={fragmentIdx}>{fragment.text}</div>
            ) : (
              <div key={fragmentIdx} className="w-4/5 py-12 mx-auto" onClick={() => {
                setCurrentOverlay(fragment.src)
                setShowOverlay(true)
              }}>
                <img src={fragment.src} alt={fragment.src} />
              </div>
            ),
          )}
        </div>
      </div>
      {showOverlay && <Overlay src={currentOverlay} callback={() => setShowOverlay(false)}/>}
    </div>
  );
};
