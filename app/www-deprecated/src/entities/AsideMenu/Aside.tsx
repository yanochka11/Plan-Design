import { FC, ReactNode } from "react";
import { Card, Text } from "@gravity-ui/uikit";
import { Xmark } from "@gravity-ui/icons";
import block from 'bem-cn-lite';
import './Aside.scss'
import { MonacoEditor } from "../MonacoEditor";

type Props = {
    children: ReactNode;
    isOpen: boolean;
    content?: ReactNode;
    name?: string;
    onClose: () => void;
    hasLayout?: boolean;
};

const b = block('aside-menu');

export const AsideMenu: FC<Props> = ({
    children,
    isOpen,
    content = <></>,
    name = "",
    onClose,
}) => {
    return (
        <div className={b()}>
            <div className={b('content')}>{children}</div>
            <aside
                className={b('aside-left', { isOpen })}
            >
                <Card className={b('aside-container')} type="action">
                    <div className={b('aside-header')}>
                        <Text>{name}</Text>
                        <div className={b('header-close-icon')} onClick={onClose}>
                            <Xmark />
                        </div>
                    </div>
                    <MonacoEditor />
                </Card>
            </aside>
        </div>
    );
};