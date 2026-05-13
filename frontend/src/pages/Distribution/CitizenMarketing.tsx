import { useState } from 'react'
import { Card, Steps, Button, Row, Col, Image, message, Input, Tag, Space } from 'antd'
import { UploadOutlined, ThunderboltOutlined, DownloadOutlined, TrophyOutlined } from '@ant-design/icons'

const TEMPLATES = [
  { id: 1, name: '咸阳打卡', cover: 'https://picsum.photos/seed/xianyang1/400/300', desc: '网红打卡风' },
  { id: 2, name: '美食探店', cover: 'https://picsum.photos/seed/xianyang2/400/300', desc: '食欲满满的探店' },
  { id: 3, name: '风景航拍', cover: 'https://picsum.photos/seed/xianyang3/400/300', desc: '大气的航拍风格' },
]

const RANKINGS = [
  { rank: 1, name: '旅行达人小王', works: 12, likes: 3600, points: 1280 },
  { rank: 2, name: '咸阳本地通', works: 8, likes: 2800, points: 960 },
  { rank: 3, name: '摄影爱好者', works: 15, likes: 2100, points: 850 },
  { rank: 4, name: '美食探店家', works: 10, likes: 1800, points: 720 },
  { rank: 5, name: '文旅创客小明', works: 6, likes: 1500, points: 560 },
]

export default function CitizenMarketing() {
  const [step, setStep] = useState(0)
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null)
  const [generating, setGenerating] = useState(false)

  const handleGenerate = () => {
    setGenerating(true)
    setTimeout(() => {
      setGenerating(false)
      setStep(2)
      message.success('作品生成成功！')
    }, 2000)
  }

  return (
    <div className="h5-page" style={{ padding: 16 }}>
      <div style={{ textAlign: 'center', padding: '16px 0', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: '#fff', borderRadius: 12, marginBottom: 16 }}>
        <h2>咸阳文旅全民营销</h2>
        <p style={{ opacity: 0.8 }}>人人都是咸阳代言人</p>
      </div>

      <Steps current={step} size="small" items={[{ title: '选模板' }, { title: '传素材' }, { title: '生成作品' }]} style={{ marginBottom: 16 }} />

      {step === 0 && (
        <div>
          <div style={{ marginBottom: 8, fontWeight: 500 }}>选择创作模板</div>
          <Row gutter={[8, 8]}>
            {TEMPLATES.map(t => (
              <Col span={8} key={t.id}>
                <Card hoverable size="small" cover={<Image src={t.cover} preview={false} style={{ height: 100, objectFit: 'cover' }} />}
                  style={{ border: selectedTemplate === t.id ? '2px solid #667eea' : '' }}
                  onClick={() => setSelectedTemplate(t.id)}
                >
                  <Card.Meta title={t.name} description={t.desc} />
                </Card>
              </Col>
            ))}
          </Row>
          <Button type="primary" block size="large" disabled={!selectedTemplate} onClick={() => setStep(1)} style={{ marginTop: 16 }}>
            下一步：上传素材
          </Button>
        </div>
      )}

      {step === 1 && (
        <div>
          <Card title="上传你的素材">
            <div style={{ textAlign: 'center', padding: 40, border: '2px dashed #ddd', borderRadius: 8, marginBottom: 16 }}>
              <UploadOutlined style={{ fontSize: 32, color: '#999' }} />
              <div style={{ marginTop: 8, color: '#999' }}>点击或拖拽上传照片/视频</div>
              <div style={{ fontSize: 12, color: '#bbb' }}>Demo 阶段模拟上传</div>
            </div>
            <Input type="text" placeholder="输入你想说的话..." style={{ marginBottom: 16 }} />
          </Card>
          <Space>
            <Button onClick={() => setStep(0)}>上一步</Button>
            <Button type="primary" icon={<ThunderboltOutlined />} onClick={handleGenerate} loading={generating}>
              AI一键生成
            </Button>
          </Space>
        </div>
      )}

      {step === 2 && (
        <div>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Image src="https://picsum.photos/seed/demo/400/300" preview={false} style={{ borderRadius: 8, maxWidth: '100%' }} />
              <div style={{ marginTop: 12, fontWeight: 600 }}>你的专属咸阳推广作品</div>
              <div style={{ color: '#888', fontSize: 12, marginTop: 4 }}>#咸阳文旅 #全民种草</div>
            </div>
            <Space style={{ marginTop: 16, width: '100%', justifyContent: 'center' }}>
              <Button type="primary" icon={<DownloadOutlined />} onClick={() => message.success('Demo 阶段模拟下载')}>下载分享</Button>
              <Button onClick={() => { setStep(0); setSelectedTemplate(null) }}>再次创作</Button>
            </Space>
          </Card>

          <Card title={<><TrophyOutlined /> 创作排行榜</>} style={{ marginTop: 16 }}>
            {RANKINGS.map(r => (
              <div key={r.rank} style={{ display: 'flex', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Tag color={r.rank <= 3 ? 'gold' : 'default'}>{r.rank}</Tag>
                <span style={{ flex: 1 }}>{r.name}</span>
                <span style={{ color: '#888', fontSize: 12 }}>{r.works}作品 · {r.likes}赞</span>
                <span style={{ marginLeft: 8, fontWeight: 600, color: '#fa8c16' }}>{r.points}分</span>
              </div>
            ))}
          </Card>
        </div>
      )}
    </div>
  )
}
