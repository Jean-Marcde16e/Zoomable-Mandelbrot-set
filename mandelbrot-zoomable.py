import pygame
import numpy as np
from multiprocessing import Pool
import os

# The width and height variables can be adjusted for a larger/smaller screen
# The iterations can also be adjusted for more/less detail
# CAUTION: This greatly affects the loading time of the application
width, height = 400, 400
iterations = 128
zoom = 0.3
zoom_factor = 2
xas = 1 / zoom
yas = height / (width * zoom)
xOffset = (-xas / zoom_factor)
yOffset = (-yas / zoom_factor)
ratio = xas / width


# The rgb function colors pixels based on the depth and distance to the nearest point of the Mandelbrot set.
def rgb(x, y, rat, xOff, yOff, iter):
    breed = (x * rat) + xOff
    hoog = (y * rat) + yOff
    tempbreed = breed
    temphoog = hoog
    i = 0
    while breed * breed + hoog * hoog < 4 and i < iter:
        ixpix = breed * breed - hoog * hoog
        iypix = 2 * breed * hoog

        breed = ixpix + tempbreed
        hoog = iypix + temphoog
        i += 1

    intensiteit = i / iter

    r = int(255 * intensiteit) % 255
    g = int(255 * (intensiteit * intensiteit)) % 255
    b = int(255 * (-np.cos(np.pi * intensiteit) + 1) / 2) % 255

    return r, g, b


# The control function adjusts the screen based on the input
def control(mouse, button):
    global xOffset, yOffset, ratio, iterations
    if button == 4:  # zoom in
        ratio /= zoom_factor
        incx = mouse[0] * ratio
        incy = mouse[1] * ratio
        xOffset += incx
        yOffset += incy
    elif button == 5:  # zoom out
        decx = mouse[0] * ratio
        decy = mouse[1] * ratio
        ratio *= zoom_factor
        xOffset -= decx
        yOffset -= decy
    elif button == 3:  # close application
        global run
        run = False
    main()


# The process_chunk function calculates a portion of the pixels to be displayed on the screen
def process_chunk(chunk):
    x_start, x_end, y_start, y_end, ratio, xOffset, yOffset, iterations = chunk
    result = np.zeros((x_end - x_start, y_end - y_start, 3), dtype=np.uint8)
    for x in range(x_start, x_end):
        for y in range(y_start, y_end):
            result[x - x_start, y -
                   y_start] = rgb(x, y, ratio, xOffset, yOffset, iterations)
    return result


# The process function calculates which pixels the screen should display using the process_chunk function
def process():
    screen = pygame.display.set_mode((width, height))
    chunks = [(x, min(x + width // 4, width), 0, height, ratio, xOffset,
               yOffset, iterations) for x in range(0, width, width // 4)]

    with Pool() as pool:
        results = pool.map(process_chunk, chunks)

    img_array = np.concatenate(results, axis=0)
    pygame.surfarray.blit_array(screen, img_array)


# The main function updates the screen when the mouse is clicked.
def main():
    global run
    process()
    while run:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                control(pygame.mouse.get_pos(), event.button)
        pygame.display.update()
    pygame.display.quit()
    pygame.quit()
    exit()


# Start the game and display the pygame welcome message only once in the terminal
if __name__ == '__main__':
    # Hide pygame support prompt
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    run = True
    pygame.init()
    main()
