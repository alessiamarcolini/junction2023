import { Sender } from "./types";

export interface MessageBase {
  type: "text" | "image" | "html" | "error";
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

export interface ErrorFragment extends MessageBase {
  type: "error";
}

export type MessageFragment = TextFragment | ImageFragment | HtmlFragment | ErrorFragment;

export type Message = {
  fragments: MessageFragment[];
  senderRole: Sender;
  decision: string[];
};
