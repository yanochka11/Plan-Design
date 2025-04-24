export interface Size {
    length: number;
    width: number;
    height: number;
}

export interface Rotation {
    z_angle: number;
}

export interface Position {
    x: number;
    y: number;
    z: number;
}

export interface ConstraintArea {
    x_neg: number;
    x_pos: number;
    y_neg: number;
    y_pos: number;
}

export interface Cluster {
    constraint_area: ConstraintArea;
}

export interface LayoutElement {
    layout_element_id: string;
    preposition: string;
}

export interface ObjectInRoom {
    object_id: string;
    preposition: string;
    is_adjacent: boolean;
}

export interface Placement {
    room_layout_elements: LayoutElement[];
    objects_in_room: ObjectInRoom[];
}

export interface SceneObject {
    new_object_id: string;
    style: string;
    material: string;
    size_in_meters: Size;
    is_on_the_floor: boolean;
    facing: string;
    placement: Placement;
    rotation: Rotation;
    cluster: Cluster;
    position: Position;
}
