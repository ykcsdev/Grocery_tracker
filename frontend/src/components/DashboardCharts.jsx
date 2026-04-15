import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Droplet } from 'lucide-react';
import { API_BASE_URL } from '../config';

const COLORS = ['#3b82f6', '#22c55e', '#f97316', '#a855f7', '#ef4444', '#14b8a6'];

const DashboardCharts = ({ refreshTrigger }) => {
  const [pieData, setPieData] = useState([]);
  const [lineData, setLineData] = useState([]);
  const [leaks, setLeaks] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Pie Chart: Top items by category
        const pieRes = await axios.get(`${API_BASE_URL}/receipts/topItemsByCategory`);
        const formattedPie = pieRes.data.map(item => ({
          name: item.category || 'Uncategorized',
          value: parseFloat(item.total_amount_spent_in_category)
        }));
        setPieData(formattedPie);

        // Line Chart: Daily spending
        const lineRes = await axios.get(`${API_BASE_URL}/dashboard/daily-spending`);
        setLineData(lineRes.data);

        // Money Leaks
        const leaksRes = await axios.get(`${API_BASE_URL}/dashboard/money-leaks`);
        setLeaks(leaksRes.data);
      } catch (error) {
        console.error("Error fetching charts data", error);
      }
    };
    fetchData();
  }, [refreshTrigger]);

  return (
    <div className="chart-grid">
      
      {/* Category Pie Chart */}
      <div className="card animate-fade-in" style={{ animationDelay: '0.2s', height: '350px' }}>
        <h2 className="card-title">Spending by Category</h2>
        <div style={{ height: 'calc(100% - 2rem)' }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={5}
                dataKey="value"
                stroke="none"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <RechartsTooltip formatter={(value) => `€${value.toFixed(2)}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Spending Trend Line Chart */}
      <div className="card animate-fade-in" style={{ animationDelay: '0.3s', height: '350px' }}>
        <h2 className="card-title">Daily Spending Trend</h2>
        <div style={{ height: 'calc(100% - 2rem)' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={lineData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="date" tick={{fontSize: 12, fill: '#64748b'}} tickLine={false} axisLine={false} />
              <YAxis tick={{fontSize: 12, fill: '#64748b'}} tickLine={false} axisLine={false} tickFormatter={(v) => `€${v}`} />
              <RechartsTooltip 
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                formatter={(value) => [`€${value}`, 'Amount']}
              />
              <Line 
                type="monotone" 
                dataKey="amount" 
                stroke="#3b82f6" 
                strokeWidth={3}
                dot={{ r: 4, fill: '#3b82f6', strokeWidth: 0 }}
                activeDot={{ r: 6, fill: '#ef4444', strokeWidth: 2, stroke: '#fff' }} /* Spikes highlighted on hover */
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Money Leak Widget */}
      <div className="card leak-widget animate-fade-in" style={{ animationDelay: '0.4s' }}>
        <h2 className="card-title">
          <Droplet size={20} color="var(--color-red)" />
          "Money Leaks" (Frequent Small Expenses)
        </h2>
        {leaks.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)' }}>No significant leaks detected this month.</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            {leaks.map((leak, i) => (
              <div key={i} style={{ 
                padding: '1rem', 
                backgroundColor: 'var(--color-red-light)', 
                borderRadius: '8px',
                border: '1px solid #fecaca'
              }}>
                <div style={{ fontWeight: 600, color: '#991b1b', textTransform: 'capitalize' }}>{leak.name}</div>
                <div style={{ fontSize: '0.875rem', color: '#b91c1c', marginTop: '0.25rem' }}>
                  €{leak.avg_price.toFixed(2)} × {leak.frequency} = <strong>€{leak.total_spent.toFixed(2)}</strong>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
};

export default DashboardCharts;
