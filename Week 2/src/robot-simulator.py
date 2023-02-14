import pygame

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
TEXTCOLOR = (0, 0, 0)
(width, height) = (200, 300)

running = True


def main(background):
    global running, screen
    last_pos = (0, 0)
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("TUFF")
    screen.fill(background)
    pygame.display.update()

    while running:
        ev = pygame.event.get()

        for event in ev:
            if event.type == pygame.MOUSEBUTTONDOWN:
                draw_circle(last_pos, background)
                last_pos = draw_circle()
                pygame.display.update()

            if event.type == pygame.QUIT:
                running = False
        key_event = pygame.key.get_pressed()
        if key_event[pygame.K_d]:
            draw_circle(last_pos, background)
            x, y = last_pos
            last_pos = draw_circle((x + 0.05, y))
            pygame.display.update()
        if key_event[pygame.K_a]:
            draw_circle(last_pos, background)
            x, y = last_pos
            last_pos = draw_circle((x - 0.05, y))
            pygame.display.update()
        if key_event[pygame.K_w]:
            draw_circle(last_pos, background)
            x, y = last_pos
            last_pos = draw_circle((x, y - 0.05))
            pygame.display.update()
        if key_event[pygame.K_s]:
            draw_circle(last_pos, background)
            x, y = last_pos
            last_pos = draw_circle((x, y + 0.05))
            pygame.display.update()


def get_pos():
    return pygame.mouse.get_pos()


def draw_circle(pos=None, color=BLUE):
    if pos is None:
        pos = get_pos()
    pygame.draw.circle(screen, color, pos, 20)
    return pos


if __name__ == "__main__":
    main(RED)
