export interface ICoordinates { x: number, y: number, z: number }
export interface IPosition extends ICoordinates { };
export interface IRotation extends ICoordinates { };
export interface IScale {
    length: number,
    width: number,
    height: number
}

export interface ObjectData {
    size_in_meters: { length: number; width: number; height: number };
    position: { x: number; y: number; z: number };
    rotation: { z_angle: number };
    new_object_id: string;
    style: string;
}
