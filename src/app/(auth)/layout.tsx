import Link from "next/link";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-forest px-4 py-12">
      <div className="w-full max-w-sm">
        <Link
          href="/"
          className="mb-8 block text-center font-[family-name:var(--font-display)] text-2xl font-semibold text-bone"
        >
          AUSELIA
        </Link>
        <div className="rounded-2xl border border-bone/10 bg-canopy p-8">{children}</div>
      </div>
    </main>
  );
}
