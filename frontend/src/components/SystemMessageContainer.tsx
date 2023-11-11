import { useState, useRef, useLayoutEffect } from "react";
import { Message } from "../Messages";
import { Overlay } from "./Overlay";
import { Modal } from "./Modal";

interface MessageContainerProps {
  message: Message;
  hideDecision?: boolean;
  children?: React.ReactNode;
}

export const SystemMessageContainer = ({
  message,
  hideDecision = false,
  children = null
}: MessageContainerProps) => {
  const [currentOverlay, setCurrentOverlay] = useState<string>("");
  const [showOverlay, setShowOverlay] = useState<boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const ref = useRef<HTMLDivElement | null>(null);

  const [width, setWidth] = useState(0);

  useLayoutEffect(() => {
    const updateSize = () => {
      if (ref.current) {
        setWidth(ref.current.offsetWidth);
      }
    };
      if (ref.current) {
        setWidth(ref.current.offsetWidth);
      }
    window.addEventListener("resize", updateSize);
    return () => window.removeEventListener("resize", updateSize);
  }, [ref]);
  return (
    <div className={"justify-items-start grid  h-fit w-full"}>
      <div className="flex items-end w-full pl-2">
        <img
          className="w-10 h-10 aspect-square mb-2"
          src="https://ia.leadoo.com/upload/images/bot_icon/WTYxNb0TNUeTcKL9.png"
          alt=""
        />
        <div
          ref={ref}
          className="bg-secondary-100 shadow-secondary-200 text-secondary-300 mr-16 rounded-xl p-4 m-2 shadow-lg w-full"
        >
          {message.fragments.map((fragment, fragmentIdx) => {
            switch (fragment.type) {
              case "text":
                return (
                  <div key={fragmentIdx}>
                    {fragment.text.split("\n").map((t, idx) => (
                      <p key={idx}>{t}</p>
                    ))}
                  </div>
                );

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
                  <div key={fragmentIdx} className="w-full px-4 py-12 mx-auto">
                    <iframe
                      width={'100%'}
                      height={width * 0.9 + 3}
                      src={fragment.src}
                    />
                  </div>
                );
              case "error":
                return (
                  <div key={fragmentIdx} className="w-full px-4 py-12 mx-auto">
                    <p className="text-red-500">Error occured during generation. Please refresh... </p>
                  </div>
                );
            }
          })}
          {children}
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
            <p key={idx}>{d}</p>
          ))}
        </Modal>
      )}
      {showOverlay && (
        <Overlay src={currentOverlay} callback={() => setShowOverlay(false)} />
      )}
    </div>
  );
};
