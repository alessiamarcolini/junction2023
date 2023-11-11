import { useEffect, useRef, useState } from "react";
import { Message, TextFragment } from "./Messages";
import { DemoMessageContainer } from "./components/DemoMessageContainer";
import { MessageContainer } from "./components/MessageContainer";
import { Spinner } from "./components/Spinner";
import { useSocket, useSocketEvent } from "./hooks/useSocket";
import { Execution, Request, TextReceivedEvent } from "./types";
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
  const [currentMessage, setCurrentMessage] = useState<string>("");
  const [decision, setDecision] = useState<string[]>([]);
  const [generating, setGenerating] = useState<boolean>(false);

  useEffect(() => scrollToBottom(messagesEnd), [messageHistory, executionState, currentMessage]);

  const io = useSocket();
  useSocketEvent("connect", () => console.log("reeeeeeeeee"));
  useSocketEvent("execution_created", (execution: Execution) =>
    setExecutionState(execution),
  );
  useSocketEvent("execution_updated", (execution: Execution) =>
    setExecutionState(execution),
  );
  useSocketEvent("text_received", (message: TextReceivedEvent) =>
    // TODO: rework this logic when we have special delimiters for images
    setCurrentMessage((current) => `${current} ${message.text}`),
  );
  useSocketEvent("debug_thought_received", (message: TextReceivedEvent) =>
    setDecision((current) => [...current, message.text]),
  );
  useSocketEvent("finalize", () => {
    setMessageHistory([
      ...messageHistory,
      {
        senderRole: "system",
        fragments: [{ type: "text", text: currentMessage }],
        decision,
      },
    ]);
    setCurrentMessage("");
    setDecision([]);
    setGenerating(false)
  });

  const onClickHandler = (message: Message) => {
    setInput("");
    const newHistory = [...messageHistory, message];
    setMessageHistory(newHistory);
    const emitData: Request[] = newHistory.map((message) => ({
      content: message.fragments
        .filter((fragment) => fragment.type === "text")
        .map((data) => (data as TextFragment).text)
        .join(" "),
      role: message.senderRole,
    }));
    setGenerating(true);
    io.emit("execute", { messages: emitData });
  };

  const demoMessageClickHandler = (message: string) => {
    const msg: Message = {
      senderRole: "user",
      fragments: [
        {
          type: "text",
          text: message,
        },
      ],
      decision: [],
    };
    setMessageHistory([msg]);
    onClickHandler(msg);
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
          {currentMessage.length > 1 && (
            <MessageContainer
              hideDecision
              message={{
                fragments: [{ type: "text", text: `${currentMessage} ...` }],
                senderRole: "system",
                decision: [],
              }}
            />
          )}
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
            disabled={generating}
            onKeyDown={(e) => {
              if (e.code === "Enter") {
                const data: Message = {
                  fragments: [{ type: "text", text: input }],
                  senderRole: "user",
                  decision: [],
                };
                onClickHandler(data);
              }
            }}
          />
          <button
            disabled={generating || input.length === 0}
            onClick={() => {
              const data: Message = {
                fragments: [{ type: "text", text: input }],
                senderRole: "user",
                decision: [],
              };
              onClickHandler(data);
            }}
            className="bg-secondary-200 min-w-[80px] rounded-lg h-full border-2 border-secondary-200 p-4 text-center duration-200 hover:bg-secondary-100 disabled:opacity-0"
          >
            Send
          </button>
        </div>
      </div>
    </WrapperContainer>
  );
}

export default App;
