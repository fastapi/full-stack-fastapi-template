import React, { useState, useEffect } from 'react';
import {Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle} from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Calendar, ChartLine, ChartColumnBig } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';


export function BrandAwarenessScoreHistoricalView() {

    const [customDateRange, setCustomDateRange] = useState({
        start: '',
        end: ''
    });
    const [showCustomDate, setShowCustomDate] = useState(false);
    const [historicalData, setHistoricalData] = useState<Array<{
        week: string;
        date: string;
        score: number;
        growthRate: number;
    }>>([]);
    const [chartType, setChartType] = useState('line');
    const [timeRange, setTimeRange] = useState('1month');


    // Mock data generator based on time range
    const generateMockData = (range) => {
        const dataPoints = {
            '1month': 4,
            '1quarter': 13,
            '1year': 52,
            'ytd': 8
        };

        const points = dataPoints[range] || 4;
        const data = [];
        const today = new Date();

        for (let i = points - 1; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - (i * 7));

            const weekLabel = `Week ${points - i}`;
            const dateStr = `${date.getMonth() + 1}/${date.getDate()}`;

            // Generate score with some variance
            const baseScore = 6.5 + (points - i) * 0.15 + (Math.random() - 0.5) * 0.4;
            const score = Math.min(10, Math.max(0, baseScore));

            // Calculate growth rate
            const growthRate = i === points - 1
                ? 0
                : ((score - data[data.length - 1]?.score) / data[data.length - 1]?.score * 100) || 0;

            data.push({
                week: weekLabel,
                date: dateStr,
                score: parseFloat(score.toFixed(2)),
                growthRate: parseFloat(growthRate.toFixed(2))
            });
        }

        return data;
    };

    // Generate data when timeRange changes
    useEffect(() => {
        const data = generateMockData(timeRange);
        setHistoricalData(data);
    }, [timeRange]);

    // Custom tooltip for charts
    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                    <p className="text-sm font-medium">{payload[0].payload.date}</p>
                    <p className="text-sm text-blue-600">
                        Score: <span className="font-bold">{payload[0].value}</span>
                    </p>
                    {payload[1] && (
                        <p className={`text-sm ${payload[1].value >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            Growth: <span className="font-bold">{payload[1].value.toFixed(2)}%</span>
                        </p>
                    )}
                </div>
            );
        }
        return null;
    };

    return (
        <div className="rounded-md bg-gradient-to-b p-6 border border-gray-200 h-full w-full">
            <h3 className="text-md font-semibold mb-4">Historical Trends</h3>
            {/* Time Range Selection */}
            <div className="space-y-4 mb-6">
                <div className="flex flex-wrap items-center gap-3">
                    <Tabs defaultValue="1month" onValueChange={(value) => {
                        if (value === 'custom') {
                            setShowCustomDate(true);
                        } else {
                            setTimeRange(value);
                            setShowCustomDate(false);
                        }
                    }}>
                        <TabsList className="grid w-full grid-cols-4 ">
                            <TabsTrigger value="1month">1M</TabsTrigger>
                            <TabsTrigger value="1quarter">1Q</TabsTrigger>
                            <TabsTrigger value="1year">1Y</TabsTrigger>
                            <TabsTrigger value="ytd">YTD</TabsTrigger>
                        </TabsList>
                    </Tabs>
                    <Button
                        variant={showCustomDate ? 'default' : 'outline'}
                        onClick={() => setShowCustomDate(!showCustomDate)}
                        size="sm"
                    >
                        <Calendar className="h-4 w-4 mr-2"/>
                        Time Range
                    </Button>

                    {/* Chart Type Selection */}
                    <div className="ml-auto">
                        <Tabs defaultValue="line" onValueChange={setChartType}>
                            <TabsList className="bg-transparent rounded-none border-b w-full justify-start h-auto p-0">
                                <TabsTrigger
                                    value="line"
                                    className="bg-transparent rounded-none shadow-none px-4 py-2
                                                data-[state=active]:bg-transparent data-[state=active]:shadow-none
                                                border-b-2 border-transparent data-[state=active]:border-primary"
                                >
                                    <ChartLine className="h-4 w-4 mr-2"/>
                                    Line
                                </TabsTrigger>
                                <TabsTrigger
                                    value="bar"
                                    className="bg-transparent rounded-none shadow-none px-4 py-2
                                                data-[state=active]:bg-transparent data-[state=active]:shadow-none
                                                border-b-2 border-transparent data-[state=active]:border-primary"
                                >
                                    <ChartColumnBig className="h-4 w-4 mr-2"/>
                                    Bar
                                </TabsTrigger>
                            </TabsList>
                        </Tabs>
                    </div>
                </div>

                {/* Custom Date Range Inputs */}
                {showCustomDate && (
                    <div className="flex gap-3 items-center p-4 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                            <label
                                className="text-sm font-medium text-gray-700 block mb-1">
                                Start Date
                            </label>
                            <input
                                type="date"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                value={customDateRange.start}
                                onChange={(e) => setCustomDateRange({
                                    ...customDateRange,
                                    start: e.target.value
                                })}
                            />
                        </div>
                        <div className="flex-1">
                            <label
                                className="text-sm font-medium text-gray-700 block mb-1">
                                End Date
                            </label>
                            <input
                                type="date"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                value={customDateRange.end}
                                onChange={(e) => setCustomDateRange({
                                    ...customDateRange,
                                    end: e.target.value
                                })}
                            />
                        </div>
                        <Button
                            className="self-end"
                            onClick={() => {
                                // Here you would fetch data based on custom range
                                console.log('Fetch data for range:', customDateRange);
                            }}
                        >
                            Apply
                        </Button>
                    </div>
                )}

                {/* Chart Display */}
                <div className="w-full h-96 bg-gray-50 rounded-lg p-4">
                    <ResponsiveContainer width="100%" height="100%">
                        {chartType === 'line' ? (
                            <LineChart data={historicalData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                                <XAxis
                                    dataKey="date"
                                    stroke="#6b7280"
                                    style={{ fontSize: '12px' }}
                                />
                                <YAxis
                                    yAxisId="left"
                                    domain={[0, 10]}
                                    stroke="#3b82f6"
                                    style={{ fontSize: '12px' }}
                                    label={{ value: 'Awareness Score', angle: -90, position: 'insideLeft', style: { fontSize: '12px' } }}
                                />
                                <YAxis
                                    yAxisId="right"
                                    orientation="right"
                                    stroke="#22c55e"
                                    style={{ fontSize: '12px' }}
                                    label={{ value: 'Growth Rate (%)', angle: 90, position: 'insideRight', style: { fontSize: '12px' } }}
                                />
                                <Tooltip content={<CustomTooltip />} />
                                <Legend />
                                <Line
                                    yAxisId="left"
                                    type="monotone"
                                    dataKey="score"
                                    stroke="#3b82f6"
                                    strokeWidth={3}
                                    dot={{ fill: '#3b82f6', r: 4 }}
                                    activeDot={{ r: 6 }}
                                    name="Awareness Score"
                                />
                                <Line
                                    yAxisId="right"
                                    type="monotone"
                                    dataKey="growthRate"
                                    stroke="#22c55e"
                                    strokeWidth={2}
                                    strokeDasharray="5 5"
                                    dot={{ fill: '#22c55e', r: 3 }}
                                    name="Growth Rate %"
                                />
                            </LineChart>
                        ) : (
                            <BarChart data={historicalData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                                <XAxis
                                    dataKey="date"
                                    stroke="#6b7280"
                                    style={{ fontSize: '12px' }}
                                />
                                <YAxis
                                    yAxisId="left"
                                    domain={[0, 10]}
                                    stroke="#3b82f6"
                                    style={{ fontSize: '12px' }}
                                    label={{ value: 'Awareness Score', angle: -90, position: 'insideLeft', style: { fontSize: '12px' } }}
                                />
                                <YAxis
                                    yAxisId="right"
                                    orientation="right"
                                    stroke="#22c55e"
                                    style={{ fontSize: '12px' }}
                                    label={{ value: 'Growth Rate (%)', angle: 90, position: 'insideRight', style: { fontSize: '12px' } }}
                                />
                                <Tooltip content={<CustomTooltip />} />
                                <Legend />
                                <Bar
                                    yAxisId="left"
                                    dataKey="score"
                                    fill="#3b82f6"
                                    name="Awareness Score"
                                    radius={[8, 8, 0, 0]}
                                />
                                <Bar
                                    yAxisId="right"
                                    dataKey="growthRate"
                                    fill="#22c55e"
                                    name="Growth Rate %"
                                    radius={[8, 8, 0, 0]}
                                />
                            </BarChart>
                        )}
                    </ResponsiveContainer>
                </div>

                {/* Data Summary */}
                <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div>
                        <div className="text-sm text-gray-500">Average Score</div>
                        <div className="text-xl font-bold text-gray-600">
                            {historicalData.length > 0
                                ? (historicalData.reduce((acc, curr) => acc + curr.score, 0) / historicalData.length).toFixed(2)
                                : '0.00'}
                        </div>
                    </div>
                    <div>
                        <div className="text-sm text-gray-500">Highest Score</div>
                        <div className="text-xl font-bold text-gray-600">
                            {historicalData.length > 0
                                ? Math.max(...historicalData.map(d => d.score)).toFixed(2)
                                : '0.00'}
                        </div>
                    </div>
                    <div>
                        <div className="text-sm text-gray-500">Lowest Score</div>
                        <div className="text-xl font-bold text-gray-600">
                            {historicalData.length > 0
                                ? Math.min(...historicalData.map(d => d.score)).toFixed(2)
                                : '0.00'}
                        </div>
                    </div>
                    <div>
                        <div className="text-sm text-gray-500">Avg Growth</div>
                        <div className="text-xl font-bold text-gray-600">
                            {historicalData.length > 0
                                ? (historicalData.reduce((acc, curr) => acc + curr.growthRate, 0) / historicalData.length).toFixed(2)
                                : '0.00'}%
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}