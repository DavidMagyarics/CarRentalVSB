import { useState, type ReactNode } from 'react';
import type { PaymentMethod, ReservationStatus } from '../api/client';

const PALETTE = ['#2563eb', '#16a34a', '#db2777', '#ea580c', '#7c3aed', '#0891b2', '#ca8a04'];

function colorFor(text: string): string {
  let hash = 0;
  for (const ch of text) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0;
  return PALETTE[hash % PALETTE.length];
}

/** Car photo, or a drawn placeholder when the car has no image_url (or it fails to load). */
export function CarImage({ src, label, small }: { src: string; label: string; small?: boolean }) {
  const [failed, setFailed] = useState(false);
  const className = small ? 'car-image small' : 'car-image';
  if (src && !failed) {
    return <img className={className} src={src} alt={label} onError={() => setFailed(true)} />;
  }
  const color = colorFor(label);
  return (
    <svg className={className} viewBox="0 0 160 90" role="img" aria-label={label}>
      <rect width="160" height="90" fill={color} opacity="0.12" />
      <path d="M22 60 L36 38 Q40 32 48 32 H108 Q116 32 121 38 L138 60 Z" fill={color} />
      <rect x="18" y="56" width="124" height="14" rx="6" fill={color} />
      <path d="M50 38 H76 V54 H40 Z M82 38 H106 L118 54 H82 Z" fill="#ffffff" opacity="0.75" />
      <circle cx="48" cy="70" r="10" fill="#1f2937" />
      <circle cx="112" cy="70" r="10" fill="#1f2937" />
      <circle cx="48" cy="70" r="4" fill="#d1d5db" />
      <circle cx="112" cy="70" r="4" fill="#d1d5db" />
    </svg>
  );
}

const STATUS_LABEL: Record<ReservationStatus, string> = {
  DRAFT: 'Čeká na schválení',
  CONFIRMED: 'Potvrzena',
  CANCELLED: 'Zrušena',
};

export function StatusBadge({ status, started }: { status: ReservationStatus; started?: boolean }) {
  return (
    <span className={`badge badge-${status.toLowerCase()}`}>
      {STATUS_LABEL[status]}
      {status === 'CONFIRMED' && started ? ' · probíhá' : ''}
    </span>
  );
}

export const paymentLabel = (method: PaymentMethod) => (method === 'CASH' ? 'Hotově' : 'Kartou');

export const formatPrice = (value: number) =>
  `${value.toLocaleString('cs-CZ', { minimumFractionDigits: 0, maximumFractionDigits: 2 })} Kč`;

export const formatDate = (iso: string) =>
  new Date(iso).toLocaleString('cs-CZ', {
    weekday: 'short',
    day: 'numeric',
    month: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

export function Message({ kind, children }: { kind: 'error' | 'success' | 'info'; children: ReactNode }) {
  return (
    <div className={`message message-${kind}`} role={kind === 'error' ? 'alert' : 'status'}>
      {children}
    </div>
  );
}
