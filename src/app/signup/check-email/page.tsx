export default function CheckEmailPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-bg px-4">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-surface p-8 text-center">
        <h1 className="font-[family-name:var(--font-display)] text-xl font-semibold text-ink">
          Check your email
        </h1>
        <p className="mt-2 text-sm text-ink2">
          We sent a confirmation link. Click it, then sign in.
        </p>
      </div>
    </main>
  );
}
