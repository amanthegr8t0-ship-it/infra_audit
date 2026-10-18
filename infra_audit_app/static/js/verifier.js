/**
 * Geometric Haversine Corridor Verifier Module.
 * Validates whether submitted field evidence GPS coordinates lie within the
 * 250m tolerance buffer of the road project corridor.
 */

export function haversineMeters(lat1, lon1, lat2, lon2) {
  const R = 6371000;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

export function distanceToCorridor(lat, lon, start, end) {
  const dStart = haversineMeters(lat, lon, start.lat, start.lon);
  const dEnd = haversineMeters(lat, lon, end.lat, end.lon);
  const midLat = (start.lat + end.lat) / 2;
  const midLon = (start.lon + end.lon) / 2;
  const dMid = haversineMeters(lat, lon, midLat, midLon);
  return Math.min(dStart, dEnd, dMid);
}
