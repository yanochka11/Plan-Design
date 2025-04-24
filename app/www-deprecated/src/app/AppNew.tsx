import React, { useState } from 'react';
import './Appnew.scss';
import { Card, Flex, Text } from '@gravity-ui/uikit';
import { MonacoEditor } from '../entities/MonacoEditor';
import block from "bem-cn-lite";
import Scene3D from '../entities/Scene/3dScene/Scene3D';

// {
//     "objects": [
//         {
//             "name": "Sofa",
//             "size": { "length": 2.0, "width": 0.9 },
//             "position": { "x": 2.2, "y": 0.45 }
//         },
//         {
//             "name": "Coffee Table",
//             "size": { "length": 1.2, "width": 0.6 },
//             "position": { "x": 2.2, "y": 2.8 }
//         },
//         {
//             "name": "TV Stand",
//             "size": { "length": 1.8, "width": 0.5 },
//             "position": { "x": 2.2, "y": 5.35 }
//         },
//         {
//             "name": "Armchair",
//             "size": { "length": 0.8, "width": 0.8 },
//             "position": { "x": 0.8, "y": 4.0 }
//         },
//         {
//             "name": "Bookshelf",
//             "size": { "length": 0.4, "width": 1.5 },
//             "position": { "x": 4.2, "y": 4.0 }
//         }
//     ]
// }

const b = block('app');

const App: React.FC = () => {
    const [jsonData, setJsonData] = useState<any>(null); // Состояние для хранения данных из JSON
    const [roomSize, setRoomSize] = useState<{ width: number; height: number }>({ width: 7.2, height: 4.0 });

    const handleSaveRoomSize = (width: number, height: number) => {
        setRoomSize({ width, height });
    };

    const handleFileUpload = (fileContent: string) => {
        try {
            const parsedData = JSON.parse(fileContent);
            setJsonData(parsedData);
        } catch (e) {
            alert('Ошибка при чтении файла: файл должен быть в формате JSON.');
        }
    };


    return (
        <Flex className={b()} gap={2}>
            {/* <MonacoEditor jsonData={jsonData} setJsonData={setJsonData} handleSaveRoomSize={handleSaveRoomSize} handleFileUpload={handleFileUpload} roomSize={roomSize} /> */}
            {/* <Card className={b('scene-card')}>
                <Flex className={b('scene')} justifyContent="center" alignItems="center" direction="column" gap={2}>
                    <Text variant="subheader-2">План комнаты</Text>
                    <div className={b('room')}>
                        <RoomLayout data={jsonData} roomWidth={roomSize.width}
                            roomHeight={roomSize.height} />
                    </div>

                </Flex>
            </Card> */}
            {/* <Scene3D /> */}
                
        </Flex>
    );
};

export default App;