import { Card, Row, Col, Typography, Spin, message } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { configApi } from '../../services/api'
import {
  RobotOutlined,
  BulbOutlined,
  ThunderboltOutlined,
  MessageOutlined,
  CustomerServiceOutlined,
} from '@ant-design/icons'

const { Title, Text } = Typography

const iconMap: Record<string, React.ReactNode> = {
  RobotOutlined: <RobotOutlined />,
  BulbOutlined: <BulbOutlined />,
  ThunderboltOutlined: <ThunderboltOutlined />,
  MessageOutlined: <MessageOutlined />,
  CustomerServiceOutlined: <CustomerServiceOutlined />,
}

interface DifyAgent {
  id: string
  name: string
  description: string
  icon: string
  token: string
  baseUrl: string
}

export default function DifyAgentList() {
  const navigate = useNavigate()
  const [agents, setAgents] = useState<DifyAgent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    try {
      const response = await configApi.getDifyAgents()
      setAgents(response.data.agents || [])
    } catch (error) {
      message.error('加载Agent配置失败')
      console.error('Failed to load agents:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        ✨ Dify Agent
      </Title>
      <Text type="secondary" style={{ fontSize: 14, display: 'block', marginBottom: 32 }}>
        选择一个 Dify Agent 开始使用
      </Text>

      <Spin spinning={loading}>
        <Row gutter={[16, 16]}>
          {agents.map((agent) => (
            <Col xs={24} sm={12} md={8} key={agent.id}>
              <Card
                hoverable
                style={{ cursor: 'pointer' }}
                cover={
                  <div style={{
                    height: 120,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    fontSize: 48,
                    color: '#fff'
                  }}>
                    {iconMap[agent.icon] || <RobotOutlined />}
                  </div>
                }
                onClick={() => navigate(`/dify/${agent.id}`)}
              >
                <Card.Meta
                  title={agent.name}
                  description={
                    <Text type="secondary" ellipsis>
                      {agent.description}
                    </Text>
                  }
                />
              </Card>
            </Col>
          ))}
        </Row>
      </Spin>
    </div>
  )
}

export { DifyAgent }
