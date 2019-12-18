# Heavily modified from https://www.pygame.org/project/1035/1838, hence the following license.
# This seemed a good idea at the time, but in retrospect wasn't.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from random import randint

import pygame


class Spinner:
    def __init__(self, screen, origin):

        # Set members
        self.screen = screen
        self.origin = origin
        self.shadow = pygame.image.load("images/shadow.png")

        # Maximum number of times we will fully spin the reel. This will limit the size of the reel surface we need.
        self.max_spins = 30

        # Load icons
        icons = [pygame.image.load("images/toaster.png").convert_alpha(),
                 pygame.image.load("images/kettle.png").convert_alpha(),
                 pygame.image.load("images/fax-machine.png").convert_alpha(),
                 pygame.image.load("images/patch-panel.png").convert_alpha(),
                 pygame.image.load("images/watering-can-icon.png").convert_alpha(),
                 pygame.image.load("images/tv.png").convert_alpha(),
                 pygame.image.load("images/etch-a-sketch.png").convert_alpha(),
                 pygame.image.load("images/cii.png").convert_alpha()]
        self.num_icons = len(icons)

        # Build surface for reel. We draw the reel as a moving window over a long sequence of repeated icons.
        # We repeat each cycle through the icons so that we have lots available in the surface
        # and we don't risk running out. This means we can ignore annoying boundary conditions providing we don't
        # spin too far.
        self.reel = pygame.Surface((128, 128 * self.num_icons * self.max_spins), pygame.SRCALPHA)
        self.reel.fill((255, 255, 255))
        self.reel.blit(icons[0], (0, 0))
        for i in range(self.max_spins):
            for j in range(self.num_icons):
                self.reel.blit(icons[j], (0, 128 * ((i * self.num_icons) + j)))

        # Initial view
        pygame.draw.rect(self.screen, (255, 255, 255),
                         (self.origin[0], self.origin[1], 128, 128 * 3))  # white background
        rect = self.screen.blit(self.reel, self.origin, (0, 0, 128, 128 * 3))  # icons
        self.screen.blit(self.shadow, self.origin)  # shadow
        pygame.display.update(rect)

    def spin(self):
        # How many times will we advance the reel by one icon?
        # TODO: there is an interesting bug here
        turns = randint(self.num_icons, (self.max_spins - 1) * self.num_icons)
        print(turns)  # debugging

        speed = 10  # How quickly to spin
        for i in range(0, 128 * turns, speed):
            pygame.draw.rect(self.screen, (255, 255, 255),
                             (self.origin[0], self.origin[1], 128, 128 * 3))  # white background
            rect = self.screen.blit(self.reel, self.origin, (0, i, 128, 128 * 3))  # icons
            self.screen.blit(self.shadow, self.origin)  # shadow
            pygame.display.update(rect)

        # Return the index of the selected icon
        return turns % self.num_icons


# Simple class to generate a random phrase from a list of provided options
class TextGenerator:
    def __init__(self, phrases):
        self.phrases = phrases

    def get_phrase(self):
        return self.phrases[randint(0, len(self.phrases)) - 1]


class Game:
    def __init__(self, screen):

        self.screen = screen

        # Font for drawing text
        self.font = pygame.font.SysFont("comicsansms", 36)

        # Draw border/background
        self.border = pygame.image.load("images/border.png")
        self.screen.fill([0, 0, 0])
        self.screen.blit(self.border, (0, 0))
        pygame.display.update()

        # Create three spinners at the specified locations
        self.spinners = [Spinner(screen, (36, 46)),
                         Spinner(screen, (166, 46)),
                         Spinner(screen, (296, 46))]

        # Create phrase generators
        self.winningPhrases = TextGenerator([
            "You win - go into M127",
            "You win - no queue in Skyways",
            "You win - another coding competition"
        ])
        self.losingPhrases = TextGenerator([
            "You lose - talk to James about STANAG 4559 Ed 4",
            "You lose - talk to James about Silicon Graphics",
            "You lose - talk to Matt about sheds",
            "You lose - talk to Stu about football",
            "You lose - talk to Martin about agile",
            "You lose - talk to Nigel about screwdrivers",
            "You lose - talk to security about... anything",
        ])

        # Main loop...
        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYDOWN:

                    # Space bar pressed...
                    if event.key == pygame.K_SPACE:

                        # Initialise view to blat out any previous text and spinners
                        self.screen.fill([0, 0, 0])
                        self.screen.blit(self.border, (0, 0))
                        pygame.display.update()

                        # Spin each spinner in turn
                        results = []
                        for spinner in self.spinners:
                            results.append(spinner.spin())

                        # Debugging
                        print(results)

                        if len(set(results)) == 1:
                            # All the same = win ;-)
                            self.winner()
                        else:
                            # Some different = lose :-(
                            self.loser()

    def winner(self):
        self._show_text(self.winningPhrases.get_phrase())

    def loser(self):
        self._show_text(self.losingPhrases.get_phrase())

    def _show_text(self, phrase):
        self._draw_text(phrase, (0, 0, 0), (35, 45, 380, 450), self.font)  # Shadow
        self._draw_text(phrase, (0, 255, 255), (36, 46, 380, 450), self.font)  # Text
        pygame.display.update()

    # From https://www.pygame.org/wiki/TextWrap
    def _draw_text(self, text, color, rect, font, aa=True, bkg=None):
        rect = pygame.Rect(rect)
        y = rect.top
        line_spacing = -2

        # get the height of the font
        font_height = font.size("Tg")[1]

        while text:
            i = 1

            # determine if the row of text will be outside our area
            if y + font_height > rect.bottom:
                break

            # determine maximum width of line
            while font.size(text[:i])[0] < rect.width and i < len(text):
                i += 1

            # if we've wrapped the text, then adjust the wrap to the last word
            if i < len(text):
                i = text.rfind(" ", 0, i) + 1

            # render the line and blit it to the surface
            if bkg:
                image = font.render(text[:i], 1, color, bkg)
                image.set_colorkey(bkg)
            else:
                image = font.render(text[:i], aa, color)

            self.screen.blit(image, (rect.left, y))
            y += font_height + line_spacing

            # remove the text we just blitted
            text = text[i:]

        return text


# Main entry point
if __name__ == "__main__":
    # pygame setup
    pygame.init()
    pygame.display.set_caption("CII Fruit Machine Game")
    pygame.mouse.set_visible(False)

    # Run the game!
    Game(pygame.display.set_mode([460, 480], 0, 32))
