"""Genera un trazo tipo EEG determinista para usar como divisor de sección.

Sale un path SVG en un viewBox de 1200 x 28. La forma cita el trazo de señal
que el logo tiene bajo el wordmark: oscilación de fondo pequeña, con espigas
ocasionales. Semilla fija -> path idéntico en cada corrida.
"""
import math
import random

W, H = 1200.0, 28.0
MID = H / 2.0
N = 300  # puntos

rnd = random.Random(20260804)

# Espigas: posiciones y amplitudes fijas, repartidas de forma irregular.
espigas = []
x = 40.0
while x < W - 30:
    espigas.append((x, rnd.uniform(0.55, 1.0) * (1 if rnd.random() < 0.72 else -1)))
    x += rnd.uniform(55.0, 130.0)

puntos = []
for i in range(N + 1):
    x = W * i / N
    # Fondo: suma de tres senos incomensurables -> ondulación no periódica.
    y = (
        0.30 * math.sin(x / 11.3)
        + 0.18 * math.sin(x / 4.7 + 1.1)
        + 0.12 * math.sin(x / 23.9 + 2.7)
    )
    # Espigas: pulso estrecho tipo gaussiana.
    for cx, amp in espigas:
        d = x - cx
        if abs(d) < 26:
            y += amp * math.exp(-(d * d) / 9.0) * 2.6
            # rebote lento posterior
            y -= amp * 0.45 * math.exp(-((d - 7.0) ** 2) / 60.0)
    puntos.append((x, MID - y * (H * 0.34)))

partes = [f"M0 {puntos[0][1]:.1f}"]
for x, y in puntos[1:]:
    partes.append(f"L{x:g} {y:.1f}")
print("".join(partes))
