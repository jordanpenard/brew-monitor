def lovibond_to_rgb(lovibond):
    # From http://brew-engine.com/engines/beer_color_calculator.html

    srm = (1.3546 * lovibond) - 0.76

    r = 0
    g = 0
    b = 0

    if 0 <= srm <= 1:
        r = 240
        g = 239
        b = 181

    elif 1 < srm <= 2:
        r = 233
        g = 215
        b = 108

    elif srm > 2:
        # Set red decimal
        if srm < 70.6843:
            r = 243.8327 - 6.4040 * srm + 0.0453 * srm * srm
        else:
            r = 17.5014

        # Set green decimal
        if srm < 35.0674:
            g = 230.929 - 12.484 * srm + 0.178 * srm * srm
        else:
            g = 12.0382

        # Set blue decimal
        if srm < 4:
            b = -54 * srm + 216
        elif 4 <= srm < 7:
            b = 0
        elif 7 <= srm < 9:
            b = 13 * srm - 91
        elif 9 <= srm < 13:
            b = 2 * srm + 8
        elif 13 <= srm < 17:
            b = -1.5 * srm + 53.5
        elif 17 <= srm < 22:
            b = 0.6 * srm + 17.8
        elif 22 <= srm < 27:
            b = -2.2 * srm + 79.4
        elif 27 <= srm < 34:
            b = -0.4285 * srm + 31.5714
        else:
            b = 17

    return "rgb(" + str(r) + ", " + str(g) + ", " + str(b) + ")"


def og_from_grain_bill(grain_bill, batch_size_l):
    # PPG = grain gravity points per pound per gallon
    # PTS = PPG * grain weight in pound * efficiency
    # OG = PTS / batch size in gallon

    efficiency = 0.7
    batch_size_g = batch_size_l * 0.219969
    pts = 0

    total_weight = 0
    total_dp = 0
    for grain_recipe in grain_bill:
        ppg = grain_recipe.grain.ppg
        grain_weight_lbs = grain_recipe.quantity_g * 0.00220462
        pts += ppg * grain_weight_lbs * efficiency

        total_dp += grain_recipe.grain.diastatic_power * grain_recipe.quantity_g
        total_weight += grain_recipe.quantity_g

    if batch_size_g == 0:
        return 1
    else:
        return 1 + (pts / batch_size_g) / 1000


def color_l_from_grain_bill(grain_bill):
    total_weight = 0
    total_color = 0
    for grain_recipe in grain_bill:
        total_color += grain_recipe.grain.color_lovibond * grain_recipe.quantity_g
        total_weight += grain_recipe.quantity_g

    if total_weight == 0:
        return 0
    else:
        return total_color / total_weight


def dp_from_grain_bill(grain_bill):
    total_weight = 0
    total_dp = 0
    for grain_recipe in grain_bill:
        total_dp += grain_recipe.grain.diastatic_power * grain_recipe.quantity_g
        total_weight += grain_recipe.quantity_g

    if total_weight == 0:
        return 0
    else:
        return total_dp / total_weight


def ibu_from_hop_bill(hop_bill, batch_size_l, og):
    # Tinseth’s IBU Formula (https://homebrewacademy.com/ibu-calculator/)
    #
    # AAU = Weight of hops (g) * % Alpha Acid rating of the hops * 1000
    # Bigness factor = 1.65 * 0.000125^(wort gravity – 1)
    # Boil Time factor = (1 – e^(-0.04 * time in mins) )/4.15
    # U = Bigness Factor * Boil Time Factor
    # IBU = AAU x U / Vol (l)

    ibu = 0

    for hop_recipe in hop_bill:
        if not hop_recipe.dry_hop:
            aau = hop_recipe.quantity_g * hop_recipe.hop.alpha_acid * 10
            bf = 1.65 * 0.000125 ** (og - 1)
            btf = (1 - 2.71828 ** (-0.04 * hop_recipe.time_min)) / 4.15
            hop_ibu = aau * bf * btf / batch_size_l

            # Pellet provides a 10% IBU increase
            if not hop_recipe.hop.whole_not_pellet:
                hop_ibu += 0.1 * hop_ibu

            ibu += hop_ibu
    return ibu


def compute_abv(og, fg):
    return (og - fg) * 131.25
