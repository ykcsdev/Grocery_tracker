import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ChevronDown, ChevronRight, Search, FileText } from 'lucide-react';

const DataExploration = ({ refreshTrigger }) => {
  const [invoices, setInvoices] = useState([]);
  const [filteredInvoices, setFilteredInvoices] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const [details, setDetails] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInvoices = async () => {
      try {
        const response = await axios.get('http://localhost:8000/invoices/');
        setInvoices(response.data);
        setFilteredInvoices(response.data);
      } catch (error) {
        console.error("Error fetching invoices list", error);
      } finally {
        setLoading(false);
      }
    };
    fetchInvoices();
  }, [refreshTrigger]);

  useEffect(() => {
    if (searchTerm) {
      setFilteredInvoices(invoices.filter(inv => 
        (inv.merchant_name && inv.merchant_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (inv.invoice_number && inv.invoice_number.toLowerCase().includes(searchTerm.toLowerCase()))
      ));
    } else {
      setFilteredInvoices(invoices);
    }
  }, [searchTerm, invoices]);

  const toggleRow = async (id) => {
    if (expandedId === id) {
      setExpandedId(null);
      return;
    }
    
    setExpandedId(id);
    if (!details[id]) {
      try {
        const res = await axios.get(`http://localhost:8000/invoices/receipts/${id}`);
        setDetails(prev => ({ ...prev, [id]: res.data }));
      } catch (error) {
        console.error("Error fetching invoice details", error);
      }
    }
  };

  return (
    <div className="card animate-fade-in" style={{ animationDelay: '0.6s' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 className="card-title" style={{ margin: 0 }}>Recent Receipts</h2>
        
        {/* Search */}
        <div style={{ display: 'flex', alignItems: 'center', background: '#f1f5f9', borderRadius: '8px', padding: '0.5rem 1rem' }}>
          <Search size={16} color="var(--text-secondary)" style={{ marginRight: '0.5rem' }} />
          <input 
            type="text" 
            placeholder="Search by merchant..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ background: 'transparent', border: 'none', outline: 'none', fontSize: '0.875rem', width: '200px' }}
          />
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              <th style={{ padding: '0.75rem 1rem' }}>Merchant</th>
              <th style={{ padding: '0.75rem 1rem' }}>Date</th>
              <th style={{ padding: '0.75rem 1rem' }}>Total</th>
              <th style={{ padding: '0.75rem 1rem' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="4" style={{ textAlign: 'center', padding: '2rem' }}>Loading tables...</td></tr>
            ) : filteredInvoices.length === 0 ? (
              <tr><td colSpan="4" style={{ textAlign: 'center', padding: '2rem' }}>No data found</td></tr>
            ) : (
              filteredInvoices.map((inv) => (
                <React.Fragment key={inv.receipt_id}>
                  {/* Main Row */}
                  <tr 
                    onClick={() => toggleRow(inv.receipt_id)}
                    style={{ 
                      borderBottom: '1px solid var(--border-color)', 
                      cursor: 'pointer',
                      backgroundColor: expandedId === inv.receipt_id ? '#f8fafc' : 'transparent',
                      transition: 'background-color 0.2s'
                    }}
                  >
                    <td style={{ padding: '1rem', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {expandedId === inv.receipt_id ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                      <FileText size={16} color="var(--text-secondary)"/>
                      {inv.merchant_name || 'Unknown Merchant'}
                    </td>
                    <td style={{ padding: '1rem' }}>{inv.purchase_datetime || 'N/A'}</td>
                    <td style={{ padding: '1rem', fontWeight: 600 }}>€{inv.total_paid?.toFixed(2)}</td>
                    <td style={{ padding: '1rem' }}>
                      <span style={{ 
                        padding: '0.25rem 0.5rem', 
                        borderRadius: '9999px', 
                        fontSize: '0.75rem', 
                        fontWeight: 500,
                        backgroundColor: inv.ready ? 'var(--color-green-light)' : 'var(--color-orange)',
                        color: inv.ready ? '#166534' : '#fff'
                      }}>
                        {inv.status}
                      </span>
                    </td>
                  </tr>
                  
                  {/* Expanded Detail Row */}
                  {expandedId === inv.receipt_id && (
                    <tr style={{ backgroundColor: '#f8fafc' }}>
                      <td colSpan="4" style={{ padding: '0', borderBottom: '1px solid var(--border-color)' }}>
                        <div style={{ padding: '1.5rem', paddingLeft: '3rem' }}>
                          {!details[inv.receipt_id] ? (
                            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Loading details...</div>
                          ) : (
                            <div>
                              <div style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Items Purchased:</div>
                              <table style={{ width: '100%', fontSize: '0.875rem' }}>
                                <tbody>
                                  {details[inv.receipt_id].items?.map(item => (
                                    <tr key={item.product_id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                                      <td style={{ padding: '0.5rem 0' }}>{item.product_name}</td>
                                      <td style={{ padding: '0.5rem 0', textAlign: 'right' }}>{item.quantity} {item.unit} × €{item.unit_price?.toFixed(2)}</td>
                                      <td style={{ padding: '0.5rem 0', textAlign: 'right', fontWeight: 500 }}>€{item.line_total?.toFixed(2)}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataExploration;
