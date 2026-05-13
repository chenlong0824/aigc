import { Routes, Route, useLocation, useNavigate, Navigate } from 'react-router-dom'
import { Layout, Menu, Button, Space } from 'antd'
import {
  DashboardOutlined,
  VideoCameraOutlined,
  ShareAltOutlined,
  SwapOutlined,
  BarChartOutlined,
  SettingOutlined,
  PictureOutlined,
  LogoutOutlined,
} from '@ant-design/icons'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import OneClickVideo from './pages/ContentFactory/OneClickVideo'
import DigitalHuman from './pages/ContentFactory/DigitalHuman'
import AccountMatrix from './pages/Distribution/AccountMatrix'
import CitizenMarketing from './pages/Distribution/CitizenMarketing'
import MonitorReport from './pages/Distribution/MonitorReport'
import AiCustomerService from './pages/Conversion/AiCustomerService'
import AttributionAnalysis from './pages/Conversion/AttributionAnalysis'
import UserProfile from './pages/Insight/UserProfile'
import Settings from './pages/Settings'
import MediaLibrary from './pages/Settings/MediaLibrary'
import { isAuthenticated, removeToken } from './services/auth'

const { Header, Sider, Content } = Layout

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: '仪表盘' },
  {
    key: '/content',
    icon: <VideoCameraOutlined />,
    label: '内容工厂',
    children: [
      { key: '/content/one-click', label: '一键成片' },
      { key: '/content/digital-human', label: '数智人播报' },
    ],
  },
  {
    key: '/distribution',
    icon: <ShareAltOutlined />,
    label: '分发网络',
    children: [
      { key: '/distribution/accounts', label: '账号矩阵' },
      { key: '/distribution/citizen', label: '全民营销' },
      { key: '/distribution/report', label: '监理报表' },
    ],
  },
  {
    key: '/conversion',
    icon: <SwapOutlined />,
    label: '流量转化',
    children: [
      { key: '/conversion/customer-service', label: 'AI智能客服' },
      { key: '/conversion/attribution', label: '归因分析' },
    ],
  },
  {
    key: '/insight',
    icon: <BarChartOutlined />,
    label: '客群洞察',
    children: [
      { key: '/insight/profiles', label: '用户画像' },
    ],
  },
  { key: '/settings', icon: <SettingOutlined />, label: '系统设置' },
  { key: '/settings/media', icon: <PictureOutlined />, label: '素材库' },
]

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

function App() {
  const location = useLocation()
  const navigate = useNavigate()

  const isLoginPage = location.pathname === '/login'
  const selectedKey = location.pathname === '/' ? '/' : location.pathname
  const openKeys = ['/content', '/distribution', '/conversion', '/insight'].filter(k => selectedKey.startsWith(k))

  const handleLogout = () => {
    removeToken()
    navigate('/login', { replace: true })
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="*"
        element={
          <ProtectedRoute>
            <Layout style={{ minHeight: '100vh' }}>
              <Sider width={220} theme="dark">
                <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <span className="logo-text">咸阳文旅AIGC</span>
                </div>
                <Menu
                  theme="dark"
                  mode="inline"
                  selectedKeys={[selectedKey]}
                  defaultOpenKeys={openKeys}
                  items={menuItems}
                  onClick={({ key }) => navigate(key)}
                />
              </Sider>
              <Layout>
                <Header style={{
                  background: '#fff',
                  padding: '0 24px',
                  fontSize: 16,
                  fontWeight: 500,
                  borderBottom: '1px solid #f0f0f0',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}>
                  <span>咸阳文旅AIGC智能营销平台 Demo</span>
                  <Button
                    type="text"
                    icon={<LogoutOutlined />}
                    onClick={handleLogout}
                    danger
                  >
                    退出登录
                  </Button>
                </Header>
                <Content className="page-container">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/content/one-click" element={<OneClickVideo />} />
                    <Route path="/content/digital-human" element={<DigitalHuman />} />
                    <Route path="/distribution/accounts" element={<AccountMatrix />} />
                    <Route path="/distribution/citizen" element={<CitizenMarketing />} />
                    <Route path="/distribution/report" element={<MonitorReport />} />
                    <Route path="/conversion/customer-service" element={<AiCustomerService />} />
                    <Route path="/conversion/attribution" element={<AttributionAnalysis />} />
                    <Route path="/insight/profiles" element={<UserProfile />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/settings/media" element={<MediaLibrary />} />
                  </Routes>
                </Content>
              </Layout>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default App
