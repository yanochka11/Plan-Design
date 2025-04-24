import { TGLBModel, TGLBModelV2, TRotation } from "./types";
import { toDegrees } from "./utils";

export const TGLBModels: TGLBModel[] =
    [
        {
            "new_object_id": "sofa_1",
            "style": "modern",
            "material": "fabric",
            "size_in_meters": {
                "length": 2.5,
                "width": 1.0,
                "height": 0.8
            },
            "is_on_the_floor": true,
            "facing": "coffee_table_1",
            "placement": {
                "room_layout_elements": [
                    {
                        "layout_element_id": "middle of the room",
                        "preposition": "on"
                    }
                ],
                "objects_in_room": [
                    {
                        "object_id": "carpet_1",
                        "preposition": "under",
                        "is_adjacent": true
                    }
                ]
            },
            "rotation": {
                "z_angle": 180.0
            },
            "cluster": {
                "constraint_area": {
                    "x_neg": 0.5,
                    "x_pos": 0.5,
                    "y_neg": 0.5,
                    "y_pos": 0.5
                }
            },
            "position": {
                "x": 2.0,
                "y": 3.0,
                "z": 0.4
            }
        },
        {
            "new_object_id": "coffee_table_1",
            "style": "modern",
            "material": "wood",
            "size_in_meters": {
                "length": 1.0,
                "width": 0.8,
                "height": 0.5
            },
            "is_on_the_floor": true,
            "facing": "sofa_1",
            "placement": {
                "room_layout_elements": [
                    {
                        "layout_element_id": "north_wall",
                        "preposition": "on"
                    }
                ],
                "objects_in_room": []
            },
            "rotation": {
                "z_angle": 90.0
            },
            "cluster": {
                "constraint_area": {
                    "x_neg": 0.4,
                    "x_pos": 0.4,
                    "y_neg": 0.4,
                    "y_pos": 0.4
                }
            },
            "position": {
                "x": 1.5,
                "y": 2.0,
                "z": 0.25
            }
        },
        {
            "new_object_id": "armchair_1",
            "style": "modern",
            "material": "leather",
            "size_in_meters": {
                "length": 1.0,
                "width": 0.9,
                "height": 1.0
            },
            "is_on_the_floor": true,
            "facing": "coffee_table_1",
            "placement": {
                "room_layout_elements": [
                    {
                        "layout_element_id": "south_wall",
                        "preposition": "on"
                    }
                ],
                "objects_in_room": [
                    {
                        "object_id": "sofa_1",
                        "preposition": "left of",
                        "is_adjacent": true
                    }
                ]
            },
            "rotation": {
                "z_angle": 360.0
            },
            "cluster": {
                "constraint_area": {
                    "x_neg": 0.3,
                    "x_pos": 0.3,
                    "y_neg": 0.3,
                    "y_pos": 0.3
                }
            },
            "position": {
                "x": 3.0,
                "y": 1.0,
                "z": 0.5
            }
        },
        {
            "new_object_id": "carpet_1",
            "style": "plush",
            "material": "fabric",
            "size_in_meters": {
                "length": 3.0,
                "width": 2.0,
                "height": 0.1
            },
            "is_on_the_floor": true,
            "facing": "",
            "placement": {
                "room_layout_elements": [
                    {
                        "layout_element_id": "middle of the room",
                        "preposition": "on"
                    }
                ],
                "objects_in_room": []
            },
            "rotation": {
                "z_angle": 0.0
            },
            "cluster": {
                "constraint_area": {
                    "x_neg": 0.6,
                    "x_pos": 0.6,
                    "y_neg": 0.6,
                    "y_pos": 0.6
                }
            },
            "position": {
                "x": 2.5,
                "y": 2.5,
                "z": 0.05
            }
        }
    ]

