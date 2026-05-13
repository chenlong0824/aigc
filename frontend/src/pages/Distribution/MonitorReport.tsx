import { useEffect, useState } from 'react'
import { Card, Row, Col, Table, Tag, Statistic, Alert } from 'antd'
import { ArrowUpOutlined, WarningOutlined } from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { distributionApi } from '../../services/api'

export default function MonitorReport() {
  const [overview, setOverview] = useState<Record<string, unknown>>({})
  const [anomalies, setAnomalies] = useState<Array<Record<string, unknown>>>([])

  useEffect(() => {
    distributionApi.getReportsOverview().then(r => setOverview(r.data.data))
    distributionApi.getReportsAnomalies().then(r => setAnomalies(r.data.data))
  }, [])

  const o = overview as Record<string, number>

  const barOption = {
    tooltip: { trigger: 'axis' as const },
    xAxis: { type: 'category' as const, data: ['播放量', '点赞', '评论', '分享', '新增粉丝'] },
    yAxis: { type: 'value' as const },
    series: [{
      type: 'bar',
      data: [o?.total_views || 0, o?.total_likes || 0, o?.total_comments || 0, o?.total_shares || 0, o?.new_followers || 0],
      itemStyle: { color: '#667eea' },
    }],
  }

  const anomalyColumns = [
    { title: '账号', dataIndex: 'account_name', key: 'account_name' },
    { title: '平台', dataIndex: 'platform', key: 'platform', render: (p: string) => <Tag color="blue">{p}</Tag> },
    { title: '指标', dataIndex: 'metric', key: 'metric', render: (m: string) => <Tag color="orange">{m}</Tag> },
    { title: '实际值', dataIndex: 'value', key: 'value', render: (v: number) => <span style={{ color: 'red', fontWeight: 600 }}>{v?.toLocaleString()}</span> },
    { title: '预期值', dataIndex: 'expected', key: 'expected' },
    { title: '原因', dataIndex: 'reason', key: 'reason', render: (r: string) => <Tag color="red">{r}</Tag> },
  ]

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={6}><Card><Statistic title="总播放量" value={o?.total_views} prefix={<ArrowUpOutlined />} /></Card></Col>
        <Col span={6}><Card><Statistic title="总点赞" value={o?.total_likes} /></Card></Col>
        <Col span={6}><Card><Statistic title="总评论" value={o?.total_comments} /></Card></Col>
        <Col span={6}><Card><Statistic title="新增粉丝" value={o?.new_followers} /></Card></Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={6}><Card><Statistic title="活跃账号" value={o?.accounts_active} /></Card></Col>
        <Col span={6}><Card><Statistic title="发布内容" value={o?.content_published} /></Card></Col>
        <Col span={6}><Card><Statistic title="环比增长" value={o?.period_growth} suffix="%" precision={1} valueStyle={{ color: '#52c41a' }} /></Card></Col>
        <Col span={6}><Card><Statistic title="达标率" value={85} suffix="%" valueStyle={{ color: '#52c41a' }} /></Card></Col>
      </Row>

      <Card title="数据总览" style={{ marginTop: 16 }}>
        <ReactECharts option={barOption} style={{ height: 350 }} />
      </Card>

      <Card title={<><WarningOutlined /> 异常检测</>} style={{ marginTop: 16 }}>
        {anomalies.length > 0 ? (
          <Table dataSource={anomalies as Array<Record<string, unknown>>} columns={anomalyColumns} rowKey="account_name" pagination={false} size="small" />
        ) : (
          <Alert type="success" message="未检测到异常数据" showIcon />
        )}
      </Card>
    </div>
  )
}
