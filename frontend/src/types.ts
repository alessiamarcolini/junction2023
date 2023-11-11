export type Sender = "system" | "user";

export type Request = {
  message: string;
  sender: Sender;
};

export type Execution = {
  id: string;
  request: Request;
  status: "requested" | "scheduled" | "started" | "completed";
  progress: number | null;
};

export type TextReceivedEvent = {
  id: string;
  text: string;
}
