import { ColorsDisctionary } from "./types"

export const isTouchDevice = (): boolean => {
    return (
        'ontouchstart' in window ||
        navigator.maxTouchPoints > 0 ||
        (navigator as any).msMaxTouchPoints > 0
    );
};

export const colors: ColorsDisctionary = {
    "TV stand": "#FF0000",  //# Red
    "bar counter": "#0000FF",  //# Blue
    "bench": "#FFFF00",  //# Yellow
    "bookshelf": "#FFBFBF",  //# Light Pink
    "cabinet": "#00FF00",  //# Green
    "chair": "#FFA500",  //# Orange
    "chair-bed": "#40E0D0",  //# Turquoise
    "coffee table": "#272643",  //# Dark Slate Blue
    "desk": "#FFD9BF",  //# Light Peach
    "dining table": "#8B00FF",  //# Violet
    "fireplace": "#FF9400",  //# Orange-ish
    "floor lamp": "#5500FF",  //# Purple
    "floor plant": "#29922C",  //# Green
    "floor vase": "#FF6347",  //# Tomato
    "kitchen island": "#ADFF2F",  //# Green Yellow
    "modular kitchen": "#FF7F50",  //# Coral
    "ottoman": "#AFCC43",  //# Lime Green
    "rocking chair": "#FF8C00",  //# Dark Orange
    "rug": "#BAE8E8",  //# Light Blue
    "shelves": "#C71585",  //# Medium Violet Red
    "side table": "#00BFFF",  //# Deep Sky Blue
    "sideboard": "#DA70D6",  //# Orchid
    "sofa": "#FF00FF",  //# Magenta
    "stool": "#DC143C",  //# Crimson
    "wardrobe": "#552743"   //# Violet dark
}

export const testObjects = [
    {
        "label": "sofa",
        "coordinates": {
            "x": 599.5,
            "y": 322.0,
            "width": 134,
            "height": 303
        }
    },
    {
        "label": "dining table",
        "coordinates": {
            "x": 286.5,
            "y": 364.0,
            "width": 131,
            "height": 305
        }
    },
    {
        "label": "chair",
        "coordinates": {
            "x": 398.5,
            "y": 271.0,
            "width": 64,
            "height": 63
        }
    },
    {
        "label": "chair",
        "coordinates": {
            "x": 398.5,
            "y": 358.0,
            "width": 65,
            "height": 66
        }
    },
    {
        "label": "chair",
        "coordinates": {
            "x": 398.5,
            "y": 444.0,
            "width": 65,
            "height": 62
        }
    },
    {
        "label": "chair",
        "coordinates": {
            "x": 179.5,
            "y": 271.0,
            "width": 75,
            "height": 64
        }
    },
    {
        "label": "chair",
        "coordinates": {
            "x": 179.5,
            "y": 359.0,
            "width": 77,
            "height": 57
        }
    },
    {
        "label": "chair",
        "coordinates": {
            "x": 179.5,
            "y": 443.0,
            "width": 78,
            "height": 63
        }
    },
    {
        "label": "shelves",
        "coordinates": {
            "x": 218.5,
            "y": 70.0,
            "width": 232,
            "height": 52
        }
    },
    {
        "label": "bar counter",
        "coordinates": {
            "x": 756.5,
            "y": 691.0,
            "width": 385,
            "height": 124
        }
    },
    {
        "label": "stool",
        "coordinates": {
            "x": 672.5,
            "y": 589.0,
            "width": 58,
            "height": 62
        }
    },
    {
        "label": "stool",
        "coordinates": {
            "x": 756.5,
            "y": 588.0,
            "width": 58,
            "height": 58
        }
    },
    {
        "label": "stool",
        "coordinates": {
            "x": 848.5,
            "y": 587.0,
            "width": 55,
            "height": 56
        }
    },
    {
        "label": "stool",
        "coordinates": {
            "x": 978.5,
            "y": 704.0,
            "width": 52,
            "height": 62
        }
    },
    {
        "label": "coffee table",
        "coordinates": {
            "x": 751.5,
            "y": 321.0,
            "width": 122,
            "height": 145
        }
    },
    {
        "label": "rug",
        "coordinates": {
            "x": 755.5,
            "y": 323.0,
            "width": 335,
            "height": 316
        }
    },
    {
        "label": "chair",
        "coordinates": {
            "x": 895.5,
            "y": 233.0,
            "width": 150,
            "height": 149
        }
    },
    {
        "label": "window",
        "coordinates": {
            "x": 12.5,
            "y": 218.0,
            "width": 14,
            "height": 133
        }
    },
    {
        "label": "window",
        "coordinates": {
            "x": 12.5,
            "y": 358.0,
            "width": 15,
            "height": 141
        }
    },
    {
        "label": "window",
        "coordinates": {
            "x": 13.5,
            "y": 500.0,
            "width": 15,
            "height": 138
        }
    },
    {
        "label": "window",
        "coordinates": {
            "x": 13.5,
            "y": 650.0,
            "width": 14,
            "height": 154
        }
    },
    {
        "label": "window",
        "coordinates": {
            "x": 985.5,
            "y": 13.0,
            "width": 85,
            "height": 16
        }
    },
    {
        "label": "window",
        "coordinates": {
            "x": 871.5,
            "y": 13.0,
            "width": 138,
            "height": 15
        }
    },
    {
        "label": "window",
        "coordinates": {
            "x": 734.5,
            "y": 13.0,
            "width": 130,
            "height": 16
        }
    },
    {
        "label": "window",
        "coordinates": {
            "x": 614.5,
            "y": 13.0,
            "width": 104,
            "height": 16
        }
    },
    {
        "label": "window",
        "coordinates": {
            "x": 504.5,
            "y": 13.0,
            "width": 113,
            "height": 15
        }
    }
]
