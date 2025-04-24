import { LogoTelegram } from "@gravity-ui/icons";
import { Button, Flex, Icon, TextArea } from "@gravity-ui/uikit";
import block from "bem-cn-lite";
import { Message } from "../../shared/types";
import { useState } from "react";
import './ChatInput.scss';

const b = block('chat-input');

interface ChatInputProps {
    addNewMessage: (message: Message) => void;
}

export const ChatInput = ({ addNewMessage }: ChatInputProps) => {
    const [value, setValue] = useState<string>('');

    const sendMessage = () => {
        if (value.trim()) {
            addNewMessage({ direction: 'user', text: value.trim() });
            setValue('');
        }
    };

    // Обработчик нажатия клавиши
    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault(); // исключить разрыв строки в TextArea
            sendMessage();
        }
    };

    return (
        <div className={b()}>
            <Flex gap={2} className={b('input-container')}>
                <TextArea
                    minRows={1}
                    maxRows={4}
                    placeholder="Напишите роботу-помощнику"
                    size="m"
                    value={value}
                    onChange={(e) => { setValue(e.target.value); }}
                    onKeyDown={handleKeyDown}
                    className={b('textarea')}
                />
                <Button 
                    size="m" 
                    className={b('button')} 
                    pin="circle-circle" 
                    onClick={sendMessage}
                    view="action"
                >
                    <Icon data={LogoTelegram} size={14} />
                </Button>
            </Flex>
        </div>
    );
}
