import { useState } from 'react'
import { useNavigate, Navigate } from 'react-router-dom'
import { Form, Input, Button, Card, Typography, message, Space } from 'antd'
import { UserOutlined, LockOutlined, VideoCameraOutlined } from '@ant-design/icons'
import { login, setToken, isAuthenticated } from '../services/auth'

const { Title, Text } = Typography

export default function Login() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  if (isAuthenticated()) {
    return <Navigate to="/" replace />
  }

  const handleLogin = async (values: { username: string; password: string }) => {
    setLoading(true)
    try {
      const result = await login(values)
      setToken(result.access_token)
      message.success('登录成功')
      navigate('/', { replace: true })
    } catch (error: any) {
      const detail = error?.response?.data?.detail || '登录失败，请检查用户名和密码'
      message.error(detail)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    }}>
      <Card
        style={{ width: 400, borderRadius: 8, boxShadow: '0 8px 24px rgba(0,0,0,0.15)' }}
        styles={{ body: { padding: '40px 32px' } }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%', textAlign: 'center' }}>
          <div>
            <VideoCameraOutlined style={{ fontSize: 48, color: '#667eea' }} />
            <Title level={3} style={{ marginTop: 12, marginBottom: 4 }}>
              咸阳文旅AIGC
            </Title>
            <Text type="secondary">智能营销平台 · 管理后台</Text>
          </div>

          <Form
            name="login"
            onFinish={handleLogin}
            layout="vertical"
            size="large"
            initialValues={{ username: 'admin' }}
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: '请输入用户名' }]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="用户名"
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="密码"
                autoComplete="current-password"
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0 }}>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
              >
                登 录
              </Button>
            </Form.Item>
          </Form>
        </Space>
      </Card>
    </div>
  )
}
