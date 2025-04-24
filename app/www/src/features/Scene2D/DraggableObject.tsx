import { useRef, useEffect } from "react";
import { useDrop } from "react-dnd";
import { CloseButton } from "./CloseButton";

interface SizeInMeters {
    length: number;
    width: number;
    height: number;
}

interface Position {
    x: number;
    y: number;
    z: number;
}

interface InputObject {
    new_object_id: string;
    size_in_meters: SizeInMeters;
    position: Position;
    rotation_z: number;
    style: string;
    material: string;
    color: string;
}

interface SVGObjectCoordinates {
    x: number;
    y: number;
    width: number;
    height: number;
}

interface PlainSVGObjectData {
    id: string;
    label: string;
    coordinates: SVGObjectCoordinates;
    style: string;
    material: string;
    color: string;
}

interface PlainSVGObjectDataWithRotation extends PlainSVGObjectData {
    rotation: number;
    furnitureType: string;
}

export interface RoomLayoutProps {
    initialObjects: InputObject[];
    updateJson: (value: string) => void;
}

interface ColorsDisctionary {
    [key: string]: string;
}

// Словарь цветов
export const colors: ColorsDisctionary = {
    "TV stand": "#FF0000",
    "bar counter": "#0000FF",
    "bench": "#FFFF00",
    "bookshelf": "#FFBFBF",
    "cabinet": "#00FF00",
    "chair": "#FFA500",
    "chair-bed": "#40E0D0",
    "coffee table": "#272643",
    "desk": "#FFD9BF",
    "dining table": "#8B00FF",
    "fireplace": "#FF9400",
    "floor lamp": "#5500FF",
    "floor plant": "#29922C",
    "floor vase": "#FF6347",
    "kitchen island": "#ADFF2F",
    "modular kitchen": "#FF7F50",
    "ottoman": "#AFCC43",
    "rocking chair": "#FF8C00",
    "rug": "#BAE8E8",
    "shelves": "#C71585",
    "side table": "#00BFFF",
    "sideboard": "#DA70D6",
    "sofa": "#FF00FF",
    "stool": "#DC143C",
    "wardrobe": "#552743",
    "armchair": "#4A2714",
    "window": "#000000",
};

