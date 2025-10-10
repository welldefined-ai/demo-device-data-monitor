import { ConfigProvider, Typography, Space, Button, Card, Tag } from 'antd'
import { CheckCircleOutlined } from '@ant-design/icons'
import { useEffect, useState } from 'react'

const { Title, Paragraph } = Typography

interface HealthStatus {
  status: string
  message?: string
}

function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(false)

  const checkHealth = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/health')
      const data = await response.json()
      setHealth(data)
    } catch (error) {
      setHealth({ status: 'error', message: 'Failed to connect to backend' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkHealth()
  }, [])

  return (
    <ConfigProvider>
      <div style={{ padding: '50px', maxWidth: '800px', margin: '0 auto' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Title level={1}>DDMS - Distributed Device Monitoring System</Title>

          <Card title="Framework Status">
            <Space direction="vertical" size="middle">
              <div>
                <Tag color="green" icon={<CheckCircleOutlined />}>
                  Frontend Running
                </Tag>
                <Paragraph style={{ marginTop: 8 }}>
                  React + TypeScript + Vite + Ant Design
                </Paragraph>
              </div>

              <div>
                {health?.status === 'healthy' ? (
                  <Tag color="green" icon={<CheckCircleOutlined />}>
                    Backend Connected
                  </Tag>
                ) : (
                  <Tag color="red">Backend Disconnected</Tag>
                )}
                <Paragraph style={{ marginTop: 8 }}>
                  {health?.status === 'healthy'
                    ? 'FastAPI backend is responding'
                    : health?.message || 'Checking...'}
                </Paragraph>
              </div>

              <Button onClick={checkHealth} loading={loading}>
                Refresh Status
              </Button>
            </Space>
          </Card>

          <Card title="Next Steps">
            <Paragraph>
              The framework is set up and ready for feature implementation:
            </Paragraph>
            <ul>
              <li>Backend API routes in <code>backend/ddms/api/</code></li>
              <li>Frontend features in <code>frontend/src/features/</code></li>
              <li>Database models in <code>backend/ddms/db/</code></li>
              <li>Run migrations with <code>alembic upgrade head</code></li>
            </ul>
          </Card>
        </Space>
      </div>
    </ConfigProvider>
  )
}

export default App
