# main.py - Loop Principal e Máquina de Estados do Jogo
import pygame
import random
import math
import sys

from config import *
from engine.sound_chip import SoundChip
from engine.crt_renderer import CRTRenderer
from assets_code.sprites_player import carregar_sprites_player
from stages.sector_1_rust import SETOR_1_FASES

# Inicialização do Pygame e Sintetizador de Áudio (Mono, 22050Hz, 16-bit)
pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()

tela_real = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
pygame.display.set_caption("WARRIOR FROM OUTER SPACE - [Python Phantasy System]")
clock = pygame.time.Clock()

superficie_interna = pygame.Surface((LARGURA_INT, ALTURA_INT))

# Inicializa Módulos da Arquitetura
FRAMES_NAVE, sprite_vida, spr_decolagem_4x, ESC_NAVE = carregar_sprites_player()
som = SoundChip()
ui = CRTRenderer(sprite_vida)

# Estrelas Warp (Intro) e Estrelas Parallax (Menu/Gameplay)
estrelas_warp = [
    {"ang": random.uniform(0, math.pi * 2), "dist": random.uniform(2, 220), "vel": random.uniform(0.8, 2.5)}
    for _ in range(70)
]

estrelas = []
for _ in range(75):
    camada = random.choice([1, 2, 3])
    cor = random.choice([(90, 50, 30), (80, 85, 100)]) if camada == 1 else (
          (160, 165, 180) if camada == 2 else (255, 255, 255))
    estrelas.append({
        "x": random.randint(10, LARGURA_INT - 12),
        "y": random.uniform(10, ALTURA_INT - 10),
        "vel": camada * 0.45,
        "cor": cor,
        "tam": 2 if camada == 3 and random.random() > 0.7 else 1
    })

# Estados: "LOGO_CAMPGAMES" -> "STORY_XT" -> "TITLE_MENU" -> "LAUNCH_SEQ" -> "GAMEPLAY"
estado_atual = "LOGO_CAMPGAMES"
timer_estado = 0

xt_linha_atual = 0
xt_char_atual = 0
xt_delay_timer = 0
som_logo_tocado = False
som_brilho_tocado = False

menu_index = 0
mostrar_aviso_opcoes = False

# Variáveis da Cinemática de Decolagem
pista_scroll_y = 0.0
pista_velocidade = 0.0
particulas_decolagem = []

