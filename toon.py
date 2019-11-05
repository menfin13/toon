import os
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from flask import Flask, send_file, request

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


def get_char_image(char_name):
    try:
        result = Image.open("cache/char_" + char_name + ".png")
    except:
        url = "https://swgoh.gg/game-asset/u/" + char_name
        response = requests.get(url)
        result = Image.open(BytesIO(response.content))
        ensure_cache_dir_exists()
        result.save("cache/char_" + char_name + ".png")
    return result


def generate_image(char, gear, stars, zetas_count, speed, relics_count):
    result = Image.new('RGBA', (150, 150), color=(0, 0, 0))

    toon = get_char_image(char)
    toon = toon.convert("RGBA")
    result.paste(toon, (11, 22), toon)

    gear_icon = Image.open("gear-icon-g" + str(gear) + ".png")
    result.paste(gear_icon, (11, 22), gear_icon)

    mask = Image.new('L', result.size, color=0)
    draw = ImageDraw.Draw(mask)
    transparent_area = (11, 22, 139, 150)
    draw.ellipse(transparent_area, fill=255)
    result.putalpha(mask)

    # ETOILES
    star1 = choose_star(1, stars).rotate(45)
    star2 = choose_star(2, stars).rotate(32)
    star3 = choose_star(3, stars).rotate(18)
    star4 = choose_star(4, stars).rotate(0)
    star5 = choose_star(5, stars).rotate(-18)
    star6 = choose_star(6, stars).rotate(-32)
    star7 = choose_star(7, stars).rotate(-45)
    result.paste(star1, (10, 26), star1)
    result.paste(star2, (25, 13), star2)
    result.paste(star3, (44, 4), star3)
    result.paste(star4, (64, 1), star4)
    result.paste(star5, (84, 4), star5)
    result.paste(star6, (103, 13), star6)
    result.paste(star7, (118, 26), star7)

    # ZETA
    if zetas_count > 0:
        zeta_img = Image.open("tex.skill_zeta.png")
        zeta_img = zeta_img.resize((60, 60))
        draw_zeta = ImageDraw.Draw(zeta_img)
        draw_zeta.text((25, 15), str(zetas_count), font=ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 18))
        result.paste(zeta_img, (0, 90), zeta_img)


    if relics_count > 0:
        relic_img = Image.open("relic_neutre.png")
        relic_img = relic_img.resize((54, 54))
        draw_relic = ImageDraw.Draw(relic_img)
        draw_relic.text((21, 15), str(relics_count), font=ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 19),
                        fill=(0, 0, 0, 255))
        draw_relic.text((22, 16), str(relics_count), font=ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 18),
                        fill=(255, 255, 255, 255))
        result.paste(relic_img, (90, 100), relic_img)

    # VITESSE
    if speed > 0:
        speed_img = Image.open("speed.png")
        speed_img = speed_img.resize((50, 50))
        draw_speed = ImageDraw.Draw(speed_img)
        draw_speed.text((9, 16), str(speed),
                        font=ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 16),
                        fill=(255, 0, 0, 255))
        result.paste(speed_img, (100, 60), speed_img)


    # gear text
    gear_text_img = Image.open("gear_text_back_" + str(gear) + ".png")
    gear_text_img = gear_text_img.resize((40, 35))
    draw_gear_text = ImageDraw.Draw(gear_text_img)
    roman_gear = toRoman(gear)
    shadow_fill = (0, 0, 0, 255)
    font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 16)
    x = 18 - len(roman_gear) * 3
    y = 10
    draw_gear_text.text((x-1, y-1), roman_gear, font=font, fill=shadow_fill)
    draw_gear_text.text((x+1, y-1), roman_gear, font=font, fill=shadow_fill)
    draw_gear_text.text((x-1, y+1), roman_gear, font=font, fill=shadow_fill)
    draw_gear_text.text((x+2, y+2), roman_gear, font=font, fill=shadow_fill)
    draw_gear_text.text((x, y), roman_gear, font=font, fill=(255, 255, 255, 255))
    result.paste(gear_text_img, (55, 115), gear_text_img)

    return result


def get_image(char, gear, stars, zetas_count, speed, relics_count):
    ensure_cache_dir_exists()
    cache_name = "cache/" + char + "_g" + str(gear) + "_" + str(stars) + "stars_" + str(zetas_count) + "zetas_" + str(
        speed) + "speed_" + str(relics_count)  + "relics" + ".png"
    try:
        result = Image.open(cache_name)
    except:
        result = generate_image(char, gear, stars, zetas_count, speed, relics_count)
        result.save(cache_name)
    return result


app = Flask(__name__)


@app.route('/toon/<char>')
def get_toon(char):
    gear = int(request.args.get('gear'))
    stars = int(request.args.get('stars'))
    if request.args.get('zetas') is not None:
        zetas = int(request.args.get('zetas'))
    else:
        zetas = 0
    if request.args.get('speed') is not None:
        speed = int(request.args.get('speed'))
    else:
        speed = 0
    if request.args.get('relics') is not None:
        relics = int(request.args.get('relics'))
    else:
        relics = 0
    byte_io = BytesIO()
    image = get_image(char, gear, stars, zetas, speed, relics)
    image.save(byte_io, 'PNG')
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/png')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
