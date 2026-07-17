export function FormError({ message }: { message?: string }) {
  if (!message) return null;
  return (
    <p
      className="rounded-md border border-[#e5bbb1] bg-[#fffafa] px-3 py-2 text-sm text-coral"
      role="alert"
    >
      {message}
    </p>
  );
}