fase_atual_num = 1
nave_x = float(AREA_JOGO_X + (AREA_JOGO_LARG // 2))
nave_y = float(AREA_JOGO_Y + AREA_JOGO_ALT - 42)
nave_roll = 0.0
timer_anuncio_fase = 180
tempo = 0

def iniciar_sequencia_decolagem():
    global estado_atual, timer_estado, pista_scroll_y, pista_velocidade, particulas_decolagem
    estado_atual = "LAUNCH_SEQ"
    timer_estado = 0
    pista_scroll_y = 0.0
    pista_velocidade = 0.0
    particulas_decolagem = []

# =====================================================================
# LOOP PRINCIPAL DO JOGO
# =====================================================================
executando = True
while executando:
    tempo += 1
    timer_estado += 1

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if mostrar_aviso_opcoes:
                    mostrar_aviso_opcoes = False
                    som.som_menu_mover.play()
                else:
                    executando = False

            elif estado_atual == "LOGO_CAMPGAMES":
                if evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                    estado_atual = "STORY_XT"
                    timer_estado = 0

            elif estado_atual == "STORY_XT":
                if evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if xt_linha_atual < len(LINHAS_HISTORIA_XT):
                        xt_linha_atual = len(LINHAS_HISTORIA_XT)
                        som.som_bip_linha.play()
                    else:
                        som.som_menu_selecionar.play()
                        estado_atual = "TITLE_MENU"
                        timer_estado = 0

            elif estado_atual == "TITLE_MENU":
                if mostrar_aviso_opcoes:
                    if evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                        mostrar_aviso_opcoes = False
                        som.som_menu_mover.play()
                else:
                    if evento.key in (pygame.K_UP, pygame.K_DOWN):
                        menu_index = 1 - menu_index
                        som.som_menu_mover.play()
                    elif evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                        som.som_menu_selecionar.play()
                        if menu_index == 0:
                            iniciar_sequencia_decolagem()
                        else:
                            mostrar_aviso_opcoes = True

    # =================================================================
    # ESTADO 1: LOGO "CAMPGAMES ARTS" SURGINDO DO FUNDO DO ESPAÇO
    # =================================================================
    if estado_atual == "LOGO_CAMPGAMES":
        superficie_interna.fill(PRETO_ESPACO)

        if not som_logo_tocado:
            som.som_logo_surgindo.play()
            som_logo_tocado = True

        cx, cy = LARGURA_INT // 2, ALTURA_INT // 2
        for est in estrelas_warp:
            est["dist"] += est["vel"] * (1.0 + est["dist"] * 0.018)
            if est["dist"] > 240:
                est["dist"] = random.uniform(1, 15)
                est["ang"] = random.uniform(0, math.pi * 2)
            ex = int(cx + math.cos(est["ang"]) * est["dist"])
            ey = int(cy + math.sin(est["ang"]) * est["dist"])
            cor_w = BRANCO if est["dist"] > 80 else METAL_CLARO
            tam_w = 2 if est["dist"] > 120 else 1
            pygame.draw.rect(superficie_interna, cor_w, (ex, ey, tam_w, tam_w))

        if timer_estado < 90:
            escala_logo = max(0.04, timer_estado / 90.0)
            alpha_logo = int(min(255, escala_logo * 300))
        elif timer_estado < 240:
            escala_logo = 1.0
            alpha_logo = 255
            if not som_brilho_tocado:
                som.som_logo_brilho.play()
                som_brilho_tocado = True
        elif timer_estado < 310:
            escala_logo = 1.0 + ((timer_estado - 240) * 0.003)
            alpha_logo = max(0, int(255 - ((timer_estado - 240) / 70.0) * 255))
        else:
            estado_atual = "STORY_XT"
            timer_estado = 0
            escala_logo = 1.0
            alpha_logo = 0

        if alpha_logo > 0:
            nova_larg = max(4, int(ui.logo_campgames_surf.get_width() * escala_logo))
            nova_alt = max(2, int(ui.logo_campgames_surf.get_height() * escala_logo))
            logo_escalado = pygame.transform.scale(ui.logo_campgames_surf, (nova_larg, nova_alt))
            logo_escalado.set_alpha(alpha_logo)
            rect_l = logo_escalado.get_rect(center=(cx, cy - 10))
            superficie_interna.blit(logo_escalado, rect_l.topleft)

            if 90 <= timer_estado < 240:
                ui.txt_centralizado(superficie_interna, "APRESENTA UMA PRODUCAO PARA", cx, cy + 42, METAL_CLARO, ui.fonte_p)
                ui.txt_centralizado(superficie_interna, "PYTHON PHANTASY SYSTEM", cx, cy + 56, AMARELO_ALERTA, ui.fonte_m)

        superficie_interna.blit(ui.moldura_intro, (0, 0))

    # =================================================================
    # ESTADO 2: TERMINAL PC XT 1980 DIGITANDO A HISTÓRIA
    # =================================================================
    elif estado_atual == "STORY_XT":
        superficie_interna.fill((4, 10, 5))
        pygame.draw.rect(superficie_interna, VERDE_XT_ESCURO, (14, 14, LARGURA_INT - 28, ALTURA_INT - 28), 1)

        if xt_linha_atual < len(LINHAS_HISTORIA_XT):
            xt_delay_timer += 1
            if xt_delay_timer >= 2:
                xt_delay_timer = 0
                linha_str = LINHAS_HISTORIA_XT[xt_linha_atual]
                if xt_char_atual < len(linha_str):
                    char_atual = linha_str[xt_char_atual]
                    xt_char_atual += 1
                    if char_atual != " " and xt_char_atual % 2 == 0:
                        som.som_tecla_xt.play()
                else:
                    xt_linha_atual += 1
                    xt_char_atual = 0
                    if xt_linha_atual < len(LINHAS_HISTORIA_XT) and LINHAS_HISTORIA_XT[xt_linha_atual - 1] != "":
                        som.som_bip_linha.play()

        y_cursor = 24
        x_cursor_final = 24
        y_cursor_final = 24
        for idx in range(min(xt_linha_atual + 1, len(LINHAS_HISTORIA_XT))):
            texto_completo = LINHAS_HISTORIA_XT[idx]
            trecho = texto_completo if idx < xt_linha_atual else texto_completo[:xt_char_atual]

            if idx < 3:
                cor_xt = LED_CIANO
            elif "C:\\WARRIOR>" in texto_completo:
                cor_xt = AMARELO_ALERTA
            elif "---" in texto_completo:
                cor_xt = VERDE_XT_ESCURO
            else:
                cor_xt = LED_VERDE

            ui.txt_pixel(superficie_interna, trecho, 24, y_cursor, cor_xt, ui.fonte_p)
            if idx == xt_linha_atual:
                x_cursor_final = 24 + ui.fonte_p.size(trecho)[0]
                y_cursor_final = y_cursor
            y_cursor += 13

        if xt_linha_atual < len(LINHAS_HISTORIA_XT):
            if (tempo // 6) % 2 == 0:
                pygame.draw.rect(superficie_interna, LED_VERDE, (x_cursor_final + 2, y_cursor_final + 1, 6, 9))
        else:
            if (tempo // 15) % 2 == 0:
                pygame.draw.rect(superficie_interna, AMARELO_ALERTA, (338, 245, 7, 10))

        superficie_interna.blit(ui.moldura_intro, (0, 0))

    # =================================================================
    # ESTADO 3: TELA DE TÍTULO COM LOGO DO JOGO E MENU
    # =================================================================
    elif estado_atual == "TITLE_MENU":
        superficie_interna.fill(PRETO_ESPACO)

        for est in estrelas:
            est["y"] += est["vel"] * 1.4
            if est["y"] >= ALTURA_INT - 8:
                est["y"] = 8
                est["x"] = random.randint(10, LARGURA_INT - 12)
            pygame.draw.rect(superficie_interna, est["cor"], (int(est["x"]), int(est["y"]), est["tam"], est["tam"]))

        cx = LARGURA_INT // 2

        ui.desenhar_placa_enferrujada(superficie_interna, 34, 22, LARGURA_INT - 68, 66, FERRUGEM_BASE)
        ui.desenhar_visor_embutido(superficie_interna, 40, 28, LARGURA_INT - 80, 54)

        for offset, cor_t in [(3, FERRUGEM_SOMBRA), (2, (160, 45, 10)), (1, LED_LARANJA), (0, AMARELO_ALERTA)]:
            t_w = ui.fonte_titulo_maior.render("WARRIOR", False, cor_t)
            superficie_interna.blit(t_w, (cx - t_w.get_width() // 2 + offset, 33 + offset))

        ui.txt_centralizado(superficie_interna, "F R O M   O U T E R   S P A C E", cx, 63, LED_LARANJA, ui.fonte_m)

        x_patrulha = cx + math.sin(tempo * 0.04) * 55
        vel_x_patrulha = math.cos(tempo * 0.04)
        frame_patrulha = -2 if vel_x_patrulha < -0.6 else (-1 if vel_x_patrulha < -0.2 else (2 if vel_x_patrulha > 0.6 else (1 if vel_x_patrulha > 0.2 else 0)))
        nave_demo = FRAMES_NAVE[frame_patrulha].copy()
        if tempo % 4 < 2:
            pygame.draw.rect(nave_demo, LED_LARANJA, (4 * ESC_NAVE, 18 * ESC_NAVE, 2 * ESC_NAVE, 2 * ESC_NAVE))
            pygame.draw.rect(nave_demo, LED_LARANJA, (7 * ESC_NAVE, 18 * ESC_NAVE, 2 * ESC_NAVE, 2 * ESC_NAVE))
        rect_demo = nave_demo.get_rect(center=(int(x_patrulha), 132))
        superficie_interna.blit(nave_demo, rect_demo.topleft)

        ui.desenhar_placa_enferrujada(superficie_interna, 85, 172, 230, 74, METAL_ESCURO)
        ui.desenhar_visor_embutido(superficie_interna, 91, 178, 218, 62)

        opcoes = ["INICIAR MISSAO (START)", "OPCOES DO SISTEMA"]
        for i, texto_op in enumerate(opcoes):
            y_op = 190 + i * 22
            if menu_index == i:
                cor_op = AMARELO_ALERTA if (tempo // 6) % 2 == 0 else BRANCO
                ui.txt_centralizado(superficie_interna, f">> {texto_op} <<", cx, y_op, cor_op, ui.fonte_m)
            else:
                ui.txt_centralizado(superficie_interna, texto_op, cx, y_op, METAL_CLARO, ui.fonte_m)

        ui.txt_centralizado(superficie_interna, "PRESSIONE [ESPACO] PARA CONFIRMAR", cx, 254, LED_VERDE, ui.fonte_p)
        ui.txt_centralizado(superficie_interna, "(C) 1986/3084 CAMPGAMES ARTS - PYTHON PHANTASY SYSTEM", cx, 274, FERRUGEM_LUZ, ui.fonte_p)

        if mostrar_aviso_opcoes:
            ui.desenhar_placa_enferrujada(superficie_interna, 60, 95, 280, 110, FERRUGEM_BASE)
            ui.desenhar_visor_embutido(superficie_interna, 66, 101, 268, 98)
            ui.txt_centralizado(superficie_interna, "[ OPCOES DO SISTEMA ]", cx, 110, AMARELO_ALERTA, ui.fonte_m)
            ui.txt_centralizado(superficie_interna, "FILTRO CRT RGB: ATIVADO", cx, 132, LED_VERDE, ui.fonte_p)
            ui.txt_centralizado(superficie_interna, "SINTETIZADOR GRAVE: ATIVADO", cx, 146, LED_VERDE, ui.fonte_p)
            ui.txt_centralizado(superficie_interna, "DIFICULDADE: HARDCORE ARCADE", cx, 160, LED_LARANJA, ui.fonte_p)
            ui.txt_centralizado(superficie_interna, "PRESSIONE [ESPACO] PARA VOLTAR", cx, 182, LED_CIANO, ui.fonte_p)

        superficie_interna.blit(ui.moldura_intro, (0, 0))

    # =================================================================
    # ESTADO 4: SEQUÊNCIA DE DECOLAGEM ESTENDIDA (3s DE PISTA + 3 BEEPS!)
    # =================================================================
    elif estado_atual == "LAUNCH_SEQ":
        centro_jogo_x = AREA_JOGO_X + (AREA_JOGO_LARG // 2)
        dados_fase = SETOR_1_FASES[fase_atual_num]

        # Disparos sonoros: "Bep... Bep... BEEEEEP!"
        if timer_estado == 20:
            som.som_beep_curto.play()
        elif timer_estado == 50:
            som.som_beep_curto.play()
        elif timer_estado == 80:
            som.som_beep_longo.play()
            som.som_garra_soltando.play()

        progresso_espaco = max(0.0, min(1.0, (timer_estado - 180) / 140.0))
        cor_ceu_base = dados_fase["cor_ceu_planeta"]
        cor_ceu = (
            int(cor_ceu_base[0] * (1 - progresso_espaco) + PRETO_ESPACO[0] * progresso_espaco),
            int(cor_ceu_base[1] * (1 - progresso_espaco) + PRETO_ESPACO[1] * progresso_espaco),
            int(cor_ceu_base[2] * (1 - progresso_espaco) + PRETO_ESPACO[2] * progresso_espaco),
        )
        superficie_interna.fill(cor_ceu)

        y_horizonte = int(50 + (progresso_espaco * 270))
        if y_horizonte < ALTURA_INT:
            pygame.draw.rect(superficie_interna, dados_fase["cor_solo_planeta"], (AREA_JOGO_X, y_horizonte, AREA_JOGO_LARG, ALTURA_INT - y_horizonte))
            pygame.draw.line(superficie_interna, FERRUGEM_LUZ, (AREA_JOGO_X, y_horizonte), (AREA_JOGO_X + AREA_JOGO_LARG, y_horizonte), 2)

        for est in estrelas:
            est["y"] += est["vel"] * (0.5 + progresso_espaco * 3.0)
            if est["y"] >= AREA_JOGO_Y + AREA_JOGO_ALT:
                est["y"] = AREA_JOGO_Y
                est["x"] = random.randint(AREA_JOGO_X, AREA_JOGO_X + AREA_JOGO_LARG - 2)
            if est["x"] < AREA_JOGO_X + AREA_JOGO_LARG and est["y"] < y_horizonte:
                pygame.draw.rect(superficie_interna, est["cor"], (int(est["x"]), int(est["y"]), est["tam"], est["tam"]))

        if timer_estado < 80:
            pista_velocidade = 0.0
        elif timer_estado < 260:
            pista_velocidade = min(11.0, pista_velocidade + 0.12)
        else:
            pista_velocidade = 11.0

        pista_scroll_y = (pista_scroll_y + pista_velocidade) % 24
        y_topo_rampa = AREA_JOGO_Y if timer_estado < 250 else int(AREA_JOGO_Y + ((timer_estado - 250) * 4.5))

        if y_topo_rampa < AREA_JOGO_Y + AREA_JOGO_ALT:
            x_pista = centro_jogo_x - 68
            area_visivel_alt = (AREA_JOGO_Y + AREA_JOGO_ALT) - y_topo_rampa
            superficie_interna.blit(
                ui.pista_lancamento_surf,
                (x_pista, y_topo_rampa),
                (0, int(24 - pista_scroll_y), 136, min(290, area_visivel_alt))
            )

            if y_topo_rampa > AREA_JOGO_Y:
                pygame.draw.rect(superficie_interna, METAL_CLARO, (x_pista, y_topo_rampa, 136, 4))
                pygame.draw.rect(superficie_interna, AMARELO_ALERTA, (x_pista + 20, y_topo_rampa + 4, 96, 3))

            for ly in range(y_topo_rampa + int(pista_scroll_y), AREA_JOGO_Y + AREA_JOGO_ALT, 24):
                if timer_estado < 50:
                    cor_luz = LED_VERMELHO if timer_estado >= 20 else FERRUGEM_SOMBRA
                elif timer_estado < 80:
                    cor_luz = AMARELO_ALERTA
                else:
                    cor_luz = LED_VERDE if ((ly // 24) + (tempo // 3)) % 3 == 0 else VERDE_XT_ESCURO
                pygame.draw.rect(superficie_interna, cor_luz, (x_pista + 12, ly, 4, 6))
                pygame.draw.rect(superficie_interna, cor_luz, (x_pista + 120, ly, 4, 6))

            abertura_garra = 0 if timer_estado < 80 else min(28, int((timer_estado - 80) * 1.8))
            y_garra = int(215 + max(0, (timer_estado - 85) * 3.0))
            if y_garra < AREA_JOGO_Y + AREA_JOGO_ALT - 10:
                pygame.draw.rect(superficie_interna, METAL_BASE, (centro_jogo_x - 42 - abertura_garra, y_garra, 18, 10))
                pygame.draw.rect(superficie_interna, AMARELO_ALERTA, (centro_jogo_x - 26 - abertura_garra, y_garra + 2, 4, 6))
                pygame.draw.rect(superficie_interna, METAL_BASE, (centro_jogo_x + 24 + abertura_garra, y_garra, 18, 10))
                pygame.draw.rect(superficie_interna, AMARELO_ALERTA, (centro_jogo_x + 22 + abertura_garra, y_garra + 2, 4, 6))

        if timer_estado < 80:
            escala_atual = 4.0
            vib_x = random.choice([-1, 0, 1]) if timer_estado >= 20 else 0
            vib_y = random.choice([-1, 0, 1]) if timer_estado >= 50 else 0
            pos_nave_x = centro_jogo_x + vib_x
            pos_nave_y = 225 + vib_y
        elif timer_estado < 260:
            prog_pista = (timer_estado - 80) / 180.0
            escala_atual = 4.0 - (prog_pista * 1.0)
            pos_nave_x = centro_jogo_x
            pos_nave_y = int(225 - (prog_pista * 80))
        else:
            prog_orbita = min(1.0, (timer_estado - 260) / 100.0)
            escala_atual = 3.0 - (prog_orbita * 1.0)
            pos_nave_x = centro_jogo_x
            pos_nave_y = int(145 - math.sin(prog_orbita * math.pi) * 20 + (prog_orbita * 105))

        if 20 <= timer_estado < 310:
            qtd_part = 2 if timer_estado < 80 else 4
            for _ in range(qtd_part):
                particulas_decolagem.append({
                    "x": pos_nave_x + random.randint(-10, 10),
                    "y": pos_nave_y + int(8 * escala_atual),
                    "vx": random.uniform(-1.3, 1.3),
                    "vy": random.uniform(3.0, 6.5),
                    "vida": random.randint(12, 24),
                    "cor": random.choice([AMARELO_ALERTA, LED_LARANJA, FERRUGEM_LUZ, METAL_CLARO])
                })

        for part in particulas_decolagem[:]:
            part["x"] += part["vx"]
            part["y"] += part["vy"]
            part["vida"] -= 1
            if part["vida"] <= 0 or part["y"] >= AREA_JOGO_Y + AREA_JOGO_ALT:
                particulas_decolagem.remove(part)
            else:
                tam_p = 3 if part["vida"] > 10 else 2
                pygame.draw.rect(superficie_interna, part["cor"], (int(part["x"]), int(part["y"]), tam_p, tam_p))

        larg_dinamica = int(13 * escala_atual)
        alt_dinamica = int(20 * escala_atual)
        nave_base_decolagem = spr_decolagem_4x.copy()
        if tempo % 4 < 2:
            pygame.draw.rect(nave_base_decolagem, BRANCO, (16, 68, 8, 10))
            pygame.draw.rect(nave_base_decolagem, BRANCO, (28, 68, 8, 10))
        nave_escalada = pygame.transform.scale(nave_base_decolagem, (larg_dinamica, alt_dinamica))
        rect_dec = nave_escalada.get_rect(center=(int(pos_nave_x), int(pos_nave_y)))
        superficie_interna.blit(nave_escalada, rect_dec.topleft)

        if timer_estado < 20:
            ui.txt_centralizado(superficie_interna, "PREPARANDO CATAPULTA...", centro_jogo_x, 28, METAL_CLARO, ui.fonte_p)
        elif timer_estado < 50:
            ui.txt_centralizado(superficie_interna, "IGNICAO: [ 2 ]", centro_jogo_x, 28, LED_VERMELHO, ui.fonte_g)
        elif timer_estado < 80:
            ui.txt_centralizado(superficie_interna, "IGNICAO: [ 1 ]", centro_jogo_x, 28, AMARELO_ALERTA, ui.fonte_g)
        elif timer_estado < 140:
            if (tempo // 3) % 2 == 0:
                ui.txt_centralizado(superficie_interna, ">> LANCAMENTO! <<", centro_jogo_x, 28, LED_VERDE, ui.fonte_g)
        elif timer_estado < 260:
            ui.txt_centralizado(superficie_interna, "ACELERACAO MAXIMA NA RAMPA!", centro_jogo_x, 28, AMARELO_ALERTA, ui.fonte_p)
        else:
            ui.txt_centralizado(superficie_interna, "ENTRANDO EM ORBITA DE DEFESA...", centro_jogo_x, 35, LED_CIANO, ui.fonte_p)

        ui.desenhar_hud_direito(superficie_interna, tempo)

        if timer_estado >= 360:
            estado_atual = "GAMEPLAY"
            timer_estado = 0
            timer_anuncio_fase = 180
            nave_x = float(centro_jogo_x)
            nave_y = float(pos_nave_y)
            nave_roll = 0.0

    # =================================================================
    # ESTADO 5: GAMEPLAY ATIVO (EM ÓRBITA)
    # =================================================================
    elif estado_atual == "GAMEPLAY":
        if timer_anuncio_fase > 0:
            timer_anuncio_fase -= 1

        teclas = pygame.key.get_pressed()
        vel_nave = 2.2
        movendo_x = 0

        if teclas[pygame.K_LEFT] and nave_x > AREA_JOGO_X + 16:
            nave_x -= vel_nave
            movendo_x = -1
        if teclas[pygame.K_RIGHT] and nave_x < AREA_JOGO_X + AREA_JOGO_LARG - 16:
            nave_x += vel_nave
            movendo_x = 1
        if teclas[pygame.K_UP] and nave_y > AREA_JOGO_Y + 24:
            nave_y -= vel_nave
        if teclas[pygame.K_DOWN] and nave_y < AREA_JOGO_Y + AREA_JOGO_ALT - 24:
            nave_y += vel_nave

        alvo_roll = movendo_x * 2.0
        nave_roll += (alvo_roll - nave_roll) * 0.25
        indice_frame = max(-2, min(2, int(round(nave_roll))))

        superficie_interna.fill(PRETO_ESPACO)

        for est in estrelas:
            est["y"] += est["vel"]
            if est["y"] >= AREA_JOGO_Y + AREA_JOGO_ALT:
                est["y"] = AREA_JOGO_Y
                est["x"] = random.randint(AREA_JOGO_X, AREA_JOGO_X + AREA_JOGO_LARG - 2)
            if est["x"] < AREA_JOGO_X + AREA_JOGO_LARG:
                pygame.draw.rect(superficie_interna, est["cor"], (int(est["x"]), int(est["y"]), est["tam"], est["tam"]))

        nave_frame = FRAMES_NAVE[indice_frame].copy()
        if tempo % 4 < 2:
            pygame.draw.rect(nave_frame, LED_LARANJA, (4 * ESC_NAVE, 18 * ESC_NAVE, 2 * ESC_NAVE, 2 * ESC_NAVE))
            pygame.draw.rect(nave_frame, LED_LARANJA, (7 * ESC_NAVE, 18 * ESC_NAVE, 2 * ESC_NAVE, 2 * ESC_NAVE))
        else:
            pygame.draw.rect(nave_frame, AMARELO_ALERTA, (4 * ESC_NAVE, 17 * ESC_NAVE, 1 * ESC_NAVE, 2 * ESC_NAVE))
            pygame.draw.rect(nave_frame, AMARELO_ALERTA, (8 * ESC_NAVE, 17 * ESC_NAVE, 1 * ESC_NAVE, 2 * ESC_NAVE))

        rect_nave = nave_frame.get_rect(center=(int(nave_x), int(nave_y)))
        superficie_interna.blit(nave_frame, rect_nave.topleft)

        centro_jogo_x = AREA_JOGO_X + (AREA_JOGO_LARG // 2)
        dados_fase = SETOR_1_FASES[fase_atual_num]
        if timer_anuncio_fase > 0:
            if timer_anuncio_fase > 40 or (timer_anuncio_fase // 4) % 2 == 0:
                pygame.draw.line(superficie_interna, FERRUGEM_LUZ, (centro_jogo_x - 80, 110), (centro_jogo_x + 80, 110))
                ui.txt_centralizado(superficie_interna, dados_fase["codigo"], centro_jogo_x, 116, LED_VERDE, ui.fonte_g)
                ui.txt_centralizado(superficie_interna, dados_fase["nome"], centro_jogo_x, 134, LED_LARANJA, ui.fonte_p)
                pygame.draw.line(superficie_interna, FERRUGEM_LUZ, (centro_jogo_x - 80, 148), (centro_jogo_x + 80, 148))

        ui.desenhar_hud_direito(superficie_interna, tempo)

    # =================================================================
    # RENDERIZAÇÃO FINAL COM FILTRO CRT
    # =================================================================
    ui.renderizar_crt(superficie_interna, tela_real)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
