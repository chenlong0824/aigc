import { useEffect, useState, useRef } from 'react'
import { Card, Table, Button, Upload, Image, Tag, Popconfirm, message, Modal, Input, Space } from 'antd'
import { UploadOutlined, DeleteOutlined, EditOutlined, InboxOutlined } from '@ant-design/icons'
import { contentApi } from '../../services/api'

const { Dragger } = Upload

export default function MediaLibrary() {
  const [mediaList, setMediaList] = useState<Array<Record<string, unknown>>>([])
  const [loading, setLoading] = useState(false)
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editTags, setEditTags] = useState('')
  const [editName, setEditName] = useState('')

  const loadMedia = async () => {
    setLoading(true)
    try {
      const res = await contentApi.getMedia()
      setMediaList(res.data.data)
    } catch { message.error('加载素材失败') }
    setLoading(false)
  }

  useEffect(() => { loadMedia() }, [])

  const handleUpload = async (file: File) => {
    try {
      await contentApi.uploadMedia(file)
      message.success(`${file.name} 上传成功`)
      loadMedia()
    } catch { message.error(`${file.name} 上传失败`) }
    return false
  }

  const handleDelete = async (id: number) => {
    await contentApi.deleteMedia(id)
    message.success('删除成功')
    loadMedia()
  }

  const handleEdit = async () => {
    if (!editingId) return
    await contentApi.updateMedia(editingId, { tags: editTags, name: editName })
    message.success('更新成功')
    setEditModalOpen(false)
    loadMedia()
  }

  const openEdit = (r: Record<string, unknown>) => {
    setEditingId(r.id as number)
    setEditTags((r.tags as string) || '')
    setEditName((r.name as string) || '')
    setEditModalOpen(true)
  }

  const columns = [
    { title: '预览', key: 'preview', width: 100, render: (_: unknown, r: Record<string, unknown>) => {
        const fp = (r.file_path as string).replace(/\\/g, '/')
        const url = fp.startsWith('E:/trae/aigc/data/media/') ? '/media/' + fp.replace('E:/trae/aigc/data/media/', '') : '/media/' + fp.split('data/media/').pop()
        return r.type === 'image'
          ? <Image src={url} width={60} height={60} style={{ objectFit: 'cover', borderRadius: 4 }} fallback="" preview={{ mask: '预览' }} />
          : <video src={url} width={60} height={60} style={{ objectFit: 'cover', borderRadius: 4 }} />
      }},
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: '类型', dataIndex: 'type', key: 'type', width: 80, render: (t: string) => <Tag color={t === 'image' ? 'blue' : 'green'}>{t === 'image' ? '图片' : '视频'}</Tag> },
    { title: '标签', dataIndex: 'tags', key: 'tags', render: (t: string) => t ? t.split(/\s+/).map((tag: string) => <Tag key={tag}>{tag}</Tag>) : <Tag color="#ddd">无标签</Tag> },
    { title: '操作', key: 'action', width: 150, render: (_: unknown, r: Record<string, unknown>) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)}>编辑</Button>
          <Popconfirm title="确定删除？" onConfirm={() => handleDelete(r.id as number)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )},
  ]

  return (
    <div>
      <Card title="素材库管理" extra={<Button onClick={loadMedia} loading={loading}>刷新</Button>}>
        <div style={{ marginBottom: 24 }}>
          <Dragger
            multiple
            accept="image/*,video/*"
            beforeUpload={(file) => { handleUpload(file); return false }}
            showUploadList={false}
          >
            <p className="ant-upload-drag-icon"><InboxOutlined /></p>
            <p>点击或拖拽图片/视频到此区域上传</p>
            <p style={{ color: '#999' }}>支持 JPG/PNG/WebP/MP4/MOV 格式</p>
          </Dragger>
        </div>

        <Table
          dataSource={mediaList}
          columns={columns}
          rowKey="id"
          pagination={{ pageSize: 20 }}
          size="small"
          locale={{ emptyText: '素材库为空，请上传图片或视频' }}
        />
      </Card>

      <Modal title="编辑素材" open={editModalOpen} onOk={handleEdit} onCancel={() => setEditModalOpen(false)}>
        <div style={{ marginBottom: 12 }}>
          <div style={{ marginBottom: 4, fontWeight: 500 }}>素材名称</div>
          <Input value={editName} onChange={e => setEditName(e.target.value)} placeholder="输入素材名称" />
        </div>
        <div>
          <div style={{ marginBottom: 4, fontWeight: 500 }}>标签（空格分隔）</div>
          <Input value={editTags} onChange={e => setEditTags(e.target.value)} placeholder="例如：古镇 美食 夜景 航拍" />
          <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>标签用于一键成片时的素材自动匹配，建议用关键词描述素材内容</div>
        </div>
      </Modal>
    </div>
  )
}
