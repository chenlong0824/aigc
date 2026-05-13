import { useEffect, useState } from 'react'
import { Card, Row, Col, Table, Statistic, Tag, Alert } from 'antd'
import { RiseOutlined, FallOutlined } from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { conversionApi } from '../../services/api'

export default function AttributionAnalysis() {
  const [funnel, setFunnel] = useState<Record<string, unknown>>({})
  const [attribution, setAttribution] = useState<Record<string, unknown>>({})
  const [roi, setRoi] = useState<Record<string, unknown>>({})

  useEffect(() => {
    conversionApi.getFunnel().then(r => setFunnel(r.data.data))
    conversionApi.getAttribution().then(r => setAttribution(r.data.data))
    conversionApi.getRoi().then(r => setRoi(r.data.data))
  }, [])

  const f = funnel as Record<string, Array<{ name: string; value: number }>>
  const a = attribution as Record<string, Array<{ name: string; channels: Array<{ channel: string; contribution: number }> }>>
  const r = roi as Record<string, unknown>

  const funnelOption = {
    tooltip: { trigger: 'item' as const },
    series: [{
      type: 'funnel' as const,
      left: '10%', top: 60, bottom: 60, width: '80%',
      sort: 'descending' as const,
      data: f?.stages?.map((s: { name: string; value: number }) => ({ name: s.name, value: s.value })) || [],
    }],
  }

  const attributionOption = {
    tooltip: { trigger: 'axis' as const },
    legend: { data: a?.models?.map((m: { name: string }) => m.name) || [], top: 30 },
    xAxis: { type: 'category' as const, data: ['抖音', '小红书', '视频号', '微信'] },
    yAxis: { type: 'value' as const, name: '贡献度(%)' },
    series: (a?.models || []).map((m: { name: string; channels: Array<{ channel: string; contribution: number }> }) => ({
      name: m.name, type: 'bar' as const,
      data: m.channels.map((c: { contribution: number }) => c.contribution),
    })),
  }

  const channels = (r?.channels as Array<Record<string, unknown>>) || []
  const channelColumns = [
    { title: '渠道', dataIndex: 'channel', key: 'channel', render: (c: string) => <Tag color="blue">{c}</Tag> },
    { title: '投入(元)', dataIndex: 'cost', key: 'cost', render: (v: number) => v?.toLocaleString() },
    { title: 'GMV(元)', dataIndex: 'gmv', key: 'gmv', render: (v: number) => v?.toLocaleString() },
    { title: 'ROI', dataIndex: 'roi', key: 'roi', render: (v: number) => <span style={{ color: v > 3 ? '#52c41a' : '#faad14', fontWeight: 600 }}>{v}</span> },
  ]

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={6}><Card><Statistic title="总GMV" value={r?.total_gmv as number} prefix="¥" /></Card></Col>
        <Col span={6}><Card><Statistic title="总投入" value={r?.total_cost as number} prefix="¥" /></Card></Col>
        <Col span={6}><Card><Statistic title="整体ROI" value={r?.overall_roi as number} prefix={<RiseOutlined />} precision={2} valueStyle={{ color: '#52c41a' }} /></Card></Col>
        <Col span={6}><Card><Statistic title="转化率" value={(funnel as Record<string, unknown>)?.conversion_rate as string || '0%'} /></Card></Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card title="转化漏斗">
            <ReactECharts option={funnelOption} style={{ height: 340 }} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="多触点归因模型对比">
            <ReactECharts option={attributionOption} style={{ height: 340 }} />
          </Card>
        </Col>
      </Row>

      <Card title="渠道ROI明细" style={{ marginTop: 16 }}>
        <Table dataSource={channels} columns={channelColumns} rowKey="channel" pagination={false} />
      </Card>

      <Card style={{ marginTop: 16 }}>
        <Alert type="info" message="AI策略建议" description={((attribution as Record<string, unknown>)?.recommendation as string) || ((roi as Record<string, unknown>)?.advice as string) || '正在分析中...'} showIcon />
      </Card>
    </div>
  )
}
