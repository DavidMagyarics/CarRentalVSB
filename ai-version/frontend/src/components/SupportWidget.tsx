import { useState } from 'react';

// UC7 Contact support - only in the browser, no backend call.
export const SUPPORT = {
  phone: '+420 597 000 000',
  email: 'podpora@carrentalvsb.cz',
  hours: 'Po–Pá 8:00–20:00',
};

export function SupportWidget() {
  const [isOpen, setOpen] = useState(false);
  const open = () => setOpen(true);
  const close = () => setOpen(false);

  return (
    <div className="support">
      {isOpen && (
        <div className="support-panel" role="dialog" aria-label="Kontakt na podporu">
          <div className="support-head">
            <strong>Potřebujete pomoc?</strong>
            <button className="icon-button" onClick={close} aria-label="Zavřít">
              ×
            </button>
          </div>
          <p>
            Telefon: <a href={`tel:${SUPPORT.phone.replace(/\s/g, '')}`}>{SUPPORT.phone}</a>
          </p>
          <p>
            E-mail: <a href={`mailto:${SUPPORT.email}`}>{SUPPORT.email}</a>
          </p>
          <p className="muted">Provozní doba: {SUPPORT.hours}</p>
        </div>
      )}
      <button className="support-button" onClick={isOpen ? close : open} aria-expanded={isOpen}>
        {isOpen ? 'Zavřít' : 'Podpora'}
      </button>
    </div>
  );
}
