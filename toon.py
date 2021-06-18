import os
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from flask import Flask, send_file, request
from unit_parameters import CharParameters, ShipParameters

# http://localhost:5000/toon/ewok_paploo?gear=10&stars=2&zetas=3
# https://menfin-swgoh.herokuapp.com/toon/ewok_paploo?gear=10&stars=2&zetas=3

romanNumeralMap = (('M', 1000),
                   ('CM', 900),
                   ('D', 500),
                   ('CD', 400),
                   ('C', 100),
                   ('XC', 90),
                   ('L', 50),
                   ('XL', 40),
                   ('X', 10),
                   ('IX', 9),
                   ('V', 5),
                   ('IV', 4),
                   ('I', 1))


def toRoman(n):
    if not (0 < n < 5000):
        raise OutOfRangeError("number out of range (must be 1..4999)")
    if int(n) != n:
        raise NotIntegerError("decimals can not be converted")

    result = ""
    for numeral, integer in romanNumeralMap:
        while n >= integer:
            result += numeral
            n -= integer
    return result


star_active = Image.open("star.png")
star_inactive = Image.open("star-inactive.png")


def choose_star(current_star, toon_stars):
    if current_star <= toon_stars:
        return star_active
    else:
        return star_inactive


def ensure_cache_dir_exists():
    if not os.path.exists("cache"):
        os.makedirs("cache")


def get_asset_image(unit_name):
    try:
        result = Image.open("cache/asset_" + unit_name + ".png")
    except:
        url = "https://swgoh.gg/game-asset/u/" + unit_name + ".png"
        response = requests.get(url)
        result = Image.open(BytesIO(response.content))
        ensure_cache_dir_exists()
        result.save("cache/asset_" + unit_name + ".png")
    return result


class ImageGenerator:
    def generate(self, params):
        pass


class ToonImageGenerator(ImageGenerator):
    def generate(self, params):
        result = Image.new('RGBA', (150, 150), color=(0, 0, 0))

        toon = get_asset_image(params.char_id)
        toon = toon.convert("RGBA")
        toon = toon.resize((128, 128))
        result.paste(toon, (11, 22), toon)

        mask = Image.new('L', result.size, color=0)
        draw = ImageDraw.Draw(mask)
        transparent_area = (11, 22, 139, 150)
        draw.ellipse(transparent_area, fill=255)
        result.putalpha(mask)

        gear_icon = Image.open("gear-icon-g" + params.get_gear_str() + ".png")
        if params.is_sided():
            result.paste(gear_icon, (0, 12), gear_icon)
        else:
            result.paste(gear_icon, (11, 22), gear_icon)

        # ETOILES
        star1 = choose_star(1, params.stars).rotate(45)
        star2 = choose_star(2, params.stars).rotate(32)
        star3 = choose_star(3, params.stars).rotate(18)
        star4 = choose_star(4, params.stars).rotate(0)
        star5 = choose_star(5, params.stars).rotate(-18)
        star6 = choose_star(6, params.stars).rotate(-32)
        star7 = choose_star(7, params.stars).rotate(-45)
        result.paste(star1, (10, 26), star1)
        result.paste(star2, (25, 13), star2)
        result.paste(star3, (44, 4), star3)
        result.paste(star4, (64, 1), star4)
        result.paste(star5, (84, 4), star5)
        result.paste(star6, (103, 13), star6)
        result.paste(star7, (118, 26), star7)

        # ZETA
        if params.zetas > 0:
            zeta_img = Image.open("tex.skill_zeta.png")
            zeta_img = zeta_img.resize((60, 60))
            draw_zeta = ImageDraw.Draw(zeta_img)
            draw_zeta.text((25, 15), str(params.zetas),
                           font=ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 18))
            result.paste(zeta_img, (0, 90), zeta_img)

        if params.relics > 0:
            filename = "relic"
            if params.side is not None:
                filename = filename + params.side
            relic_img = Image.open(filename + ".png")
            relic_img = relic_img.resize((54, 54))
            draw_relic = ImageDraw.Draw(relic_img)
            draw_relic.text((21, 15), str(params.relics),
                            font=ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 19),
                            fill=(0, 0, 0, 255))
            draw_relic.text((22, 16), str(params.relics),
                            font=ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 18),
                            fill=(255, 255, 255, 255))
            result.paste(relic_img, (50, 100), relic_img)

        # VITESSE
        if params.speed > 0:
            speed_img = Image.open("speed.png")
            speed_img = speed_img.resize((50, 50))
            draw_speed = ImageDraw.Draw(speed_img)
            draw_speed.text((9, 16), str(params.speed),
                            font=ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 16),
                            fill=(255, 0, 0, 255))
            result.paste(speed_img, (100, 60), speed_img)

        # gear text
        if params.gear < 13:
            gear_text_img = Image.open("gear_text_back_" + str(params.gear) + ".png")
            gear_text_img = gear_text_img.resize((40, 35))
            draw_gear_text = ImageDraw.Draw(gear_text_img)
            roman_gear = toRoman(params.gear)
            shadow_fill = (0, 0, 0, 255)
            font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 16)
            x = 18 - len(roman_gear) * 3
            y = 10
            draw_gear_text.text((x - 1, y - 1), roman_gear, font=font, fill=shadow_fill)
            draw_gear_text.text((x + 1, y - 1), roman_gear, font=font, fill=shadow_fill)
            draw_gear_text.text((x - 1, y + 1), roman_gear, font=font, fill=shadow_fill)
            draw_gear_text.text((x + 2, y + 2), roman_gear, font=font, fill=shadow_fill)
            draw_gear_text.text((x, y), roman_gear, font=font, fill=(255, 255, 255, 255))
            result.paste(gear_text_img, (55, 115), gear_text_img)

        return result


