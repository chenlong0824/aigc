import { Button, Typography, Alert, Spin } from 'antd'
import { useParams, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { configApi } from '../../services/api'
import DifyChatbot from '../../components/DifyChatbot'
import {
  RobotOutlined,
  BulbOutlined,
  ThunderboltOutlined,
  MessageOutlined,
  CustomerServiceOutlined,
} from '@ant-design/icons'

const { Title } = Typography

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

export default function AgentDetail() {
  const { agentId } = useParams()
  const navigate = useNavigate()
  const [agent, setAgent] = useState<DifyAgent | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAgent()
  }, [agentId])

  const loadAgent = async () => {
    try {
      const response = await configApi.getDifyAgents()
      const agents = response.data.agents || []
      const found = agents.find((a: DifyAgent) => a.id === agentId)
      setAgent(found || null)
    } catch (error) {
      console.error('Failed to load agent:', error)
      setAgent(null)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <Spin spinning />
  }

  if (!agent) {
    return (
      <div>
        <Alert message="Agent 不存在" type="error" showIcon />
        <Button style={{ marginTop: 16 }} onClick={() => navigate('/dify')}>
          返回列表
        </Button>
      </div>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center', gap: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/dify')}>
          返回
        </Button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: 24 }}>{iconMap[agent.icon] || <RobotOutlined />}</span>
          <Title level={2} style={{ margin: 0 }}>
            {agent.name}
          </Title>
        </div>
      </div>

      <Alert
        message={agent.description}
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      {agent.token && agent.baseUrl ? (
        <DifyChatbot token={agent.token} baseUrl={agent.baseUrl} />
      ) : (
        <Alert
          message="请配置 Agent"
          description="请在服务器上配置该 Agent 的 token 和 baseUrl，然后重启后端服务"
          type="warning"
          showIcon
        />
      )}
    </div>
  )
}
