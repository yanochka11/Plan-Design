import React, { useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { Text, Plane, OrbitControls } from '@react-three/drei';
import { Helpers, SceneLights } from './components';
import { TGLBModels } from './constants';

interface ModelProps {
    position: [number, number, number];
    size_in_meters: { length: number; width: number; height: number };
    name: string;
}

const Model: React.FC<ModelProps> = ({ position, size_in_meters, name }) => {
    useEffect(() => {
        // Placeholder effect if needed in the future
    }, [position, size_in_meters]);

    return (
        <>
            <mesh position={[position[0], position[1], position[2]]}>
                <boxGeometry args={[size_in_meters.length, size_in_meters.width, size_in_meters.height]} />
                <meshStandardMaterial color="lightblue" />
            </mesh>

            <Plane
                position={[position[0], position[1], position[2] + size_in_meters.height / 2 + 0.3]}
                args={[1, 0.3]}
                rotation={[0, 0, 0]}
            >
                <meshBasicMaterial color="white" />
            </Plane>

            <Text
                position={[position[0], position[1], position[2] + size_in_meters.height / 2 + 0.35]}
                fontSize={0.2}
                color="black"
                anchorX="center"
                anchorY="middle"
            >
                {name}
            </Text>
        </>
    );
};

const Scene: React.FC = () => {
    return (
        <Canvas
            camera={{ position: [0, 0, 10], up: [0, 0, 1], near: 1, far: 1000 }}
            style={{ width: "100%", height: "100%" }}
        >
            <OrbitControls />
            <Helpers />
            <SceneLights />

            {TGLBModels.map(obj => (
                <Model
                    key={obj.new_object_id}
                    position={[Math.abs(obj.position.x), Math.abs(obj.position.y), Math.abs(obj.position.z)]}
                    size_in_meters={obj.size_in_meters}
                    name={obj.new_object_id}
                />
            ))}
        </Canvas>
    );
};

export default Scene;