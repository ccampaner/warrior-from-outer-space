# engine/sound_chip.py - Sintetizador de Som 8-Bits Grave & Industrial
import pygame
import math
import array

class SoundChip:
    def __init__(self):
        self.som_tecla_xt = self.gerar_som_grave_industrial(190, 130, 0.016, 0.09, "tri")
        self.som_bip_linha = self.gerar_som_grave_industrial(110, 95, 0.045, 0.12, "saw")
        self.som_menu_mover = self.gerar_som_grave_industrial(130, 165, 0.05, 0.15, "tri")
        self.som_menu_selecionar = self.gerar_som_grave_industrial(98, 196, 0.25, 0.18, "saw")
        self.som_logo_surgindo = self.gerar_som_grave_industrial(55, 110, 1.6, 0.18, "saw")
        self.som_logo_brilho = self.gerar_som_grave_industrial(110, 165, 0.8, 0.16, "tri")

        # Os 3 Bips de Lançamento: "Bep... Bep... BEEEEEP!" + destravamento mecânico da garra
        self.som_beep_curto = self.gerar_som_grave_industrial(220, 220, 0.12, 0.18, "tri")
        self.som_beep_longo = self.gerar_som_grave_industrial(440, 440, 0.45, 0.22, "saw")
        self.som_garra_soltando = self.gerar_som_grave_industrial(85, 42, 0.25, 0.20, "saw")

    @staticmethod
    def gerar_som_grave_industrial(freq_inicial, freq_final, duracao_seg, volume=0.15, tipo="saw"):
        taxa = 22050
        n_amostras = int(taxa * duracao_seg)
        buf = array.array('h')
        fase = 0.0
        val_anterior = 0.0

        for i in range(n_amostras):
            progresso = i / max(1, n_amostras)
            freq = freq_inicial + (freq_final - freq_inicial) * progresso
            fase += (2.0 * math.pi * freq) / taxa

            if tipo == "saw":
                onda_base = 2.0 * ((fase / (2.0 * math.pi)) - math.floor(0.5 + (fase / (2.0 * math.pi))))
            else:
                onda_base = (2.0 / math.pi) * math.asin(math.sin(fase))

            sub_oitava = math.sin(fase * 0.5)
            sinal_bruto = (onda_base * 0.6) + (sub_oitava * 0.4)

            sinal_filtrado = val_anterior * 0.72 + sinal_bruto * 0.28
            val_anterior = sinal_filtrado

            ataque = min(1.0, i / (taxa * 0.008))
            decay = (1.0 - progresso) ** 0.6
            amostra = int(sinal_filtrado * 32767 * volume * ataque * decay)
            buf.append(max(-32767, min(32767, amostra)))

        return pygame.mixer.Sound(buffer=buf)
