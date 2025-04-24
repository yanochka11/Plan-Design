import { useEffect, useRef, useMemo } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { Flex } from "@gravity-ui/uikit";

const getSafeDimension = (value: any, defaultValue: number) => {
    const num = Number(value);
    return Number.isFinite(num) && num > 0 ? num : defaultValue;
};

export const Scene3D = () => {
    const mountRef = useRef<HTMLDivElement>(null);

    // Получение и валидация параметров
    const { L, W, H } = useMemo(() => {
        const storage = JSON.parse(localStorage.getItem('design') || '{}');
        return {
            L: getSafeDimension(storage.length, 4),
            W: getSafeDimension(storage.width, 5),
            H: getSafeDimension(storage.height, 3)
        };
    }, []);

    // Создание геометрий с проверкой значений
    const geometries = useMemo(() => {
        return {
            walls: new THREE.BoxGeometry(L, H, W),
            floor: new THREE.PlaneGeometry(L, W),
            ceiling: new THREE.PlaneGeometry(L, W)
        };
    }, [L, W, H]);

    // Создание текстур
    const textures = useMemo(() => {
        const loader = new THREE.TextureLoader();
        return {
            wall: loader.load("https://i.imgur.com/7QzHuKb.jpg"),
            floor: loader.load("https://i.imgur.com/3K8hQ5a.jpg"),
            ceiling: new THREE.MeshStandardMaterial({ color: 0xffffff })
        };
    }, []);

    // Создание 3D объектов
    const { room, camera } = useMemo(() => {
        // Группа для комнаты
        const room = new THREE.Group();

        // Стены
        const walls = new THREE.Mesh(
            new THREE.BoxGeometry(L, H, W),
            new THREE.MeshStandardMaterial({
                map: textures.wall,
                side: THREE.DoubleSide
            })
        );
        walls.position.y = H / 2;

        // Пол
        const floor = new THREE.Mesh(
            new THREE.PlaneGeometry(L, W),
            new THREE.MeshStandardMaterial({
                map: textures.floor,
                roughness: 0.8
            })
        );
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;

        // Потолок
        const ceiling = new THREE.Mesh(
            new THREE.PlaneGeometry(L, W),
            textures.ceiling
        );
        ceiling.rotation.x = Math.PI / 2;
        ceiling.position.y = H;

        room.add(walls, floor, ceiling);

        // Камера
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100);
        camera.position.set(L / 4, H / 2, W / 4);

        return { room, camera };
    }, [L, W, H, textures]);

    useEffect(() => {
        if (!mountRef.current) return;

        // Инициализация сцены
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xf0f0f0);
        scene.add(room);

        // Рендерер
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        mountRef.current.appendChild(renderer.domElement);

        // Освещение
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(0, H * 2, 0);
        directionalLight.castShadow = true;
        scene.add(ambientLight, directionalLight);

        // Управление
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;

        // Анимация
        const animate = () => {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        };
        animate();

        // Очистка
        return () => {
            controls.dispose();
            mountRef.current?.removeChild(renderer.domElement);
        };
    }, [room, camera, H]);

    return <Flex ref={mountRef} style={{
        width: '100%',
        height: '100vh',
        cursor: 'grab'
    }} />;
};
