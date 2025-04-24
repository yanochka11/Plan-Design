import React, { useState } from 'react';
import { Flex, Text, TextInput, Button, Card } from '@gravity-ui/uikit';
import block from 'bem-cn-lite';
import './RoomSizeInput.scss';

interface RoomSizeInputProps {
    onSave: (width: number, height: number) => void;
    roomSize: { width: number; height: number }
}

const b = block('room-size-input')

export const RoomSizeInput: React.FC<RoomSizeInputProps> = ({ onSave, roomSize }) => {
    const [width, setWidth] = useState<string>(String(roomSize.width));
    const [height, setHeight] = useState<string>(String(roomSize.height));

    const handleSave = () => {
        const widthNumber = parseFloat(width);
        const heightNumber = parseFloat(height);

        if (!isNaN(widthNumber) && !isNaN(heightNumber)) {
            onSave(widthNumber, heightNumber);
        } else {
            alert('Пожалуйста, введите корректные числа для ширины и высоты.');
        }
    };

    return (
        <Card className={b()}>
            <Flex direction="column" gap={4} alignItems="center" justifyContent="center" className={b('container')}>
                <Text variant="subheader-2">Размер комнаты</Text>
                <Flex gap={2} direction="column" className={b('inputs')}>
                    <TextInput
                        type="number"
                        value={width}
                        onChange={(e: any) => setWidth(e.target.value)}
                        placeholder="Ширина (м)"
                        className={b('input')}
                    />
                    <TextInput
                        type="number"
                        value={height}
                        onChange={(e: any) => setHeight(e.target.value)}
                        placeholder="Высота (м)"
                        className={b('input')}
                    />
                    <Button onClick={handleSave}>Сохранить</Button>
                </Flex>
            </Flex>
        </Card>

    );
};