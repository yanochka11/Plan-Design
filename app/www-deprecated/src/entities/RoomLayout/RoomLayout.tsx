import React from 'react';
import { Stage, Layer, Rect, Text, Line } from 'react-konva';

interface RoomLayoutProps {
    data: {
        objects: {
            name: string;
            size: { length: number; width: number };
            position: { x: number; y: number };
        }[];
    };
    roomWidth: number; // Ширина комнаты в метрах
    roomHeight: number; // Высота комнаты в метрах
}

export const RoomLayout: React.FC<RoomLayoutProps> = ({ data, roomHeight, roomWidth }) => {
    const scale = 100; // 100 пикселей на метр

    // Конвертация метров в пиксели
    const meterToPixel = (meters: number) => {
        return meters * scale;
    };

    const pixelWidth = meterToPixel(roomWidth);
    const pixelHeight = meterToPixel(roomHeight);

    // Функция для инвертирования координаты Y
    const invertY = (y: number) => pixelHeight - y;

    // Генерация линий сетки и подписей осей
    const gridLines = [];
    const axisLabels = [];

    // Вертикальные линии (ось X)
    for (let x = 0; x <= pixelWidth / scale; x++) {
        gridLines.push(
            <Line
                key={`vline-${x}`}
                points={[x * scale, 0, x * scale, pixelHeight]}
                stroke="lightgray"
                strokeWidth={1}
            />
        );
        axisLabels.push(
            <Text key={`xlabel-${x}`} x={x * scale + 5} y={pixelHeight - 20} text={`${x}m`} fontSize={10} />
        );
    }

    // Горизонтальные линии (ось Y)
    for (let y = 0; y <= pixelHeight / scale; y++) {
        gridLines.push(
            <Line
                key={`hline-${y}`}
                points={[0, y * scale, pixelWidth, y * scale]}
                stroke="lightgray"
                strokeWidth={1}
            />
        );
        axisLabels.push(
            <Text key={`ylabel-${y}`} x={5} y={invertY(y * scale) + 5} text={`${y}m`} fontSize={10} />
        );
    }

    return (
        <Stage width={pixelWidth} height={pixelHeight} style={{ marginTop: 20 }}>
            <Layer>
                {/* Контур комнаты */}
                <Rect
                    x={0}
                    y={0}
                    width={pixelWidth}
                    height={pixelHeight}
                    stroke="black"
                    strokeWidth={2}
                />

                {/* Линии сетки */}
                {gridLines}

                {/* Ось X */}
                <Line
                    points={[0, pixelHeight, pixelWidth, pixelHeight]}
                    stroke="black"
                    strokeWidth={2}
                />
                {/* Ось Y */}
                <Line
                    points={[0, 0, 0, pixelHeight]}
                    stroke="black"
                    strokeWidth={2}
                />

                {/* Подписи осей */}
                {axisLabels}

                {/* Названия осей */}
                <Text x={pixelWidth - 20} y={pixelHeight - 10} text="X" fontSize={12} fill="black" />
                <Text x={10} y={10} text="Y" fontSize={12} fill="black" />

                {/* Отрисовка объектов */}
                <Text x={pixelWidth / 2 - 30} y={10} text="North Wall" fontSize={12} fill="black" />
                <Text x={pixelWidth - 60} y={pixelHeight / 2 - 10} text="East Wall" fontSize={12} fill="black" />
                <Text x={pixelWidth / 2 - 30} y={pixelHeight - 20} text="South Wall" fontSize={12} fill="black" />
                <Text x={10} y={pixelHeight / 2 - 10} text="West Wall" fontSize={12} fill="black" />

                {data && data.objects.map((obj, index) => {
                    const x = meterToPixel(obj.position.x);
                    const y = invertY(meterToPixel(obj.position.y + obj.size.width)); // Инвертируем Y и учитываем высоту объекта
                    const width = meterToPixel(obj.size.length);
                    const height = meterToPixel(obj.size.width);

                    return (
                        <React.Fragment key={index}>
                            <Rect
                                x={x}
                                y={y}
                                width={width}
                                height={height}
                                fill="lightblue"
                                stroke="black"
                            />
                            <Text x={x + 5} y={y + 5} text={obj.name} fontSize={10} />
                        </React.Fragment>
                    );
                })}
            </Layer>
        </Stage>
    );
};