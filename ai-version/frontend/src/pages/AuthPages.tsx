import { useState, type FormEvent } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Message } from '../components/common';
import { useAuth } from '../state/auth';

type ReturnState = { from?: string; reserveCarId?: number } | null;

function useReturn() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as ReturnState;
  return {
    state,
    goBack: () => navigate(state?.from ?? '/', { replace: true, state: state?.reserveCarId ? state : null }),
  };
}

/** UC2 Log in */
export function LoginPage() {
  const { login } = useAuth();
  const { state, goBack } = useReturn();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(email, password);
      goBack();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Přihlášení selhalo');
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={submit}>
      <h1>Přihlášení</h1>
      {state?.reserveCarId && <Message kind="info">Pro rezervaci se prosím přihlaste.</Message>}
      {error && <Message kind="error">{error}</Message>}
      <label>
        E-mail
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoFocus />
      </label>
      <label>
        Heslo
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      </label>
      <button type="submit" disabled={busy}>
        {busy ? 'Přihlašuji…' : 'Přihlásit se'}
      </button>
      <p className="muted">
        Nemáte účet?{' '}
        <Link to="/register" state={state}>
          Vytvořit účet
        </Link>
      </p>
    </form>
  );
}

/** UC1 Register */
export function RegisterPage() {
  const { register } = useAuth();
  const { state, goBack } = useReturn();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (password.length < 6) {
      setError('Heslo musí mít alespoň 6 znaků');
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await register(name, email, password);
      goBack();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registrace selhala');
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={submit}>
      <h1>Vytvořit účet</h1>
      {error && <Message kind="error">{error}</Message>}
      <label>
        Jméno
        <input value={name} onChange={(e) => setName(e.target.value)} required autoFocus />
      </label>
      <label>
        E-mail
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </label>
      <label>
        Heslo (min. 6 znaků)
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
      </label>
      <button type="submit" disabled={busy}>
        {busy ? 'Registruji…' : 'Zaregistrovat se'}
      </button>
      <p className="muted">
        Už máte účet?{' '}
        <Link to="/login" state={state}>
          Přihlásit se
        </Link>
      </p>
    </form>
  );
}
