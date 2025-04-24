import { useDrag } from "react-dnd";
import { Furniture } from "../../../types";
import { colors } from "../../../utils";
import { categories } from "./utils";

// Компонент для отдельного элемента мебели
const SidebarItem: React.FC<{ label: Furniture }> = ({ label }) => {
    const [{ isDragging }, drag] = useDrag(() => ({
        type: "object",
        item: { label },
        collect: (monitor) => ({
            isDragging: !!monitor.isDragging(),
        }),
    }));

    // Используем точный цвет из словаря
    const color = colors[label];

    return (
        <div
            ref={drag}
            style={{
                padding: "10px",
                marginBottom: "8px",
                backgroundColor: "white",
                border: `2px solid ${color}`,
                borderRadius: "4px",
                cursor: "grab",
                opacity: isDragging ? 0.5 : 1,
                display: "flex",
                alignItems: "center",
                transition: "all 0.2s ease",
                boxShadow: isDragging ? "none" : "0 2px 4px rgba(0,0,0,0.1)",
            }}
        >
            <div
                style={{
                    width: "24px",
                    height: "24px",
                    backgroundColor: color,
                    marginRight: "10px",
                    borderRadius: "3px",
                }}
            />
            <span>{label}</span>
        </div>
    );
};


export const FurnitureComponent = () => {
    return (
        <div>
            {Object.entries(categories).map(([category, items]) => (
                <div key={category} style={{ marginBottom: "20px" }}>
                    <h3 style={{
                        fontSize: "16px",
                        padding: "5px 0",
                        borderBottom: "1px solid #ddd",
                        marginBottom: "10px"
                    }}>
                        {category}
                    </h3>
                    <div>
                        {items.map(item => (
                            <SidebarItem
                                key={item}
                                label={item as Furniture}
                            />
                        ))}
                    </div>
                </div>
            ))}

            {/* Элементы, которые могли быть не включены в категории */}
            {Object.keys(colors).filter(item =>
                !Object.values(categories).flat().includes(item)
            ).length > 0 && (
                    <div style={{ marginBottom: "20px" }}>
                        <h3 style={{
                            fontSize: "16px",
                            padding: "5px 0",
                            borderBottom: "1px solid #ddd",
                            marginBottom: "10px"
                        }}>
                            Другое
                        </h3>
                        <div>
                            {Object.keys(colors)
                                .filter(item => !Object.values(categories).flat().includes(item))
                                .map(item => (
                                    <SidebarItem
                                        key={item}
                                        label={item as Furniture}
                                    />
                                ))}
                        </div>
                    </div>
                )}
        </div>
    )
}