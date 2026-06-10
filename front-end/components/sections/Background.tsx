export default function Background() {
  const particles = Array.from({ length: 14 }, (_, i) => i);
  return (
    <>
      <div className="bg-layer bg-mesh" />
      <div className="bg-layer bg-grid" />
      <div className="bg-layer bg-noise" />
      <div className="particles" aria-hidden="true">
        {particles.map((i) => {
          const left = (i * 7.3 + 4) % 100;
          const dur = 16 + (i % 7) * 3.5;
          const delay = -(i * 2.6);
          const scale = 0.6 + (i % 4) * 0.22;
          return (
            <span
              key={i}
              className="particle"
              style={{
                left: `${left}%`,
                animationDuration: `${dur}s`,
                animationDelay: `${delay}s`,
                transform: `scale(${scale})`,
              }}
            />
          );
        })}
      </div>
    </>
  );
}
