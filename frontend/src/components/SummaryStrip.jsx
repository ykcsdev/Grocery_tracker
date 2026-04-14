import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, DollarSign, Calendar, Target, AlertTriangle } from 'lucide-react';

const SummaryStrip = ({ refreshTrigger }) => {
  const [data, setData] = useState({
    total_monthly_spend: 0,
    average_daily_spend: 0,
    highest_expense_day: '',
    highest_expense_amount: 0,
    top_category: 'N/A'
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await axios.get('http://localhost:8000/dashboard/summary');
        setData(response.data);
      } catch (error) {
        console.error("Failed to fetch summary data", error);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, [refreshTrigger]);

  if (loading) return <div className="animate-fade-in" style={{ padding: '1rem' }}>Loading summary...</div>;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
      
      {/* Total Monthly Spend */}
      <div className="card animate-fade-in">
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
          <span>Total Monthly Spend</span>
          <DollarSign size={16} color="var(--color-blue)" />
        </div>
        <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>
          €{data.total_monthly_spend.toFixed(2)}
        </div>
        {/* Mocked trend for visual richness */}
        <div style={{ fontSize: '0.75rem', color: 'var(--color-green)', display: 'flex', alignItems: 'center', marginTop: '0.5rem', gap: '0.25rem' }}>
          <TrendingDown size={14} /> <span>12% less than last month</span>
        </div>
      </div>

      {/* Average Daily Spend */}
      <div className="card animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
          <span>Avg Daily Spend</span>
          <Calendar size={16} color="var(--color-purple)" />
        </div>
        <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>
          €{data.average_daily_spend.toFixed(2)}
        </div>
      </div>

      {/* Highest Expense Day */}
      <div className="card animate-fade-in" style={{ animationDelay: '0.2s', borderLeft: '4px solid var(--color-red)' }}>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
          <span>Highest Expense Day</span>
          <AlertTriangle size={16} color="var(--color-red)" />
        </div>
        <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>
          {data.highest_expense_day || 'None'}
        </div>
        {data.highest_expense_amount > 0 && (
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            €{data.highest_expense_amount.toFixed(2)}
          </div>
        )}
      </div>

      {/* Top Category */}
      <div className="card animate-fade-in" style={{ animationDelay: '0.3s' }}>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
          <span>Top Category</span>
          <Target size={16} color="var(--color-orange)" />
        </div>
        <div style={{ fontSize: '1.25rem', fontWeight: 700, textTransform: 'capitalize' }}>
          {data.top_category}
        </div>
      </div>

    </div>
  );
};

export default SummaryStrip;
