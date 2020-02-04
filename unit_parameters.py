from werkzeug.datastructures import MultiDict


class UnitParameters:
    def __init__(self):
        pass


class CharParameters:
    def __init__(self, char_id, args):
        self.char_id = char_id
        self.gear = int(args.get('gear'))
        self.stars = int(args.get('stars'))
        self.zetas = int(args.get('zetas')) if args.get('zetas') is not None else 0
        self.speed = int(args.get('speed')) if args.get('speed') is not None else 0
        self.relics = int(args.get('relics')) if args.get('relics') is not None else 0
        self.side = args.get('side')

    def get_hash(self):
        return self.char_id \
               + "_g" + str(self.gear) \
               + "_" + str(self.stars) + "stars_" \
               + str(self.zetas) + "zetas_" \
               + str(self.speed) + "speed_" \
               + str(self.relics) + "relics_" \
               + (self.side if self.side is not None else '')

    def is_sided(self):
        return self.gear == 13 and self.side is not None

    def get_gear_str(self):
        return str(self.gear) + (self.side if self.is_sided() else '')


class ShipParameters:
    def __init__(self, ship_id, args):
        self.char_params = []
        self.ship_id = ship_id
        self.stars = int(args.get('stars'))
        self.speed = int(args.get('speed')) if args.get('speed') is not None else 0

        for i in range(1, 4):
            param = CharParameters(args.get('c' + str(i)), self.get_char_args(args, i)) \
                if args.get('c' + str(i)) is not None else None
            self.char_params.append(param)

    @staticmethod
    def get_char_args(args, index):
        return MultiDict([
            ('gear', args.get('gc' + str(index))),
            ('stars', args.get('sc' + str(index))),
            ('zetas', args.get('zc' + str(index))),
            ('speed', args.get('speed_c' + str(index))),
            ('relics', args.get('rc' + str(index))),
            ('side', args.get('side_c' + str(index)))
        ])

    def get_hash(self):
        result = self.ship_id + "_" + str(self.stars) + "stars_" + str(self.speed) + "speed_"
        for i in range(3):
            result = result + (self.char_params[i].get_hash() + "_" if self.char_params[i] is not None else "")
        return result

    def has_char2(self):
        return self.char_params[1] is not None

    def has_char3(self):
        return self.char_params[2] is not None
