import { Button, Typography, Alert } from 'antd'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { DIFY_AGENTS } from '../../config/difyAgents'
import DifyChatbot from '../../components/DifyChatbot'

const { Title } = Typography

export default function AgentDetail() {
  const { agentId } = useParams()
  const navigate = useNavigate()

  const agent = DIFY_AGENTS.find(a => a.id === agentId)

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
          <span style={{ fontSize: 24 }}>{agent.icon}</span>
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
          description="请在 config/difyAgents.ts 中配置该 Agent 的 token 和 baseUrl"
          type="warning"
          showIcon
        />
      )}
    </div>
  )
}
