export const predefinedScenes = [
    {
        id: "living-room",
        name: "Гостиная",
        data: {
            roomDimensions: { width: 1024, height: 1024 },
            objects: [
                { id: "sofa-1", label: "sofa", coordinates: { x: 300, y: 200, width: 200, height: 80 }, rotation: 0 },
                { id: "coffee-table-1", label: "coffee table", coordinates: { x: 300, y: 300, width: 120, height: 60 }, rotation: 0 },
                { id: "TV-stand-1", label: "TV stand", coordinates: { x: 300, y: 400, width: 180, height: 40 }, rotation: 0 }
            ]
        }
    },
    {
        id: "dining-room",
        name: "Столовая",
        data: {
            roomDimensions: { width: 1024, height: 1024 },
            objects: [
                { id: "dining-table-1", label: "dining table", coordinates: { x: 500, y: 500, width: 160, height: 80 }, rotation: 0 },
                { id: "chair-1", label: "chair", coordinates: { x: 440, y: 460, width: 40, height: 40 }, rotation: 0 },
                { id: "chair-2", label: "chair", coordinates: { x: 560, y: 460, width: 40, height: 40 }, rotation: 0 },
                { id: "chair-3", label: "chair", coordinates: { x: 440, y: 540, width: 40, height: 40 }, rotation: 0 },
                { id: "chair-4", label: "chair", coordinates: { x: 560, y: 540, width: 40, height: 40 }, rotation: 0 }
            ]
        }
    },
    {
        id: "bedroom",
        name: "Спальня",
        data: {
            roomDimensions: { width: 1024, height: 1024 },
            objects: [
                { id: "wardrobe-1", label: "wardrobe", coordinates: { x: 200, y: 150, width: 120, height: 60 }, rotation: 0 },
                { id: "chair-bed-1", label: "chair-bed", coordinates: { x: 400, y: 300, width: 180, height: 90 }, rotation: 0 },
                { id: "side-table-1", label: "side table", coordinates: { x: 500, y: 250, width: 50, height: 50 }, rotation: 0 }
            ]
        }
    }
];