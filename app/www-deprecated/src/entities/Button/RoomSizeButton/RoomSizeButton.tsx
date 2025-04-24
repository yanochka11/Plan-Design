import { Card, Flex, TextInput, Text } from "@gravity-ui/uikit"
import block from "bem-cn-lite";
import './RoomSizeButton.scss';

const b = block('room-size-button');

interface RoomResizeButtonProps {changeXValue: (arg1: string) => void, changeYValue: (arg1: string) => void, changeZValue: (arg1: string) => void}

export const RoomSizeButton = ({changeXValue, changeYValue, changeZValue}: RoomResizeButtonProps) => {
    return (
        <Card className={b()}>
            <Flex direction="column" gap={2}>
                <Flex alignItems="center" gap={2}>
                    <Text variant="subheader-1">X</Text>
                    <TextInput defaultValue="0" onChange={(text) => {text.stopPropagation(); changeXValue(text.currentTarget.value)}}/>
                </Flex>
                <Flex alignItems="center" gap={2}>
                    <Text variant="subheader-1">Y</Text>
                    <TextInput defaultValue="0" onChange={(text) => {text.stopPropagation(); changeYValue(text.currentTarget.value)}}/>
                </Flex>
                <Flex alignItems="center" gap={2}>
                    <Text variant="subheader-1">Z</Text>
                    <TextInput defaultValue="0" onChange={(text) => {text.stopPropagation(); changeZValue(text.currentTarget.value)}}/>
                </Flex>
            </Flex>
        </Card>

    )
}