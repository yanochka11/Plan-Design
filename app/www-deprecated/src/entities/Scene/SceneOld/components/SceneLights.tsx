import { Fragment } from 'react';
import * as THREE from 'three';

export const SceneLights = () => {
    return (
        <Fragment>
            <ambientLight intensity={0.5} />
            <directionalLight position={[10, 10, 10]} intensity={1} castShadow />
            <hemisphereLight intensity={0.35} groundColor={new THREE.Color('#888')} />
        </Fragment>
    )
}