export const TGLBModelsV2: TGLBModelV2[] = [
    {
        "new_object_id": "sofa_1",
        "size_in_meters": {
            "length": 3.77,
            "width": 1.29,
            "height": 0.98
        },
        "position": {
            "x": 5.83,
            "y": 5.73,
            "z": 0.0
        },
        "rotation_z": 90,
        "style": "Modern",
        "material": "leather",
        "color": "black"
    },
    {
        "new_object_id": "sofa_2",
        "size_in_meters": {
            "length": 3.77,
            "width": 1.29,
            "height": 0.98
        },
        "position": {
            "x": 3.33,
            "y": 9.98,
            "z": 0.0
        },
        "rotation_z": 0,
        "style": "Modern",
        "material": "leather",
        "color": "black"
    },
    {
        "new_object_id": "side table_1",
        "size_in_meters": {
            "length": 0.69,
            "width": 0.68,
            "height": 0.45
        },
        "position": {
            "x": 5.84,
            "y": 1.7,
            "z": 0.0
        },
        "rotation_z": 90,
        "style": "Modern",
        "material": "glass",
        "color": "black"
    },
    {
        "new_object_id": "armchair_1",
        "size_in_meters": {
            "length": 1.16,
            "width": 0.94,
            "height": 0.9
        },
        "position": {
            "x": 5.92,
            "y": 2.86,
            "z": 0.0
        },
        "rotation_z": 0,
        "style": "Modern",
        "material": "leather",
        "color": "black"
    },
    {
        "new_object_id": "rug_1",
        "size_in_meters": {
            "length": 6.91,
            "width": 4.54,
            "height": 0.02
        },
        "position": {
            "x": 3.37,
            "y": 5.75,
            "z": 0.0
        },
        "rotation_z": 90,
        "style": "Modern",
        "material": "wool",
        "color": "grey"
    },
    {
        "new_object_id": "coffee table_1",
        "size_in_meters": {
            "length": 1.12,
            "width": 0.68,
            "height": 0.41
        },
        "position": {
            "x": 2.93,
            "y": 3.79,
            "z": 0.0
        },
        "rotation_z": 0,
        "style": "Modern",
        "material": "glass",
        "color": "black"
    },
    {
        "new_object_id": "coffee table_2",
        "size_in_meters": {
            "length": 1.12,
            "width": 0.68,
            "height": 0.41
        },
        "position": {
            "x": 3.83,
            "y": 4.74,
            "z": 0.0
        },
        "rotation_z": 90,
        "style": "Modern",
        "material": "glass",
        "color": "black"
    },
    {
        "new_object_id": "coffee table_3",
        "size_in_meters": {
            "length": 1.12,
            "width": 0.68,
            "height": 0.41
        },
        "position": {
            "x": 3.79,
            "y": 6.9,
            "z": 0.0
        },
        "rotation_z": 90,
        "style": "Modern",
        "material": "glass",
        "color": "black"
    },
    {
        "new_object_id": "coffee table_4",
        "size_in_meters": {
            "length": 1.12,
            "width": 0.68,
            "height": 0.41
        },
        "position": {
            "x": 2.89,
            "y": 7.77,
            "z": 0.0
        },
        "rotation_z": 90,
        "style": "Modern",
        "material": "glass",
        "color": "black"
    },
    {
        "new_object_id": "floor lamp_1",
        "size_in_meters": {
            "length": 0.61,
            "width": 0.59,
            "height": 1.44
        },
        "position": {
            "x": 5.84,
            "y": 9.91,
            "z": 0.0
        },
        "rotation_z": 90,
        "style": "Modern",
        "material": "stainless steel",
        "color": "silver"
    },
    {
        "new_object_id": "floor plant_1",
        "size_in_meters": {
            "length": 0.8,
            "width": 0.61,
            "height": 0.82
        },
        "position": {
            "x": 1.06,
            "y": 3.99,
            "z": 0.0
        },
        "rotation_z": 0,
        "style": "Modern",
        "material": "ceramic pot",
        "color": "green"
    },
    {
        "new_object_id": "floor plant_2",
        "size_in_meters": {
            "length": 0.8,
            "width": 0.61,
            "height": 0.82
        },
        "position": {
            "x": 0.97,
            "y": 9.72,
            "z": 0.0
        },
        "rotation_z": 0,
        "style": "Modern",
        "material": "ceramic pot",
        "color": "green"
    },
    {
        "new_object_id": "armchair_2",
        "size_in_meters": {
            "length": 1.22,
            "width": 1.04,
            "height": 0.9
        },
        "position": {
            "x": 0.9,
            "y": 5.07,
            "z": 0.0
        },
        "rotation_z": 0,
        "style": "Modern",
        "material": "leather",
        "color": "black"
    },
    {
        "new_object_id": "armchair_3",
        "size_in_meters": {
            "length": 1.2,
            "width": 1.04,
            "height": 0.9
        },
        "position": {
            "x": 0.9,
            "y": 2.94,
            "z": 0.0
        },
        "rotation_z": 0,
        "style": "Modern",
        "material": "leather",
        "color": "black"
    },
    {
        "new_object_id": "sofa_3",
        "size_in_meters": {
            "length": 3.77,
            "width": 1.29,
            "height": 0.98
        },
        "position": {
            "x": 3.39,
            "y": 1.47,
            "z": 0.0
        },
        "rotation_z": 0,
        "style": "Modern",
        "material": "leather",
        "color": "black"
    },
    {
        "new_object_id": "armchair_4",
        "size_in_meters": {
            "length": 1.21,
            "width": 0.91,
            "height": 0.9
        },
        "position": {
            "x": 5.87,
            "y": 8.56,
            "z": 0.0
        },
        "rotation_z": 0,
        "style": "Modern",
        "material": "leather",
        "color": "black"
    },
    {
        "new_object_id": "side table_2",
        "size_in_meters": {
            "length": 0.69,
            "width": 0.67,
            "height": 0.45
        },
        "position": {
            "x": 1.06,
            "y": 1.7,
            "z": 0.0
        },
        "rotation_z": 0,
        "style": "Modern",
        "material": "glass",
        "color": "black"
    },
    {
        "new_object_id": "side table_3",
        "size_in_meters": {
            "length": 0.38,
            "width": 0.35,
            "height": 0.45
        },
        "position": {
            "x": 3.77,
            "y": 3.61,
            "z": 0.0
        },
        "rotation_z": 90,
        "style": "Modern",
        "material": "glass",
        "color": "black"
    },
    {
        "new_object_id": "side table_4",
        "size_in_meters": {
            "length": 0.37,
            "width": 0.32,
            "height": 0.45
        },
        "position": {
            "x": 3.74,
            "y": 8.02,
            "z": 0.0
        },
        "rotation_z": 0,
        "style": "Modern",
        "material": "glass",
        "color": "black"
    },
    {
        "new_object_id": "window_1",
        "size_in_meters": {
            "length": 4.23,
            "width": 0.66,
            "height": 1.4
        },
        "position": {
            "x": 3.79,
            "y": 0.26,
            "z": 1.0
        },
        "rotation_z": 0,
        "style": "Modern",
        "material": "aluminum",
        "color": "white"
    },
    {
        "new_object_id": "window_2",
        "size_in_meters": {
            "length": 5.23,
            "width": 0.66,
            "height": 1.4
        },
        "position": {
            "x": 8.05,
            "y": 5.8,
            "z": 1.0
        },
        "rotation_z": 90,
        "style": "Modern",
        "material": "aluminum",
        "color": "white"
    }
]



