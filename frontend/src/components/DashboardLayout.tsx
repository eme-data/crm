import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    LayoutDashboard,
    Package,
    FileText,
    Users,
    LogOut,
    Menu,
    X,
    Upload
} from 'lucide-react'
import { authService, User } from '../services/authService'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [sidebarOpen, setSidebarOpen] = useState(true)
    const navigate = useNavigate()

    useEffect(() => {
        const storedUser = authService.getStoredUser()
        if (!storedUser) {
            navigate('/login')
        } else {
            setUser(storedUser)
        }
    }, [navigate])

    const handleLogout = () => {
        authService.logout()
        navigate('/login')
    }

    const menuItems = [
        { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
        { icon: Package, label: 'Matériaux', path: '/materials' },
        { icon: FileText, label: 'Articles', path: '/articles' },
        { icon: FileText, label: 'Services', path: '/services' },
        { icon: Upload, label: 'Import', path: '/import' },
        { icon: Users, label: 'Clients', path: '/clients' },
    ]

    if (!user) return null

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Sidebar */}
            <aside
                className={`
          bg-white border-r border-gray-200 transition-all duration-300
          ${sidebarOpen ? 'w-64' : 'w-20'}
        `}
            >
                {/* Header */}
                <div className="h-16 border-b border-gray-200 flex items-center justify-between px-4">
                    {sidebarOpen && (
                        <div className="flex items-center">
                            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                                <LayoutDashboard className="w-5 h-5 text-white" />
                            </div>
                            <span className="ml-3 font-semibold text-gray-900">CRM BTP</span>
                        </div>
                    )}
                    <button
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        {sidebarOpen ? (
                            <X className="w-5 h-5 text-gray-600" />
                        ) : (
                            <Menu className="w-5 h-5 text-gray-600" />
                        )}
                    </button>
                </div>

                {/* Menu */}
                <nav className="p-4 space-y-2">
                    {menuItems.map((item) => (
                        <button
                            key={item.path}
                            onClick={() => navigate(item.path)}
                            className={`
                w-full flex items-center p-3 rounded-lg transition-colors
                hover:bg-blue-50 hover:text-blue-600
                ${window.location.pathname === item.path ? 'bg-blue-50 text-blue-600' : 'text-gray-700'}
              `}
                        >
                            <item.icon className="w-5 h-5 flex-shrink-0" />
                            {sidebarOpen && <span className="ml-3">{item.label}</span>}
                        </button>
                    ))}
                </nav>

                {/* User */}
                <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-white">
                    {sidebarOpen ? (
                        <div className="flex items-center justify-between">
                            <div className="flex items-center min-w-0">
                                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                                    <span className="text-white font-semibold text-sm">
                                        {user.first_name[0]}{user.last_name[0]}
                                    </span>
                                </div>
                                <div className="ml-3 min-w-0 flex-1">
                                    <p className="text-sm font-medium text-gray-900 truncate">
                                        {user.first_name} {user.last_name}
                                    </p>
                                    <p className="text-xs text-gray-500 truncate">{user.role}</p>
                                </div>
                            </div>
                            <button
                                onClick={handleLogout}
                                className="p-2 hover:bg-gray-100 rounded-lg transition-colors flex-shrink-0"
                                title="Déconnexion"
                            >
                                <LogOut className="w-5 h-5 text-gray-600" />
                            </button>
                        </div>
                    ) : (
                        <button
                            onClick={handleLogout}
                            className="w-full p-2 hover:bg-gray-100 rounded-lg transition-colors"
                            title="Déconnexion"
                        >
                            <LogOut className="w-5 h-5 text-gray-600 mx-auto" />
                        </button>
                    )}
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                {children}
            </main>
        </div>
    )
}
