import { useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { useToast } from './Toast'

interface Props {
  onSuccess: () => void
  message?: string
}

export default function AuthForms({ onSuccess, message }: Props) {
  const { login, register } = useAuth()
  const { show } = useToast()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      if (mode === 'login') {
        await login(email, password)
        show('Přihlášení proběhlo úspěšně.', 'success')
      } else {
        await register(name, email, password)
        show('Účet byl vytvořen.', 'success')
      }
      onSuccess()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Něco se pokazilo')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-panel">
      <div className="auth-tabs">
        <button
          type="button"
          className={mode === 'login' ? 'active' : ''}
          onClick={() => setMode('login')}
        >
          Přihlásit se
        </button>
        <button
          type="button"
          className={mode === 'register' ? 'active' : ''}
          onClick={() => setMode('register')}
        >
          Vytvořit účet
        </button>
      </div>

      {message && <p className="hint">{message}</p>}

      <form onSubmit={handleSubmit}>
        {mode === 'register' && (
          <label>
            Jméno
            <input required value={name} onChange={(e) => setName(e.target.value)} />
          </label>
        )}
        <label>
          E-mail
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
        <label>
          Heslo
          <input
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={submitting}>
          {submitting ? 'Chvilku…' : mode === 'login' ? 'Přihlásit se' : 'Vytvořit účet'}
        </button>
      </form>

      {mode === 'login' && (
        <p className="hint auth-demo-hint">Demo účet admina: admin@carrentalvsb.cz / admin123</p>
      )}
    </div>
  )
}
