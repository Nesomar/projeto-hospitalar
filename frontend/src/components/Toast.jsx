export default function Toast({ message }) {
  if (!message) return null;
  return (
    <div
      style={{
        position: "fixed",
        bottom: 24,
        right: 24,
        background: "oklch(24% 0.02 258)",
        color: "#fff",
        padding: "14px 20px",
        borderRadius: 14,
        fontSize: 13.5,
        fontWeight: 600,
        boxShadow: "0 10px 30px -10px rgba(0,0,0,0.35)",
        zIndex: 1000,
      }}
    >
      {message}
    </div>
  );
}
