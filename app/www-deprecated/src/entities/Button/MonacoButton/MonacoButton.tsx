import { ChevronRight } from "@gravity-ui/icons";
import { Button, Flex, Icon } from "@gravity-ui/uikit"
import block from "bem-cn-lite";
import './MonacoButton.scss';

const b = block('monaco-button');
export const MonacoButton = ({onClick}: {onClick: (e: React.MouseEvent<HTMLAnchorElement | HTMLButtonElement>) => void}) => {
    return <Flex className={b()}>
        <Button size="xl" pin="circle-circle" onClick={(e) => onClick(e)}><Icon data={ChevronRight} size={20}/></Button>
    </Flex>
}