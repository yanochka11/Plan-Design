import { Comments } from "@gravity-ui/icons";
import { Button, Flex, Icon } from "@gravity-ui/uikit"
import block from "bem-cn-lite";
import './ChatButton.scss';

const b = block('chat-button');
export const ChatButton = ({onClick}: {onClick: (e: React.MouseEvent<HTMLAnchorElement | HTMLButtonElement>) => void}) => {
    return <Flex className={b()}>
        <Button size="xl" pin="circle-circle" onClick={(e) => onClick(e)}><Icon data={Comments} ></Icon></Button>
    </Flex>
}