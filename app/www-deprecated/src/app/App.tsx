// import React, { useState } from 'react';
// import './styles/App.scss';
// import { SceneWidget } from '../widgets';
// import SceneOld from '../entities/Scene/SceneOld/SceneOld';
// import { Flex } from '@gravity-ui/uikit';
// import SceneOldPlain from '../entities/Scene/SceneOld/SceneOldPlain';

// const App: React.FC = () => {
//   const [is3D, set3D] = useState<boolean>(false);

//   return (
//     <Flex style={{ width: '100vw', height: '100vh' }}>
//       <SceneWidget is3D={is3D} changeDMode={() => { set3D(o => !o) }}>
//         {is3D ? <SceneOld key="3d" /> : <SceneOldPlain key="2d" />}
//       </SceneWidget>
//     </Flex>
//   );
// };

// export default App;

import React from 'react';
import './Appnew.scss';
import { Flex } from '@gravity-ui/uikit';
import block from "bem-cn-lite";

const b = block('app');

const App: React.FC = () => {
    return (

        <Flex className={b()} gap={2}>
            {/* <MonacoEditor jsonData={jsonData} setJsonData={setJsonData} handleSaveRoomSize={handleSaveRoomSize} handleFileUpload={handleFileUpload} roomSize={roomSize} />
            <Card className={b('scene-card')}>
                <Flex className={b('scene')} justifyContent="center" alignItems="center" direction="column" gap={2}>
                    <Text variant="subheader-2">План комнаты</Text>
                    <div className={b('room')}>
                        <RoomLayout data={jsonData} roomWidth={roomSize.width}
                            roomHeight={roomSize.height} />
                    </div>

                </Flex>
            </Card> */}

        </Flex>


    );
};

export default App;