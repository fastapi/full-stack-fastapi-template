import React, { useState } from 'react';
import {TrendingDown, TrendingUp} from "lucide-react";


export function BrandAwarenessScoreCurrentScore() {
    /* brand awareness score */
    const [currentScore, setCurrentScore] = useState(7.8);
    const [previousScore, setPreviousScore] = useState(7.2);

    const getTrend = () => {
        const diff = currentScore - previousScore;
        if (Math.abs(diff) < 0.05) return 'flat';
        return diff > 0 ? 'up' : 'down';
    };

    const getTrendIcon = () => {
        const trend = getTrend();
        const iconClass = "h-6 w-6";

        switch(trend) {
            case 'up':
                return <TrendingUp className={`${iconClass} text-green-600`} />;
            case 'down':
                return <TrendingDown className={`${iconClass} text-red-600`} />;
            default:
                return <Minus className={`${iconClass} text-gray-600`} />;
        }
    };

    const getTrendColor = () => {
        const trend = getTrend();
        switch(trend) {
            case 'up': return 'text-green-600';
            case 'down': return 'text-red-600';
            default: return 'text-gray-600';
        }
    };


    return (
        /* Current Score */
        <div className="rounded-md bg-gradient-to-b p-6 border border-gray-200 h-full w-full">
            <div className="flex justify-start">
                <h3 className="text-md font-semibold mb-4">Latest Score</h3>
            </div>
            <div className="flex items-center justify-center gap-4">
                <div className="text-6xl font-bold text-blue-600">
                    {currentScore.toFixed(1)}
                </div>
                <div className="flex flex-col items-center">
                    {getTrendIcon()}
                    <span className={`text-sm font-medium ${getTrendColor()}`}>
                                                    {Math.abs(currentScore - previousScore).toFixed(2)}
                                                </span>
                </div>
            </div>
            <p className="text-center text-sm text-gray-500 mt-2">
                {getTrend() === 'up' ? 'Improving' : getTrend() === 'down' ? 'Declining' : 'Stable'} from
                previous period
            </p>
        </div>
    );
}