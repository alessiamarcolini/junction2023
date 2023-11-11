import { Sender } from "./types";

export interface MessageBase {
  type: "text" | "image" | "html";
}

export interface TextFragment extends MessageBase {
  type: "text";
  text: string;
}

export interface ImageFragment extends MessageBase {
  type: "image";
  src: string;
}

export interface HtmlFragment extends MessageBase {
  type: "html";
  src: string;
}

export type MessageFragment = TextFragment | ImageFragment | HtmlFragment;

export type Message = {
  fragments: MessageFragment[];
  senderRole: Sender;
  decision: string[];
};
