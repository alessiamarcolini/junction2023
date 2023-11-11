import { useState } from "react";
import { Message } from "../Messages";
import { Overlay } from "./Overlay";
import { Modal } from "./Modal";

interface MessageContainerProps {
  message: Message;
  hideDecision?: boolean;
}

export const SystemMessageContainer = ({
  message,
  hideDecision = false,
}: MessageContainerProps) => {
  const [currentOverlay, setCurrentOverlay] = useState<string>("");
  const [showOverlay, setShowOverlay] = useState<boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  return (
    <div className={"justify-items-start grid  h-fit w-full"}>
      <div className="flex items-end">
        <img
          className="w-10 h-10 aspect-square"
          src="https://ia.leadoo.com/upload/images/bot_icon/WTYxNb0TNUeTcKL9.png"
          alt=""
        />
        <div className="bg-secondary-100 shadow-secondary-200 text-secondary-300 mr-16 rounded-xl p-4 m-4 shadow-lg">
          {message.fragments.map((fragment, fragmentIdx) => {
            switch (fragment.type) {
              case "text":
                return <div key={fragmentIdx}>{fragment.text}</div>;

              case "image":
                return (
                  <div
                    key={fragmentIdx}
                    className="w-4/5 py-12 mx-auto"
                    onClick={() => {
                      setCurrentOverlay(fragment.src);
                      setShowOverlay(true);
                    }}
                  >
                    <img src={fragment.src} alt={fragment.src} />
                  </div>
                );
              case "html":
                return (
                  <div key={fragmentIdx} className="w-4/5 py-12 mx-auto">
                    <iframe src={fragment.src} />
                  </div>
                );
            }
          })}
          {!hideDecision && (
            <button
              onClick={() => setShowModal(true)}
              className="text-secondary-300 rounded-xl border-2 border-secondary-300 hover:opacity-200 p-2 mt-4 text-xs"
            >
              Show thought process
            </button>
          )}
        </div>
      </div>
      {showModal && (
        <Modal
          callback={() => {
            setShowModal(false);
          }}
        >
          {message.decision.map((d, idx) => (
            <div key={idx}>{d}</div>
          ))}
        </Modal>
      )}
      {showOverlay && (
        <Overlay src={currentOverlay} callback={() => setShowOverlay(false)} />
      )}
    </div>
  );
};