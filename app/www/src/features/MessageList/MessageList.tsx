import { type Message } from "../../shared/types";
import block from "bem-cn-lite";
import './MessageList.scss';
import { MessageWithAvatar } from "../../entities/MessageWithAvatar";
import { Flex } from "@gravity-ui/uikit";
import { useEffect, useRef } from "react";

const b = block('message-list');

interface MessageListProps {
    messages: Message[]
}

export const MessageList = ({ messages }: MessageListProps) => {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (containerRef.current) {
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
    }, [messages]);

    return (
        <div className={b()} ref={containerRef}>
            <div className={b('content')}>
                <Flex direction="column" gap={1}>
                    {messages.map(({ direction, text }: Message, index: number) => (
                        <MessageWithAvatar 
                            direction={direction} 
                            text={text} 
                            key={index}
                        />
                    ))}
                </Flex>
            </div>
        </div>
    );
}
