from matplotlib import pyplot as plt
import numpy as np
from twins import Furnace
from utils import PID, grid
from constants import RHO_AIR, C_AIR, ALPHA_AIR


def simulate(furnace: Furnace, controller: PID, current_temperature, target_temperature, resolution=0.01, steps=200, dt=3):
    nx, ny, nz = grid(furnace.L, furnace.H, furnace.W, resolution)
    temperatures = np.ones((nx, ny, nz)) * current_temperature
    resistor = (nx // 2, ny // 2, 0)  # Localização da resistência

    results = []
    times = np.arange(0, steps * dt, dt)

    for i, t in enumerate(times):
        current_temperature = np.mean(temperatures)
        print(f"iteration: {i}  temperature: {current_temperature}")
        results.append(current_temperature)

        watts = controller.compute(current=current_temperature, target=target_temperature)
        watts = max(furnace.P, watts)
        watts *= 0.1

        joules = watts * dt

        # Cálculo do aumento de temperatura (delta_T_air) considerando a massa de ar
        delta_T_air = joules / (RHO_AIR * C_AIR * (resolution ** 3))  # Ajuste de acordo com a resolução

        # Agora aplicamos o calor da resistência de forma mais gradual
        temperature_increase = np.zeros_like(temperatures)

        # Aumento de temperatura na resistência (ponto específico)
        temperature_increase[resistor] += delta_T_air

        # Espalhamento do calor nas células vizinhas de forma mais suave
        spread_factor = 0.2  # Controla quanto do calor vai para as células vizinhas
        for i in range(max(0, resistor[0] - 1), min(nx, resistor[0] + 2)):
            for j in range(max(0, resistor[1] - 1), min(ny, resistor[1] + 2)):
                for k in range(max(0, resistor[2] - 1), min(nz, resistor[2] + 2)):
                    if (i, j, k) != resistor:  # Não aplicar calor na célula da resistência diretamente
                        temperature_increase[i, j, k] += delta_T_air * spread_factor

        # Atualizando a temperatura no grid
        temperatures += temperature_increase

        # Difusão térmica (equação de calor)
        updated_temperatures = np.copy(temperatures)
        for i in range(1, nx - 1):
            for j in range(1, ny - 1):
                for k in range(1, nz - 1):
                    updated_temperatures[i, j, k] = temperatures[i, j, k] + ALPHA_AIR * dt * (
                        (temperatures[i + 1, j, k] - 2 * temperatures[i, j, k] + temperatures[i - 1, j, k]) / (resolution ** 2) +
                        (temperatures[i, j + 1, k] - 2 * temperatures[i, j, k] + temperatures[i, j - 1, k]) / (resolution ** 2) +
                        (temperatures[i, j, k + 1] - 2 * temperatures[i, j, k] + temperatures[i, j, k - 1]) / (resolution ** 2)
                    )

        temperatures = np.copy(updated_temperatures)

    return times, results




times, results = simulate(Furnace(),
                          PID(0.1, 0.1, 0.15), 25, 200)

plt.figure(figsize=(10, 5))
plt.plot(times, results, label="Temperatura")
plt.axhline(y=200, color='r', linestyle='--', label="Setpoint")
# plt.title("Resposta do Forno com Controlador Nebuloso")
plt.xlabel("Tempo (s)")
plt.ylabel("Temperatura (°C)")
plt.legend()
plt.grid(True)
plt.show()
