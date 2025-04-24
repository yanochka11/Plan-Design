import { Flex, User } from "@gravity-ui/uikit"
import { MessageDirection } from "../../types"

interface AvatarProps {
    direction: MessageDirection;
}

export const Avatar = ({ direction }: AvatarProps) => {
    return (
        <Flex direction={"row"}>
            <User avatar={{ text: direction === 'robot' ? 'Charles Darwin' : 'Вы', theme: 'normal' }} size="s" />
        </Flex>
    )
}