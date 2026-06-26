import {useState, useEffect} from 'react'
import Label from '../components/Label.tsx'
import closeButton from '../assets/close-unhovered.png'
import closeButtonHovered from '../assets/close-hovered.png'
import fullScreen from '../assets/full-screen.png'

import { Link } from 'react-router'

type MainPanelProps = {
    time:string;
    setTicker: (val:string) => void;
}

type stockViewProps = {
    ticker?: string;
    weekHighPrice?:number;
    monthHighPrice?:number;
    yearHighPrice?:number;
    allHighPrice?:number;
    weekLowPrice?:number;
    monthLowPrice?:number;
    yearLowPrice?:number;
    allLowPrice?:number;
    weekChange?:number,
    monthChange?:number,
    yearChange?:number,
    allChange?:number,
    predictedPrice?:number
}

export default function MainPanel({time, setTicker}:MainPanelProps): React.ReactElement {    
    const [stockView, setStockView] = useState<stockViewProps>();
    const [isCloseHovered, setCloseHovered]  = useState<boolean>(false);

    const changeHovered = (isHovered: boolean):void => {
        setCloseHovered(isHovered);
    }

    const highlightTicker = (ticker:string):void  => {
        setTicker(ticker);
    }
    
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

    const TICKER_TO_STOCK: Record<string, string> = {
        'AAPL': 'apple',
        'AMZN': 'amazon',
        'MSFT': 'microsoft',
        'NVDA': 'nvidia',
    };

    const TIME_TO_WINDOW: Record<string, string> = {
        'All Time': 'alltime',
        '1 Year': 'year',
        '1 Month': 'month',
        '1 Week': 'week',
    };

    const getPlotUrl = (ticker: string | undefined, time: string): string | undefined => {
        if (!ticker) return undefined;
        const stock = TICKER_TO_STOCK[ticker];
        if (!stock) return undefined;
        const window = TIME_TO_WINDOW[time] || 'alltime';
        return `${API_URL}/plot/window/${stock}/${window}`;
    };

    useEffect(():void =>{
        fetch(`${API_URL}/analyze`)
        }, []);

    const showFullChart = (ticker:string, time:string) => {
        // TODO: Fix how to add this in the flow
        if (ticker === 'AAPL'){
            if(time === 'All Time' || time === '1 Year' || time === '1 Month' || time === '1 Week'){
                fetch(`${API_URL}/stocks/apple`)
                .then(res => res.json())
                .then(data => {
                setStockView({
                    ticker: data['ticker'],
                    weekHighPrice: data['weekly high'],
                    monthHighPrice: data['monthly high'],
                    yearHighPrice: data['yearly high'],
                    allHighPrice: data['all high'],
                    weekLowPrice: data['weekly low'],
                    monthLowPrice: data['monthly low'],
                    yearLowPrice: data['yearly low'],
                    allLowPrice: data['all low'],
                    allChange: data['all change'],
                    weekChange:data['weekly change'],
                    monthChange: data['monthly change'],
                    yearChange: data['yearly change'],
                    predictedPrice: data['predicted price']
                    })
                })
            }
        }
        else if(ticker === 'AMZN'){
            if(time === 'All Time' || time === '1 Year' || time === '1 Month' || time === '1 Week'){
                fetch(`${API_URL}/stocks/amazon`)
                .then(res => res.json())
                .then(data => {
                setStockView({
                    ticker: data['ticker'],
                    weekHighPrice: data['weekly high'],
                    monthHighPrice: data['monthly high'],
                    yearHighPrice: data['yearly high'],
                    allHighPrice: data['all high'],
                    weekLowPrice: data['weekly low'],
                    monthLowPrice: data['monthly low'],
                    yearLowPrice: data['yearly low'],
                    allLowPrice: data['all low'],
                    allChange: data['all change'],
                    weekChange:data['weekly change'],
                    monthChange: data['monthly change'],
                    yearChange: data['yearly change'],
                    predictedPrice: data['predicted price']
                    })
                })
            }
        }
        else if(ticker === 'MSFT'){
            if(time === 'All Time' || time === '1 Year' || time === '1 Month' || time === '1 Week'){
                fetch(`${API_URL}/stocks/microsoft`)
                .then(res => res.json())
                .then(data => {
                setStockView({
                    ticker: data['ticker'],
                    weekHighPrice: data['weekly high'],
                    monthHighPrice: data['monthly high'],
                    yearHighPrice: data['yearly high'],
                    allHighPrice: data['all high'],
                    weekLowPrice: data['weekly low'],
                    monthLowPrice: data['monthly low'],
                    yearLowPrice: data['yearly low'],
                    allLowPrice: data['all low'],
                    allChange: data['all change'],
                    weekChange:data['weekly change'],
                    monthChange: data['monthly change'],
                    yearChange: data['yearly change'],
                    predictedPrice: data['predicted price']
                    })
                })
            }
        }
        else if(ticker === 'NVDA'){
            if(time === 'All Time' || time === '1 Year' || time === '1 Month' || time === '1 Week'){
                fetch(`${API_URL}/stocks/nvidia`)
                .then(res => res.json())
                .then(data => {
                setStockView({
                    ticker: data['ticker'],
                    weekHighPrice: data['weekly high'],
                    monthHighPrice: data['monthly high'],
                    yearHighPrice: data['yearly high'],
                    allHighPrice: data['all high'],
                    weekLowPrice: data['weekly low'],
                    monthLowPrice: data['monthly low'],
                    yearLowPrice: data['yearly low'],
                    allLowPrice: data['all low'],
                    allChange: data['all change'],
                    weekChange:data['weekly change'],
                    monthChange: data['monthly change'],
                    yearChange: data['yearly change'],
                    predictedPrice: data['predicted price']
                    })
                })
            }
        }
        else{
             setStockView({ticker: ''})
        }
    }

    return (
        <>
        {/* MAIN SCREEN */}
        <div className="flex justify-center items-center flex-col h-[888px] w-screen bg-blue-100">

            {/* FULL CHART TOGGLE */}
            <div className={(stockView?.ticker === 'AAPL' || stockView?.ticker === 'AMZN' || stockView?.ticker === 'MSFT' || stockView?.ticker === 'NVDA') ? 
                                'flex flex-col justify-evenly items-start h-150 w-250 bg-gray-800 z-1 absolute rounded-4xl' : 
                                'hidden h-150 w-250 bg-gray-800 z-1 absolute rounded-4xl'}>

                {/*Stock Ticker*/}
                <div className='flex flex-row pl-5 pr-5 justify-between items-center w-full'>
                    <div className='flex flex-row justify-between items-center w-fit'>
                        <label className='text-white font-voces text-[2em] mr-3'>{stockView?.ticker === 'AMZN' ? 
                        'AMZN - Amazon.com, Inc.' : (stockView?.ticker === 'AAPL' ?     
                        'AAPL - Apple Inc.' : (stockView?.ticker === 'MSFT' ? 
                        'MSFT - Microsoft Corporation' : (stockView?.ticker === 'NVDA') ? 
                        'NVDA - NVIDIA Corporation': ''))}
                        </label>
                        <label className={time === 'All Time' ? (((stockView?.allChange ?? 0) > 0) ? 
                            'flex justify-center items-center text-black font-voces text-[1.2em] bg-green-300 rounded-4xl h-10 w-[110px]' : 
                            'flex justify-center items-center text-black font-voces text-[1.2em] bg-red-300 rounded-4xl h-10 w-[110px]') : (time === '1 Year' ? (((stockView?.yearChange ?? 0) > 0) ? 
                            'flex justify-center items-center text-black font-voces text-[1.2em] bg-green-300 rounded-4xl h-10 w-[110px]' : 
                            'flex justify-center items-center text-black font-voces text-[1.2em] bg-red-300 rounded-4xl h-10 w-[110px]') : (time === '1 Month' ? (((stockView?.monthChange ?? 0) > 0) ? 
                            'flex justify-center items-center text-black font-voces text-[1.2em] bg-green-300 rounded-4xl h-10 w-[110px]' : 
                            'flex justify-center items-center text-black font-voces text-[1.2em] bg-red-300 rounded-4xl h-10 w-[110px]'): (time === '1 Week' ? (((stockView?.weekChange ?? 0) > 0) ? 
                            'flex justify-center items-center text-black font-voces text-[1.2em] bg-green-300 rounded-4xl h-10 w-[110px]' : 
                            'flex justify-center items-center text-black font-voces text-[1.2em] bg-red-300 rounded-4xl h-10 w-[110px]'): '')))}>

                            {time === 'All Time' ? stockView?.allChange : 
                            (time === '1 Year' ? stockView?.yearChange : 
                            (time === '1 Month' ? stockView?.monthChange : 
                            (time === '1 Week' ? stockView?.weekChange : 0.00)))}%
                        </label>
                        <label className='flex justify-center items-center text-black font-voces text-[1em] bg-blue-300 rounded-4xl h-8 w-[80px] ml-4'>High</label>
                        <label className='flex justify-center items-center text-black font-voces text-[1em] bg-red-300 rounded-4xl h-8 w-[80px] ml-4'>Low</label>
                        <label className='flex justify-center items-center text-black font-voces text-[1em] bg-gray-300 rounded-4xl h-8 w-[80px] ml-4'>Next</label>
                    </div>
                    <img className='w-10 cursor-pointer' src={isCloseHovered ? closeButtonHovered : closeButton} 
                        onClick={():void => showFullChart('','')} 
                        onMouseEnter={():void => {changeHovered(true)}} 
                        onMouseLeave={():void => {changeHovered(false)}}/>
                </div>

                <div className='flex justify-evenly items-center h-1/2 w-full'>
                    <img className='h-full w-[760px] object-cover bg-gray-100 rounded-3xl cursor-pointer'
                    src={getPlotUrl(stockView?.ticker, time)}/>

                    <div className='flex flex-col justify-evenly items-center h-2/3 w-1/5'>
                        {/* Stock high/low price */}
                        <div className='flex flex-row justify-start items-center h-1/5 w-[150px] rounded-4xl'>
                            <label className='flex justify-center items-center bg-blue-300 font-voces text-[2em] rounded-bl-4xl rounded-tl-4xl h-full w-[50px]'>H</label>
                            <label className='flex flex-row justify-center items-center text-black font-voces text-[1.5em] h-full w-[100px] bg-gray-200 rounded-tr-4xl rounded-br-4xl'>
                                {time === 'All Time' ? 
                                stockView?.allHighPrice : ((time === '1 Year') ? 
                                stockView?.yearHighPrice : ((time === '1 Month') ? 
                                stockView?.monthHighPrice : ((time === '1 Week') ? 
                                stockView?.weekHighPrice : 0.00)))}
                            </label>
                        </div>

                        <div className='flex flex-row justify-start items-center h-1/5 w-[150px] rounded-4xl'>
                            <label className='flex justify-center items-center bg-red-300 font-voces text-[2em] rounded-bl-4xl rounded-tl-4xl h-full w-[50px]'>L</label>
                            <label className='flex flex-row justify-center items-center text-black font-voces text-[1.5em] h-full w-[100px] bg-gray-200 rounded-tr-4xl rounded-br-4xl'>
                               {time === 'All Time' ? 
                                stockView?.allLowPrice : ((time === '1 Year') ? 
                                stockView?.yearLowPrice : ((time === '1 Month') ? 
                                stockView?.monthLowPrice : ((time === '1 Week') ? 
                                stockView?.weekLowPrice : 0.00)))}
                            </label>
                        </div>

                        <div className='flex flex-row justify-start items-center h-1/5 w-[150px] rounded-4xl'>
                            <label className='flex justify-center items-center bg-gray-300 font-voces text-[2em] rounded-bl-4xl rounded-tl-4xl h-full w-[50px]'>N</label>
                            <label className='flex flex-row justify-center items-center text-black font-voces text-[1.5em] h-full w-[100px] bg-gray-200 rounded-tr-4xl rounded-br-4xl'>
                               {stockView?.predictedPrice}
                            </label>
                        </div>

                        <Link className='flex flex-row justify-evenly items-center bg-gray-200 pl-3 pr-3 pt-2 pb-2 w-37 rounded-4xl hover:cursor-pointer hover:bg-white duration-300' 
                               to={stockView?.ticker === 'AAPL' ? '/Apple' : stockView?.ticker === 'AMZN' ? '/Amazon': stockView?.ticker === 'MSFT' ? '/Microsoft' : stockView?.ticker === 'NVDA' ? '/Nvidia' : ''} 
                               onClick={():void => {highlightTicker(stockView?.ticker ?? '')}}>
                                <label className='text-[1.2em]'>Full Chart</label>
                                <img className='w-8' src={fullScreen}/>
                        </Link>
                    </div>
                </div>
                <div className='flex justify-start items-center h-1/3 w-full pl-3 pr-3'>
                     <img className='h-full w-[760px] object-cover bg-gray-100 rounded-3xl cursor-pointer'
                    src={getPlotUrl(stockView?.ticker, time)}/>
                </div>
            </div>

            {/* UPPER MAIN SCREEN */}
            <div className="flex justify-evenly items-center flex-row h-1/2 w-screen pt-3.5 pb-3.5">
                <div className='h-full flex flex-col items-start
                                hover:scale-101 duration-300'>
                    <Label text='Amazon.com, Inc.'/>
                    <div className="h-full w-2xl" onClick={():void => showFullChart('AMZN',time)}>
                        <img className='h-full w-full object-cover bg-gray-100 rounded-b-3xl rounded-tr-3xl cursor-pointer' 
                        src={time === "All Time" ? `${API_URL}/plot/window/amazon/alltime` : 
                        (time === "1 Year" ? `${API_URL}/plot/window/amazon/year` : 
                        (time === "1 Month" ? `${API_URL}/plot/window/amazon/month` : 
                        (time === "1 Week" ? `${API_URL}/plot/window/amazon/week` : `${API_URL}/plot/window/amazon/alltime`)))}/>
                    </div>
                </div>
                <div className='h-full flex flex-col justify-between items-start 
                                hover:scale-101 duration-300'>
                    <Label text='Apple Inc.'/>
                    <div className="h-full w-2xl" onClick={():void => showFullChart('AAPL',time)}>
                        <img className='h-full w-full object-cover bg-gray-100 rounded-b-3xl rounded-tr-3xl cursor-pointer' 
                        src={time === "All Time" ? `${API_URL}/plot/window/apple/alltime`: 
                        (time === "1 Year" ? `${API_URL}/plot/window/apple/year` : 
                        (time === "1 Month" ? `${API_URL}/plot/window/apple/month` : 
                        (time === "1 Week" ? `${API_URL}/plot/window/apple/week` : `${API_URL}/plot/window/apple/alltime`)))}/>
                    </div>
                </div>
            </div>

            {/* LOWER MAIN SCREEN */}
            <div className="flex justify-evenly items-center flex-row h-1/2 w-screen pt-3.5 pb-3.5">
                <div className='h-full flex flex-col justify-between items-start 
                                hover:scale-101 duration-300'>
                    <Label text='Microsoft Corporation'/>
                    <div className="h-full w-2xl" onClick={():void => showFullChart('MSFT',time)}>
                        <img className='h-full w-full object-cover bg-gray-100 rounded-b-3xl rounded-tr-3xl cursor-pointer'
                        src={time === "All Time" ? `${API_URL}/plot/window/microsoft/alltime`: 
                        (time === "1 Year" ? `${API_URL}/plot/window/microsoft/year`: 
                        (time === "1 Month" ? `${API_URL}/plot/window/microsoft/month` : 
                        (time === "1 Week" ? `${API_URL}/plot/window/microsoft/week` : `${API_URL}/plot/window/microsoft/alltime`)))}/>
                    </div>
                </div>
                <div className='h-full flex flex-col justify-between items-start 
                                hover:scale-101 duration-300'>
                    <Label text='NVIDIA Corporation'/>
                    <div className="h-full w-2xl" onClick={():void => showFullChart('NVDA',time)}>
                        <img className='h-full w-full object-cover bg-gray-100 rounded-b-3xl rounded-tr-3xl cursor-pointer'
                        src={time === "All Time" ? `${API_URL}/plot/window/nvidia/alltime`: 
                        (time === "1 Year" ? `${API_URL}/plot/window/nvidia/year` : 
                        (time === "1 Month" ? `${API_URL}/plot/window/nvidia/month` : 
                        (time === "1 Week" ? `${API_URL}/plot/window/nvidia/week` : `${API_URL}/plot/window/nvidia/alltime`)))}/>
                    </div>
                </div>
            </div>
        </div>
        </>
    )
}