// GraphLegend.jsx
// Explains node colors and types.

import React from 'react';

export default function GraphLegend() {
  return (
    <div style={{ padding: 8 }}>
      <h4>Legend</h4>
      <ul>
        <li><span style={{ color: '#4f83cc' }}>■</span> Student</li>
        <li><span style={{ color: '#4caf50' }}>■</span> Salaried</li>
        <li><span style={{ color: '#8e44ad' }}>■</span> Business</li>
      </ul>
    </div>
  );
}
