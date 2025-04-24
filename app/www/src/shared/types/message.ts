export type MessageDirection = "robot" | "user";

export interface Message {
    text: string;
    direction: MessageDirection;
}