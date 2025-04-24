import { Flex, Loader, Text } from "@gravity-ui/uikit";
import block from "bem-cn-lite";
import './Chat.scss';
import { ChatInput, MessageList } from "../../features";
import { useCallback, useEffect, useState } from "react";
import { Message } from "../../shared/types";
import { getMessageList } from "./utils";
import { useNavigate } from "react-router-dom";

const b = block('chat');

export const Chat = () => {
    const [messages, setMessages] = useState<Message[]>(() => getMessageList());
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const addNewMessage = useCallback((message: Message) => {
        setMessages((prevMessages) => [...prevMessages, message]);

        const storedObject = JSON.parse(localStorage.getItem('design') || '{}');
        let updatedObject = { ...storedObject };

        if (message.direction === 'user' && message.text) {
            let newRobotMessage = null;

            updatedObject.description = message.text;
            setIsLoading(true);

            setTimeout(() => {
                navigate('/model/2d');
            }, 10000);

            localStorage.setItem('design', JSON.stringify(updatedObject));

            if (newRobotMessage) {
                setTimeout(() => {
                    setMessages((prevMessages) => [...prevMessages, newRobotMessage]);
                }, 1000);
            }
        }
    }, [navigate]);

    useEffect(() => {
        const storedObject = JSON.parse(localStorage.getItem('design') || '{}');
        let updatedObject = { ...storedObject };

        if (updatedObject.description) {
            navigate('/model/2d');
        }
    }, [navigate]);

    return (
        <Flex className={b()} direction="column">
            <div className={b('messages-container')}>
                <MessageList messages={messages} />
                {isLoading && (
                    <div className={b('loader-container')}>
                        <Flex gap={2} alignItems="center" className={b('loader')}>
                            <Text variant="caption-2">Генерируем</Text>
                            <Loader size="s" />
                        </Flex>
                    </div>
                )}
            </div>
            <ChatInput addNewMessage={addNewMessage} />
        </Flex>
    );
}
