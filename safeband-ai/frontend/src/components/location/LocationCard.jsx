import { MapPin, ExternalLink, Navigation, Clock } from 'lucide-react';
import { timeAgo } from '../../utils/formatDate';

export default function LocationCard({ sensor, lastUpdated }) {
  const lat = sensor?.latitude;
  const lng = sensor?.longitude;
  const hasLocation = lat !== undefined && lat !== null && lng !== undefined && lng !== null;

  const mapsUrl = hasLocation
    ? `https://www.google.com/maps?q=${lat},${lng}`
    : null;

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-brand-600" />
          <p className="section-title">User Location</p>
        </div>
        {hasLocation && (
          <span className="badge bg-green-100 text-green-700 border-green-200">Available</span>
        )}
      </div>

      {hasLocation ? (
        <>
          <div className="bg-slate-50 rounded-xl border border-slate-100 p-4 mb-4 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400">Latitude</p>
                <p className="text-sm font-bold text-slate-700 font-mono">{lat.toFixed(6)}</p>
              </div>
              <Navigation className="w-5 h-5 text-brand-400" />
              <div className="text-right">
                <p className="text-xs text-slate-400">Longitude</p>
                <p className="text-sm font-bold text-slate-700 font-mono">{lng.toFixed(6)}</p>
              </div>
            </div>
          </div>

          <a
            href={mapsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary w-full justify-center"
          >
            <ExternalLink className="w-4 h-4" />
            Open in Google Maps
          </a>
        </>
      ) : (
        <div className="text-center py-6">
          <MapPin className="w-8 h-8 text-slate-300 mx-auto mb-2" />
          <p className="text-sm text-slate-500">Location not available</p>
          <p className="text-xs text-slate-400 mt-1">GPS data not received from device</p>
        </div>
      )}

      {lastUpdated && (
        <p className="flex items-center gap-1 text-xs text-slate-400 mt-3">
          <Clock className="w-3 h-3" />
          Last updated: {timeAgo(lastUpdated)}
        </p>
      )}
    </div>
  );
}
