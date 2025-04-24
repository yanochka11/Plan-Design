import { useState } from "react";

interface GenerateProps {
    onGenerateScene: (prompt: string) => void;
}
export const Generate = ({ onGenerateScene }: GenerateProps) => {
    const [prompt, setPrompt] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);
    const handleGenerateScene = () => {
        if (!prompt.trim()) return;

        setIsGenerating(true);
        onGenerateScene(prompt);

        // Простая имитация асинхронного процесса
        setTimeout(() => {
            setIsGenerating(false);
            setPrompt("");
        }, 2000);
    };


    return (
        <div>
            <h3 style={{
                fontSize: "16px",
                padding: "5px 0",
                borderBottom: "1px solid #ddd",
                marginBottom: "15px"
            }}>
                Генерация по описанию
            </h3>

            <div style={{ marginBottom: "15px" }}>
                <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Опишите желаемую комнату..."
                    style={{
                        width: "100%",
                        height: "120px",
                        padding: "10px",
                        borderRadius: "4px",
                        border: "1px solid #ccc",
                        resize: "vertical",
                        fontFamily: "inherit",
                        fontSize: "14px"
                    }}
                    disabled={isGenerating}
                />
            </div>

            <button
                onClick={handleGenerateScene}
                disabled={isGenerating || !prompt.trim()}
                style={{
                    width: "100%",
                    padding: "10px",
                    backgroundColor: isGenerating ? "#cccccc" : "#4CAF50",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: isGenerating ? "not-allowed" : "pointer",
                    fontSize: "14px",
                    fontWeight: "bold",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center"
                }}
            >
                {isGenerating ? (
                    <>
                        <span style={{ display: "inline-block", marginRight: "10px" }}>
                            Генерируем...
                        </span>
                        <div
                            style={{
                                width: "20px",
                                height: "20px",
                                border: "3px solid rgba(255,255,255,0.3)",
                                borderRadius: "50%",
                                borderTopColor: "white",
                                animation: "spin 1s linear infinite"
                            }}
                        />
                        <style>
                            {`
                  @keyframes spin {
                    to { transform: rotate(360deg); }
                  }
                `}
                        </style>
                    </>
                ) : (
                    "Сгенерировать"
                )}
            </button>

            <div style={{ marginTop: "15px", fontSize: "14px", color: "#666" }}>
                <p>Примеры запросов:</p>
                <ul style={{ paddingLeft: "20px" }}>
                    <li>"Создай гостиную с диваном и двумя креслами"</li>
                    <li>"Спальня с двуспальной кроватью и шкафом"</li>
                    <li>"Офис с рабочим столом у окна"</li>
                </ul>
            </div>
        </div>
    )
}