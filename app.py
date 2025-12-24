import pygame
import sys
import os

WIDTH = 400
HEIGHT = 600
FPS = 60

ASSETS_DIR = "assets"
BACK_IMAGE = "ui/background.png"

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("고양이 키우기")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.bg_color = (240, 240, 240)

        self.back_image = self.load_image(BACK_IMAGE)
        self.back_image = pygame.transform.scale(self.back_image, (WIDTH, HEIGHT))
        self.back_rect = self.back_image.get_rect()
        self.back_rect.topleft = (0, 0)

    def load_image(self, filename):
        path = os.path.join(ASSETS_DIR, filename)
        try:
            image = pygame.image.load(path).convert_alpha()
            return image
        except pygame.error as e:
            print(f"[ERROR] 이미지 로드 실패: {path}")
            print(e)
            pygame.quit()
            sys.exit()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.draw()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def draw(self):
        self.screen.fill(self.bg_color)

        self.screen.blit(self.back_image, self.back_rect)

        pygame.display.flip()


if __name__ == "__main__":
    Game().run()
