import { Flex } from "@gravity-ui/uikit"
import { Chat } from "../../widgets/Chat"
import block from "bem-cn-lite";
import './Home.scss';

const b = block('home')
export const Home = () => {
    return (
        <Flex direction="column" alignItems="center" justifyContent="center" className={b()}>
            <Chat />
        </Flex>
    )
}