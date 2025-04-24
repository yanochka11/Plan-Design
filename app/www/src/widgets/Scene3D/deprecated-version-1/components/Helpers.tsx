import { Fragment } from "react"

export const Helpers = () => {
    return (
        <Fragment>
            <axesHelper args={[10]} />
            <gridHelper args={[10, 10, '#999', '#555']} rotation={[Math.PI / 2, 0, 0]} />
        </Fragment>
    )
}