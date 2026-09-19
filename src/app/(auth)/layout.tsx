import Link from "next/link";
import Wordmark from "@/components/wordmark";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-forest px-4 py-12">
      <div className="w-full max-w-sm">
        <Link href="/" className="mb-8 flex justify-center">
          <Wordmark size={34} tone="onDark" />
        </Link>
        <div className="rounded-2xl border border-bone/10 bg-canopy p-8">{children}</div>
      </div>
    </main>
  );
}
