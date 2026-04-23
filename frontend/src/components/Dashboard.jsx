// import React, { useState } from 'react';

// const Dashboard = () => {
//   const [activeTab, setActiveTab] = useState('Dashboard');

//   // Dummy data for the UI
//   const stats = [
//     { label: 'Total Interactions', value: '1,248', icon: '📊', desc: '+12% from last month' },
//     { label: 'Interactions Today', value: '8', icon: '📅', desc: '3 pending logs' },
//     { label: 'Pending Follow-ups', value: '12', icon: '⏰', desc: '5 due this week' },
//     { label: 'Total HCPs', value: '342', icon: '🧑‍⚕️', desc: 'Across 14 territories' },
//   ];

//   const recentInteractions = [
//     { id: 1, name: 'Dr. Sarah Jenkins', date: 'Oct 24, 2023 • 10:30 AM', type: 'Meeting', sentiment: 'Positive' },
//     { id: 2, name: 'Dr. Michael Chen', date: 'Oct 23, 2023 • 02:15 PM', type: 'Call', sentiment: 'Neutral' },
//     { id: 3, name: 'Dr. Emily Rodriguez', date: 'Oct 22, 2023 • 09:00 AM', type: 'Email', sentiment: 'Positive' },
//     { id: 4, name: 'Dr. James Wilson', date: 'Oct 21, 2023 • 11:45 AM', type: 'Conference', sentiment: 'Negative' },
//   ];

//   const getSentimentBadge = (sentiment) => {
//     switch(sentiment) {
//       case 'Positive': return <span className="px-2.5 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">Positive</span>;
//       case 'Neutral': return <span className="px-2.5 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">Neutral</span>;
//       case 'Negative': return <span className="px-2.5 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">Negative</span>;
//       default: return null;
//     }
//   };

//   return (
//     <div className="flex h-screen bg-slate-50 font-sans text-slate-800">
      
//       {/* Sidebar Navigation */}
//       <aside className="w-64 bg-white border-r border-slate-200 flex flex-col shadow-sm hidden md:flex">
//         <div className="h-16 flex items-center px-6 border-b border-slate-100">
//           <div className="w-8 h-8 bg-sky-500 rounded-lg flex items-center justify-center text-white font-bold text-lg mr-3 shadow-sm">
//             H
//           </div>
//           <span className="font-bold text-lg text-slate-800 tracking-tight">HCP Connect</span>
//         </div>
        
//         <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
//           {['Dashboard', 'Log Interaction', 'AI Chat', 'Interaction History'].map((item) => (
//             <button
//               key={item}
//               onClick={() => setActiveTab(item)}
//               className={`w-full flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
//                 activeTab === item 
//                 ? 'bg-sky-50 text-sky-600' 
//                 : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
//               }`}
//             >
//               {/* Simple icons based on item name */}
//               <span className="mr-3 text-lg">
//                 {item === 'Dashboard' && '🏠'}
//                 {item === 'Log Interaction' && '📝'}
//                 {item === 'AI Chat' && '✨'}
//                 {item === 'Interaction History' && '📋'}
//               </span>
//               {item}
//             </button>
//           ))}
//         </nav>
        
//         <div className="p-4 border-t border-slate-100">
//           <button className="w-full flex items-center px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-red-50 hover:text-red-600 transition-colors">
//             <span className="mr-3 text-lg">🚪</span> Profile / Logout
//           </button>
//         </div>
//       </aside>

//       {/* Main Content Area */}
//       <main className="flex-1 flex flex-col overflow-hidden">
        
//         {/* Top Header */}
//         <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 shadow-sm z-10">
//           <h1 className="text-xl font-bold text-slate-800">{activeTab}</h1>
          
//           <div className="flex items-center space-x-6">
//             <div className="relative">
//               <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">🔍</span>
//               <input 
//                 type="text" 
//                 placeholder="Search HCPs or interactions..." 
//                 className="w-64 pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/50 focus:bg-white transition-colors"
//               />
//             </div>
            
//             <div className="flex items-center space-x-3 border-l border-slate-200 pl-6">
//               <div className="text-right hidden sm:block">
//                 <p className="text-sm font-semibold text-slate-700">Alex Rep</p>
//                 <p className="text-xs text-slate-500">Field Representative</p>
//               </div>
//               <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-700 font-bold border border-indigo-200 shadow-sm">
//                 AR
//               </div>
//             </div>
//           </div>
//         </header>

//         {/* Scrollable Dashboard Content */}
//         <div className="flex-1 overflow-y-auto p-8">
//           <div className="max-w-6xl mx-auto space-y-8">
            
//             {/* Quick Actions */}
//             <div className="flex flex-col sm:flex-row items-center justify-between bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
//               <div>
//                 <h3 className="text-lg font-bold text-slate-800">Ready to log a recent visit?</h3>
//                 <p className="text-sm text-slate-500 mt-1">Use our AI assistant to quickly summarize your interactions.</p>
//               </div>
//               <div className="flex space-x-3 mt-4 sm:mt-0">
//                 <button className="px-5 py-2.5 bg-white border border-slate-300 text-slate-700 font-medium rounded-xl hover:bg-slate-50 hover:shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-slate-200 text-sm">
//                   Log Interaction (Form)
//                 </button>
//                 <button className="px-5 py-2.5 bg-sky-500 text-white font-medium rounded-xl hover:bg-sky-600 hover:shadow-md transition-all flex items-center focus:outline-none focus:ring-2 focus:ring-sky-500/50 focus:ring-offset-2 text-sm shadow-sm">
//                   <span className="mr-2 text-base">✨</span> Log via AI Chat
//                 </button>
//               </div>
//             </div>

