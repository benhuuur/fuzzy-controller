from dataclasses import dataclass


@dataclass
class Furnace:
    def __init__(self, Kf, K_loss):
        self.Kf = Kf       # Coeficiente de aquecimento
        self.K_loss = K_loss  # Coeficiente de perda de calor
