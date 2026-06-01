// GraphControls.jsx
// Simple controls for zooming and layout selection.

import React from 'react';

export default function GraphControls({ cy }) {
  return (
    <div style={{ padding: 8 }}>
      <button onClick={() => cy && cy.zoom({ level: cy.zoom() * 1.2 })}>Zoom In</button>
      <button onClick={() => cy && cy.zoom({ level: cy.zoom() * 0.8 })}>Zoom Out</button>
      <button onClick={() => cy && cy.fit()}>Fit</button>
    </div>
  );
}
