import { useState, useEffect } from 'react'
import { Card, Input, Select, Button, Steps, Spin, message, Alert, Tag, Space, Row, Col, Empty } from 'antd'
import { VideoCameraOutlined, ThunderboltOutlined, DownloadOutlined, FireOutlined, TeamOutlined, ClockCircleOutlined } from '@ant-design/icons'
import axios from 'axios'
import { contentApi, insightApi } from '../../services/api'

interface Topic {
  title: string
  reason: string
  audience: string
  publish_time: string
  score: number
}

export default function OneClickVideo() {
  const [topic, setTopic] = useState('')
  const [style, setStyle] = useState('探店')
  const [current, setCurrent] = useState(0)
  const [loading, setLoading] = useState(false)
  const [script, setScript] = useState<Record<string, unknown> | null>(null)
  const [taskId, setTaskId] = useState<number | null>(null)
  const [videoStatus, setVideoStatus] = useState('')
  const [outputPath, setOutputPath] = useState('')
  const [topics, setTopics] = useState<Topic[]>([])
  const [topicsLoading, setTopicsLoading] = useState(false)
  const [showTopicRecommend, setShowTopicRecommend] = useState(true)

  /**
   * 生成文案
   */
  const handleGenerateScript = async () => {
    if (!topic.trim()) { message.warning('请输入创作主题'); return }
    setLoading(true)
    try {
      const res = await contentApi.generateScript(topic, style)
      setScript(res.data.data)
      setCurrent(1)
      message.success('文案生成成功')
    } catch {
      message.error('文案生成失败')
    }
    setLoading(false)
  }

  /**
   * 加载选题推荐
   */
  const loadTopics = async () => {
    setTopicsLoading(true)
    try {
      const res = await insightApi.getTopics()
      setTopics(res.data.data)
    } catch {
      message.error('获取选题推荐失败')
    }
    setTopicsLoading(false)
  }

  useEffect(() => {
    if (showTopicRecommend && topics.length === 0) {
      loadTopics()
    }
  }, [showTopicRecommend])

  /**
   * 使用选题
   */
  const handleUseTopic = (t: Topic) => {
    setTopic(t.title)
    setShowTopicRecommend(false)
    setCurrent(0)
  }

  /**
   * 刷新选题
   */
  const handleRefreshTopics = () => {
    loadTopics()
  }

  /**
   * 跳过选题推荐
   */
  const handleSkipTopics = () => {
    setShowTopicRecommend(false)
  }

  /**
   * 合成视频
   */
  const handleCompose = async () => {
    setLoading(true)
    setCurrent(2)
    try {
      const res = await contentApi.composeVideo(topic, 1, style)
      setTaskId(res.data.data?.task_id)
      setVideoStatus(res.data.data?.status || 'completed')
      setOutputPath(res.data.data?.output_path || '')
      if (res.data.data?.script) {
        setScript(res.data.data.script)
      }
      setTimeout(() => setCurrent(3), 2000)
      message.success('视频生成完成')
    } catch (e) {
      console.error('视频合成失败:', e)
      message.error('视频合成失败，请稍后重试')
      setCurrent(1)
    }
    setLoading(false)
  }

  /**
   * 下载视频
   */
  const handleDownload = async () => {
    if (!taskId) { message.warning('没有可下载的视频'); return }
    try {
      message.loading({ content: '正在下载视频...', key: 'download', duration: 0 })
      const res = await axios.get(`/api/content/tasks/${taskId}/download`, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.download = `video_${taskId}.mp4`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      message.success({ content: '视频下载成功', key: 'download' })
    } catch {
      message.error({ content: '下载失败，请重试', key: 'download' })
    }
  }

  /**
   * 热度评分颜色
   */
  const getScoreColor = (score: number) => {
    if (score >= 85) return '#52c41a'
    if (score >= 70) return '#faad14'
    return '#ff4d4f'
  }

  return (
    <div>
      <Card title={<><VideoCameraOutlined /> 一键成片</>} extra={
        !showTopicRecommend && current === 0 && (
          <Button type="link" icon={<FireOutlined />} onClick={() => setShowTopicRecommend(true)}>
            查看爆款选题
          </Button>
        )
      }>
        {/* 步骤条 */}
        <Steps current={current} items={[{ title: '输入主题' }, { title: '生成文案' }, { title: '合成视频' }, { title: '预览下载' }]} style={{ marginBottom: 24 }} />

        {/* 爆款选题推荐区域 */}
        {showTopicRecommend && current === 0 && (
          <Card
            title={<><FireOutlined /> 爆款选题推荐</>}
            extra={<Button icon={<ThunderboltOutlined />} onClick={handleRefreshTopics} loading={topicsLoading}>刷新推荐</Button>}
            style={{ marginBottom: 24, background: '#fff7e6' }}
          >
            {topicsLoading ? (
              <div style={{ textAlign: 'center', padding: 40 }}><Spin /></div>
            ) : topics.length === 0 ? (
              <Empty description="暂无选题推荐" />
            ) : (
              <Row gutter={[12, 12]}>
                {topics.map((t, i) => (
                  <Col xs={24} sm={12} lg={8} key={i}>
                    <Card size="small" hoverable style={{ borderColor: getScoreColor(t.score) }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                        <Tag color={getScoreColor(t.score)} style={{ fontWeight: 600 }}>{t.score}分</Tag>
                      </div>
                      <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 8 }}>{t.title}</div>
                      <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>{t.reason}</div>
                      <div style={{ fontSize: 12, color: '#888' }}>
                        <TeamOutlined /> {t.audience} &nbsp;
                        <ClockCircleOutlined /> {t.publish_time}
                      </div>
                      <Button type="primary" size="small" block style={{ marginTop: 12 }} onClick={() => handleUseTopic(t)}>
                        使用此选题
                      </Button>
                    </Card>
                  </Col>
                ))}
              </Row>
            )}
            <div style={{ textAlign: 'center', marginTop: 16 }}>
              <Button onClick={handleSkipTopics}>没有合适的，直接输入主题</Button>
            </div>
          </Card>
        )}

        {/* 步骤1：输入主题 */}
        {current === 0 && !showTopicRecommend && (
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <div>
              <div style={{ marginBottom: 8, fontWeight: 500 }}>创作主题</div>
              <Input placeholder="例如：咸阳春日赏花、袁家村美食探店..." value={topic} onChange={e => setTopic(e.target.value)} size="large" />
            </div>
            <div>
              <div style={{ marginBottom: 8, fontWeight: 500 }}>视频风格</div>
              <Select value={style} onChange={setStyle} size="large" style={{ width: 200 }}
                options={[{ value: '探店', label: '快节奏探店' }, { value: '航拍', label: '唯美航拍' }, { value: '故事', label: '故事讲述' }]}
              />
            </div>
            <Button type="primary" size="large" icon={<ThunderboltOutlined />} onClick={handleGenerateScript} loading={loading}>
              AI生成文案
            </Button>
          </Space>
        )}

        {/* 步骤2：文案预览 */}
        {current >= 1 && script && (
          <Card title={`文案预览：${script.title as string || topic}`} style={{ marginBottom: 16 }}>
            {/* 分镜列表 */}
            {(script.scenes as Array<Record<string, unknown>>)?.map((scene, i) => (
              <div key={i} style={{ marginBottom: 12, padding: 12, background: '#fafafa', borderRadius: 8 }}>
                <Tag color="blue">分镜{i + 1}</Tag>
                <span style={{ marginLeft: 8, color: '#888' }}>时长：{scene.duration as number}秒</span>
                <div style={{ marginTop: 8 }}><strong>画面：</strong>{scene.description as string}</div>
                <div style={{ marginTop: 4 }}><strong>字幕：</strong>{scene.subtitle as string}</div>
              </div>
            ))}
            <Space>
              <Button onClick={() => setCurrent(0)}>重新生成</Button>
              {current === 1 && (
                <Button type="primary" icon={<VideoCameraOutlined />} onClick={handleCompose} loading={loading}>
                  合成视频
                </Button>
              )}
            </Space>
          </Card>
        )}

        {/* 步骤3和4：合成中/下载 */}
        {current >= 2 && (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin size="large" spinning={current === 2} />
            {current === 3 && (
              <Card style={{ marginTop: 16 }}>
                <Alert type="success" message="视频生成成功！" showIcon />
                {/* 视频预览区域 */}
                <div style={{ marginTop: 16, padding: 20, background: '#000', borderRadius: 8, color: '#fff', textAlign: 'center', minHeight: 200, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                  <VideoCameraOutlined style={{ fontSize: 48 }} />
                  <div style={{ marginTop: 12, fontSize: 14 }}>视频已就绪</div>
                  <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>{topic}</div>
                  {taskId && <div style={{ fontSize: 11, color: '#666', marginTop: 4 }}>任务 ID: {taskId}</div>}
                </div>
                {/* 操作按钮 */}
                <Space style={{ marginTop: 16 }}>
                  <Button type="primary" size="large" icon={<DownloadOutlined />} onClick={handleDownload}>
                    下载视频
                  </Button>
                  <Button size="large" onClick={() => { setCurrent(0); setScript(null); setTopic(''); setTaskId(null) }}>
                    再次创作
                  </Button>
                </Space>
              </Card>
            )}
          </div>
        )}
      </Card>
    </div>
  )
}
