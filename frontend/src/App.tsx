import { useEffect, useRef, useState } from "react";
import { Message, TextFragment } from "./Messages";
import { DemoMessageContainer } from "./components/DemoMessageContainer";
import { MessageContainer } from "./components/MessageContainer";
import { Spinner } from "./components/Spinner";
import { useSocket, useSocketEvent } from "./hooks/useSocket";
import { Execution, Request } from "./types";
import { calculateSpinnerMessage, scrollToBottom } from "./utils";
import { RECOMMENDED_DEMO_MESSAGES } from "./constants";
import { WrapperContainer } from "./components/WrapperContainer";

function App() {
  const [input, setInput] = useState<string>("");
  const messagesEnd = useRef<HTMLDivElement | null>(null);
  const [messageHistory, setMessageHistory] = useState<Message[]>([]);
  const [executionState, setExecutionState] = useState<Execution | undefined>(
    undefined,
  );

  useEffect(() => scrollToBottom(messagesEnd), [messageHistory]);

  const io = useSocket();
  useSocketEvent("connect", () => console.log("reeeeeeeeee"));
  useSocketEvent("execution_created", (execution: Execution) =>
    setExecutionState(execution),
  );
  useSocketEvent("execution_updated", (execution: Execution) =>
    setExecutionState(execution),
  );

  const demoMessageClickHandler = (message: string) => {
    setMessageHistory([
      {
        owner: "user",
        fragments: [
          {
            type: "text",
            text: message,
          },
        ],
      },
    ]);
  };

  const onClickHandler = () => {
    const data: Message = {
      fragments: [{ type: "text", text: input }],
      owner: "user",
    };
    setInput("");
    const newHistory = [...messageHistory, data];
    setMessageHistory(newHistory);
    const emitData: Request[] = newHistory.map((message) => ({
      message: message.fragments
        .filter((fragment) => fragment.type === "text")
        .map((data) => (data as TextFragment).text)
        .join(" "),
      sender: message.owner,
    }));
    io.emit("execute", { messages: emitData });
  };

  return (
    <WrapperContainer>
      <div className="flex flex-col gap-4 w-full max-w-2xl px-4 bg-secondary-300 rounded-lg m-4 mt-0 overflow-hidden">
        <div className="bg-secondary-100 flex flex-col w-full h-full rounded-lg overflow-scroll">
          {messageHistory.length === 0 && (
            <>
              <div className="text-center w-full p-4">
                Hello there, how can I help you?
              </div>
              {RECOMMENDED_DEMO_MESSAGES.map((demoMsg, idx) => (
                <DemoMessageContainer
                  key={idx}
                  message={demoMsg}
                  onClickCallback={() => demoMessageClickHandler(demoMsg)}
                />
              ))}
            </>
          )}
          {messageHistory.map((message, idx) => (
            <MessageContainer message={message} key={idx} />
          ))}
          {executionState && executionState.progress != null && (
            <Spinner
              message={calculateSpinnerMessage(executionState.progress)}
            />
          )}
          <div ref={(el) => (messagesEnd.current = el)}></div>
        </div>
        <div className="flex gap-4 w-full">
          <input
            className="shadow appearance-none border border-primary-400 h-full rounded-xl w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="Input..."
            onChange={(e) => setInput(e.target.value)}
            value={input}
            onKeyDown={(e) => {
              if (e.code === "Enter") {
                onClickHandler();
              }
            }}
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
    </WrapperContainer>
  );
}

export default App;
