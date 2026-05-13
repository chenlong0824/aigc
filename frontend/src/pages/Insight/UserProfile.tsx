import { useEffect, useState } from 'react'
import { Card, Row, Col, Table, Tag, Progress } from 'antd'
import ReactECharts from 'echarts-for-react'
import { insightApi } from '../../services/api'

export default function UserProfile() {
  const [profiles, setProfiles] = useState<Record<string, unknown>>({})

  useEffect(() => {
    insightApi.getProfiles().then(r => setProfiles(r.data.data))
  }, [])

  const p = profiles as Record<string, Array<Record<string, unknown>>>
  const o = profiles as Record<string, Record<string, number>>

  const radarOption = {
    tooltip: {},
    legend: { data: p?.user_segments?.map((s: Record<string, unknown>) => s.name as string) || [] },
    radar: { indicator: [{ name: '亲子', max: 100 }, { name: '自然', max: 100 }, { name: '美食', max: 100 }, { name: '文化', max: 100 }, { name: '拍照', max: 100 }] },
    series: [{
      type: 'radar',
      data: p?.user_segments?.map((s: Record<string, unknown>, i: number) => ({
        name: s.name as string,
        value: [[80, 90, 50, 30, 40], [30, 20, 30, 90, 20], [40, 30, 80, 20, 90], [20, 40, 30, 80, 10]][i] || [50, 50, 50, 50, 50],
      })) || [],
    }],
  }

  const pieOption = {
    tooltip: { trigger: 'item' as const },
    series: [{
      type: 'pie' as const, radius: ['40%', '70%'],
      data: Object.entries(o?.source_distribution || {}).map(([name, value]) => ({ name, value })),
    }],
  }

  const ageOption = {
    tooltip: { trigger: 'item' as const },
    series: [{
      type: 'pie' as const, radius: '70%',
      data: Object.entries(o?.age_distribution || {}).map(([name, value]) => ({ name, value })),
      label: { formatter: '{b}: {c}%' },
    }],
  }

  const segments = (p?.user_segments || []) as Array<Record<string, unknown>>
  const segColumns = [
    { title: '客群', dataIndex: 'name', key: 'name' },
    { title: '占比', dataIndex: 'percentage', key: 'percentage', render: (v: number) => <Progress percent={v} size="small" /> },
    { title: '标签', dataIndex: 'tags', key: 'tags', render: (t: Array<string>) => t?.map(tag => <Tag key={tag}>{tag}</Tag>) },
    { title: '消费水平', dataIndex: 'avg_consumption', key: 'avg_consumption' },
    { title: '活跃时段', dataIndex: 'active_time', key: 'active_time' },
  ]

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card title="客群雷达图对比">
            <ReactECharts option={radarOption} style={{ height: 400 }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card title="客源地分布">
            <ReactECharts option={pieOption} style={{ height: 400 }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card title="年龄分布">
            <ReactECharts option={ageOption} style={{ height: 400 }} />
          </Card>
        </Col>
      </Row>

      <Card title="客群细分详情" style={{ marginTop: 16 }}>
        <Table dataSource={segments} columns={segColumns} rowKey="name" pagination={false} />
      </Card>
    </div>
  )
}
