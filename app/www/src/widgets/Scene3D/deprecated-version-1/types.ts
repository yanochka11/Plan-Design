export interface TRotation {
    z_angle?: number,
    y_angle?: number,
    x_angle?: number
}

export interface TModelSize {
    length: number,
    width: number,
    height: number
};

export interface Position {
    x: number;
    y: number;
    z: number;
}

export interface TGLBModel {
    new_object_id: string,
    style: string,
    material: string,
    size_in_meters: TModelSize,
    is_on_the_floor: boolean,
    facing: string,
    placement: any,
    rotation: TRotation,
    cluster: any;
    position: Position
}


export interface TGLBModelV2 {
    new_object_id: string,
    size_in_meters: TModelSize,
    position: Position,
    rotation_z: number,
    style: string,
    material: string,
    color: string
}
