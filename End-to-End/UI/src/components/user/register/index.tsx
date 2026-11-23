import { FormEvent, useState } from "react";
import { registerUser } from "../../../service";
import styles from "./index.module.scss";

export const RegistrationPage = (): JSX.Element => {
  const [fname, setFirstName] = useState("");
  const [lname, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await registerUser({ fname, lname, email, password });
      setSuccess(true);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Could not create your account. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className={styles.authScreen}>
      <section className="auth-panel" aria-labelledby="register-title">
        <a className="auth-brand" href="/" aria-label="101 home">
          101<span>.</span>
        </a>
        <p className="auth-eyebrow">YOUR MONEY, IN MOTION</p>
        <h1 id="register-title">Create your account</h1>
        <p className="auth-intro">Set up your 101 account to get started.</p>

        {success ? (
          <div className="auth-notice auth-success" role="status">
            <p>Your account is ready.</p>
            <a href="/login">Continue to sign in</a>
          </div>
        ) : (
          <form className="auth-form" onSubmit={handleSubmit}>
            <label htmlFor="register-name">First name</label>
            <input
              id="register-first-name"
              name="firstName"
              autoComplete="firstName"
              value={fname}
              onChange={(event) => setFirstName(event.target.value)}
              maxLength={100}
              required
              disabled={isSubmitting}
            />
            <label htmlFor="register-name">Last name</label>
            <input
              id="register-last-name"
              name="lastName"
              autoComplete="lastName"
              value={lname}
              onChange={(event) => setLastName(event.target.value)}
              maxLength={100}
              required
              disabled={isSubmitting}
            />

            <label htmlFor="register-email">Email address</label>
            <input
              id="register-email"
              name="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              maxLength={254}
              required
              disabled={isSubmitting}
            />

            <label htmlFor="register-password">Password</label>
            <input
              id="register-password"
              name="password"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={8}
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
              {isSubmitting ? "Creating account..." : "Create account"}
            </button>
          </form>
        )}

        <p className="auth-switch">
          Already registered? <a href="/login">Sign in</a>
        </p>
      </section>
    </main>
  );
};
