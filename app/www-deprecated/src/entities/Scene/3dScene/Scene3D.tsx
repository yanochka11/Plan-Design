import React, { useRef, useEffect, useState } from 'react';
import { Canvas, useLoader } from '@react-three/fiber';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { OrbitControls, Grid } from '@react-three/drei'; // Импорт Grid
import * as THREE from 'three'; // Импорт AxesHelper из three
import { objectsInRoom } from '../utils';

// Типы для данных из JSON
interface SizeInMeters {
    length: number;
    width: number;
    height: number;
}

interface Placement {
    room_layout_elements: Array<{
        layout_element_id: string;
        preposition: string;
    }>;
    objects_in_room: Array<{
        object_id: string;
        preposition: string;
        is_adjacent: boolean;
    }>;
}

interface Cluster {
    constraint_area: {
        x_neg: number;
        x_pos: number;
        y_neg: number;
        y_pos: number;
    };
}

interface ObjectData {
    new_object_id: string;
    style: string;
    material: string;
    size_in_meters: SizeInMeters;
    is_on_the_floor: boolean;
    facing: string;
    placement: Placement;
    rotation: {
        z_angle: number;
    };
    cluster: Cluster;
    position: {
        x: number;
        y: number;
        z: number;
    };
}

// Пропсы для компонента Object3D
interface Object3DProps {
    data: ObjectData;
    glbPath: string;
}

// Компонент для загрузки и отображения GLB-модели
const Object3D: React.FC<Object3DProps> = ({ data, glbPath }) => {
    const gltf = useLoader(GLTFLoader, glbPath);
    const ref = useRef<THREE.Group>(null);
    const [isLoaded, setIsLoaded] = useState(false);

    // Применяем трансформации (позиция, вращение, масштаб)
    useEffect(() => {
        if (ref.current && gltf.scene.children.length > 0) {
            const mesh = gltf.scene.children[0];

            // Проверка наличия геометрии
            if (mesh && mesh.geometry && mesh.geometry.boundingBox) {
                // Позиция
                ref.current.position.set(data.position.x, data.position.y, data.position.z);

                // Вращение (в радианах)
                const zRotation = (data.rotation.z_angle / 180) * Math.PI;
                ref.current.rotation.set(0, 0, zRotation);

                // Масштабирование
                const { length, width, height } = data.size_in_meters;
                const scaleX = length / mesh.geometry.boundingBox.max.x;
                const scaleY = width / mesh.geometry.boundingBox.max.y;
                const scaleZ = height / mesh.geometry.boundingBox.max.z;
                ref.current.scale.set(scaleX, scaleY, scaleZ);

                setIsLoaded(true);
            } else {
                console.error('Модель не содержит геометрии или boundingBox:', gltf);
            }
        }
    }, [data, gltf]);

    if (!isLoaded) {
        return null; // Не рендерить, пока модель не загрузится
    }

    return <primitive object={gltf.scene} ref={ref} />;
};

// Основной компонент сцены
const SceneBuilder: React.FC<{ objects: ObjectData[] }> = ({ objects }) => {
    return (
        <Canvas camera={{ position: [5, 5, 5], fov: 50 }}>
            {/* Сетка */}
            <Grid
                position={[0, 0, 0]} // Позиция сетки
                args={[10, 10]} // Размер сетки (ширина, высота)
                cellSize={1} // Размер ячейки
                cellColor="#cccccc" // Цвет линий сетки
                sectionColor="#888888" // Цвет основных линий
                sectionSize={5} // Расстояние между основными линиями
            />

            {/* Оси */}
            <axesHelper args={[5]} /> {/* Длина осей */}

            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} />
            {objects.map((obj) => (
                <Object3D key={obj.new_object_id} data={obj} glbPath={`/assets/${obj.new_object_id}.glb`} />
            ))}
            <OrbitControls />
        </Canvas>
    );
};

// Пример использования
const Scene: React.FC = () => {
    return (
        <div style={{ width: '100vw', height: '100vh' }}>
            <SceneBuilder objects={objectsInRoom} />
        </div>
    );
};

export default Scene;