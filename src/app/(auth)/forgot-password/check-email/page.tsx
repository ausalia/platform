import CheckEmailNotice from "@/components/check-email-notice";

export default function CheckEmailPage() {
  return (
    <CheckEmailNotice
      title="Check your email"
      body="If an account exists for that address, we sent a password reset link."
    />
  );
}
