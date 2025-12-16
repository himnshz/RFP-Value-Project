import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { DollarSign, Activity, CheckCircle, BarChart2 } from 'lucide-react';

const AnalyticsStats = ({ stats }) => {
    if (!stats) return null;

    const cards = [
        {
            title: "Total Pipeline Value",
            value: `$${stats.total_value.toLocaleString()}`,
            icon: DollarSign,
            color: "text-green-400",
            bg: "bg-green-900/20",
            border: "border-green-500/30"
        },
        {
            title: "Approval Rate",
            value: `${stats.approval_rate}%`,
            icon: CheckCircle,
            color: "text-blue-400",
            bg: "bg-blue-900/20",
            border: "border-blue-500/30"
        },
        {
            title: "Avg. AI Confidence",
            value: `${stats.avg_confidence}%`,
            icon: Activity,
            color: "text-purple-400",
            bg: "bg-purple-900/20",
            border: "border-purple-500/30"
        },
        {
            title: "Total RFPs",
            value: stats.total_rfps,
            icon: BarChart2,
            color: "text-orange-400",
            bg: "bg-orange-900/20",
            border: "border-orange-500/30"
        }
    ];

    return (
        <div className="space-y-6 mb-8">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {cards.map((card, index) => (
                    <div key={index} className={`p-4 rounded-xl border ${card.bg} ${card.border} backdrop-blur-sm`}>
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-slate-400 text-sm font-medium">{card.title}</p>
                                <h3 className="text-2xl font-bold text-white mt-1">{card.value}</h3>
                            </div>
                            <div className={`p-2 rounded-lg ${card.bg}`}>
                                <card.icon className={`w-5 h-5 ${card.color}`} />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Status Distribution Chart */}
                <div className="lg:col-span-2 bg-[#1e293b]/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                    <h3 className="text-lg font-semibold text-white mb-6">RFP Status Distribution</h3>
                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={stats.status_distribution}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                <XAxis
                                    dataKey="name"
                                    stroke="#94a3b8"
                                    tick={{ fill: '#94a3b8' }}
                                    axisLine={false}
                                    tickLine={false}
                                />
                                <YAxis
                                    stroke="#94a3b8"
                                    tick={{ fill: '#94a3b8' }}
                                    axisLine={false}
                                    tickLine={false}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#0f172a',
                                        border: '1px solid #334155',
                                        borderRadius: '8px',
                                        color: '#fff'
                                    }}
                                    cursor={{ fill: '#334155', opacity: 0.2 }}
                                />
                                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                    {stats.status_distribution.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={
                                            entry.name === 'Approved' ? '#22c55e' :
                                                entry.name === 'Rejected' ? '#ef4444' :
                                                    entry.name === 'Processed' ? '#3b82f6' :
                                                        '#eab308'
                                        } />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Quick Actions / Summary (Placeholder for future) */}
                <div className="bg-[#1e293b]/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm flex flex-col justify-center items-center text-center">
                    <div className="p-4 bg-blue-500/10 rounded-full mb-4">
                        <Activity className="w-8 h-8 text-blue-400" />
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">System Health</h3>
                    <p className="text-slate-400 text-sm mb-6">
                        All agents are operational. Database connection is stable.
                    </p>
                    <div className="w-full bg-slate-700/50 rounded-full h-2 mb-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{ width: '100%' }}></div>
                    </div>
                    <p className="text-xs text-green-400 font-mono">100% Uptime</p>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsStats;