export const DraggableObject: React.FC<{
    obj: PlainSVGObjectDataWithRotation;
    index: number;
    roomHeight: number;
    roomWidth: number;
    bounds: { minX: number; maxX: number; minY: number; maxY: number };
    onMove: (id: string, x: number, y: number) => void;
    onUpdate: (id: string, updates: Partial<PlainSVGObjectDataWithRotation>) => void;
    onSelect: (id: string) => void;
    onDeselect: () => void;
    onEndAction: (id: string) => void;
    isSelected: boolean;
    getMouseSVGCoordinates: (clientX: number, clientY: number) => { x: number; y: number };
    isInsideRoom: (x: number, y: number, width: number, height: number, rotation: number) => boolean;
    onDeleteObject?: (id: string) => void;
}> = ({
    obj,
    bounds,
    onMove,
    onUpdate,
    onSelect,
    onDeselect,
    onEndAction,
    isSelected,
    getMouseSVGCoordinates,
    isInsideRoom,
    onDeleteObject
}) => {
        const ref = useRef<SVGGElement>(null);

        // Добавляем поддержку drag-and-drop для каждого объекта
        const [, drop] = useDrop(() => ({
            accept: "object",
            // Прозрачный обработчик, который просто пропускает событие дальше
            hover: (item, monitor) => {
                // Позволяем событию всплывать дальше
            },
            // Предотвращаем обработку здесь, чтобы событие дошло до родительского компонента
            canDrop: () => false
        }));

        // Инициализируем ref для drag-n-drop
        useEffect(() => {
            if (ref.current) {
                drop(ref.current);
            }
        }, [drop]);

        // Перемещение объекта
        const handleMouseDown = (e: React.MouseEvent) => {
            if (e.button !== 0) return;
            e.stopPropagation();

            // Выбираем объект при начале перетаскивания
            onSelect(obj.id);

            const startCoords = { ...obj.coordinates };
            const { x: startX, y: startY } = getMouseSVGCoordinates(e.clientX, e.clientY);
            const offsetX = startX - obj.coordinates.x;
            const offsetY = startY - obj.coordinates.y;

            const handleMouseMove = (moveEvent: MouseEvent) => {
                const { x: currentX, y: currentY } = getMouseSVGCoordinates(moveEvent.clientX, moveEvent.clientY);

                let newX = currentX - offsetX;
                let newY = currentY - offsetY;

                // Проверяем, находится ли объект полностью внутри комнаты
                if (isInsideRoom(newX, newY, obj.coordinates.width, obj.coordinates.height, obj.rotation)) {
                    onMove(obj.id, newX, newY);
                }
            };

            const handleMouseUp = () => {
                document.removeEventListener('mousemove', handleMouseMove);
                document.removeEventListener('mouseup', handleMouseUp);
                onEndAction(obj.id);
            };

            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
        };

        // Изменение размера
        const handleResize = (e: MouseEvent, corner: string, initialData: {
            width: number;
            height: number;
            x: number;
            y: number;
            mouseX: number;
            mouseY: number;
            rotation: number;
        }) => {
            const { x: currentX, y: currentY } = getMouseSVGCoordinates(e.clientX, e.clientY);

            const dx = currentX - initialData.mouseX;
            const dy = currentY - initialData.mouseY;

            let newWidth = initialData.width;
            let newHeight = initialData.height;
            let newX = initialData.x;
            let newY = initialData.y;

            const minSize = 20; // Минимальный размер в пикселях

            switch (corner) {
                case 'topLeft':
                    newWidth = Math.max(minSize, initialData.width - dx);
                    newHeight = Math.max(minSize, initialData.height - dy);
                    newX = initialData.x - (dx / 2);
                    newY = initialData.y - (dy / 2);
                    break;
                case 'topRight':
                    newWidth = Math.max(minSize, initialData.width + dx);
                    newHeight = Math.max(minSize, initialData.height - dy);
                    newX = initialData.x + (dx / 2);
                    newY = initialData.y - (dy / 2);
                    break;
                case 'bottomLeft':
                    newWidth = Math.max(minSize, initialData.width - dx);
                    newHeight = Math.max(minSize, initialData.height + dy);
                    newX = initialData.x - (dx / 2);
                    newY = initialData.y + (dy / 2);
                    break;
                case 'bottomRight':
                    newWidth = Math.max(minSize, initialData.width + dx);
                    newHeight = Math.max(minSize, initialData.height + dy);
                    newX = initialData.x + (dx / 2);
                    newY = initialData.y + (dy / 2);
                    break;
            }

            // Проверяем, находится ли объект после изменения размера внутри комнаты
            if (isInsideRoom(newX, newY, newWidth, newHeight, initialData.rotation)) {
                onUpdate(obj.id, {
                    coordinates: {
                        width: newWidth,
                        height: newHeight,
                        x: newX,
                        y: newY
                    }
                });
            }
        };

        // Вращение
        const handleRotate = (e: MouseEvent, initialData: {
            rotation: number;
            centerX: number;
            centerY: number;
            startAngle: number;
            width: number;
            height: number;
        }) => {
            const { x: currentX, y: currentY } = getMouseSVGCoordinates(e.clientX, e.clientY);

            const currentAngle = Math.atan2(
                currentY - initialData.centerY,
                currentX - initialData.centerX
            ) * (180 / Math.PI);

            let newRotation = initialData.rotation + (currentAngle - initialData.startAngle);
            newRotation = ((newRotation % 360) + 360) % 360;

            // Проверяем, находится ли объект после вращения внутри комнаты
            if (isInsideRoom(
                initialData.centerX,
                initialData.centerY,
                initialData.width,
                initialData.height,
                newRotation
            )) {
                onUpdate(obj.id, { rotation: newRotation });
            }
        };

        // Удаление объекта
        const handleDelete = () => {
            if (onDeleteObject) {
                onDeleteObject(obj.id);
            } else {
                onDeselect(); // Если функция удаления не предоставлена, просто снимаем выделение
            }
        };

        const x = obj.coordinates.x - obj.coordinates.width / 2;
        const y = obj.coordinates.y - obj.coordinates.height / 2;
        const centerX = obj.coordinates.x;
        const centerY = obj.coordinates.y;

        return (
            <g
                ref={ref}
                transform={`rotate(${-obj.rotation} ${centerX} ${centerY})`}
                style={{ cursor: 'move', pointerEvents: 'all' }}
                onMouseDown={handleMouseDown}
                onClick={(e) => {
                    e.stopPropagation();
                    onSelect(obj.id);
                }}
            >
                <rect
                    x={x}
                    y={y}
                    width={obj.coordinates.width}
                    height={obj.coordinates.height}
                    fill={obj.color}
                    fillOpacity={0.3}
                    stroke={isSelected ? "#00FF00" : obj.color}
                    strokeWidth={isSelected ? 3 : 2}
                    strokeDasharray={isSelected ? "5,5" : "none"}
                    style={{ pointerEvents: "visiblePainted" }} // Важно для корректной обработки событий
                />
                <text
                    x={centerX}
                    y={centerY}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fill="black"
                    fontSize="12"
                    pointerEvents="none"
                >
                    {obj.furnitureType}
                </text>

                {isSelected && (
                    <>
                        <CloseButton
                            x={x + obj.coordinates.width + 20}
                            y={y - 20}
                            onClick={handleDelete}
                        />

                        {/* Углы для изменения размера */}
                        {['topLeft', 'topRight', 'bottomLeft', 'bottomRight'].map((corner) => {
                            const cornerX = corner.includes('Right') ? x + obj.coordinates.width : x;
                            const cornerY = corner.includes('Bottom') ? y + obj.coordinates.height : y;
                            const cursor = corner === 'topLeft' || corner === 'bottomRight' ? 'nwse-resize' : 'nesw-resize';

                            return (
                                <circle
                                    key={corner}
                                    cx={cornerX}
                                    cy={cornerY}
                                    r={6}
                                    fill="white"
                                    stroke="#00FF00"
                                    strokeWidth={2}
                                    cursor={cursor}
                                    onMouseDown={(e) => {
                                        e.stopPropagation();
                                        const initialData = {
                                            width: obj.coordinates.width,
                                            height: obj.coordinates.height,
                                            x: obj.coordinates.x,
                                            y: obj.coordinates.y,
                                            mouseX: getMouseSVGCoordinates(e.clientX, e.clientY).x,
                                            mouseY: getMouseSVGCoordinates(e.clientX, e.clientY).y,
                                            rotation: obj.rotation
                                        };

                                        const handleMouseMove = (moveEvent: MouseEvent) => {
                                            handleResize(moveEvent, corner, initialData);
                                        };

                                        const handleMouseUp = () => {
                                            document.removeEventListener('mousemove', handleMouseMove);
                                            document.removeEventListener('mouseup', handleMouseUp);
                                            onEndAction(obj.id);
                                        };

                                        document.addEventListener('mousemove', handleMouseMove);
                                        document.addEventListener('mouseup', handleMouseUp);
                                    }}
                                />
                            );
                        })}

                        {/* Контрол вращения */}
                        <line
                            x1={centerX}
                            y1={y - 20}
                            x2={centerX}
                            y2={y}
                            stroke="#00FF00"
                            strokeWidth={2}
                            pointerEvents="none"
                        />
                        <circle
                            cx={centerX}
                            cy={y - 20}
                            r={8}
                            fill="white"
                            stroke="#00FF00"
                            strokeWidth={2}
                            cursor="grab"
                            onMouseDown={(e) => {
                                e.stopPropagation();
                                const startAngle = Math.atan2(
                                    getMouseSVGCoordinates(e.clientX, e.clientY).y - centerY,
                                    getMouseSVGCoordinates(e.clientX, e.clientY).x - centerX
                                ) * (180 / Math.PI);

                                const initialData = {
                                    rotation: obj.rotation,
                                    centerX,
                                    centerY,
                                    startAngle,
                                    width: obj.coordinates.width,
                                    height: obj.coordinates.height
                                };

                                const handleMouseMove = (moveEvent: MouseEvent) => {
                                    handleRotate(moveEvent, initialData);
                                };

                                const handleMouseUp = () => {
                                    document.removeEventListener('mousemove', handleMouseMove);
                                    document.removeEventListener('mouseup', handleMouseUp);
                                    onEndAction(obj.id);
                                };

                                document.addEventListener('mousemove', handleMouseMove);
                                document.addEventListener('mouseup', handleMouseUp);
                            }}
                        />
                    </>
                )}
            </g>
        );
    };
