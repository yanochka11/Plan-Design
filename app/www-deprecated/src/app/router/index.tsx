import { createBrowserRouter } from "react-router-dom";
import { TextAreaPage } from "../../pages";

export const router = createBrowserRouter([
    {
      path: "/",
      element: <TextAreaPage/>,
    },
  ]);
  