// src/components/ModelLoader.tsx
import React, { Suspense } from 'react';
import { useGLTF } from '@react-three/drei';

// Preload models - this will start loading models as soon as the component is mounted
const preloadModels = (modelPaths: string[]) => {
    modelPaths.forEach(path => {
        useGLTF.preload(path);
    });
};

interface ModelLoaderProps {
    children: React.ReactNode;
}

const ModelLoader: React.FC<ModelLoaderProps> = ({ children }) => {
    // Here you would list all the models you want to preload
    const modelPaths = [
        './models/sofa_1.glb',
        './models/coffee_table_1.glb',
        './models/armchair_1.glb',
        './models/carpet_1.glb'
    ];

    // Start preloading
    preloadModels(modelPaths);

    return (
        <Suspense fallback={<LoadingPlaceholder />}>
            {children}
        </Suspense>
    );
};

// A simple loading placeholder
const LoadingPlaceholder: React.FC = () => {
    return (
        <mesh>
            <sphereGeometry args={[0.5, 16, 16]} />
            <meshStandardMaterial color="#cccccc" />
        </mesh>
    );
};

export default ModelLoader;
