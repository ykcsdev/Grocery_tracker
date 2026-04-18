import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, DollarSign, Calendar, Target, AlertTriangle } from 'lucide-react';
import { API_BASE_URL } from '../config';

const formatCurrency = (value) =>
  new Intl.NumberFormat('en-IE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value || 0);

const SummaryStrip = ({ refreshTrigger }) => {
  const [data, setData] = useState({
    summary_month: null,
    total_monthly_spend: 0,
    average_daily_spend: 0,
    highest_expense_day: '',
    highest_expense_amount: 0,
    top_category: 'N/A',
    comparison_to_previous_month_pct: null,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/dashboard/summary`);
        setData(response.data);
      } catch (error) {
        console.error('Failed to fetch summary data', error);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, [refreshTrigger]);

  if (loading) return <div className="animate-fade-in" style={{ padding: '1rem' }}>Loading summary...</div>;

  const comparisonPct = data.comparison_to_previous_month_pct;
  const comparisonIsDecrease = typeof comparisonPct === 'number' && comparisonPct < 0;
  const comparisonColor = comparisonIsDecrease ? 'var(--color-green)' : 'var(--color-red)';
  const comparisonIcon = comparisonIsDecrease ? <TrendingDown size={14} /> : <TrendingUp size={14} />;
  const comparisonText = typeof comparisonPct === 'number'
    ? `${Math.abs(comparisonPct).toFixed(0)}% ${comparisonIsDecrease ? 'less' : 'more'} than previous month`
    : (data.summary_month ? `Based on ${data.summary_month}` : 'No monthly comparison available');

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
      <div className="card animate-fade-in">
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
          <span>Total Monthly Spend</span>
          <DollarSign size={16} color="var(--color-blue)" />
        </div>
        <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>
          {formatCurrency(data.total_monthly_spend)}
        </div>
        <div style={{ fontSize: '0.75rem', color: comparisonColor, display: 'flex', alignItems: 'center', marginTop: '0.5rem', gap: '0.25rem' }}>
          {typeof comparisonPct === 'number' ? comparisonIcon : null}
          <span>{comparisonText}</span>
        </div>
      </div>

      <div className="card animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
          <span>Avg Daily Spend</span>
          <Calendar size={16} color="var(--color-purple)" />
        </div>
        <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>
          {formatCurrency(data.average_daily_spend)}
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
          {data.summary_month ? `Calculated for ${data.summary_month}` : 'No month available'}
        </div>
      </div>

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
            {formatCurrency(data.highest_expense_amount)}
          </div>
        )}
      </div>

      <div className="card animate-fade-in" style={{ animationDelay: '0.3s' }}>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
          <span>Top Category</span>
          <Target size={16} color="var(--color-orange)" />
        </div>
        <div style={{ fontSize: '1.25rem', fontWeight: 700, textTransform: 'capitalize' }}>
          {data.top_category}
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
          {data.summary_month ? `Top category in ${data.summary_month}` : 'No month available'}
        </div>
      </div>
    </div>
  );
};

export default SummaryStrip;
