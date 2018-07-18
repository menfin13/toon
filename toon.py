import os
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from flask import Flask, send_file, request

#http://localhost:5000/toon?char=ewok_paploo&gear=10&stars=2&zetas=3
#menfin.pythonanywhere.com/toon?char=ewok_paploo&gear=10&stars=2&zetas=3

star_active = Image.open("star.png")
star_inactive = Image.open("star-inactive.png")

def choose_star(current_star, toon_stars):
    if current_star <= toon_stars:
        return star_active
    else:
        return star_inactive

def get_char_image(char_name):
    url = "https://swgoh.gg/static/img/assets/tex.charui_" + char_name + ".png"
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

def generate_image(char, gear, stars, zetas_count):
    result = Image.new('RGB', (150, 150), color=(0, 0, 0))

    toon = get_char_image(char)
    result.paste(toon, (11, 22), toon)

    gear_icon = Image.open("gear-icon-g" + str(gear) + ".png")
    result.paste(gear_icon, (11, 22), gear_icon)

    mask = Image.new('L', result.size, color=0)
    draw = ImageDraw.Draw(mask)
    transparent_area = (11,22,139,150)
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

    draw_gear = ImageDraw.Draw(result)

#    draw_gear.text((75, 75), "XI", font=ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf", 15))

    return result


app = Flask(__name__)

@app.route('/toon')
def get_toon():
    char = request.args.get('char')
    gear = int(request.args.get('gear'))
    stars = int(request.args.get('stars'))
    zetas = int(request.args.get('zetas'))
    byte_io = BytesIO()
    image = generate_image(char, gear, stars, zetas)
    image.save(byte_io, 'PNG')
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/png')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, port=port)
