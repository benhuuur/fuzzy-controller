from matplotlib import pyplot as plt
import numpy as np
from twins import Furnace
from utils import PID


def simulate_PID(furnace: Furnace, controller: PID, current_temperature, target_temperature, steps=200, dt=3, ambient_temperature=25):
    times = np.arange(0, steps * dt, dt)
    temperatures = []
    powers = []

    for t in times:
        power = controller.compute(target_temperature, current_temperature, dt)
        power = max(0, power)

        dT_heating = furnace.Kf * power
        dT_loss = furnace.K_loss * (current_temperature - ambient_temperature)

        current_temperature += (dT_heating - dT_loss) * dt

        temperatures.append(current_temperature)
        powers.append(power)

    return times, temperatures, powers


times, temperatures, powers = simulate_PID(Furnace(0.05, 0.02),
                                           PID(1.0, 0.02, 0.01), 25, 200)

# Plotando os resultados
plt.figure(figsize=(12, 6))

# Temperatura do forno ao longo do tempo
plt.subplot(1, 2, 1)
plt.plot(times, temperatures, label="Temperatura do forno")
plt.axhline(200, color='r', linestyle='--', label="Temperatura alvo")
plt.title("Temperatura do Forno ao Longo do Tempo")
plt.xlabel("Tempo (s)")
plt.ylabel("Temperatura (°C)")
plt.legend()

# Potência aplicada ao forno
plt.subplot(1, 2, 2)
plt.plot(times, powers, label="Potência aplicada", color="orange")
plt.title("Potência Aplicada ao Forno ao Longo do Tempo")
plt.xlabel("Tempo (s)")
plt.ylabel("Potência")
plt.legend()

plt.tight_layout()
plt.show()


def simulate_fuzzy(furnace: Furnace, controller, current_temperature, steps=200, dt=3, ambient_temperature=25):
    temperatures = []
    times = np.arange(0, steps * dt, dt)
    powers = []
    previous_temperature = current_temperature
    
    for t in times:
        controller.input['Current Temperature'] = current_temperature
        controller.input['Rate of Change'] = (current_temperature - previous_temperature) if t > 0 else 0
        controller.compute()
        power = controller.output['Furnace Control']

        dT_heating = furnace.Kf * power
        dT_loss = furnace.K_loss * (current_temperature - ambient_temperature)

        current_temperature += (dT_heating - dT_loss) * dt

        temperatures.append(current_temperature)
        powers.append(power)

        previous_temperature = current_temperature
    
    return times, temperatures, powers

from matplotlib import pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

current_temperature = ctrl.Antecedent(np.arange(0, 301, 1), 'Current Temperature')
rate_of_change = ctrl.Antecedent(np.arange(-10, 11, 1), 'Rate of Change')
furnace_control = ctrl.Consequent(np.arange(0, 101, 1), 'Furnace Control')


current_temperature['low'] = fuzz.trimf(current_temperature.universe, [0, 0, 180])
current_temperature['medium'] = fuzz.trimf(current_temperature.universe, [170, 200, 230])
current_temperature['high'] = fuzz.trimf(current_temperature.universe, [220, 300, 300])

rate_of_change['decreasing'] = fuzz.trimf(rate_of_change.universe, [-10, -5, 0])
rate_of_change['stable'] = fuzz.trimf(rate_of_change.universe, [-1, 0, 1])
rate_of_change['increasing'] = fuzz.trimf(rate_of_change.universe, [0, 5, 10])

furnace_control['off'] = fuzz.trimf(furnace_control.universe, [0, 0, 20])
furnace_control['maintain'] = fuzz.trimf(furnace_control.universe, [30, 50, 70])
furnace_control['on'] = fuzz.trimf(furnace_control.universe, [60, 100, 100])


rule1 = ctrl.Rule(current_temperature['high'] & rate_of_change['decreasing'], furnace_control['off'])
rule2 = ctrl.Rule(current_temperature['low'] & rate_of_change['increasing'], furnace_control['on'])
rule3 = ctrl.Rule(current_temperature['medium'] & rate_of_change['stable'], furnace_control['maintain'])
rule4 = ctrl.Rule(current_temperature['low'] & rate_of_change['stable'], furnace_control['on'])
rule5 = ctrl.Rule(current_temperature['high'] & rate_of_change['stable'], furnace_control['off'])  # Regra ajustada
rule6 = ctrl.Rule(current_temperature['medium'] & rate_of_change['increasing'], furnace_control['on'])


control = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6])
fuzzy_control = ctrl.ControlSystemSimulation(control)

times, temperatures, powers = simulate_fuzzy(Furnace(0.05, 0.02), fuzzy_control, 25, 200)

plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(times, temperatures, label="Temperatura do forno")
plt.axhline(200, color='r', linestyle='--', label="Temperatura alvo")
plt.title("Temperatura do Forno ao Longo do Tempo")
plt.xlabel("Tempo (s)")
plt.ylabel("Temperatura (°C)")
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(times, powers, label="Potência aplicada", color="orange")
plt.title("Potência Aplicada ao Forno ao Longo do Tempo")
plt.xlabel("Tempo (s)")
plt.ylabel("Potência")
plt.legend()

plt.tight_layout()
plt.show()
