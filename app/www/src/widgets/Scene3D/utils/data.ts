import { SceneObject } from "../types/SceneTypes";

// Add the complete objects array from the JSON
export const data: SceneObject[] = [
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
  ];
  