//             {/* Stats Section */}
//             <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
//               {stats.map((stat, idx) => (
//                 <div key={idx} className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow">
//                   <div className="flex items-start justify-between">
//                     <div>
//                       <p className="text-sm font-medium text-slate-500">{stat.label}</p>
//                       <h4 className="text-3xl font-bold text-slate-800 mt-2">{stat.value}</h4>
//                     </div>
//                     <div className="w-10 h-10 rounded-full bg-slate-50 flex items-center justify-center text-xl border border-slate-100">
//                       {stat.icon}
//                     </div>
//                   </div>
//                   <div className="mt-4 text-xs font-medium text-slate-400 bg-slate-50 inline-block px-2 py-1 rounded">
//                     {stat.desc}
//                   </div>
//                 </div>
//               ))}
//             </div>

//             {/* Bottom Row: Table & AI Insights */}
//             <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              
//               {/* Recent Interactions Table */}
//               <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden flex flex-col">
//                 <div className="px-6 py-5 border-b border-slate-100 flex justify-between items-center bg-white">
//                   <h3 className="font-bold text-slate-800">Recent Interactions</h3>
//                   <button className="text-sm text-sky-500 hover:text-sky-600 font-medium">View All</button>
//                 </div>
//                 <div className="overflow-x-auto">
//                   <table className="w-full text-left text-sm">
//                     <thead className="bg-slate-50/50 text-slate-500 border-b border-slate-200">
//                       <tr>
//                         <th className="px-6 py-3 font-medium">HCP Name</th>
//                         <th className="px-6 py-3 font-medium">Date & Time</th>
//                         <th className="px-6 py-3 font-medium">Type</th>
//                         <th className="px-6 py-3 font-medium">Sentiment</th>
//                         <th className="px-6 py-3 font-medium text-right">Actions</th>
//                       </tr>
//                     </thead>
//                     <tbody className="divide-y divide-slate-100">
//                       {recentInteractions.map((row) => (
//                         <tr key={row.id} className="hover:bg-slate-50 transition-colors">
//                           <td className="px-6 py-4 font-semibold text-slate-700">{row.name}</td>
//                           <td className="px-6 py-4 text-slate-500">{row.date}</td>
//                           <td className="px-6 py-4">
//                             <span className="flex items-center text-slate-600">
//                               <span className="w-1.5 h-1.5 rounded-full bg-slate-400 mr-2"></span>
//                               {row.type}
//                             </span>
//                           </td>
//                           <td className="px-6 py-4">{getSentimentBadge(row.sentiment)}</td>
//                           <td className="px-6 py-4 text-right">
//                             <button className="text-slate-400 hover:text-sky-500 transition-colors p-1">
//                               ✏️
//                             </button>
//                           </td>
//                         </tr>
//                       ))}
//                     </tbody>
//                   </table>
//                 </div>
//               </div>

//               {/* AI Insights Panel */}
//               <div className="bg-gradient-to-br from-indigo-50 to-sky-50 rounded-2xl shadow-sm border border-indigo-100 p-6 relative overflow-hidden">
//                 <div className="absolute top-0 right-0 w-32 h-32 bg-sky-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 -translate-y-1/2 translate-x-1/2"></div>
                
//                 <div className="flex items-center mb-6 relative z-10">
//                   <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center text-white mr-3 shadow-sm">
//                     ✨
//                   </div>
//                   <h3 className="font-bold text-slate-800 text-lg">AI Insights</h3>
//                 </div>

//                 <div className="space-y-4 relative z-10">
//                   <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl border border-indigo-50 shadow-sm">
//                     <p className="text-sm text-slate-700 font-medium leading-relaxed">
//                       "Dr. Smith showed high interest in <span className="text-indigo-600 font-bold bg-indigo-50 px-1 rounded">Product X</span> clinical trials during yesterday's meeting."
//                     </p>
//                     <div className="mt-3 flex gap-2">
//                       <span className="text-[10px] uppercase font-bold tracking-wider text-indigo-500 bg-indigo-50 px-2 py-1 rounded">Prescribing Intent</span>
//                     </div>
//                   </div>

//                   <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl border border-sky-50 shadow-sm">
//                     <div className="flex items-start">
//                       <span className="text-amber-500 mr-2 mt-0.5">🔔</span>
//                       <div>
//                         <p className="text-sm text-slate-700 font-medium">Follow-up recommended</p>
//                         <p className="text-xs text-slate-500 mt-1">Schedule a follow-up with Dr. Emily Rodriguez in 7 days regarding side-effect profile concerns.</p>
//                       </div>
//                     </div>
//                   </div>
//                 </div>

//                 <button className="w-full mt-6 py-2.5 bg-white border border-indigo-100 text-indigo-600 text-sm font-bold rounded-xl hover:bg-indigo-50 transition-colors shadow-sm relative z-10">
//                   View All Insights
//                 </button>
//               </div>

//             </div>
//           </div>
//         </div>
//       </main>
//     </div>
//   );
// };

// export default Dashboard;
