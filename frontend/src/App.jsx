import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { format, parseISO } from 'date-fns';

// REPLACE THIS with your actual Render URL if it differs slightly
const API_BASE_URL = "https://reint-wind-challenge.onrender.com/api/wind-data/";

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Default to the first week of Jan 2024 to match our Elexon dataset
  const [startDate, setStartDate] = useState('2024-01-01T00:00');
  const [endDate, setEndDate] = useState('2024-01-07T23:59');
  const [horizon, setHorizon] = useState(4); // Default 4 hours as per PDF

  useEffect(() => {
    fetchData();
  }, [startDate, endDate, horizon]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const startUtc = new Date(startDate).toISOString();
      const endUtc = new Date(endDate).toISOString();
      
      // Updated to use the Production Render URL
      const response = await axios.get(API_BASE_URL, {
        params: { start: startUtc, end: endUtc, horizon: horizon }
      });
      setData(response.data.data);
    } catch (error) {
      console.error("Error fetching data from Render Backend:", error);
    }
    setLoading(false);
  };

  // Format X-Axis ticks to look clean
  const formatXAxis = (tickItem) => {
    return format(parseISO(tickItem), 'HH:mm dd/MM/yy');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto bg-white rounded-xl shadow-lg p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-6 border-b pb-4">Wind Power Forecast Monitoring App</h1>
        
        {/* Controls Section - Replicating the PDF UI */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 bg-gray-100 p-5 rounded-lg border border-gray-200 shadow-sm">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Start Time</label>
            <input 
              type="datetime-local" 
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">End Time</label>
            <input 
              type="datetime-local" 
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Forecast Horizon: <span className="font-bold text-blue-600 bg-blue-100 px-2 py-1 rounded">{horizon}h</span>
            </label>
            <input 
              type="range" 
              min="0" max="48" step="1"
              value={horizon}
              onChange={(e) => setHorizon(e.target.value)}
              className="w-full h-2 bg-gray-300 rounded-lg appearance-none cursor-pointer mt-3"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-2 font-medium">
              <span>0h</span>
              <span>24h</span>
              <span>48h</span>
            </div>
          </div>
        </div>

        {/* Chart Section */}
        <div className="h-[500px] w-full border border-gray-100 rounded-xl p-2 bg-white shadow-sm">
          {loading ? (
            <div className="w-full h-full flex flex-col items-center justify-center text-gray-500">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
              <p className="font-semibold">Querying Render Backend...</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} vertical={false} />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={formatXAxis}
                  minTickGap={60}
                  tick={{ fontSize: 12, fill: '#6b7280' }}
                  tickMargin={10}
                />
                <YAxis 
                  label={{ value: 'Power (MW)', angle: -90, position: 'insideLeft', offset: -10 }}
                  tick={{ fill: '#6b7280' }} 
                />
                <Tooltip 
                  labelFormatter={(label) => format(parseISO(label), 'PPP p')}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Legend verticalAlign="top" height={40} iconType="circle" />
                <Line 
                  type="monotone" 
                  dataKey="actual_mw" 
                  name="Actual Generation" 
                  stroke="#2563eb" 
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{ r: 6, fill: '#2563eb', stroke: '#fff', strokeWidth: 2 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="forecast_mw" 
                  name="Forecasted Generation" 
                  stroke="#16a34a" 
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{ r: 6, fill: '#16a34a', stroke: '#fff', strokeWidth: 2 }}
                  connectNulls={true}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;