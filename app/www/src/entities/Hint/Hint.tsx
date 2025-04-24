import { CircleQuestion } from "@gravity-ui/icons";
import { Button, Flex, Icon, Loader, Popup } from "@gravity-ui/uikit";
import { useState, useEffect } from "react";
import block from 'bem-cn-lite';
import './Hint.scss';
import { Editor } from "@monaco-editor/react";

const b = block('hint');

export const Hint = () => {
    const [buttonElement, setButtonElement] = useState(null);
    const [open, setOpen] = useState(false);
    const [jsonContent, setJsonContent] = useState<string>("");
    const [_editorHeight, setEditorHeight] = useState<string>("100px");

    useEffect(() => {
        const storagedObjectString = localStorage.getItem('design') ?? '{}';
        const formattedJson = JSON.stringify(JSON.parse(storagedObjectString), null, 2);
        setJsonContent(formattedJson);

        const lineHeight = 19;
        const numberOfLines = formattedJson.split('\n').length;
        const padding = 20;
        setEditorHeight(`${numberOfLines * lineHeight + padding}px`);
    }, [open]);


    return (
        <Flex className={b()}>
            <Button ref={setButtonElement} onClick={() => setOpen((prevOpen) => !prevOpen)}>
                <Icon data={CircleQuestion} size={16} />
            </Button>
            <Popup anchorElement={buttonElement} open={open} placement="bottom" hasArrow={true}>
                <Flex className={b('popup')}>
                    <Editor
                        height="150px"
                        language="json"
                        theme="light"
                        className={b('editor')}
                        loading={<Loader size="s" />}
                        value={jsonContent}
                        options={{
                            readOnly: true,
                            lineNumbers: "off",
                            minimap: { enabled: false },
                        }}
                    />
                </Flex>
            </Popup>
        </Flex>
    );
}
