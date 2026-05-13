import { useState } from 'react'
import { Card, Select, Input, Button, Spin, message, Alert } from 'antd'
import { SoundOutlined, PlayCircleOutlined, DownloadOutlined } from '@ant-design/icons'
import { contentApi } from '../../services/api'

const { TextArea } = Input

const AVATARS = [
  { id: 'avatar_1', name: '端庄新闻型', scene: '天气预警', color: '#1890ff' },
  { id: 'avatar_2', name: '亲和导游型', scene: '客流提醒', color: '#52c41a' },
  { id: 'avatar_3', name: '活泼主持型', scene: '活动预告', color: '#fa8c16' },
]

const SCENE_TEMPLATES: Record<string, string> = {
  avatar_1: '各位游客请注意，咸阳文旅局发布重要天气预警。预计未来6小时内，咸阳市将出现强降雨天气，请各景区做好防汛准备，游客请合理安排出行。',
  avatar_2: '亲爱的游客朋友们，欢迎来到咸阳！目前乾陵景区客流量较大，建议您错峰游览，可以先前往茂陵或咸阳湖景区，祝您旅途愉快！',
  avatar_3: '咸阳的夏天来啦！本周末咸阳湖将举办大型音乐喷泉表演和美食市集，还有非遗手作体验，带上家人朋友一起来吧！',
}

export default function DigitalHuman() {
  const [avatarId, setAvatarId] = useState('avatar_1')
  const [script, setScript] = useState(SCENE_TEMPLATES.avatar_1)
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)
  const [taskId, setTaskId] = useState<number | null>(null)

  const handleAvatarChange = (id: string) => {
    setAvatarId(id)
    setScript(SCENE_TEMPLATES[id] || '')
    setDone(false)
  }

  const handleGenerate = async () => {
    if (!script.trim()) { message.warning('请输入播报文案'); return }
    setLoading(true)
    try {
      const res = await contentApi.generateDigitalHuman(avatarId, script)
      const newTaskId = res.data.data?.task_id
      if (newTaskId) setTaskId(newTaskId)
      setTimeout(() => {
        setDone(true)
        setLoading(false)
        message.success('数智人视频生成完成')
      }, 2000)
    } catch {
      setLoading(false)
      message.error('生成失败')
    }
  }

  const handleDownload = async () => {
    if (!taskId) { message.warning('没有可下载的视频'); return }
    try {
      message.loading({ content: '正在下载视频...', key: 'dl', duration: 0 })
      const res = await contentApi.downloadTask(taskId)
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.download = `digital_${taskId}.mp4`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      message.success({ content: '视频下载成功', key: 'dl' })
    } catch {
      message.error({ content: '下载失败，请重试', key: 'dl' })
    }
  }

  const selectedAvatar = AVATARS.find(a => a.id === avatarId)

  return (
    <div>
      <Card title={<><SoundOutlined /> 数智人播报</>}>
        <div style={{ marginBottom: 24 }}>
          <div style={{ marginBottom: 8, fontWeight: 500 }}>选择数智人形象</div>
          <div style={{ display: 'flex', gap: 16 }}>
            {AVATARS.map(a => (
              <Card
                key={a.id}
                size="small"
                hoverable
                style={{
                  width: 180, textAlign: 'center',
                  border: avatarId === a.id ? `2px solid ${a.color}` : '1px solid #f0f0f0',
                }}
                onClick={() => handleAvatarChange(a.id)}
              >
                <div style={{ width: 80, height: 80, borderRadius: '50%', background: a.color, margin: '0 auto 8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 24 }}>
                  {a.name[0]}
                </div>
                <div style={{ fontWeight: 600 }}>{a.name}</div>
                <div style={{ color: '#888', fontSize: 12 }}>{a.scene}</div>
              </Card>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8, fontWeight: 500 }}>播报场景</div>
          <Select value={avatarId} onChange={handleAvatarChange} style={{ width: 200 }}
            options={AVATARS.map(a => ({ value: a.id, label: `${a.name} - ${a.scene}` }))}
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8, fontWeight: 500 }}>播报文案（可编辑）</div>
          <TextArea value={script} onChange={e => setScript(e.target.value)} rows={4} placeholder="请输入播报文案..." />
        </div>

        <Button type="primary" size="large" icon={<PlayCircleOutlined />} onClick={handleGenerate} loading={loading}>
          生成数智人视频
        </Button>

        {done && (
          <Card style={{ marginTop: 24 }}>
            <Alert type="success" message="数智人视频已生成" description="FFmpeg未安装时为模拟结果，安装后可正常生成。" showIcon />
            <div style={{ marginTop: 16, padding: 20, background: selectedAvatar?.color, borderRadius: 8, color: '#fff', textAlign: 'center', minHeight: 200, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ width: 80, height: 80, borderRadius: '50%', background: 'rgba(255,255,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 36 }}>
                {selectedAvatar?.name[0]}
              </div>
              <div style={{ marginTop: 12, fontWeight: 600 }}>{selectedAvatar?.name} · {selectedAvatar?.scene}</div>
              <div style={{ marginTop: 8, fontSize: 12, opacity: 0.8, maxWidth: 300 }}>{script.slice(0, 60)}...</div>
              <Button type="primary" icon={<DownloadOutlined />} onClick={handleDownload}>下载视频</Button>
            </div>
          </Card>
        )}
      </Card>
    </div>
  )
}
