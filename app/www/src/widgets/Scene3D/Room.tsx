import React, { useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Text } from '@react-three/drei';
import { SceneObject } from './types/SceneTypes';
import MockObject from './MockObject';

interface RoomProps {
    sceneObjects: SceneObject[];
    roomWidth: number;
    roomDepth: number;
    roomHeight: number;
}

const Room: React.FC<RoomProps> = ({ sceneObjects, roomWidth, roomDepth, roomHeight }) => {
    return (
        <Canvas
            style={{ width: '100%', height: '100vh' }}
            shadows
            camera={{ position: [roomWidth / 2, -2, roomHeight * 2], fov: 75 }}
        >
            <color attach="background" args={['#f0f0f0']} />
            <ambientLight intensity={0.5} />
            <directionalLight position={[10, 10, 5]} intensity={1} castShadow />

            {/* Настройка камеры */}
            <PerspectiveCamera
                makeDefault
                position={[roomWidth / 2, -2, roomHeight * 2]}
                fov={75}
            />
            <OrbitControls target={[roomWidth / 2, roomDepth / 2, roomHeight / 2]} />

            {/* Пол */}
            <mesh position={[roomWidth / 2, roomDepth / 2, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
                <planeGeometry args={[roomWidth, roomDepth]} />
                <meshStandardMaterial color="#e0e0e0" />
            </mesh>

            {/* Северная стена */}
            <mesh position={[roomWidth / 2, roomDepth, roomHeight / 2]} rotation={[0, 0, 0]} receiveShadow>
                <planeGeometry args={[roomWidth, roomHeight]} />
                <meshStandardMaterial color="#f5f5f5" />
            </mesh>

            {/* Южная стена */}
            <mesh position={[roomWidth / 2, 0, roomHeight / 2]} rotation={[0, Math.PI, 0]} receiveShadow>
                <planeGeometry args={[roomWidth, roomHeight]} />
                <meshStandardMaterial color="#f5f5f5" />
            </mesh>

            {/* Восточная стена */}
            <mesh position={[roomWidth, roomDepth / 2, roomHeight / 2]} rotation={[0, -Math.PI / 2, 0]} receiveShadow>
                <planeGeometry args={[roomDepth, roomHeight]} />
                <meshStandardMaterial color="#f0f0f0" />
            </mesh>

            {/* Западная стена */}
            <mesh position={[0, roomDepth / 2, roomHeight / 2]} rotation={[0, Math.PI / 2, 0]} receiveShadow>
                <planeGeometry args={[roomDepth, roomHeight]} />
                <meshStandardMaterial color="#f0f0f0" />
            </mesh>

            {/* Объекты в комнате */}
            {sceneObjects.map((obj) => (
                <MockObject key={obj.new_object_id} object={obj} />
            ))}
        </Canvas>
    );
};

export default Room;
