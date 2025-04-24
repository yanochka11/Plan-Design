import React, { ChangeEvent } from 'react';
import { Button, Icon } from '@gravity-ui/uikit';
import { ArrowDownToLine } from '@gravity-ui/icons';

interface FileUploadButtonProps {
    onFileUpload: (fileContent: string) => void;
}

export const FileUploadButton: React.FC<FileUploadButtonProps> = ({ onFileUpload }) => {

    const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const content = e.target?.result as string;
                onFileUpload(content);
            };
            reader.readAsText(file);
        }
    };

    return (
        <div>
            <input
                type="file"
                id="file-upload"
                style={{ display: 'none' }}
                onChange={handleFileChange}
                accept=".json" // Ограничиваем загрузку только JSON-файлами
            />
            <label htmlFor="file-upload">
                <Button component="span">
                    <Icon data={ArrowDownToLine} size={16} />
                </Button>
            </label>
        </div>
    );
};