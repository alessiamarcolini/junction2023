import { useState } from "react";
import { Message } from "./Messages";
import { MessageContainer } from "./components/MessageContainer";
import { Spinner } from "./components/Spinner";

function App() {
  const [input, setInput] = useState<string>("");
  const messages: Message[] = [
    {
      fragments: [
        {
          type: "text",
          text: "This is a very nice response",
        },
      ],
      owner: "user",
    },
    {
      fragments: [
        {
          type: "text",
          text: "It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like).",
        },
        {
          type: "image",
          src: "https://cdn.builtin.com/sites/www.builtin.com/files/styles/ckeditor_optimize/public/inline-images/2_boxplots.jpg",
        },
        {
          type: "text",
          text: "This is a very nice text message",
        },
      ],
      owner: "bot",
      decision: "yolo",
    },
    {
      fragments: [
        {
          type: "text",
          text: "It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like).",
        },
        {
          type: "image",
          src: "https://www.shareicon.net/data/2017/03/07/880593_media_512x512.png",
        },
        {
          type: "text",
          text: "This is a very nice text message",
        },
      ],
      owner: "bot",
      decision: "yolo again",
    },
  ];
  const [messageHistory, setMessageHistory] = useState<Message[]>([]);

  return (
    <div className="text-secondary-300 bg-secondary-300 w-full grid justify-items-center h-screen">
      <div className="flex flex-col gap-4 w-full max-w-2xl bg-secondary-300 rounded-lg p-10 m-4 overflow-hidden">
        <div className="bg-secondary-100 flex flex-col w-full h-full rounded-lg overflow-scroll">
          {messageHistory.length === 0 && <div className='text-center w-full p-4'>Hello there, how can I help you?</div>}
          {messageHistory.map((message, idx) => (
            <MessageContainer message={message} key={idx} />
          ))}
          <Spinner message="76%" />
        </div>
        <div className="flex gap-4 w-full">
          <input
            className="shadow appearance-none border border-primary-400 h-full rounded-xl w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="Input..."
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            disabled={input.length === 0}
            onClick={() => {
              const data: Message = {
                fragments: [{ type: "text", text: input }],
                owner: 'user'
              };
            setMessageHistory([...messageHistory, data])
            }}
            className="bg-secondary-200 min-w-[80px] rounded-lg h-full p-4 text-center duration-200 hover:bg-secondary-100"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
