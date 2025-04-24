import { RoomLayout, Sidebar } from '../../features/Scene2D';
import { data } from './utils';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { Flex, Button } from '@gravity-ui/uikit';
import block from "bem-cn-lite";
import './Scene2D.scss'
import { useState, useRef, useCallback, useEffect } from 'react';

const b = block('scene-2d')

export const Scene2D = () => {
    const [sceneJSON, setSceneJSON] = useState<string>("");
    const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
    const [scale, setScale] = useState<number>(1);
    const roomLayoutRef = useRef<any>(null);
    const layoutContainerRef = useRef<HTMLDivElement>(null);

    // Обновление JSON при изменениях в сцене
    const updateJson = useCallback((value: string) => {
        setSceneJSON(value);
    }, []);

    // Обработчик загрузки сцены из JSON
    const handleUpdateFromJSON = useCallback((jsonData: any) => {
        if (roomLayoutRef.current && roomLayoutRef.current.loadSceneFromData) {
            roomLayoutRef.current.loadSceneFromData(jsonData);
        }
    }, []);

    // Обработчик загрузки готовой сцены
    const handleLoadScene = useCallback((sceneData: any) => {
        if (roomLayoutRef.current && roomLayoutRef.current.loadSceneFromData) {
            roomLayoutRef.current.loadSceneFromData(sceneData);
        }
    }, []);

    // Обработчик генерации сцены
    const handleGenerateScene = useCallback((prompt: string) => {
        // Здесь будет логика генерации сцены по промпту
        console.log("Генерация сцены по промпту:", prompt);
    }, []);

    // Переключатель состояния сайдбара
    const toggleSidebar = useCallback(() => {
        setIsSidebarOpen(prev => !prev);
    }, []);

    // Функция изменения масштаба
    const handleZoomIn = useCallback(() => {
        setScale(prev => Math.min(prev + 0.1, 2));
    }, []);

    const handleZoomOut = useCallback(() => {
        setScale(prev => Math.max(prev - 0.1, 0.5));
    }, []);

    const handleResetZoom = useCallback(() => {
        setScale(1);
    }, []);

    // Автоматическое масштабирование при изменении размера окна
    useEffect(() => {
        const calculateScale = () => {
            if (!layoutContainerRef.current) return;

            const containerWidth = layoutContainerRef.current.clientWidth;
            const containerHeight = layoutContainerRef.current.clientHeight;

            // Предполагаемые размеры сцены (8.3м × 10.96м в пикселях + отступы)
            const roomWidthPx = 8.3 * 100 + 40; // Ширина комнаты в пикселях + отступы
            const roomHeightPx = 10.96 * 100 + 40; // Высота комнаты в пикселях + отступы

            // Определение оптимального масштаба
            const widthScale = containerWidth / roomWidthPx;
            const heightScale = containerHeight / roomHeightPx;

            // Берем минимальный из двух масштабов, чтобы вся сцена поместилась
            const optimalScale = Math.min(widthScale, heightScale, 1); // Но не больше 1, чтобы не растягивать

            // Плавное изменение масштаба
            setScale(optimalScale);
        };

        // Добавляем задержку, чтобы дать время контейнеру изменить свои размеры после изменения состояния сайдбара
        const timeoutId = setTimeout(calculateScale, 300);

        // Также пересчитываем масштаб при изменении размера окна
        window.addEventListener('resize', calculateScale);

        return () => {
            clearTimeout(timeoutId);
            window.removeEventListener('resize', calculateScale);
        };
    }, [isSidebarOpen]); // Пересчитываем при переключении сайдбара

    return (
        <DndProvider backend={HTML5Backend}>
            <Flex className={b()} justifyContent="space-between">
                <div className={b('layout-container', { 'sidebar-open': isSidebarOpen })} ref={layoutContainerRef}>
                    <div className={b('layout-wrapper')} style={{ transform: `scale(${scale})`, transition: 'transform 0.3s ease' }}>
                        <RoomLayout
                            ref={roomLayoutRef}
                            initialObjects={data}
                            updateJson={updateJson}
                        />
                    </div>

                    <div className={b('zoom-controls')}>
                        <Button view="flat" onClick={handleZoomOut}>-</Button>
                        <Button view="flat" onClick={handleResetZoom}>{Math.round(scale * 100)}%</Button>
                        <Button view="flat" onClick={handleZoomIn}>+</Button>
                    </div>

                    <Button
                        className={b('toggle-sidebar')}
                        onClick={toggleSidebar}
                        view="action"
                    >
                        {isSidebarOpen ? '»' : '«'}
                    </Button>
                </div>

                <Sidebar
                    isOpen={isSidebarOpen}
                    onToggle={toggleSidebar}
                    onLoadScene={handleLoadScene}
                    onGenerateScene={handleGenerateScene}
                    onUpdateFromJSON={handleUpdateFromJSON}
                    sceneJSON={sceneJSON}
                />
            </Flex>
        </DndProvider>
    )
}
