import { Message } from "../Messages";

interface UserMessageContainerProps {
  message: Message;
}

export const UserMessageContainer = ({
  message,
}: UserMessageContainerProps) => {
  return (
    <div className="justify-items-end grid h-fit w-full">
      <div className="flex items-end">
        <div className="bg-secondary-200 shadow-secondary-300 text-secondary-100 ml-16 rounded-xl p-4 m-4 shadow-lg">
          {message.fragments.map((fragment, idx) => {
            return fragment.type === "text" ? (
              <div key={idx}>{fragment.text}</div>
            ) : null;
          })}
        </div>
      </div>
    </div>
  );
};
