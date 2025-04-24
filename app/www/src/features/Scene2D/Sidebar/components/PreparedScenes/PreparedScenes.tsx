import { Fragment } from "react/jsx-runtime"
import { predefinedScenes } from "./constants"

const ScenePresetItem: React.FC<{
    name: string;
    id: string;
    onLoad: (id: string) => void;
}> = ({ name, id, onLoad }) => {
    return (
        <div
            style={{
                padding: "10px",
                marginBottom: "8px",
                backgroundColor: "white",
                border: "1px solid #ccc",
                borderRadius: "4px",
                cursor: "pointer",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                transition: "all 0.2s ease",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
            }}
            onClick={() => onLoad(id)}
        >
            <span>{name}</span>
            <button
                style={{
                    backgroundColor: "#4CAF50",
                    color: "white",
                    border: "none",
                    borderRadius: "3px",
                    padding: "4px 8px",
                    fontSize: "12px",
                    cursor: "pointer",
                }}
            >
                Загрузить
            </button>
        </div>
    );
};

interface PreparedScenesTabProps {
    onLoadScene: (sceneData: any) => void;
}

export const PreparedScenesTab = ({ onLoadScene }: PreparedScenesTabProps) => {

    // Обработчик загрузки сцены
    const handleLoadScene = (sceneId: string) => {
        const scene = predefinedScenes.find(scene => scene.id === sceneId);
        if (scene) {
            onLoadScene(scene.data);
        }
    };
    return (<Fragment>
        <div>
            <h3 style={{
                fontSize: "16px",
                padding: "5px 0",
                borderBottom: "1px solid #ddd",
                marginBottom: "15px"
            }}>
                Готовые сцены
            </h3>

            {predefinedScenes.map(scene => (
                <ScenePresetItem
                    key={scene.id}
                    id={scene.id}
                    name={scene.name}
                    onLoad={handleLoadScene}
                />
            ))}
        </div>
    </Fragment>)
}