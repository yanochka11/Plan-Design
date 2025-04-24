import { Message } from "../../shared/types";

export const GREETING_ROBOT_MESSAGE: Message = { direction: "robot", text: "Привет, я виртуальный помощник Plan Design. Я помогу вам собрать расстановку вашей мечты. Составьте свой запрос, чтобы начать работу" };

export const getMessageList = (): Message[] => {
    const storagedObjectString = localStorage.getItem('design') ?? '{}';
    const storagedObject = JSON.parse(storagedObjectString);

    const messages: Message[] = [];

    messages.push(GREETING_ROBOT_MESSAGE);

    if (storagedObject.username) {
        messages.push({ direction: 'user', text: storagedObject.username });
    } else {
        return messages;
    }

    return messages;
};
