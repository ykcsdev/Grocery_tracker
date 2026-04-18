import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Legend } from 'recharts';
import { Droplet } from 'lucide-react';
import { API_BASE_URL } from '../config';

const COLORS = ['#3b82f6', '#22c55e', '#f97316', '#a855f7', '#ef4444', '#14b8a6'];

const formatCurrency = (value) =>
  new Intl.NumberFormat('en-IE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value || 0);

const DashboardCharts = ({ refreshTrigger }) => {
  const [pieData, setPieData] = useState([]);
  const [trendData, setTrendData] = useState([]);
  const [leaks, setLeaks] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const pieRes = await axios.get(`${API_BASE_URL}/receipts/topItemsByCategory`);
        const formattedPie = pieRes.data.map((item) => ({
          name: item.category || 'Uncategorized',
          value: parseFloat(item.total_amount_spent_in_category),
        }));
        setPieData(formattedPie);

        const trendRes = await axios.get(`${API_BASE_URL}/dashboard/monthly-trend`);
        setTrendData(trendRes.data);

        const leaksRes = await axios.get(`${API_BASE_URL}/dashboard/money-leaks`);
        setLeaks(leaksRes.data);
      } catch (error) {
        console.error('Error fetching charts data', error);
      }
    };
    fetchData();
  }, [refreshTrigger]);

  return (
    <div className="chart-grid">
      <div className="card animate-fade-in" style={{ animationDelay: '0.2s', height: '350px' }}>
        <h2 className="card-title">Spending by Category</h2>
        <div style={{ height: 'calc(100% - 2rem)' }}>
          {pieData.length === 0 ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>No values to display</div>
          ) : (
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
                <RechartsTooltip formatter={(value) => formatCurrency(Number(value))} />
                <Legend layout="horizontal" verticalAlign="bottom" align="center" wrapperStyle={{ fontSize: '0.75rem', paddingTop: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="card animate-fade-in" style={{ animationDelay: '0.3s', height: '350px' }}>
        <h2 className="card-title">Avg Daily Spend Trend</h2>
        <div style={{ height: 'calc(100% - 2rem)' }}>
          {trendData.length === 0 ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>No values to display</div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData} margin={{ top: 16, right: 20, left: 8, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                <XAxis dataKey="month" tick={{ fontSize: 12, fill: 'var(--text-secondary)' }} />
                <YAxis tickFormatter={(value) => `${Number(value).toFixed(0)}`} tick={{ fontSize: 12, fill: 'var(--text-secondary)' }} />
                <RechartsTooltip
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)', backgroundColor: 'var(--panel-bg)', color: 'var(--text-primary)' }}
                  formatter={(value, _name, payload) => [
                    formatCurrency(Number(value)),
                    `Avg Daily Spend (${payload?.payload?.month || ''})`,
                  ]}
                  labelFormatter={() => 'Monthly average based on uploaded receipts'}
                />
                <Line
                  type="monotone"
                  dataKey="average_daily_spend"
                  stroke="var(--color-blue)"
                  strokeWidth={3}
                  dot={{ r: 4, strokeWidth: 2, fill: 'var(--panel-bg)' }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="card leak-widget animate-fade-in" style={{ animationDelay: '0.4s' }}>
        <h2 className="card-title">
          <Droplet size={20} color="var(--color-red)" />
          Frequent Small Expenses
        </h2>
        {leaks.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)' }}>No significant leaks detected for the latest available month.</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            {leaks.map((leak, i) => (
              <div
                key={i}
                style={{
                  padding: '1rem',
                  backgroundColor: 'var(--color-red-light)',
                  borderRadius: '8px',
                  border: '1px solid #fecaca',
                }}
              >
                <div style={{ fontWeight: 600, color: '#991b1b', textTransform: 'capitalize' }}>{leak.name}</div>
                <div style={{ fontSize: '0.875rem', color: '#b91c1c', marginTop: '0.25rem' }}>
                  {formatCurrency(leak.avg_price)} x {leak.frequency} = <strong>{formatCurrency(leak.total_spent)}</strong>
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
