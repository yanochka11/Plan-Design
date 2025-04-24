import React from 'react';
import { SceneObject } from '../types/SceneTypes';
import * as THREE from 'three';

interface MockObjectProps {
    object: SceneObject;
}

const MockObject: React.FC<MockObjectProps> = ({ object }) => {
    // Преобразуем угол из градусов в радианы и добавляем PI, как в оригинальном скрипте
    const rotationZ = (object.rotation.z_angle / 180.0) * Math.PI + Math.PI;

    // Выбираем цвет в зависимости от типа объекта
    const getObjectColor = () => {
        const objectType = object.new_object_id.split('_')[0];
        switch (objectType) {
            case 'sofa':
                return '#A97142'; // коричневый
            case 'coffee':
                return '#D2B48C'; // песочный
            case 'armchair':
                return '#8B4513'; // темно-коричневый
            case 'carpet':
                return '#DEB887'; // светло-коричневый
            default:
                return '#CCCCCC'; // серый
        }
    };

    return (
        <group
            position={[object.position.x, object.position.y, object.position.z]}
            rotation={[0, 0, rotationZ]}
        >
            <mesh castShadow receiveShadow>
                <boxGeometry
                    args={[
                        object.size_in_meters.length,
                        object.size_in_meters.width,
                        object.size_in_meters.height
                    ]}
                />
                <meshStandardMaterial color={getObjectColor()} />
            </mesh>

            {/* Добавляем небольшую метку с названием объекта */}
            <mesh position={[0, 0, object.size_in_meters.height / 2 + 0.05]}>
                {/* <textGeometry args={[object.new_object_id, { size: 0.1, height: 0.02 }]} /> */}
                <meshBasicMaterial color="black" />
            </mesh>
        </group>
    );
};

export default MockObject;
