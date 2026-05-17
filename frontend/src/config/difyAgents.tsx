import { RobotOutlined, BulbOutlined, ThunderboltOutlined } from '@ant-design/icons'

export interface DifyAgentConfig {
  id: string
  name: string
  description: string
  icon: React.ReactNode
  token: string
  baseUrl: string
}

export const DIFY_AGENTS: DifyAgentConfig[] = [
  {
    id: 'demo_test1',
    name: '旅游demo',
    description: '专业解答咸阳旅游相关问题，提供景点推荐、美食攻略等',
    icon: <RobotOutlined />,
    token: 'spcjGPdHHHqq9yUg',
    baseUrl: 'http://localhost:8080',
  },
  {
    id: 'demo_test2',
    name: '矿工demo',
    description: '采矿相关',
    icon: <BulbOutlined />,
    token: 'pP2fZ2obLf2dDEzP',
    baseUrl: 'http://localhost:8080',
  },
  {
    id: 'content-assistant',
    name: '内容创作助手',
    description: '助力短视频、文案创作，提供灵感和素材建议',
    icon: <ThunderboltOutlined />,
    token: '',
    baseUrl: 'http://localhost',
  },
]
