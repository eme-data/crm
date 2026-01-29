import { Package, FileText, Users, TrendingUp } from 'lucide-react'
import DashboardLayout from '../components/DashboardLayout'

export default function DashboardPage() {
    const stats = [
        {
            icon: Package,
            label: 'Matériaux',
            value: '0',
            color: 'bg-blue-500',
            link: '/materials'
        },
        {
            icon: FileText,
            label: 'Articles',
            value: '0',
            color: 'bg-green-500',
            link: '/articles'
        },
        {
            icon: FileText,
            label: 'Services',
            value: '0',
            color: 'bg-purple-500',
            link: '/services'
        },
        {
            icon: Users,
            label: 'Clients',
            value: '0',
            color: 'bg-orange-500',
            link: '/clients'
        },
    ]

    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
                    <p className="text-gray-600">Vue d'ensemble de votre CRM</p>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {stats.map((stat) => (
                        <div
                            key={stat.label}
                            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
                            onClick={() => window.location.href = stat.link}
                        >
                            <div className="flex items-center justify-between mb-4">
                                <div className={`${stat.color} w-12 h-12 rounded-lg flex items-center justify-center`}>
                                    <stat.icon className="w-6 h-6 text-white" />
                                </div>
                                <TrendingUp className="w-5 h-5 text-green-500" />
                            </div>
                            <h3 className="text-gray-600 text-sm font-medium mb-1">{stat.label}</h3>
                            <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                        </div>
                    ))}
                </div>

                {/* Quick Actions */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">Actions rapides</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <button className="btn-primary text-left p-4 rounded-lg">
                            <Package className="w-5 h-5 mb-2" />
                            <span className="block font-medium">Nouveau matériau</span>
                            <span className="text-sm opacity-80">Ajouter au catalogue</span>
                        </button>
                        <button className="btn-secondary text-left p-4 rounded-lg">
                            <FileText className="w-5 h-5 mb-2 text-gray-700" />
                            <span className="block font-medium text-gray-900">Importer Excel</span>
                            <span className="text-sm text-gray-600">Importer votre matrice</span>
                        </button>
                        <button className="btn-secondary text-left p-4 rounded-lg">
                            <Users className="w-5 h-5 mb-2 text-gray-700" />
                            <span className="block font-medium text-gray-900">Nouveau client</span>
                            <span className="text-sm text-gray-600">Ajouter un client</span>
                        </button>
                    </div>
                </div>

                {/* Info Phase 3 */}
                <div className="mt-8 p-6 bg-blue-50 border border-blue-200 rounded-xl">
                    <h3 className="font-semibold text-blue-900 mb-2">🎉 Phase 3 - Frontend React</h3>
                    <p className="text-sm text-blue-800">
                        Interface utilisateur moderne en cours de développement.
                        Les pages de gestion du catalogue seront bientôt disponibles.
                    </p>
                </div>
            </div>
        </DashboardLayout>
    )
}
