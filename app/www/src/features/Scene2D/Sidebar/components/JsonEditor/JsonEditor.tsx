import { Editor, Monaco } from "@monaco-editor/react";
import { useRef, useState, useEffect } from "react";
import { Text, Button, Flex, useToaster } from "@gravity-ui/uikit";
import block from "bem-cn-lite";

const b = block('json-editor');

interface JsonEditorProps {
    onUpdateFromJSON: (jsonData: any) => void;
    sceneJSON: string;
}

export const JsonEditor = ({ onUpdateFromJSON, sceneJSON }: JsonEditorProps) => {
    const { add } = useToaster();
    const editorRef = useRef<any>(null);
    const [editorErrors, setEditorErrors] = useState<string | null>(null);
    const [currentValue, setCurrentValue] = useState<string>(sceneJSON || '{}');
    const [autoApply, setAutoApply] = useState<boolean>(true);
    const [showToast, setShowToast] = useState<boolean>(false);
    const [toastMessage, setToastMessage] = useState<string>("");
    const timeoutRef = useRef<any>(null);

    useEffect(() => {
        if (editorErrors) {
            add({
                name: "Warning",
                title: editorErrors,
                theme: "warning"
            });
        }

    }, [editorErrors])

    // Обновляем editor когда приходят новые данные из props
    useEffect(() => {
        if (sceneJSON && sceneJSON !== currentValue) {
            setCurrentValue(sceneJSON);
            if (editorRef.current) {
                editorRef.current.setValue(sceneJSON);
            }
        }
    }, [sceneJSON]);

    // Показываем уведомление с таймером
    const showNotification = (message: string, isError = false) => {
        setToastMessage(message);
        setShowToast(true);

        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
        }

        timeoutRef.current = setTimeout(() => {
            setShowToast(false);
        }, 3000);
    };

    // Очищаем таймер при размонтировании
    useEffect(() => {
        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, []);

    // Обработчик изменений в Monaco Editor
    const handleEditorChange = (value: string | undefined) => {
        if (!value) return;
        setCurrentValue(value);

        // Если включен автоматический режим, применяем изменения сразу
        if (autoApply) {
            try {
                const sceneData = JSON.parse(value);

                // Проверяем валидность JSON
                if (!sceneData.objects || !Array.isArray(sceneData.objects)) {
                    setEditorErrors("Неверный формат данных: objects должен быть массивом");
                    return;
                }

                // Применяем изменения
                onUpdateFromJSON(sceneData);
                setEditorErrors(null);
                add({
                    name: "Success",
                    title: "Изменения успешно применены",
                    theme: "success"
                });
                showNotification("JSON успешно применен");
            } catch (e) {
                const errorMessage = "Ошибка парсинга JSON: " + (e as Error).message;
                setEditorErrors(errorMessage);
                showNotification(errorMessage, true);
            }
        }
    };

    // Применение изменений из редактора вручную
    const handleApplyJSON = () => {
        if (editorRef.current) {
            try {
                const value = editorRef.current.getValue();
                const sceneData = JSON.parse(value);
                onUpdateFromJSON(sceneData);
                setEditorErrors(null);
                add({
                    name: "Success",
                    title: "Изменения успешно применены",
                    theme: "success"
                });
                showNotification("JSON успешно применен");
            } catch (e) {
                const errorMessage = "Ошибка парсинга JSON: " + (e as Error).message;
                setEditorErrors(errorMessage);
                showNotification(errorMessage, true);
            }
        }
    };

    // Функция для скачивания JSON
    const handleDownloadJSON = () => {
        if (editorRef.current) {
            const value = editorRef.current.getValue();
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(value);
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", "room-layout.json");
            document.body.appendChild(downloadAnchorNode);
            downloadAnchorNode.click();
            downloadAnchorNode.remove();
            showNotification("JSON файл скачан");
        }
    };

    // Функция для форматирования JSON
    const handleFormatJSON = () => {
        if (editorRef.current) {
            try {
                const value = editorRef.current.getValue();
                const parsed = JSON.parse(value);
                const formatted = JSON.stringify(parsed, null, 2);
                editorRef.current.setValue(formatted);
                showNotification("JSON отформатирован");
            } catch (e) {
                const errorMessage = "Ошибка форматирования JSON: " + (e as Error).message;
                setEditorErrors(errorMessage);
                showNotification(errorMessage, true);
            }
        }
    };

    // Настройка Monaco Editor
    const handleEditorDidMount = (editor: any, monaco: Monaco) => {
        editorRef.current = editor;

        // Если есть начальные данные, загрузим их
        if (sceneJSON) {
            editor.setValue(sceneJSON);
        }

        // Добавим автоформатирование при Shift+Alt+F
        editor.addCommand(monaco.KeyMod.Shift | monaco.KeyMod.Alt | monaco.KeyCode.KeyF, () => {
            handleFormatJSON();
        });

        // Настройка автоформатирования для массива объектов
        monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
            validate: true,
            schemas: [
                {
                    uri: "http://myserver/scene-schema.json",
                    fileMatch: ["*"],
                    schema: {
                        type: "array",
                        items: {
                            oneOf: [
                                // Первый элемент - размеры комнаты
                                {
                                    type: "object",
                                    properties: {
                                        room_dimensions: {
                                            type: "array",
                                            items: { type: "number" },
                                            minItems: 3,
                                            maxItems: 3
                                        }
                                    },
                                    required: ["room_dimensions"]
                                },
                                // Последующие элементы - объекты мебели
                                {
                                    type: "object",
                                    properties: {
                                        new_object_id: { type: "string" },
                                        size_in_meters: {
                                            type: "object",
                                            properties: {
                                                length: { type: "number" },
                                                width: { type: "number" },
                                                height: { type: "number" }
                                            },
                                            required: ["length", "width", "height"]
                                        },
                                        position: {
                                            type: "object",
                                            properties: {
                                                x: { type: "number" },
                                                y: { type: "number" },
                                                z: { type: "number" }
                                            },
                                            required: ["x", "y", "z"]
                                        },
                                        rotation_z: { type: "number" },
                                        style: { type: "string" },
                                        material: { type: "string" },
                                        color: { type: "string" }
                                    },
                                    required: ["new_object_id", "size_in_meters", "position", "rotation_z"]
                                }
                            ]
                        },
                        minItems: 1
                    }
                }
            ]
        });
    };

    return (
        <Flex className={b()} direction={"column"} gap={2} style={{ padding: "10px 0" }}>

            {/* {editorErrors && (
                <Alert theme="warning" title="Warning" message={editorErrors} />
            )} */}

            <Flex gap="2" alignItems="center" style={{ marginBottom: '10px' }}>
                <input
                    type="checkbox"
                    id="autoApply"
                    checked={autoApply}
                    onChange={() => setAutoApply(!autoApply)}
                />
                <label htmlFor="autoApply">Автоматически применять изменения</label>
            </Flex>
            <Flex gap={2}>
                <Button
                    view="action"
                    onClick={handleApplyJSON}
                    className={b('button')}
                    disabled={autoApply}
                >
                    Применить
                </Button>
                <Button
                    view="normal"
                    onClick={handleFormatJSON}
                    className={b('button')}
                >
                    Форматировать
                </Button>
                <Button
                    view="normal"
                    onClick={handleDownloadJSON}
                    className={b('button')}
                >
                    Скачать JSON
                </Button>
            </Flex>

            <Flex className={b('editor-container')} style={{ height: "400px", marginBottom: "16px" }}>
                <Editor
                    height="85vh"
                    defaultLanguage="json"
                    value={currentValue}
                    onChange={handleEditorChange}
                    options={{
                        minimap: { enabled: false },
                        lineNumbers: "on",
                        scrollBeyondLastLine: false,
                        wordWrap: "on",
                        wrappingIndent: "indent",
                        automaticLayout: true,
                        formatOnPaste: true,
                        formatOnType: false,
                        tabSize: 2
                    }}
                    onMount={handleEditorDidMount}
                />
            </Flex>
        </Flex>
    );
}
