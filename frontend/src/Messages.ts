export interface MessageBase {
  type: "text" | "image";
}

export interface TextFragment extends MessageBase {
  type: "text";
  text: string;
}

export interface ImageFragment extends MessageBase {
  type: "image";
  src: string;
}

export type MessageFragment = TextFragment | ImageFragment

export type Message = {
  fragments: MessageFragment[],
  owner: 'bot' | 'user',
  decision?: string
}
