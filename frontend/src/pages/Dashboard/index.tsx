import { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic } from 'antd'
import { VideoCameraOutlined, ShareAltOutlined, DollarOutlined, UserOutlined } from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { dashboardApi } from '../../services/api'

export default function Dashboard() {
  const [summary, setSummary] = useState<Record<string, unknown>>({})
  const [trends, setTrends] = useState<Record<string, unknown>>({})

  useEffect(() => {
    dashboardApi.getSummary().then(r => setSummary(r.data.data))
    dashboardApi.getTrends().then(r => setTrends(r.data.data))
  }, [])

  const s = summary as Record<string, Record<string, unknown>>

  const lineOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['播放量', 'GMV', '粉丝数'] },
    xAxis: { type: 'category' as const, data: (trends as Record<string, Array<{ date: string }>>)?.views_trend?.map((i: { date: string }) => i.date) || [] },
    yAxis: { type: 'value' as const },
    series: [
      { name: '播放量', type: 'line', data: (trends as Record<string, Array<{ views: number }>>)?.views_trend?.map((i: { views: number }) => i.views) || [], smooth: true },
      { name: 'GMV', type: 'line', data: (trends as Record<string, Array<{ gmv: number }>>)?.gmv_trend?.map((i: { gmv: number }) => i.gmv) || [], smooth: true },
      { name: '粉丝数', type: 'line', data: (trends as Record<string, Array<{ followers: number }>>)?.follower_trend?.map((i: { followers: number }) => (i.followers - 100000) / 1000) || [], smooth: true },
    ],
  }

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="视频生成数" value={s?.content_factory?.videos_generated as number || 0} prefix={<VideoCameraOutlined />} /></Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="社媒账号数" value={s?.distribution?.accounts_count as number || 0} prefix={<ShareAltOutlined />} /></Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="总GMV(元)" value={s?.conversion?.total_gmv as number || 0} prefix={<DollarOutlined />} /></Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="用户客群数" value={s?.insight?.user_segments as number || 0} prefix={<UserOutlined />} /></Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} sm={12}>
          <Card><Statistic title="今日发布" value={s?.distribution?.today_published as number || 0} /></Card>
        </Col>
        <Col xs={24} sm={12}>
          <Card><Statistic title="互动率" value={s?.distribution?.avg_engagement_rate as string || '0%'} /></Card>
        </Col>
        <Col xs={24} sm={12}>
          <Card><Statistic title="咨询量" value={s?.conversion?.consultations as number || 0} /></Card>
        </Col>
        <Col xs={24} sm={12}>
          <Card><Statistic title="预订量" value={s?.conversion?.booking_count as number || 0} /></Card>
        </Col>
      </Row>

      <Card title="近7日趋势" style={{ marginTop: 24 }}>
        <ReactECharts option={lineOption} style={{ height: 400 }} />
      </Card>
    </div>
  )
}
