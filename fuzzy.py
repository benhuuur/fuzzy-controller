# Reutilizando o código do controlador nebuloso já apresentado
from matplotlib import pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Definindo variáveis de entrada e saída
temperatura_atual = ctrl.Antecedent(np.arange(0, 301, 1), 'Temperatura Atual')
taxa_variacao = ctrl.Antecedent(np.arange(-10, 11, 1), 'Taxa de Variação')
controle_forno = ctrl.Consequent(np.arange(0, 101, 1), 'Controle do Forno')

# Funções de pertinência
temperatura_atual['baixa'] = fuzz.trimf(
    temperatura_atual.universe, [0, 0, 200])
temperatura_atual['media'] = fuzz.trimf(
    temperatura_atual.universe, [180, 200, 220])
temperatura_atual['alta'] = fuzz.trimf(
    temperatura_atual.universe, [200, 300, 300])

taxa_variacao['diminuindo'] = fuzz.trimf(taxa_variacao.universe, [-10, -5, 0])
taxa_variacao['estavel'] = fuzz.trimf(taxa_variacao.universe, [-1, 0, 1])
taxa_variacao['aumentando'] = fuzz.trimf(taxa_variacao.universe, [0, 5, 10])

controle_forno['desligar'] = fuzz.trimf(controle_forno.universe, [0, 0, 20])
controle_forno['manter'] = fuzz.trimf(controle_forno.universe, [40, 60, 80])
controle_forno['ligar'] = fuzz.trimf(controle_forno.universe, [60, 80, 100])

# Regras do sistema nebuloso
regra1 = ctrl.Rule(
    temperatura_atual['alta'] & taxa_variacao['diminuindo'], controle_forno['desligar'])
regra2 = ctrl.Rule(
    temperatura_atual['baixa'] & taxa_variacao['aumentando'], controle_forno['ligar'])
regra3 = ctrl.Rule(
    temperatura_atual['media'] & taxa_variacao['estavel'], controle_forno['manter'])
regra4 = ctrl.Rule(
    temperatura_atual['baixa'] & taxa_variacao['estavel'], controle_forno['ligar'])
regra5 = ctrl.Rule(
    temperatura_atual['alta'] & taxa_variacao['estavel'], controle_forno['manter'])
regra6 = ctrl.Rule(
    temperatura_atual['media'] & taxa_variacao['aumentando'], controle_forno['ligar'])

# Sistema de controle
controle = ctrl.ControlSystem([regra1, regra2, regra3, regra4, regra5, regra6])
controle_fuzzy = ctrl.ControlSystemSimulation(controle)

# Função para simular o sistema nebuloso


def simula_forno_nebuloso(controlador, setpoint, initial_temp, time_steps):
    temperature = initial_temp
    temperatures = []
    times = np.arange(time_steps)
    for t in times:
        controlador.input['Temperatura Atual'] = temperature
        controlador.input['Taxa de Variação'] = (
            temperature - previous_temperature) if t > 0 else 0
        controlador.compute()
        power = controlador.output['Controle do Forno']
        temperature += power * 0.1  # Aumento de temperatura conforme a potência
        temperatures.append(temperature)
        previous_temperature = temperature
    return times, temperatures


# Parâmetros do processo de simulação
setpoint = 200  # Temperatura desejada (°C)
initial_temp = 50  # Temperatura inicial do forno (°C)
time_steps = 100  # Número de passos de tempo
# Simulação com controlador nebuloso
times_nebuloso, temperatures_nebuloso = simula_forno_nebuloso(
    controle_fuzzy, setpoint, initial_temp, time_steps)

# Plotando os resultados do controlador nebuloso
plt.figure(figsize=(10, 5))
plt.plot(times_nebuloso, temperatures_nebuloso, label="Temperatura (Nebuloso)")
plt.axhline(y=setpoint, color='r', linestyle='--', label="Setpoint")
plt.title("Resposta do Forno com Controlador Nebuloso")
plt.xlabel("Tempo (s)")
plt.ylabel("Temperatura (°C)")
plt.legend()
plt.grid(True)
plt.show()
