from fractal_renderer import FractalRenderer


def main():
    # Создает и запускает рендер фракталов зубочисток
    renderer = FractalRenderer('config.json')
    renderer.run()


main()