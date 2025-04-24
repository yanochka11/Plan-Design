
// Компонент кнопки закрытия
export const CloseButton: React.FC<{
    x: number;
    y: number;
    onClick: () => void;
}> = ({ x, y, onClick }) => {
    return (
        <g
            transform={`translate(${x}, ${y})`}
            onClick={(e) => {
                e.stopPropagation();
                onClick();
            }}
            style={{ cursor: 'pointer' }}
        >
            <circle
                cx={0}
                cy={0}
                r={12}
                fill="#FF5555"
                stroke="#FFFFFF"
                strokeWidth={2}
            />
            <line
                x1={-6}
                y1={-6}
                x2={6}
                y2={6}
                stroke="#FFFFFF"
                strokeWidth={2}
                strokeLinecap="round"
            />
            <line
                x1={-6}
                y1={6}
                x2={6}
                y2={-6}
                stroke="#FFFFFF"
                strokeWidth={2}
                strokeLinecap="round"
            />
        </g>
    );
};