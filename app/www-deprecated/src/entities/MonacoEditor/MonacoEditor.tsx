import React, { useState } from 'react';
import { Editor, OnMount } from "@monaco-editor/react";
import { Card, Flex, Loader, Text } from "@gravity-ui/uikit";
import "./MonacoEditor.scss";
import block from 'bem-cn-lite';
import { RoomSizeInput } from '../RoomLayout/RoomSizeInput';
import { FileUploadButton } from './FileUploadButton';

const b = block('monaco');

interface MonacoEditorProps {
    setJsonData: React.Dispatch<any>;
    jsonData: any;
    handleSaveRoomSize: (width: number, height: number) => void;
    handleFileUpload: (fileContent: string) => void;
    roomSize: { width: number; height: number }
}
export const MonacoEditor = ({ setJsonData, handleSaveRoomSize, handleFileUpload, roomSize }: MonacoEditorProps) => {
    const [error, setError] = useState<string | null>(null); // Состояние для ошибок парсинга JSON

    const handleEditorWillMount = () => {
        // Здесь можно настроить monaco перед монтированием, если необходимо
    };

    const handleEditorDidMount: OnMount = (editor, monaco) => {
        // Изначально форматируем документ после монтирования
        //@ts-expect-error
        editor.getAction('editor.action.formatDocument').run();

        // Форматируем документ при потере фокуса
        editor.onDidBlurEditorText(() => {
            //@ts-expect-error
            editor.getAction('editor.action.formatDocument').run();
        });

        // Форматируем документ по нажатии Ctrl + S или Cmd + S
        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
            //@ts-expect-error
            editor.getAction('editor.action.formatDocument').run();
        });

        // Обработка изменений в редакторе
        editor.onDidChangeModelContent(() => {
            const value = editor.getValue();
            try {
                const parsedData = JSON.parse(value); // Парсим JSON
                setJsonData(parsedData); // Сохраняем данные в состояние
                setError(null); // Очищаем ошибку, если парсинг успешен
            } catch (e) {
                setError('Invalid JSON'); // Устанавливаем ошибку, если JSON невалидный
                setJsonData(null); // Очищаем данные
            }
        });
    };

    return (
        <Flex className={b()} direction="column" gap={2} alignItems="center">
            <Card className={b('editor-card')}>
                <Flex className={b('editor-container')} direction={"column"} alignItems={"center"} gap={2}>
                    <Flex justifyContent={'space-between'} alignItems={'center'} className={b('header')}>
                        <Text variant="subheader-2">Редактор</Text>
                        <FileUploadButton onFileUpload={handleFileUpload} />
                    </Flex>
                    <Editor
                        language="json"
                        theme="light"
                        className={b('editor')}
                        beforeMount={handleEditorWillMount}
                        onMount={handleEditorDidMount}
                        loading={<Loader size="l" />}
                    />
                </Flex>
            </Card>
            <RoomSizeInput onSave={handleSaveRoomSize} roomSize={roomSize}/>
            {error && <Text color="danger">{error}</Text>}
        </Flex>
    );
};