import { Card, Row, Col, Typography } from 'antd'
import { useNavigate } from 'react-router-dom'
import { DIFY_AGENTS } from '../../config/difyAgents'

const { Title, Text } = Typography

export default function DifyAgentList() {
  const navigate = useNavigate()

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        ✨ Dify Agent
      </Title>
      <Text type="secondary" style={{ fontSize: 14, display: 'block', marginBottom: 32 }}>
        选择一个 Dify Agent 开始使用
      </Text>

      <Row gutter={[16, 16]}>
        {DIFY_AGENTS.map((agent) => (
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
                  {agent.icon}
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
    </div>
  )
}
