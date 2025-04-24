import { Flex, Text } from "@gravity-ui/uikit"
import block from 'bem-cn-lite';
import './MessageList.scss';

const b = block('message-list');

export const MessageList = ({messages}: {messages: {id: number | string, text: string, isUser: boolean}[]}) => {
    return (
        <Flex className={b()}>
            <Flex className={b('message-list-container')} direction="column" gap={2}>
                {messages.map((message, index) => {
                    return (
                        <Flex className={b('message', { isUser: (index % 2 === 1) })} key={message.id}>
                            <Text variant="body-2">
                                {message.text}
                            </Text>
                        </Flex>
                    )
                })}
            </Flex>

        </Flex>
    )
}