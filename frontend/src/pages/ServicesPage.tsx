import { useState, useEffect } from 'react'
import { Search, Trash2, Briefcase } from 'lucide-react'
import DashboardLayout from '../components/DashboardLayout'
import { servicesService, Service } from '../services/servicesService'

export default function ServicesPage() {
    const [services, setServices] = useState<Service[]>([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')

    useEffect(() => {
        loadServices()
    }, [])

    const loadServices = async () => {
        try {
            setLoading(true)
            const data = await servicesService.list({
                active_only: true,
                search: search || undefined
            })
            setServices(data)
        } catch (error) {
            console.error('Erreur chargement services:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleDelete = async (id: string) => {
        if (!confirm('Êtes-vous sûr de vouloir supprimer ce service ?')) return

        try {
            await servicesService.delete(id)
            loadServices()
        } catch (error) {
            alert('Erreur lors de la suppression')
        }
    }

    return (
        <DashboardLayout>
            <div className="p-8">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">Services</h1>
                        <p className="text-gray-600">Prestations et services forfaitaires</p>
                    </div>
                </div>

                {/* Search */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
                    <div className="flex items-center gap-4">
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                            <input
                                type="text"
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && loadServices()}
                                placeholder="Rechercher par code ou nom..."
                                className="w-full pl-11 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                            />
                        </div>
                        <button onClick={loadServices} className="btn-primary">
                            Rechercher
                        </button>
                    </div>

                    <div className="mt-4 flex items-center text-sm text-gray-600">
                        <Briefcase className="w-4 h-4 mr-2" />
                        <span className="font-medium">{services.length}</span>
                        <span className="ml-1">service{services.length > 1 ? 's' : ''}</span>
                    </div>
                </div>

                {/* Services Table */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    {loading ? (
                        <div className="p-12 text-center">
                            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
                            <p className="mt-4 text-gray-600">Chargement...</p>
                        </div>
                    ) : services.length === 0 ? (
                        <div className="p-12 text-center">
                            <Briefcase className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun service</h3>
                            <p className="text-gray-600">
                                {search ? 'Aucun résultat pour cette recherche' : 'Importez vos services depuis Excel'}
                            </p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-gray-50 border-b border-gray-200">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unité</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prix Net</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prix Brut</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Marge</th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {services.map((service) => (
                                        <tr key={service.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className="font-mono text-sm font-medium text-gray-900">{service.code}</span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="text-sm font-medium text-gray-900">{service.name}</div>
                                                {service.description && (
                                                    <div className="text-sm text-gray-500">{service.description}</div>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm">{service.unit}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                                {service.price_net.toFixed(2)} €
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {service.price_gross.toFixed(2)} €
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className="text-sm font-medium text-green-600">
                                                    +{service.margin.toFixed(2)} €
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                                                <button
                                                    onClick={() => handleDelete(service.id)}
                                                    className="text-red-600 hover:text-red-800"
                                                    title="Supprimer"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </DashboardLayout>
    )
}
