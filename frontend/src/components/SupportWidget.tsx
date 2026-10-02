import { useState } from 'react'
import { OPENING_HOURS_LABEL } from '../constants'

export default function SupportWidget() {
  const [open, setOpen] = useState(false)

  return (
    <div className="support-widget">
      {open && (
        <div className="support-panel">
          <div className="support-panel-header">
            <h4>Potřebujete pomoc?</h4>
            <button
              type="button"
              className="modal-close"
              onClick={() => setOpen(false)}
              aria-label="Zavřít"
            >
              ×
            </button>
          </div>
          <p className="support-panel-text">
            Náš tým zákaznické podpory vám rád pomůže s rezervací i čímkoliv dalším.
          </p>
          <a className="support-contact" href="tel:+420800123456">
            <span className="support-contact-label">Telefon</span>
            <span>+420 800 123 456</span>
          </a>
          <a className="support-contact" href="mailto:podpora@carrentalvsb.cz">
            <span className="support-contact-label">E-mail</span>
            <span>podpora@carrentalvsb.cz</span>
          </a>
          <p className="hint">{OPENING_HOURS_LABEL}</p>
        </div>
      )}
      <button
        type="button"
        className="support-button"
        onClick={() => setOpen((prev) => !prev)}
        aria-label="Otevřít podporu"
      >
        {open ? (
          '×'
        ) : (
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"
            />
          </svg>
        )}
      </button>
    </div>
  )
}
