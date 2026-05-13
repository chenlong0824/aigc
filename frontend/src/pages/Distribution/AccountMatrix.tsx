import { useEffect, useState } from 'react'
import { Card, Table, Button, Modal, Form, Input, Select, InputNumber, Space, Tag, Popconfirm, message, Row, Col, DatePicker } from 'antd'
import { PlusOutlined, SendOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { distributionApi } from '../../services/api'

export default function AccountMatrix() {
  const [accounts, setAccounts] = useState<Array<Record<string, unknown>>>([])
  const [logs, setLogs] = useState<Array<Record<string, unknown>>>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [editingAccount, setEditingAccount] = useState<Record<string, unknown> | null>(null)
  const [publishModalOpen, setPublishModalOpen] = useState(false)
  const [form] = Form.useForm()
  const [publishForm] = Form.useForm()

  const loadAccounts = async () => {
    const res = await distributionApi.getAccounts()
    setAccounts(res.data.data)
  }

  const loadLogs = async () => {
    const res = await distributionApi.getPublishLogs()
    setLogs(res.data.data)
  }

  useEffect(() => { loadAccounts(); loadLogs() }, [])

  const handleSave = async () => {
    const values = form.getFieldsValue()
    if (editingAccount) {
      await distributionApi.updateAccount(editingAccount.id as number, values)
      message.success('更新成功')
    } else {
      await distributionApi.createAccount(values)
      message.success('创建成功')
    }
    setModalOpen(false)
    setEditingAccount(null)
    form.resetFields()
    loadAccounts()
  }

  const handleDelete = async (id: number) => {
    await distributionApi.deleteAccount(id)
    message.success('删除成功')
    loadAccounts()
  }

  const handlePublish = async () => {
    const values = publishForm.getFieldsValue()
    await distributionApi.schedulePublish({
      account_id: values.account_id,
      content_title: values.content_title,
      scheduled_at: values.scheduled_at.toISOString(),
    })
    message.success('已加入发布队列')
    setPublishModalOpen(false)
    publishForm.resetFields()
    loadLogs()
  }

  const columns = [
    { title: '账号名称', dataIndex: 'name', key: 'name' },
    { title: '平台', dataIndex: 'platform', key: 'platform', render: (p: string) => <Tag color={p === '抖音' ? 'blue' : p === '小红书' ? 'red' : 'green'}>{p}</Tag> },
    { title: '分组', dataIndex: 'group_name', key: 'group_name', render: (g: string) => <Tag>{g}</Tag> },
    { title: '粉丝数', dataIndex: 'followers', key: 'followers', render: (f: number) => (f / 10000).toFixed(1) + 'w' },
    { title: '状态', dataIndex: 'status', key: 'status', render: (s: string) => <Tag color={s === 'active' ? 'green' : 'red'}>{s === 'active' ? '活跃' : '停用'}</Tag> },
    { title: '操作', key: 'action', render: (_: unknown, r: Record<string, unknown>) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => { setEditingAccount(r); form.setFieldsValue(r); setModalOpen(true) }}>编辑</Button>
          <Popconfirm title="确定删除？" onConfirm={() => handleDelete(r.id as number)}>
            <Button size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const logColumns = [
    { title: '账号', dataIndex: 'account_id', key: 'account_id' },
    { title: '内容标题', dataIndex: 'content_title', key: 'content_title' },
    { title: '状态', dataIndex: 'status', key: 'status', render: (s: string) => <Tag color={s === 'success' ? 'green' : s === 'pending' ? 'orange' : 'red'}>{s === 'success' ? '已发布' : s === 'pending' ? '待发布' : '失败'}</Tag> },
    { title: '计划时间', dataIndex: 'scheduled_at', key: 'scheduled_at' },
    { title: '发布时间', dataIndex: 'published_at', key: 'published_at' },
  ]

  return (
    <div>
      <Row gutter={16}>
        <Col span={14}>
          <Card title="账号管理" extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingAccount(null); form.resetFields(); setModalOpen(true) }}>添加账号</Button>}>
            <Table dataSource={accounts as Array<Record<string, unknown>>} columns={columns} rowKey="id" pagination={false} size="small" />
          </Card>
        </Col>
        <Col span={10}>
          <Card title="发布日志" extra={<Button icon={<SendOutlined />} onClick={() => { publishForm.resetFields(); setPublishModalOpen(true) }}>模拟发布</Button>}>
            <Table dataSource={logs as Array<Record<string, unknown>>} columns={logColumns} rowKey="id" pagination={false} size="small" />
          </Card>
        </Col>
      </Row>

      <Modal title={editingAccount ? '编辑账号' : '添加账号'} open={modalOpen} onOk={handleSave} onCancel={() => setModalOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="账号名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="platform" label="平台" rules={[{ required: true }]}>
            <Select options={[{ value: '抖音', label: '抖音' }, { value: '小红书', label: '小红书' }, { value: '视频号', label: '视频号' }]} />
          </Form.Item>
          <Form.Item name="group_name" label="分组"><Input /></Form.Item>
          <Form.Item name="followers" label="粉丝数"><InputNumber style={{ width: '100%' }} /></Form.Item>
        </Form>
      </Modal>

      <Modal title="模拟发布" open={publishModalOpen} onOk={handlePublish} onCancel={() => setPublishModalOpen(false)}>
        <Form form={publishForm} layout="vertical">
          <Form.Item name="account_id" label="选择账号" rules={[{ required: true }]}>
            <Select options={accounts.map(a => ({ value: a.id as number, label: a.name as string }))} />
          </Form.Item>
          <Form.Item name="content_title" label="内容标题" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="scheduled_at" label="发布时间"><DatePicker showTime style={{ width: '100%' }} /></Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
