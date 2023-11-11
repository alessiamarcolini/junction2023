import { useContext, useEffect, useRef, useState } from "react";
import { Message, TextFragment } from "./Messages";
import { MessageContainer } from "./components/MessageContainer";
import { Spinner } from "./components/Spinner";
import { SocketContext, useSocket, useSocketEvent } from "./hooks/useSocket";

function App() {
  const [input, setInput] = useState<string>("");
  const messagesEnd = useRef<HTMLDivElement | null>(null);
  const [messageHistory, setMessageHistory] = useState<Message[]>([]);

  const scrollToBottom = () => {
    messagesEnd?.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => scrollToBottom(), [messageHistory]);

  const io = useSocket();
  useSocketEvent("connect", () => console.log("reeeeeeeeee"));

  const onClickHandler = () => {
    const data: Message = {
      fragments: [{ type: "text", text: input }],
      owner: "user",
    };
    const newHistory = [...messageHistory, data];
    setMessageHistory(newHistory);
    const emitData = newHistory.map((message) => ({
      message: message.fragments
        .filter((fragment) => fragment.type === "text")
        .map((data) => (data as TextFragment).text)
        .join(" "),
      sender: message.owner,
    }));
    io.emit("execute", { messages: emitData });
  };

  return (
    <div className="text-secondary-300 bg-secondary-300 w-full grid justify-items-center h-screen">
      <div className="flex flex-col gap-4 w-full max-w-2xl bg-secondary-300 rounded-lg p-10 m-4 overflow-hidden">
        <div className="bg-secondary-100 flex flex-col w-full h-full rounded-lg overflow-scroll">
          {messageHistory.length === 0 && (
            <div className="text-center w-full p-4">
              Hello there, how can I help you?
            </div>
          )}
          {messageHistory.map((message, idx) => (
            <MessageContainer message={message} key={idx} />
          ))}
          <Spinner message="76%" />
          <div ref={(el) => (messagesEnd.current = el)}></div>
        </div>
        <div className="flex gap-4 w-full">
          <input
            className="shadow appearance-none border border-primary-400 h-full rounded-xl w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="Input..."
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            disabled={input.length === 0}
            onClick={() => onClickHandler()}
            className="bg-secondary-200 min-w-[80px] rounded-lg h-full border-2 border-secondary-200 p-4 text-center duration-200 hover:bg-secondary-100 disabled:bg-secondary-300 disabled:border-secondary-200 disabled:text-secondary-200"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
