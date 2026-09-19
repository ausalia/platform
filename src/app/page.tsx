import Link from "next/link";
import ThemeToggle from "@/components/theme-toggle";

export default function Home() {
  return (
    <main className="min-h-screen bg-bg text-ink">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-6">
        <span className="font-[family-name:var(--font-display)] text-lg font-semibold">
          AUSELIA
        </span>
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <Link
            href="/login"
            className="rounded-full border border-border px-4 py-1.5 text-xs font-mono uppercase tracking-wide text-ink2"
          >
            Partner sign in
          </Link>
        </div>
      </div>

      <div className="mx-auto flex max-w-3xl flex-col items-start px-6 pb-24 pt-16 sm:pt-24">
        <span className="font-mono text-xs uppercase tracking-[0.18em] text-ink2">
          Edge-AI silicon that listens to plants
        </span>
        <h1 className="mt-4 font-[family-name:var(--font-display)] text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          Auselia is listening...
        </h1>
        <p className="mt-5 max-w-xl text-base text-ink2 sm:text-lg">
          A field node that hears the quiet acoustic signs of drought stress in a plant&apos;s
          xylem, long before it shows by looking. We&apos;re still early. Right now it&apos;s
          listening to one plant, named{" "}
          <span className="font-semibold text-accent">Hope</span>.
        </p>

        <div className="mt-8 flex flex-wrap items-center gap-3">
          <Link
            href="/demo"
            className="rounded-lg bg-amber px-5 py-2.5 text-sm font-semibold text-forest"
          >
            Explore the live demo
          </Link>
          <Link
            href="/login"
            className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium text-ink"
          >
            Partner sign in
          </Link>
        </div>

        <p className="mt-16 font-mono text-xs uppercase tracking-[0.14em] text-ink2">
          We listen to what plants can&apos;t say.
        </p>
      </div>
    </main>
  );
}
