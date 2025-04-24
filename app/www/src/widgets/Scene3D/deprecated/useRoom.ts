import { useMemo } from "react";
import * as THREE from "three";


export const useRoom = (length: number, width: number, height: number) => {
    const textures = useMemo(() => {
        const loader = new THREE.TextureLoader();
        return {
            wall: loader.load("https://i.imgur.com/7QzHuKb.jpg"), // Светлые обои
            floor: loader.load("https://i.imgur.com/3K8hQ5a.jpg"), // Ламинат
            ceiling: new THREE.MeshStandardMaterial({ color: 0xffffff }) // Белый потолок
        };
    }, []);

    const roomGroup = useMemo(() => {
        const group = new THREE.Group();

        // Стены
        const wallMaterial = new THREE.MeshStandardMaterial({
            map: textures.wall,
            normalMap: textures.wall,
            side: THREE.DoubleSide
        });

        const walls = new THREE.Mesh(
            new THREE.BoxGeometry(length, height, width),
            wallMaterial
        );
        walls.geometry.translate(0, height / 2, 0);

        // Пол
        const floorMaterial = new THREE.MeshStandardMaterial({
            map: textures.floor,
            normalMap: textures.floor,
            roughness: 0.8
        });

        const floor = new THREE.Mesh(
            new THREE.PlaneGeometry(length, width),
            floorMaterial
        );
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;

        // Потолок
        const ceiling = new THREE.Mesh(
            new THREE.PlaneGeometry(length, width),
            textures.ceiling
        );
        ceiling.rotation.x = Math.PI / 2;
        ceiling.position.y = height;

        // Настройка повторения текстур
        textures.wall.repeat.set(length / 2, height / 2);
        textures.wall.wrapS = THREE.RepeatWrapping;
        textures.wall.wrapT = THREE.RepeatWrapping;

        textures.floor.repeat.set(length / 2, width / 2);
        textures.floor.wrapS = THREE.RepeatWrapping;
        textures.floor.wrapT = THREE.RepeatWrapping;

        group.add(walls, floor, ceiling);
        return group;
    }, [length, width, height, textures]);

    return roomGroup;
};