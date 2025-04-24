import { Button, Card, Flex, Icon, Text, TextArea } from "@gravity-ui/uikit";
import block from 'bem-cn-lite';
import './ChatWidget.scss';
import { FileArrowRight, Xmark } from "@gravity-ui/icons";
import { MessageList } from "./MessageList/MessageList";
import { useState } from "react";

const b = block('chat-widget');

interface ChatWidgetProps {
    onCloseChat: () => void;
    messagesList: {id: string, text: string, isUser: boolean}[];
    addMessage: (arg1: {id: string, text: string, isUser: boolean}) => void;
}

export const ChatWidget = ({ onCloseChat, messagesList, addMessage }: ChatWidgetProps) => {
    const [textAreaContent, setTextAreaContent] = useState("");

    const handleSendMessage = () => {
        if (textAreaContent.trim() === "") return;

        const userMessage = {
            id: String(crypto.randomUUID()),
            text: textAreaContent,
            isUser: true
        };
        
        addMessage(userMessage);

        setTimeout(() => {
            const botResponse = {
                id: String(crypto.randomUUID()),
                text: `Ваш запрос принят в обработку, процесс генерации начался, ваш тикет ${crypto.randomUUID()}`,
                isUser: false
            };
            addMessage(botResponse);
        }, 2000);

        setTextAreaContent("");
    };

    return (
        <Card className={b()}>
            <Flex className={b('chat-container')} direction="column">
                <Flex className={b('chat-widget-header')} alignItems="center" gap={3} justifyContent="space-between">
                    <Flex gap={3} alignItems="center">
                        <Text variant="header-1" color="secondary">Chat with AI</Text>
                        <div className={b('ai-status')} />
                    </Flex>
                    <Flex onClick={onCloseChat} className={b('close')}>
                        <Icon data={Xmark} size={20} />
                    </Flex>
                </Flex>
                <MessageList messages={messagesList} />
                <Flex className={b('message-footer')} gap={3} alignItems="center">
                    <TextArea
                        maxRows={10}
                        className={b('text-area')}
                        minRows={2}
                        value={textAreaContent}
                        onChange={(text) => setTextAreaContent(text.currentTarget.value)}
                        onKeyDown={(event) => {
                            if (event.key === 'Enter' && !event.shiftKey) {
                                event.preventDefault();
                                handleSendMessage();
                            }
                        }}
                    />
                    <Button
                        pin="circle-circle"
                        size="l"
                        view="flat-success"
                        className={b('button')}
                        onClick={handleSendMessage}
                    >
                        <Icon data={FileArrowRight} />
                    </Button>
                </Flex>
            </Flex>
        </Card>
    );
};