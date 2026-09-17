import { login } from "./actions";
import Link from "next/link";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  const { error } = await searchParams;

  return (
    <>
      <p className="text-sm text-sap">Sign in to your dashboard.</p>

      {error && (
        <p className="mt-4 rounded-lg border border-status-critical/40 bg-status-critical/10 px-3 py-2 text-sm text-bone">
          {error}
        </p>
      )}

      <form action={login} className="mt-6 flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <label htmlFor="email" className="text-xs font-mono font-medium uppercase tracking-wide text-sap">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            className="rounded-lg border border-bone/15 bg-forest px-3 py-2 text-sm text-bone outline-none focus:border-amber"
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <label htmlFor="password" className="text-xs font-mono font-medium uppercase tracking-wide text-sap">
              Password
            </label>
            <Link href="/forgot-password" className="text-xs text-sap underline">
              Forgot?
            </Link>
          </div>
          <input
            id="password"
            name="password"
            type="password"
            required
            className="rounded-lg border border-bone/15 bg-forest px-3 py-2 text-sm text-bone outline-none focus:border-amber"
          />
        </div>
        <button
          type="submit"
          className="mt-2 rounded-lg bg-amber px-4 py-2 text-sm font-semibold text-forest"
        >
          Sign in
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-sap">
        No account yet?{" "}
        <Link href="/signup" className="text-bone underline">
          Sign up
        </Link>
      </p>
    </>
  );
}
