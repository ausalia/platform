export default function CheckEmailNotice({
  title,
  body,
}: {
  title: string;
  body: string;
}) {
  return (
    <div className="text-center">
      <h1 className="font-[family-name:var(--font-display)] text-xl font-semibold text-bone">
        {title}
      </h1>
      <p className="mt-2 text-sm text-sap">{body}</p>
    </div>
  );
}
