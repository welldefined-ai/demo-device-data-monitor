import { ConfigProvider, theme } from 'antd';
import React from 'react';

function App(): JSX.Element {
  return (
    <ConfigProvider theme={{ algorithm: theme.defaultAlgorithm }}>
      <div style={{ padding: 24 }}>
        <h1>DDMS</h1>
        <p>Frontend scaffolding is ready.</p>
      </div>
    </ConfigProvider>
  );
}

export default App;

