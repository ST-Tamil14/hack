import { Inbox } from 'lucide-react';

export default function EmptyState({ message = 'No data available.', icon: Icon = Inbox, className = '' }) {
  return (
    <div className={`flex flex-col items-center justify-center py-16 text-slate-400 ${className}`}>
      <Icon className="w-10 h-10 mb-3 text-slate-300" />
      <p className="text-sm font-medium text-slate-500">{message}</p>
    </div>
  );
}