class ShipImageGenerator(ImageGenerator):
    def generate(self, params):
        result = Image.new('RGBA', (414, 256), color=(0, 0, 0))

        ship = get_asset_image(params.ship_id)
        ship = ship.convert("RGBA")
        ship = ship.resize((406, 406))
        result.paste(ship, (5, -75), ship)

        frame = Image.open("ship-frame.png")
        result.paste(frame, (0, 0), frame)

        if params.has_char1():
            toon = ToonImageGenerator().generate(params.char_params[0])
            toon = toon.resize((150, 150))
            result.paste(toon, (10, 90), toon)

        if params.has_char2():
            toon = ToonImageGenerator().generate(params.char_params[1])
            toon = toon.resize((100, 100))
            result.paste(toon, (165, 140), toon)

        if params.has_char3():
            toon = ToonImageGenerator().generate(params.char_params[2])
            toon = toon.resize((100, 100))
            result.paste(toon, (260, 140), toon)

        # ETOILES
        star1 = choose_star(1, params.stars)
        star2 = choose_star(2, params.stars)
        star3 = choose_star(3, params.stars)
        star4 = choose_star(4, params.stars)
        star5 = choose_star(5, params.stars)
        star6 = choose_star(6, params.stars)
        star7 = choose_star(7, params.stars)
        result.paste(star1, (50, 13), star1)
        result.paste(star2, (100, 13), star2)
        result.paste(star3, (150, 13), star3)
        result.paste(star4, (200, 13), star4)
        result.paste(star5, (250, 13), star5)
        result.paste(star6, (300, 13), star6)
        result.paste(star7, (350, 13), star7)

        # VITESSE
        if params.speed > 0:
            draw_speed = ImageDraw.Draw(result)
            draw_speed.text((360, 215), str(params.speed),
                            font=ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 24),
                            fill=(255, 255, 255, 255))

        return result


def get_image(params, generator):
    ensure_cache_dir_exists()
    cache_name = "cache/" + params.get_hash() + ".png"
    try:
        result = Image.open(cache_name)
        print("Image found in cache: " + cache_name)
    except:
        print("Not found in cache, generate image")
        result = generator.generate(params)
        result.save(cache_name)
    return result


app = Flask(__name__)


@app.route('/toon/<char>')
def get_toon(char):
    params = CharParameters(char, request.args)
    byte_io = BytesIO()
    image = get_image(params, ToonImageGenerator())
    image.save(byte_io, 'PNG')
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/png')


@app.route('/ship/<ship>')
def get_ship(ship):
    params = ShipParameters(ship, request.args)
    byte_io = BytesIO()
    image = get_image(params, ShipImageGenerator())
    image.save(byte_io, 'PNG')
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/png')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
