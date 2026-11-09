# engine/crt_renderer.py - Renderizador CRT, Scanlines, HUD Enferrujado e Pista
import pygame
import random
import math
from config import *

class CRTRenderer:
    def __init__(self, sprite_vida):
        self.sprite_vida = sprite_vida
        self.fonte_p = pygame.font.SysFont("Courier", 10, bold=True)
        self.fonte_m = pygame.font.SysFont("Courier", 12, bold=True)
        self.fonte_g = pygame.font.SysFont("Courier", 15, bold=True)
        self.fonte_titulo_maior = pygame.font.SysFont("Courier", 24, bold=True)

        self.mascara_crt = self.criar_mascara_crt()
        self.carcaca_hud = self.construir_moldura_e_hud_estatico()
        self.moldura_intro = self.construir_moldura_tela_cheia()
        self.pista_lancamento_surf = self.construir_segmento_pista_metal(136, 320)
        self.logo_campgames_surf = self.construir_emblema_campgames()

    def construir_emblema_campgames(self):
        surf = pygame.Surface((240, 74), pygame.SRCALPHA)
        pygame.draw.rect(surf, (15, 45, 105), (10, 6, 220, 62), border_radius=6)
        pygame.draw.rect(surf, (45, 155, 240), (10, 6, 220, 62), 3, border_radius=6)
        pygame.draw.rect(surf, (140, 235, 255), (13, 9, 214, 56), 1, border_radius=4)
        
        for px, py in [(17, 13), (221, 13), (17, 59), (221, 59)]:
            pygame.draw.rect(surf, (255, 220, 60), (px, py, 3, 3))

        for dx, dy, cor in [(2, 2, (10, 20, 50)), (0, 1, (35, 130, 230)), (0, 0, (120, 235, 255))]:
            t1 = self.fonte_titulo_maior.render("CAMPGAMES", False, cor)
            surf.blit(t1, (120 - t1.get_width() // 2 + dx, 12 + dy))

        pygame.draw.rect(surf, (25, 85, 175), (68, 42, 104, 18))
        pygame.draw.rect(surf, (215, 155, 20), (68, 42, 104, 18), 1)
        t2 = self.fonte_g.render("* ARTS *", False, (255, 225, 80))
        surf.blit(t2, (120 - t2.get_width() // 2, 43))
        return surf

    @staticmethod
    def desenhar_placa_enferrujada(surf, x, y, larg, alt, cor_base=FERRUGEM_BASE):
        pygame.draw.rect(surf, cor_base, (x, y, larg, alt))
        random.seed(x * 100 + y)
        for _ in range((larg * alt) // 28):
            rx = random.randint(x + 2, max(x + 2, x + larg - 6))
            ry = random.randint(y + 2, max(y + 2, y + alt - 6))
            rw = random.randint(2, 5)
            rh = random.randint(1, 3)
            cor_mancha = random.choice([FERRUGEM_SOMBRA, FERRUGEM_LUZ, METAL_ESCURO])
            pygame.draw.rect(surf, cor_mancha, (rx, ry, rw, rh))

        pygame.draw.line(surf, FERRUGEM_LUZ, (x, y), (x + larg - 1, y))
        pygame.draw.line(surf, FERRUGEM_LUZ, (x, y), (x, y + alt - 1))
        pygame.draw.line(surf, FERRUGEM_SOMBRA, (x, y + alt - 1), (x + larg - 1, y + alt - 1))
        pygame.draw.line(surf, FERRUGEM_SOMBRA, (x + larg - 1, y), (x + larg - 1, y + alt - 1))

    @staticmethod
    def desenhar_rebite(surf, x, y):
        pygame.draw.rect(surf, FERRUGEM_SOMBRA, (x, y, 2, 2))
        surf.set_at((x, y), METAL_CLARO)

    @staticmethod
    def desenhar_visor_embutido(surf, x, y, larg, alt):
        pygame.draw.rect(surf, PRETO_VISOR, (x, y, larg, alt))
        pygame.draw.rect(surf, FERRUGEM_SOMBRA, (x, y, larg, alt), 1)
        pygame.draw.line(surf, METAL_BASE, (x + 1, y + alt - 1), (x + larg - 1, y + alt - 1))
        pygame.draw.line(surf, METAL_BASE, (x + larg - 1, y + 1), (x + larg - 1, y + alt - 1))
        for px, py in [(x + 2, y + 2), (x + larg - 4, y + 2), (x + 2, y + alt - 4), (x + larg - 4, y + alt - 4)]:
            surf.set_at((px, py), METAL_ESCURO)

    def construir_moldura_e_hud_estatico(self):
        surf = pygame.Surface((LARGURA_INT, ALTURA_INT), pygame.SRCALPHA)
        self.desenhar_placa_enferrujada(surf, 0, 0, HUD_X, 8)
        self.desenhar_placa_enferrujada(surf, 0, ALTURA_INT - 8, HUD_X, 8)
        self.desenhar_placa_enferrujada(surf, 0, 8, 8, ALTURA_INT - 16)
        self.desenhar_placa_enferrujada(surf, HUD_X - 8, 8, 8, ALTURA_INT - 16)
        
        for ry in range(14, ALTURA_INT - 12, 26):
            self.desenhar_rebite(surf, 3, ry)
            self.desenhar_rebite(surf, HUD_X - 5, ry)
        for rx in range(14, HUD_X - 12, 30):
            self.desenhar_rebite(surf, rx, 3)
            self.desenhar_rebite(surf, rx, ALTURA_INT - 5)

        self.desenhar_placa_enferrujada(surf, HUD_X, 0, HUD_LARG, ALTURA_INT, FERRUGEM_BASE)
        self.desenhar_placa_enferrujada(surf, HUD_X + 5, 6, HUD_LARG - 10, 36, METAL_ESCURO)
        for rx in [HUD_X + 8, HUD_X + HUD_LARG - 10]:
            for ry in [9, 37]:
                self.desenhar_rebite(surf, rx, ry)

        faixa_y = 46
        pygame.draw.rect(surf, PRETO_VISOR, (HUD_X + 5, faixa_y, HUD_LARG - 10, 6))
        for hx in range(HUD_X + 7, HUD_X + HUD_LARG - 10, 8):
            pygame.draw.polygon(surf, AMARELO_ALERTA, [
                (hx, faixa_y + 5), (hx + 4, faixa_y), (hx + 7, faixa_y), (hx + 3, faixa_y + 5)
            ])

        self.desenhar_visor_embutido(surf, HUD_X + 6, 58, HUD_LARG - 12, 38)
        self.desenhar_visor_embutido(surf, HUD_X + 6, 104, HUD_LARG - 12, 38)
        self.desenhar_visor_embutido(surf, HUD_X + 6, 150, HUD_LARG - 12, 54)
        self.desenhar_visor_embutido(surf, HUD_X + 6, 212, HUD_LARG - 12, 58)

        self.desenhar_placa_enferrujada(surf, HUD_X + 5, 278, HUD_LARG - 10, 16, METAL_ESCURO)
        self.desenhar_rebite(surf, HUD_X + 8, 285)
        self.desenhar_rebite(surf, HUD_X + HUD_LARG - 10, 285)
        return surf

    def construir_moldura_tela_cheia(self):
        surf = pygame.Surface((LARGURA_INT, ALTURA_INT), pygame.SRCALPHA)
        self.desenhar_placa_enferrujada(surf, 0, 0, LARGURA_INT, 8)
        self.desenhar_placa_enferrujada(surf, 0, ALTURA_INT - 8, LARGURA_INT, 8)
        self.desenhar_placa_enferrujada(surf, 0, 8, 8, ALTURA_INT - 16)
        self.desenhar_placa_enferrujada(surf, LARGURA_INT - 8, 8, 8, ALTURA_INT - 16)
        for rx in range(16, LARGURA_INT - 12, 32):
            self.desenhar_rebite(surf, rx, 3)
            self.desenhar_rebite(surf, rx, ALTURA_INT - 5)
        for ry in range(16, ALTURA_INT - 12, 28):
            self.desenhar_rebite(surf, 3, ry)
            self.desenhar_rebite(surf, LARGURA_INT - 5, ry)
        return surf

    def construir_segmento_pista_metal(self, larg, alt):
        surf = pygame.Surface((larg, alt))
        self.desenhar_placa_enferrujada(surf, 0, 0, larg, alt, FERRUGEM_BASE)
        
        pygame.draw.rect(surf, METAL_ESCURO, (8, 0, 12, alt))
        pygame.draw.rect(surf, METAL_ESCURO, (larg - 20, 0, 12, alt))
        pygame.draw.line(surf, METAL_CLARO, (8, 0), (8, alt))
        pygame.draw.line(surf, METAL_CLARO, (larg - 20, 0), (larg - 20, alt))

        pygame.draw.rect(surf, PRETO_VISOR, (larg // 2 - 24, 0, 48, alt))
        for gy in range(0, alt, 6):
            pygame.draw.line(surf, METAL_ESCURO, (larg // 2 - 24, gy), (larg // 2 + 24, gy), 2)
            cor_faixa = AMARELO_ALERTA if (gy // 6) % 2 == 0 else FERRUGEM_SOMBRA
            pygame.draw.rect(surf, cor_faixa, (larg // 2 - 30, gy, 5, 5))
            pygame.draw.rect(surf, cor_faixa, (larg // 2 + 25, gy, 5, 5))

        for sy in range(0, alt, 24):
            pygame.draw.line(surf, FERRUGEM_SOMBRA, (0, sy), (larg, sy), 2)
            pygame.draw.line(surf, FERRUGEM_LUZ, (0, sy + 2), (larg, sy + 2), 1)
            self.desenhar_rebite(surf, 4, sy + 6)
            self.desenhar_rebite(surf, larg - 6, sy + 6)

        return surf

    @staticmethod
    def criar_mascara_crt():
        surf = pygame.Surface((TELA_LARGURA, TELA_ALTURA), pygame.SRCALPHA)
        for y in range(0, TELA_ALTURA, 2):
            pygame.draw.line(surf, (0, 0, 0, 75), (0, y), (TELA_LARGURA, y))
        pygame.draw.rect(surf, (0, 0, 0, 90), (0, 0, TELA_LARGURA, TELA_ALTURA), 6)
        return surf

    def renderizar_crt(self, surf_interna, tela_destino):
        escalada = pygame.transform.scale(surf_interna, (TELA_LARGURA, TELA_ALTURA))
        tela_destino.blit(escalada, (0, 0))
        glow = escalada.copy()
        glow.set_alpha(28)
        tela_destino.blit(glow, (2, 0))
        tela_destino.blit(self.mascara_crt, (0, 0))

    def txt_pixel(self, surf, texto, x, y, cor, fonte=None):
        if fonte is None:
            fonte = self.fonte_p
        sombra = fonte.render(texto, False, (0, 0, 0))
        frente = fonte.render(texto, False, cor)
        surf.blit(sombra, (x + 1, y + 1))
        surf.blit(frente, (x, y))

    def txt_centralizado(self, surf, texto, x_centro, y, cor, fonte=None):
        if fonte is None:
            fonte = self.fonte_p
        larg_txt = fonte.size(texto)[0]
        self.txt_pixel(surf, texto, x_centro - (larg_txt // 2), y, cor, fonte)

    def desenhar_hud_direito(self, surf, tempo_atual, score=1450, hi_score=99990, vidas=3):
        surf.blit(self.carcaca_hud, (0, 0))
        centro_hud_x = HUD_X + (HUD_LARG // 2)
        self.txt_centralizado(surf, "WARRIOR", centro_hud_x, 9, LED_LARANJA, self.fonte_g)
        self.txt_centralizado(surf, "FROM OUTER SPACE", centro_hud_x, 25, AMARELO_ALERTA, self.fonte_p)

        self.txt_centralizado(surf, "RECORDE MAX", centro_hud_x, 62, LED_VERMELHO, self.fonte_p)
        self.txt_centralizado(surf, f"{hi_score:06d}", centro_hud_x, 76, BRANCO, self.fonte_g)

        self.txt_centralizado(surf, "PONTUACAO", centro_hud_x, 108, LED_CIANO, self.fonte_p)
        self.txt_centralizado(surf, f"{score:06d}", centro_hud_x, 122, BRANCO, self.fonte_g)

        self.txt_centralizado(surf, "VALKYRIE-X8", centro_hud_x, 155, LED_VERDE, self.fonte_p)
        larg_total_vidas = (3 * 14) + (2 * 8)
        inicio_vidas_x = centro_hud_x - (larg_total_vidas // 2)
        for i in range(vidas):
            surf.blit(self.sprite_vida, (inicio_vidas_x + i * 22, 172))

        self.txt_centralizado(surf, "WAVE BEAM", centro_hud_x, 217, LED_LARANJA, self.fonte_p)
        bx, by, bw, bh = HUD_X + 14, 233, HUD_LARG - 28, 12
        pygame.draw.rect(surf, FERRUGEM_SOMBRA, (bx, by, bw, bh))
        pygame.draw.rect(surf, METAL_BASE, (bx, by, bw, bh), 1)
        
        carga_pct = (math.sin(tempo_atual * 0.05) + 1) * 0.5
        carga_larg = int(carga_pct * (bw - 4))
        cor_barra = LED_VERMELHO if carga_pct > 0.85 and (tempo_atual // 4) % 2 == 0 else LED_CIANO
        pygame.draw.rect(surf, cor_barra, (bx + 2, by + 2, carga_larg, bh - 4))
        for seg in range(bx + 8, bx + bw - 2, 6):
            pygame.draw.line(surf, PRETO_VISOR, (seg, by + 1), (seg, by + bh - 2))

        status_txt = "[ PRONTO! ]" if carga_pct > 0.85 else f"CHARGE: {int(carga_pct * 100):02d}%"
        cor_status = AMARELO_ALERTA if carga_pct > 0.85 else METAL_CLARO
        self.txt_centralizado(surf, status_txt, centro_hud_x, 250, cor_status, self.fonte_p)
        self.txt_centralizado(surf, "CAMPGAMES ARTS", centro_hud_x, 281, AMARELO_ALERTA, self.fonte_p)
