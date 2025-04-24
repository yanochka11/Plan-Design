import { Button, Flex, Text } from "@gravity-ui/uikit"
import block from "bem-cn-lite";
import { ReactElement } from "react";
import './SceneWidget.scss'

const b = block('scene-widget');

interface SceneWidgetProps {
    is3D: boolean;
    changeDMode: () => void;
    children: ReactElement;
}

export const SceneWidget = ({ is3D, changeDMode,children }: SceneWidgetProps) => {
    return (
        <Flex className={b()}>
            <Button onClick={(e) => { e.stopPropagation(); changeDMode() }} className={b('threed-button')} size="xl">
                {is3D ? (<Text variant="subheader-2">2D</Text>) : (<Text variant="subheader-2">3D</Text>)}
            </Button>
            {children}
        </Flex>
    )
}