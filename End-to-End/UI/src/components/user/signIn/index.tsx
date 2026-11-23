import { FormEvent, useState } from "react";
import { loginUser } from "../../../service";

export const SignInPage = (): JSX.Element => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSignedIn, setIsSignedIn] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const result = await loginUser({ email, password });
      window.localStorage.setItem("access_token", result.access_token);
      setIsSignedIn(true);
      window.location.href = "/chat";
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Could not sign in. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="auth-screen">
      <section className="auth-panel" aria-labelledby="login-title">
        <a className="auth-brand" href="/" aria-label="101 home">
          101<span>.</span>
        </a>
        <p className="auth-eyebrow">WELCOME BACK</p>
        <h1 id="login-title">Sign in to 101</h1>
        <p className="auth-intro">Use your account email and password.</p>

        {isSignedIn ? (
          <div className="auth-notice auth-success" role="status">
            <p>You’re signed in. Your access token is saved in this browser.</p>
            <a href="/">Continue to the assistant</a>
          </div>
        ) : (
          <form className="auth-form" onSubmit={handleSubmit}>
            <label htmlFor="login-email">Email address</label>
            <input
              id="login-email"
              name="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              maxLength={254}
              required
              disabled={isSubmitting}
            />

            <label htmlFor="login-password">Password</label>
            <input
              id="login-password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              maxLength={256}
              required
              disabled={isSubmitting}
            />

            {error && (
              <p className="auth-notice auth-error" role="alert">
                {error}
              </p>
            )}

            <button
              className="auth-submit"
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Signing in..." : "Sign in"}
            </button>
          </form>
        )}

        <p className="auth-switch">
          New to 101? <a href="/register">Create an account</a>
        </p>
      </section>
    </main>
  );
};
