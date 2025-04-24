export interface Coordinates {
    x: number;
    y: number;
    width: number;
    height: number;
}

export type Furniture =
    "TV stand" |
    "bar counter" |
    "bench" |
    "bookshelf" |
    "cabinet" |
    "chair" |
    "chair-bed" |
    "coffee table" |
    "desk" |
    "dining table" |
    "fireplace" |
    "floor lamp" |
    "floor plant" |
    "floor vase" |
    "kitchen island" |
    "modular kitchen" |
    "ottoman" |
    "rocking chair" |
    "rug" |
    "shelves" |
    "side table" |
    "sideboard" |
    "sofa" |
    "stool" |
    "wardrobe" |
    "window";

export interface PlainSVGObjectData {
    rotation_z: number,
    style: string,
    material: string,
    color: string
    new_object_id: string
    size_in_meters: {length: number, width: number, height: number}
    position: {x: number, y: number, z: number}
}

export interface RoomLayoutProps {
    initialObjects: PlainSVGObjectData[];
}

export interface PlainSVGDataResponse {
    image: string;
    annotations: PlainSVGObjectData[];
}

export type ColorsDisctionary = Record<Furniture, string>;
