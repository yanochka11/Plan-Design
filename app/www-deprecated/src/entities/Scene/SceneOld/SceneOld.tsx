import React, { useEffect, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';
import * as THREE from 'three';
import { Helpers, SceneLights } from './components';
import { TRotation } from './types';
import { TGLBModels } from './constants';

function rescaleObject(obj: THREE.Object3D, targetSize: { length: number; width: number; height: number }) {
    const bbox = new THREE.Box3().setFromObject(obj);
    const size = bbox.getSize(new THREE.Vector3());

    const scale = new THREE.Vector3(
        targetSize.length / size.x,
        targetSize.width / size.y,
        targetSize.height / size.z
    );

    obj.scale.copy(scale);
}

function centerObject(obj: THREE.Object3D) {
    const bbox = new THREE.Box3().setFromObject(obj);
    const center = bbox.getCenter(new THREE.Vector3());

    // Смещаем объект так, чтобы его центр был в начале координат
    obj.position.sub(center);
}

function degToRad(deg: number): number {
    return (deg * Math.PI) / 180;
}

interface ModelProps {
    modelPath: string;
    position: [number, number, number];
    rotation: TRotation;
    size_in_meters: { length: number; width: number; height: number };
}

const Model: React.FC<ModelProps> = ({ modelPath, position, rotation, size_in_meters }) => {
    const { scene } = useGLTF(modelPath) as { scene: THREE.Object3D };

    const model = useMemo(() => {
        const clonedScene = scene.clone();
        rescaleObject(clonedScene, size_in_meters);
        centerObject(clonedScene);
        clonedScene.position.set(...position);
        clonedScene.rotation.set(
            degToRad(rotation.x_angle ?? 0),
            degToRad(rotation.y_angle ?? 0),
            degToRad((rotation.z_angle ?? 0) + Math.PI)
        );
        return clonedScene;
    }, [scene, position, rotation, size_in_meters]);

    return <primitive object={model} />;
};

const Room: React.FC = () => {
    return (
        <>
            {/* Пол */}
            <mesh receiveShadow position={[0, 0, -0.]}>
                <planeGeometry args={[10, 10]} />
                <meshStandardMaterial color="lightgray" />
            </mesh>

            {/* Потолок */}
            <mesh receiveShadow position={[0, 0, 4.5]}>
                <planeGeometry args={[10, 10]} />
                <meshStandardMaterial color="lightgray" side={THREE.BackSide} />
            </mesh>

            {/* Стена слева */}
            <mesh receiveShadow position={[-5, 0, 2]}>
                <planeGeometry args={[10, 5]} />
                <meshStandardMaterial color="lightgray" side={THREE.DoubleSide} />
            </mesh>

            {/* Стена справа */}
            <mesh receiveShadow position={[5, 0, 2]}>
                <planeGeometry args={[10, 5]} />
                <meshStandardMaterial color="lightgray" side={THREE.DoubleSide} />
            </mesh>

            {/* Стена сзади */}
            <mesh receiveShadow position={[0, -5, 2]}>
                <planeGeometry args={[10, 5]} />
                <meshStandardMaterial color="lightgray" side={THREE.DoubleSide} />
            </mesh>
        </>
    );
};

const Scene: React.FC = () => {
    return (
        <Canvas
            shadows
            camera={{ position: [5, 5, 5], up: [0, 0, 1] }}
            style={{ width: "100%", height: "100%" }}
        >
            <OrbitControls />
            <Helpers />
            <SceneLights />
            <Room />

            {TGLBModels.map(obj => (
                <Model
                    key={obj.new_object_id}
                    modelPath={`/assets/${obj.new_object_id}.glb`}
                    position={[obj.position.x, obj.position.y, obj.position.z]}
                    rotation={obj.rotation}
                    size_in_meters={obj.size_in_meters}
                />
            ))}
        </Canvas>
    );
};

export default Scene;