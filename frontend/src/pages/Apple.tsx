const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

type AppleProps = {
    time:string;
}

export default function Apple({time}:AppleProps):React.ReactElement{
    const timeMap: Record<string, string> = {
        'All Time': 'alltime',
        '1 Year': 'year',
        '1 Month': 'month',
        '1 Week': 'week',
    };
    const window = timeMap[time] || 'alltime';

    return (
        <>
            <iframe
                className="flex flex-col justify-center items-center h-[888px] w-screen bg-blue-100"
                src={`${API_URL}/chart/plotly/apple/${window}`}
            />
        </>
    )
}