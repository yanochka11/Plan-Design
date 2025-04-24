import React, { useState } from "react";
import { PreparedScenesTab } from "./components/PreparedScenes/PreparedScenes";
import { FurnitureComponent, Generate, JsonEditor } from "./components";
import { Flex, SegmentedRadioGroup, Button } from "@gravity-ui/uikit";
import block from "bem-cn-lite";
import './Sidebar.scss';

const b = block('sidebar');

export const Sidebar: React.FC<{
  isOpen: boolean;
  onToggle: () => void;
  onLoadScene: (sceneData: any) => void;
  onGenerateScene: (prompt: string) => void;
  onUpdateFromJSON: (jsonData: any) => void;
  sceneJSON: string;
}> = ({ isOpen, onToggle, onLoadScene, onGenerateScene, onUpdateFromJSON, sceneJSON }) => {
  const [activeTab, setActiveTab] = useState("furniture"); // "furniture", "scenes", "generate", "json"

  return (
    <div className={b({ open: isOpen })}>
      {isOpen ? (
        <Flex
          className={b('content')}
          direction="column"
        >
          <Flex justifyContent="space-between" alignItems="center">
            <SegmentedRadioGroup name={'tabs'} defaultValue="furniture" onUpdate={(value) => { setActiveTab(value) }} width="auto">
              <SegmentedRadioGroup.Option value="furniture" content="Мебель" />
              {/* <SegmentedRadioGroup.Option value="scenes" content="Готовые решения" /> */}
              {/* <SegmentedRadioGroup.Option value="generate" content="Генерация" /> */}
              <SegmentedRadioGroup.Option value="json" content="Json" />
            </SegmentedRadioGroup>
          </Flex>

          <Flex direction="column" className={b('body')}>
            {activeTab === "furniture" && (<FurnitureComponent />)}
            {activeTab === "scenes" && (<PreparedScenesTab onLoadScene={onLoadScene} />)}
            {activeTab === "generate" && (<Generate onGenerateScene={onGenerateScene} />)}
            {activeTab === "json" && (<JsonEditor onUpdateFromJSON={onUpdateFromJSON} sceneJSON={sceneJSON} />)}
          </Flex>
        </Flex>
      ) : (
        <Button
          className={b('toggle-button')}
          onClick={onToggle}
          view="action"
        >
          «
        </Button>
      )}
    </div>
  );
};
