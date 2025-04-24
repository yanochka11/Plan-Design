import { Flex, Text } from "@gravity-ui/uikit"
import block from "bem-cn-lite";
import { MessageDirection } from "../../types";
import './Message.scss';

interface CommentProps {
    direction: MessageDirection;
    text: string;
}


const b = block('comment');

export const Message = ({ direction, text }: CommentProps) => {
    return (
        <div className={b({ direction })}>
            {direction === 'robot' && (
                <div className={b('tail')} />
            )}
            <Text variant="body-2">{text}</Text>
            {direction === 'user' && (
                <div className={b('tail')} />
            )}
        </div>
    )
}
