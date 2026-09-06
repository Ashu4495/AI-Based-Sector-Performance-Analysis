import React from 'react';

export default function HealthBadge({ label, size = 'md' }) {
  if (!label) return null;

  const getStyle = (lbl) => {
    switch (lbl) {
      case 'Strong Buy':
      case 'Buy':
        return 'text-signal-buy bg-signal-buy border-signal-buy';
      case 'Neutral':
        return 'text-signal-neutral bg-signal-neutral border-signal-neutral';
      case 'Avoid':
      case 'Strong Avoid':
        return 'text-signal-avoid bg-signal-avoid border-signal-avoid';
      default:
        return 'text-muted bg-surface border-subtle';
    }
  };

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[11px]',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm font-medium',
  };

  return (
    <span
      className={`inline-flex items-center justify-center font-mono font-medium rounded border ${sizeClasses[size]} ${getStyle(
        label
      )} tracking-wide transition-all`}
    >
      {label}
    </span>
  );
}