export const rotationSettings: Record<string, TRotation> = {
    "sofa_1": { x_angle: 0, y_angle: 0, z_angle: 0 },
    "armchair_1": { x_angle: 0, y_angle: 180, z_angle: 0 },
    "carpet_1": { x_angle: 0, y_angle: 0, z_angle: 0 },
    "coffee_table_1": { x_angle: 0, y_angle: 90, z_angle: 0 },
};

export const rotationSettings2: Record<string, TRotation> = {
    "sofa_1": { x_angle: 0, y_angle: 270, z_angle: 0 },
    "sofa_2": { x_angle: 0, y_angle: 0, z_angle: 0 },
    "side table_1": { x_angle: 0, y_angle: 90, z_angle: 0 },
    "armchair_1": { x_angle: 0, y_angle: 270, z_angle: 0 },
    "rug_1": { x_angle: 0, y_angle: 90, z_angle: 0 },
    "coffee table_1": { x_angle: 0, y_angle: 90, z_angle: 0 },
    "coffee table_2": { x_angle: 0, y_angle: 90, z_angle: 0 },
    "coffee table_3": { x_angle: 0, y_angle: 90, z_angle: 0 },
    "coffee table_4": { x_angle: 0, y_angle: 90, z_angle: 0 },
    "floor lamp_1": { x_angle: 0, y_angle: 270, z_angle: 0 },
    "floor plant_1": { x_angle: 0, y_angle: 0, z_angle: 0 },
    "floor plant_2": { x_angle: 0, y_angle: 0, z_angle: 0 },
    "armchair_2": { x_angle: 0, y_angle: 90, z_angle: 0 },
    "armchair_3": { x_angle: 0, y_angle: 90, z_angle: 0 },
    "sofa_3": { x_angle: 0, y_angle: 180, z_angle: 0 },
    "armchair_4": { x_angle: 0, y_angle: 270, z_angle: 0 },
    "side table_2": { x_angle: 0, y_angle: 90, z_angle: 0 },
    "side table_3": { x_angle: 0, y_angle: 90, z_angle: 0 },
    "side table_4": { x_angle: 0, y_angle: 0, z_angle: 0 },
    "window_1": { x_angle: 0, y_angle: 180, z_angle: 0 },
    "window_2": { x_angle: 0, y_angle: 270, z_angle: 0 }
};
