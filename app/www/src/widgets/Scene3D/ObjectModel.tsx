import React, { useEffect, useState, useMemo } from 'react';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { SceneObject } from './types/SceneTypes';
import { Box3, Mesh, Vector3 } from 'three';
import { degToRad } from './utils/mathUtils';

interface ObjectModelProps {
    object: SceneObject;
}

const ObjectModel: React.FC<ObjectModelProps> = ({ object }) => {
    // Function to determine what to show when model loading fails
    const renderPlaceholder = () => (
        <mesh
            position={[object.position.x, object.position.y, object.position.z]}
            rotation={[0, 0, degToRad(object.rotation.z_angle) + Math.PI]}
        >
            <boxGeometry
                args={[
                    object.size_in_meters.length,
                    object.size_in_meters.width,
                    object.size_in_meters.height
                ]}
            />
            <meshStandardMaterial
                color={getColorForObject(object.new_object_id)}
                wireframe={true}
            />
        </mesh>
    );

    // Generate model path
    const modelPath = useMemo(() => {
        try {
            // In production, ensure this path actually exists or is a valid URL
            return `./models/${object.new_object_id}.glb`;
        } catch (error) {
            console.error(`Failed to generate model path for ${object.new_object_id}:`, error);
            return null;
        }
    }, [object.new_object_id]);

    // Safe model loading with error boundary
    const [model, setModel] = useState<THREE.Group | null>(null);
    const [loadError, setLoadError] = useState<boolean>(false);

    useEffect(() => {
        if (!modelPath) {
            setLoadError(true);
            return;
        }

        const loader = new GLTFLoader();
        loader.load(
            modelPath,
            (gltf) => {
                console.log(`Successfully loaded model: ${object.new_object_id}`);
                setModel(gltf.scene);
            },
            undefined, // Progress callback
            (error) => {
                console.error(`Failed to load model for ${object.new_object_id}:`, error);
                setLoadError(true);
            }
        );

        // Cleanup function to abort any pending loads if component unmounts
        return () => {
            setModel(null);
        };
    }, [modelPath, object.new_object_id]);

    // If there was an error loading the model, show placeholder
    if (loadError || !modelPath) {
        return renderPlaceholder();
    }

    // If model still loading, show loading indicator or nothing
    if (!model) {
        return (
            <mesh position={[object.position.x, object.position.y, object.position.z]}>
                <sphereGeometry args={[0.2, 16, 16]} />
                <meshStandardMaterial color="#aaaaaa" />
            </mesh>
        );
    }

    // Apply transformations to the loaded model
    useEffect(() => {
        if (model) {
            // Apply scaling to match the dimensions from the JSON
            model.traverse((child) => {
                if (child instanceof Mesh) {
                    // Calculate bounding box
                    const box = new Box3().setFromObject(child);
                    const size = new Vector3();
                    box.getSize(size);

                    if (size.x > 0 && size.y > 0 && size.z > 0) {
                        // Calculate scale factors
                        const scaleX = object.size_in_meters.length / size.x;
                        const scaleY = object.size_in_meters.width / size.y;
                        const scaleZ = object.size_in_meters.height / size.z;

                        child.scale.set(scaleX, scaleY, scaleZ);
                    }
                }
            });
        }
    }, [model, object.size_in_meters]);

    // Convert rotation
    const rotationZ = degToRad(object.rotation.z_angle) + Math.PI;

    return (
        <primitive
            object={model}
            position={[object.position.x, object.position.y, object.position.z]}
            rotation={[0, 0, rotationZ]}
        />
    );
};

// Helper function to get colors
function getColorForObject(objectId: string): string {
    const objectType = objectId.split('_')[0];

    switch (objectType) {
        case 'sofa':
            return '#8B4513'; // Brown
        case 'coffee':
            return '#A0522D'; // Sienna
        case 'armchair':
            return '#CD853F'; // Peru
        case 'carpet':
            return '#DEB887'; // BurlyWood
        default:
            return '#C0C0C0'; // Silver
    }
}

export default ObjectModel;
