// import React, { useEffect } from 'react';
// import { Canvas } from '@react-three/fiber';
// import { OrbitControls, useGLTF } from '@react-three/drei';
// import * as THREE from 'three';
// import { Helpers } from '../../entities';
// import { TGLBModels, TRotation } from '../../shared/utils/json';
// import { Cubes } from '../../entities/Cubes';
// import { SceneLights } from '../../entities/SceneLights/SceneLights';

// function rescaleObject(obj: THREE.Object3D, targetSize: { length: number; width: number; height: number }) {
//     const bbox = new THREE.Box3().setFromObject(obj);
//     const size = bbox.getSize(new THREE.Vector3());

//     const scale = new THREE.Vector3(
//         targetSize.length / size.x,
//         targetSize.width / size.y,
//         targetSize.height / size.z
//     );

//     obj.scale.copy(scale);
// }

// function degToRad(deg: number, isZ?: boolean): number {
//     console.log(deg, 'deg')
//     return deg * (Math.PI / 180)
// }


// interface ModelProps {
//     modelPath: string;
//     position: [number, number, number];
//     rotation: TRotation;
//     size_in_meters: { length: number; width: number; height: number };
// }

// const Model: React.FC<ModelProps> = ({ modelPath, position, rotation, size_in_meters }) => {
//     const { scene} = useGLTF(modelPath);

//     // useEffect(() => {
//     //     rescaleObject(scene, size_in_meters);

//     //     console.log(rotation, 'testing')
//     //     scene.position.set(...position);
//     //     scene.rotation.set(
//     //         Math.PI,
//     //         Math.PI + 1,
//     //         (rotation.z_angle ?? 0 / 180.0) * Math.PI + Math.PI,
//     //         "YZX"
//     //     );
//     // }, [scene, position, rotation, size_in_meters]);

//     React.useEffect(() => {
//         scene.traverse((child) => {
//             if ((child as THREE.Mesh).isMesh) {
//                 const mesh = child as THREE.Mesh;
//                 mesh.geometry.center();
//                 mesh.geometry.computeBoundingBox();
//                 mesh.geometry.computeBoundingSphere();
//             }
//         });

//         rescaleObject(scene, size_in_meters);
//         const [x, y, z] = position;
//         scene.position.set(x, y, z);

//         const xAngle = degToRad(rotation.y_angle ?? 0);
//         const yAngle = degToRad(rotation.x_angle ?? 0);
//         const zAngle = degToRad(rotation.z_angle ?? 0) + Math.PI;

//         scene.rotation.set(xAngle, yAngle, zAngle);

//     }, [scene, position, rotation, size_in_meters]);



//     return <primitive object={scene} />;
// };

// const Scene: React.FC = () => {
//     return (
//         <Canvas
//             camera={{ position: [5, 5, 5], up: [0, 0, 1] }}
//         >
//             <OrbitControls />
//             <Helpers />
//             <Cubes />
//             <SceneLights />

//             {TGLBModels.map(obj => (
//                 <Model
//                     key={obj.new_object_id}
//                     modelPath={`/assets/${obj.new_object_id}.glb`}
//                     position={[obj.position.x, obj.position.y, obj.position.z]}
//                     rotation={obj.rotation}
//                     size_in_meters={obj.size_in_meters}
//                 />
//             ))}
//         </Canvas>
//     );
// };

// export default Scene;


// import React, { useRef, useEffect } from 'react';
// import { Canvas, useFrame, useLoader } from '@react-three/fiber';
// import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
// import { OrbitControls } from '@react-three/drei';

// // Типы для данных из scene_graph.json
// interface ObjectData {
//   new_object_id: string;
//   position: { x: number; y: number; z: number };
//   rotation: { z_angle: number };
//   size_in_meters: { length: number; width: number; height: number };
// }

// // Пропсы для компонента Object3D
// interface Object3DProps {
//   data: ObjectData;
//   glbPath: string;
// }

// // Компонент для загрузки и отображения GLB-модели
// const Object3D: React.FC<Object3DProps> = ({ data, glbPath }) => {
//   const gltf = useLoader(GLTFLoader, glbPath);
//   const ref = useRef<THREE.Group>(null);

//   // Применяем трансформации (позиция, вращение, масштаб)
//   useEffect(() => {
//     if (ref.current) {
//       // Позиция
//       ref.current.position.set(data.position.x, data.position.y, data.position.z);

//       // Вращение (в радианах)
//       const zRotation = (data.rotation.z_angle / 180) * Math.PI + Math.PI;
//       ref.current.rotation.set(0, 0, zRotation);

//       // Масштабирование
//       const { length, width, height } = data.size_in_meters;
//       const scaleX = length / gltf.scene.children[0].geometry.boundingBox.max.x;
//       const scaleY = width / gltf.scene.children[0].geometry.boundingBox.max.y;
//       const scaleZ = height / gltf.scene.children[0].geometry.boundingBox.max.z;
//       ref.current.scale.set(scaleX, scaleY, scaleZ);
//     }
//   }, [data, gltf]);

//   return <primitive object={gltf.scene} ref={ref} />;
// };

// // Основной компонент сцены
// const SceneBuilder: React.FC = () => {
//   // Пример данных из scene_graph.json
//   const objectsInRoom: ObjectData[] = [
//     {
//       new_object_id: 'object1',
//       position: { x: 1, y: 1, z: 0 },
//       rotation: { z_angle: 45 },
//       size_in_meters: { length: 1, width: 1, height: 1 },
//     },
//     {
//       new_object_id: 'object2',
//       position: { x: -1, y: -1, z: 0 },
//       rotation: { z_angle: 90 },
//       size_in_meters: { length: 1, width: 1, height: 1 },
//     },
//   ];

//   const glbPaths: { [key: string]: string } = {
//     object1: '/path/to/object1.glb',
//     object2: '/path/to/object2.glb',
//   };

//   return (
//     <Canvas camera={{ position: [5, 5, 5], fov: 50 }}>
//       <ambientLight intensity={0.5} />
//       <pointLight position={[10, 10, 10]} />
//       {objectsInRoom.map((obj) => (
//         <Object3D key={obj.new_object_id} data={obj} glbPath={glbPaths[obj.new_object_id]} />
//       ))}
//       <OrbitControls />
//     </Canvas>
//   );
// };

// export default SceneBuilder;