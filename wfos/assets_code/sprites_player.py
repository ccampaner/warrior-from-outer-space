# assets_code/sprites_player.py - Matrizes Pixel Art da Valkyrie-X8 e Emblemas
import pygame

PALETA_SPRITES = {
    '1': (135, 128, 115), # Metal Desgastado Claro (Canos e Arestas)
    '2': (82, 78, 72),    # Ferro Escuro / Gunmetal
    '3': (35, 30, 28),    # Sombra Profunda / Grelhas / Óleo Queimado
    '4': (130, 52, 18),   # Ferrugem Pesada (Casco Principal)
    '5': (180, 95, 28),   # Ocre Queimado / Chapa Oxidada Iluminada
    '6': (255, 215, 55),  # Núcleo da Turbina
    '7': (225, 60, 15),   # Fogo da Turbina
    '8': (22, 24, 28),    # Fresta Blindada do Cockpit
    '9': (185, 35, 25),   # Ogiva dos Lança-Foguetes
}

MATRIZ_VALKYRIE_CENTRO = [
    "....1...1....",
    "....1.3.1....",
    "....23432....",
    "....24542....",
    "....34343....",
    "...2454542...",
    "...2438342...",
    "...3482843...",
    ".9.3458543.9.",
    "3132454542313",
    "3244543454423",
    "3245432345423",
    "3144324234413",
    "3334324234333",
    "..343333343..",
    "...323.323...",
    "...363.363...",
    "....76.67....",
    "....77.77....",
    "....7...7....",
]

MATRIZ_VALKYRIE_DIR_1 = [
    "....1...1....",
    "....1.3.1....",
    "....24432....",
    "....25542....",
    "....35343....",
    "...2554432...",
    "...2548342...",
    "...3548833...",
    ".9.3554843.9.",
    "313255443231.",
    "324554344332.",
    "324553234332.",
    "314543243313.",
    ".3344323333..",
    "..34433333...",
    "...323.323...",
    "...363.363...",
    "....76.67....",
    "....77.77....",
    "....7...7....",
]

MATRIZ_VALKYRIE_DIR_2 = [
    "....1..1.....",
    "....1.31.....",
    "....2443.....",
    "....25532....",
    "....35432....",
    "...255533....",
    "...255483....",
    "...3554833...",
    "..935548339..",
    ".3125544331..",
    ".3245543332..",
    ".3245532332..",
    ".314543233...",
    "..33443233...",
    "...344333....",
    "...323.32....",
    "...363.36....",
    "....76.67....",
    "....77.77....",
    "....7...7....",
]

MATRIZ_MINI_VIDA = [
    "..1.1..",
    "..242..",
    "..484..",
    "9345439",
    "3453543",
    ".32.23.",
    ".76.67."
]

def criar_sprite(matriz, escala=1):
    altura = len(matriz)
    largura = len(matriz[0])
    surf = pygame.Surface((largura * escala, altura * escala), pygame.SRCALPHA)
    for y, linha in enumerate(matriz):
        for x, char in enumerate(linha):
            if char in PALETA_SPRITES:
                pygame.draw.rect(surf, PALETA_SPRITES[char], (x * escala, y * escala, escala, escala))
    return surf

def carregar_sprites_player():
    esc_nave = 2
    spr_centro = criar_sprite(MATRIZ_VALKYRIE_CENTRO, escala=esc_nave)
    spr_dir_1 = criar_sprite(MATRIZ_VALKYRIE_DIR_1, escala=esc_nave)
    spr_dir_2 = criar_sprite(MATRIZ_VALKYRIE_DIR_2, escala=esc_nave)
    spr_esq_1 = pygame.transform.flip(spr_dir_1, True, False)
    spr_esq_2 = pygame.transform.flip(spr_dir_2, True, False)

    frames_nave = {
        -2: spr_esq_2,
        -1: spr_esq_1,
         0: spr_centro,
         1: spr_dir_1,
         2: spr_dir_2
    }
    sprite_vida = criar_sprite(MATRIZ_MINI_VIDA, escala=2)
    spr_decolagem_4x = criar_sprite(MATRIZ_VALKYRIE_CENTRO, escala=4)
    return frames_nave, sprite_vida, spr_decolagem_4x, esc_nave
