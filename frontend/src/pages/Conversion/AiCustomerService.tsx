import { useState, useRef, useEffect } from 'react'
import { Card, Input, Button, Space, Tag, Alert, Typography, message } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined, PhoneOutlined } from '@ant-design/icons'
import { conversionApi } from '../../services/api'

const { Text } = Typography

interface Message {
  role: 'user' | 'assistant'
  content: string
  hasIntent?: boolean
}

export default function AiCustomerService() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: '您好！我是咸阳文旅智能客服助手，请问有什么可以帮您的？您可以问我景点、美食、交通、住宿、票务等相关问题。' },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string>('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return
    const userMsg: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await conversionApi.chatAsk(input, sessionId || undefined)
      const { answer, session_id, has_booking_intent } = res.data.data
      if (session_id) setSessionId(session_id)
      setMessages(prev => [...prev, { role: 'assistant', content: answer, hasIntent: has_booking_intent }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: '抱歉，智能客服暂时不可用，请稍后重试或拨打客服热线。' }])
    }
    setLoading(false)
  }

  const QUICK_QUESTIONS = ['咸阳有哪些必去景点？', '推荐咸阳特色美食', '乾陵门票多少钱？', '从西安怎么去咸阳？']

  return (
    <Card title={<><RobotOutlined /> AI智能客服</>}>
      <Alert
        type="info"
        message="模拟入口"
        description="游客在视频中看到挂载的客服入口，点击后进入此对话页面。下方模拟了AI客服的完整交互流程。"
        style={{ marginBottom: 16 }}
        showIcon
      />

      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((msg, i) => (
            <div key={i}>
              <div className={`message-bubble ${msg.role === 'user' ? 'message-user' : 'message-assistant'}`}>
                <div style={{ fontSize: 12, marginBottom: 4, opacity: 0.7 }}>
                  {msg.role === 'assistant' ? <><RobotOutlined /> AI客服</> : <><UserOutlined /> 游客</>}
                </div>
                <div>{msg.content}</div>
              </div>
              {msg.hasIntent && (
                <Alert
                  type="success"
                  message="检测到预订意向！"
                  description={<span>为您推荐官方预约入口：<a href="#">点击前往咸阳文旅官方预约平台</a></span>}
                  style={{ marginBottom: 8, maxWidth: '70%' }}
                  showIcon
                />
              )}
            </div>
          ))}
          {loading && (
            <div className="message-bubble message-assistant">
              <Text type="secondary">AI正在思考...</Text>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-area">
          <Space style={{ marginBottom: 8 }} wrap>
            {QUICK_QUESTIONS.map(q => (
              <Tag key={q} style={{ cursor: 'pointer' }} onClick={() => setInput(q)}>{q}</Tag>
            ))}
          </Space>
          <Space.Compact style={{ width: '100%' }}>
            <Input
              value={input}
              onChange={e => setInput(e.target.value)}
              onPressEnter={handleSend}
              placeholder="输入您的问题..."
              disabled={loading}
              prefix={<RobotOutlined />}
            />
            <Button type="primary" icon={<SendOutlined />} onClick={handleSend} loading={loading}>发送</Button>
          </Space.Compact>
          <div style={{ textAlign: 'center', marginTop: 8 }}>
            <Button type="link" size="small" icon={<PhoneOutlined />} onClick={() => message.info('Demo 阶段：模拟转人工')}>转人工客服（Demo模拟）</Button>
          </div>
        </div>
      </div>
    </Card>
  )
}
