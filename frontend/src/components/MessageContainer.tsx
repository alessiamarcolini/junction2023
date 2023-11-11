import { Message } from "../Messages";
import { SystemMessageContainer } from "./SystemMessageContainer";
import { UserMessageContainer } from "./UserMessageContainer";

interface MessageContainerProps {
  message: Message;
  hideDecision?: boolean;
}

export const MessageContainer = ({
  message,
  hideDecision = false,
}: MessageContainerProps) => {
  return message.senderRole === "system" ? (
    <SystemMessageContainer message={message} hideDecision={hideDecision} />
  ) : (
    <UserMessageContainer message={message} />
  );
};
