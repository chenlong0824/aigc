import { Card, Form, Input, Button, message, Divider, Alert } from 'antd'
import { SaveOutlined, PictureOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

export default function Settings() {
  const [form] = Form.useForm()
  const navigate = useNavigate()

  const handleSave = () => {
    message.success('设置已保存（Demo阶段配置存储在本地）')
  }

  return (
    <div>
      <Card title="系统设置">
        <Alert
          type="info"
          message="Demo 阶段说明"
          description="以下为Demo展示用配置项，实际部署时可对接真实API Key和服务地址。当前Ollama和Edge TTS使用本地服务。"
          style={{ marginBottom: 24 }}
          showIcon
        />

        <Form form={form} layout="vertical" onFinish={handleSave}>
          <Divider titlePlacement="left">AI 模型配置</Divider>
          <Form.Item label="Ollama 服务地址" name="ollama_host" initialValue="http://localhost:11434">
            <Input />
          </Form.Item>
          <Form.Item label="Ollama 模型" name="ollama_model" initialValue="qwen3.5:2b">
            <Input />
          </Form.Item>

          <Divider titlePlacement="left">视频处理</Divider>
          <Form.Item label="FFmpeg 路径" name="ffmpeg_path" initialValue="ffmpeg">
            <Input />
          </Form.Item>

          <Divider titlePlacement="left">素材管理</Divider>
          <Form.Item label="本地素材库路径" name="media_path" initialValue="data/media">
            <Input />
          </Form.Item>
          <Button icon={<PictureOutlined />} onClick={() => navigate('/settings/media')} style={{ marginBottom: 16 }}>
            进入素材库管理（上传/标签/删除）
          </Button>

          <Button type="primary" htmlType="submit" icon={<SaveOutlined />} size="large">
            保存设置
          </Button>
        </Form>
      </Card>
    </div>
  )
}
