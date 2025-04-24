import * as THREE from 'three';

interface RoomProps {
    roomSize: number[];
}

export const Room = ({roomSize}: RoomProps) => (
    <mesh position={[roomSize[0] / 2, roomSize[1] / 2, roomSize[2] / 2]}>
        <boxGeometry args={[roomSize[0], roomSize[1], roomSize[2]]} />
        <meshStandardMaterial
            color="lightgray"
            side={THREE.DoubleSide}
            opacity={0.2}
            transparent
        />
    </mesh>
);