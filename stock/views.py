from django.shortcuts import render, redirect, get_object_or_404
from .models import Ingredient, Grain, Hop, Yeast, Stock, Recipe, GrainRecipe, HopRecipe, Brew
from monitor.models import Project, Sensor
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


def index(request):
    return render(request, 'index.html')


def stock(request):
    # Filtering the list of ingredients so the list to add a new entry in the stock only shows ingredients that aren't yet in the stock
    used_ingredients = Stock.objects.filter(owner=request.user).values_list("ingredient", flat=True)

    context = {'grain_stock': Stock.objects.filter(owner=request.user, ingredient__in=Grain.objects.all()),
               'grain_unused_ingredients': Grain.objects.all().exclude(pk__in=used_ingredients),
               'hop_stock': Stock.objects.filter(owner=request.user, ingredient__in=Hop.objects.all()),
               'hop_unused_ingredients': Hop.objects.all().exclude(pk__in=used_ingredients),
               'yeast_stock': Stock.objects.filter(owner=request.user, ingredient__in=Yeast.objects.all()),
               'yeast_unused_ingredients': Yeast.objects.all().exclude(pk__in=used_ingredients)}
    return render(request, 'stock.html', context)


@login_required()
@require_POST
def add_stock(request):
    ingredient = request.POST['ingredient']
    quantity_g = request.POST['quantity_g']

    new_entry = Stock(ingredient=Ingredient.objects.get(pk=ingredient), quantity_g=quantity_g, owner=request.user)
    new_entry.save()
    return redirect("stock")


@login_required()
@require_POST
def edit_stock(request):
    pk = request.POST['pk']
    quantity_g = request.POST['quantity_g']

    Stock.objects.filter(pk=pk, owner=request.user).update(quantity_g=quantity_g)
    return redirect("stock")


def ingredients(request):
    context = {'grain': Grain.objects.all(), 'hop': Hop.objects.all(), 'yeast': Yeast.objects.all()}
    return render(request, 'ingredients.html', context)


@login_required()
@require_POST
def add_ingredients(request):
    name = request.POST['name']
    if request.POST['ingredient_type'] == "yeast":
        liquid_not_dry = request.POST['liquid_not_dry']

        new_entry = Yeast(name=name, liquid_not_dry=liquid_not_dry)
        new_entry.save()

    elif request.POST['ingredient_type'] == "hop":
        alpha_acid = request.POST['alpha_acid']
        whole_not_pellet = request.POST['whole_not_pellet']

        new_entry = Hop(name=name, alpha_acid=alpha_acid, whole_not_pellet=whole_not_pellet)
        new_entry.save()

    elif request.POST['ingredient_type'] == "grain":
        color_lovibond = request.POST['color_lovibond']
        ppg = request.POST['ppg']
        diastatic_power = request.POST['diastatic_power']

        new_entry = Grain(name=name, color_lovibond=color_lovibond, ppg=ppg, diastatic_power=diastatic_power)
        new_entry.save()

    else:
        messages.error(request, "Malformed request")

    return redirect("ingredients")


def get_recipe_stock_check(request, current_recipe):
    if not request.user.is_authenticated:
        return []

    stock_checker = []

    for grain_recipe in GrainRecipe.objects.filter(recipe=current_recipe.pk):
        quantity_in_stock_g = 0
        try:
            quantity_in_stock_g = Stock.objects.get(owner=request.user, ingredient=grain_recipe.grain).quantity_g
        except:
            pass

        data = {"name": str(grain_recipe.grain),
                "quantity_needed_g": grain_recipe.quantity_g,
                "quantity_in_stock_g": quantity_in_stock_g}
        stock_checker.append(data)

    for ret in HopRecipe.objects.filter(recipe=current_recipe.pk).values('hop').distinct().annotate(quantity_needed_g=Sum('quantity_g')):
        hop = ret["hop"]

        quantity_in_stock_g = 0
        try:
            quantity_in_stock_g = Stock.objects.get(owner=request.user, ingredient=hop).quantity_g
        except:
            pass

        data = {"name": str(Hop.objects.get(pk=hop)),
                "quantity_needed_g": ret["quantity_needed_g"],
                "quantity_in_stock_g": quantity_in_stock_g}
        stock_checker.append(data)

    return stock_checker


def is_everything_in_stock(request, current_recipe):
    status = True
    for item in get_recipe_stock_check(request, current_recipe):
        if item["quantity_needed_g"] > item["quantity_in_stock_g"]:
            status = False

    return status


def recipe(request):
    context = {'recipes': Recipe.objects.all().order_by("-pk"),
               'grain_recipes': GrainRecipe.objects.all(),
               'hop_recipes': HopRecipe.objects.all(),
               'yeasts': Yeast.objects.all()}
    return render(request, 'recipe.html', context)


@login_required()
@require_POST
def add_recipe(request):
    recipe_name = request.POST["name"]
    new_entry = Recipe(owner=request.user, name=recipe_name)
    new_entry.save()

    return redirect("edit_recipe", pk=new_entry.pk)

@login_required()
@require_POST
def delete_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.user == recipe.owner:
        recipe.delete()
    return redirect("recipe")


@login_required()
@require_POST
def delete_brew(request, pk):
    brew = get_object_or_404(Brew, pk=pk)
    if request.user == brew.owner:
        brew.delete()
    return redirect("brew")

@login_required()
@require_POST
def delete_stock_entry(request, pk):
    entry = get_object_or_404(Stock, pk=pk)
    if request.user == entry.owner:
        entry.delete()
    return redirect("stock")


def edit_recipe(request, pk):
    current_recipe = Recipe.objects.get(pk=pk)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        if current_recipe.owner != request.user:
            messages.error(request, "You can't edit someone else's recipe")
            return redirect("edit_recipe", pk)

        current_recipe.name = request.POST['name']
        current_recipe.mash_temperature_c = request.POST['mash_temperature_c']
        current_recipe.fermentation_temperature_c = request.POST['fermentation_temperature_c']
        current_recipe.batch_size_l = request.POST['batch_size_l']
        current_recipe.yeast = Yeast.objects.get(pk=request.POST['yeast'])
        current_recipe.comments = request.POST['comments']
        current_recipe.save()
        return redirect("edit_recipe", pk)

    else:
        if not request.user.is_authenticated or current_recipe.owner != request.user:
            messages.warning(request, "Read only as someone else owns this recipe")
            read_only = True
        else:
            read_only = False

        used_grains = GrainRecipe.objects.filter(recipe=pk).values_list("grain")

        grain_recipes = GrainRecipe.objects.filter(recipe=pk)
        total_grain_bill_g = sum([recipe.quantity_g for recipe in grain_recipes])

        context = {'recipe': current_recipe,
                   'read_only': read_only,
                   'disabled': "disabled" if read_only else "",
                   'grain_recipes': grain_recipes,
                   'total_grain_bill_g': total_grain_bill_g,
                   'hop_recipes': HopRecipe.objects.filter(recipe=pk).order_by('-time_min', 'dry_hop'),
                   'all_grain': Grain.objects.all(),
                   'all_hop': Hop.objects.all(),
                   'unused_grain': Grain.objects.all().exclude(pk__in=used_grains),
                   'all_yeast': Yeast.objects.all(),
                   'stock_checker': get_recipe_stock_check(request, current_recipe)}
        return render(request, 'edit_recipe.html', context)

@login_required()
def clone_recipe(request, pk):
    ref_recipe = Recipe.objects.get(pk=pk)
    new_recipe = Recipe(owner=request.user, name=f"{ref_recipe.name} clone", 
                        batch_size_l=ref_recipe.batch_size_l, 
                        comments=ref_recipe.comments, yeast=ref_recipe.yeast, 
                        mash_temperature_c=ref_recipe.mash_temperature_c, 
                        fermentation_temperature_c=ref_recipe.fermentation_temperature_c, 
                        boil_time_min=ref_recipe.boil_time_min)
    new_recipe.save()

    for ref_grain_recipe in GrainRecipe.objects.filter(recipe=ref_recipe):
        new_grain_recipe = GrainRecipe(recipe=new_recipe, grain=ref_grain_recipe.grain, 
                                       quantity_g=ref_grain_recipe.quantity_g)
        new_grain_recipe.save()

    for ref_hop_recipe in HopRecipe.objects.filter(recipe=ref_recipe):
        new_hop_recipe = HopRecipe(recipe=new_recipe, hop=ref_hop_recipe.hop, 
                                   quantity_g=ref_hop_recipe.quantity_g, 
                                   time_min=ref_hop_recipe.time_min,
                                   dry_hop=ref_hop_recipe.dry_hop)
        new_hop_recipe.save()

    return redirect("edit_recipe", new_recipe.pk)


@login_required()
def add_grain(request, pk):
    current_recipe = Recipe.objects.get(pk=pk)
    if current_recipe.owner != request.user:
        messages.error(request, "You can't edit someone else's recipe")
        return redirect("edit_recipe", pk)

    if request.method != "POST":
        return redirect("recipe")

    grain = request.POST['grain']
    quantity_g = request.POST['quantity_g']

    new_entry = GrainRecipe(recipe=current_recipe, grain=Grain.objects.get(pk=grain), quantity_g=quantity_g)
    new_entry.save()

    return redirect("edit_recipe", pk)


@login_required()
def add_hop(request, pk):
    current_recipe = Recipe.objects.get(pk=pk)
    if current_recipe.owner != request.user:
        messages.error(request, "You can't edit someone else's recipe")
        return redirect("edit_recipe", pk)

    if request.method != "POST":
        return redirect("recipe")

    hop = request.POST['hop']
    quantity_g = request.POST['quantity_g']
    time_min = request.POST['time_min']

    if request.POST.get('dry_hop', False):
        dry_hop = True
        time_min = 0
    else:
        dry_hop = False

    new_entry = HopRecipe(recipe=current_recipe, hop=Hop.objects.get(pk=hop), quantity_g=quantity_g, time_min=time_min, dry_hop=dry_hop)
    new_entry.save()

    return redirect("edit_recipe", pk)


@login_required()
def edit_grain(request, pk):
    current_recipe = GrainRecipe.objects.get(pk=pk)
    if current_recipe.recipe.owner != request.user:
        messages.error(request, "You can't edit someone else's recipe")
        return redirect("edit_recipe", current_recipe.recipe.pk)

    if request.method != "POST":
        return redirect("recipe")

    if request.POST['quantity_g'] == "0":
        current_recipe.delete()
    else:
        current_recipe.grain = Grain.objects.get(pk=request.POST['grain'])
        current_recipe.quantity_g = request.POST['quantity_g']
        current_recipe.save()

    return redirect("edit_recipe", pk=current_recipe.recipe.pk)


@login_required()
def edit_hop(request, pk):
    current_recipe = HopRecipe.objects.get(pk=pk)
    if current_recipe.recipe.owner != request.user:
        messages.error(request, "You can't edit someone else's recipe")
        return redirect("edit_recipe", current_recipe.recipe.pk)

    if request.method != "POST":
        return redirect("recipe")

    if request.POST['quantity_g'] == "0":
        current_recipe.delete()
    else:
        current_recipe.hop = Hop.objects.get(pk=request.POST['hop'])
        current_recipe.quantity_g = request.POST['quantity_g']
        current_recipe.time_min = request.POST['time_min']

        if request.POST.get('dry_hop', False):
            current_recipe.dry_hop = True
            current_recipe.time_min = 0
        else:
            current_recipe.dry_hop = False

        current_recipe.save()

    return redirect("edit_recipe", pk=current_recipe.recipe.pk)


def brew(request):

    context = {'brews': Brew.objects.all().order_by("-pk")}

    return render(request, 'brew.html', context)


@login_required()
def new_brew(request, recipe_pk):
    new_entry = Brew(recipe=Recipe.objects.get(pk=recipe_pk), owner=request.user)
    new_entry.save()
    new_entry.name = new_entry.recipe.name
    new_entry.save()

    return redirect("edit_brew", pk=new_entry.pk)


def edit_brew(request, pk):
    current_brew = Brew.objects.get(pk=pk)
    projects = Project.objects.order_by("-pk").all()
    available_sensors = Sensor.objects.all()

    grain_mass_g = 0
    for grain in GrainRecipe.objects.filter(recipe=current_brew.recipe):
        grain_mass_g += grain.quantity_g

    mash_volume_l = current_brew.mash_thickness_lpkg * grain_mass_g/1000
    evaporation_l = current_brew.evaporation_lph * current_brew.recipe.boil_time_min/60
    grain_absorption_l = grain_mass_g/1000
    target_pre_boil_volume_l = current_brew.recipe.batch_size_l + evaporation_l
    target_pre_sparge_volume_l = mash_volume_l - grain_absorption_l
    sparge_volume_l = target_pre_boil_volume_l - target_pre_sparge_volume_l

    target_pre_boil_gravity = 1 + (float(current_brew.recipe.stats()['og'])-1) * (current_brew.recipe.batch_size_l/target_pre_boil_volume_l)

    # Mash strike temperature is the temperature at which the water needs to be so once we added the grain we hit
    #  our target mash temperature (Assuming the grains are at 18 degree C)
    # Formula from https://homebrewanswers.com/document/calculating-strike-water-temperature-for-mashing
    mash_strike_temperature_c = (0.41/current_brew.mash_thickness_lpkg) * (current_brew.recipe.mash_temperature_c - 18) + current_brew.recipe.mash_temperature_c

    total_mash_mass_kg = (grain_mass_g/1000)+mash_volume_l
    sparge_strike_temperature_c = (current_brew.mash_out_temp_c * (total_mash_mass_kg+sparge_volume_l) - total_mash_mass_kg * current_brew.recipe.mash_temperature_c)/sparge_volume_l

    if current_brew.pre_boil_volume_l > 0:
        estimated_volume_l = current_brew.pre_boil_volume_l - evaporation_l
        estimated_og = 1 + current_brew.pre_boil_volume_l * (current_brew.pre_boil_gravity - 1) / estimated_volume_l
    else:
        estimated_og = float(current_brew.recipe.stats()['og'])
        estimated_volume_l = current_brew.recipe.batch_size_l

    if not request.user.is_authenticated or current_brew.owner != request.user:
        messages.warning(request, "Read only as someone else owns this brew")
        read_only = True
    else:
        read_only = False

    grain_recipes = GrainRecipe.objects.filter(recipe=current_brew.recipe.pk)
    total_grain_bill_g = sum([recipe.quantity_g for recipe in grain_recipes])

    context = {'brew': current_brew,
               'projects': projects,
               'available_sensors': available_sensors,
               'read_only': read_only,
               'disabled': "disabled" if read_only else "",
               'is_everything_in_stock': is_everything_in_stock(request, current_brew.recipe),
               'grain_recipes': grain_recipes,
               'total_grain_bill_g': total_grain_bill_g,
               'boil_hop_recipes': HopRecipe.objects.filter(recipe=current_brew.recipe.pk, dry_hop=False).order_by('-time_min'),
               'dry_hop_recipes': HopRecipe.objects.filter(recipe=current_brew.recipe.pk, dry_hop=True).order_by('-time_min'),
               'mash_volume_l': '{:.1f}'.format(mash_volume_l),
               'target_pre_sparge_volume_l': '{:.1f}'.format(target_pre_sparge_volume_l),
               'target_pre_boil_volume_l': '{:.1f}'.format(target_pre_boil_volume_l),
               'target_pre_boil_gravity': '{:.3f}'.format(target_pre_boil_gravity),
               'mash_strike_temperature_c': '{:.1f}'.format(mash_strike_temperature_c),
               'sparge_strike_temperature_c': '{:.1f}'.format(sparge_strike_temperature_c),
               'estimated_volume_l': '{:.1f}'.format(estimated_volume_l),
               'estimated_og': '{:.3f}'.format(estimated_og),
               'sparge_volume_l': '{:.1f}'.format(sparge_volume_l),
               'stock_checker': get_recipe_stock_check(request, current_brew.recipe)}

    return render(request, 'edit_brew.html', context)


@login_required()
def next_state_brew(request, pk):
    current_brew = Brew.objects.get(pk=pk)

    if current_brew.owner != request.user:
        messages.error(request, "You can't edit someone else's brew")
        return redirect("edit_brew", pk=pk)

    if current_brew.state == Brew.BrewState.PREP:
        current_brew.state = Brew.BrewState.MASH
    elif current_brew.state == Brew.BrewState.MASH:
        current_brew.state = Brew.BrewState.BOIL
    elif current_brew.state == Brew.BrewState.BOIL:
        current_brew.state = Brew.BrewState.FERMENTING
    elif current_brew.state == Brew.BrewState.FERMENTING:
        current_brew.state = Brew.BrewState.COMPLETED
    current_brew.save()

    return redirect("edit_brew", pk=pk)


@login_required()
def previous_state_brew(request, pk):
    current_brew = Brew.objects.get(pk=pk)

    if current_brew.owner != request.user:
        messages.error(request, "You can't edit someone else's brew")
        return redirect("edit_brew", pk=pk)

    if current_brew.state == Brew.BrewState.MASH:
        current_brew.state = Brew.BrewState.PREP
    elif current_brew.state == Brew.BrewState.BOIL:
        current_brew.state = Brew.BrewState.MASH
    elif current_brew.state == Brew.BrewState.FERMENTING:
        current_brew.state = Brew.BrewState.BOIL
    elif current_brew.state == Brew.BrewState.COMPLETED:
        current_brew.state = Brew.BrewState.FERMENTING
    current_brew.save()

    return redirect("edit_brew", pk=pk)


@login_required()
def save_prep(request, pk):
    current_brew = Brew.objects.get(pk=pk)

    if current_brew.owner != request.user:
        messages.error(request, "You can't edit someone else's brew")
        return redirect("edit_brew", pk=pk)

    current_brew.name = request.POST['name']
    current_brew.brew_date = request.POST['brew_date']
    current_brew.mash_thickness_lpkg = request.POST['mash_thickness_lpkg']
    current_brew.evaporation_lph = request.POST['evaporation_lph']
    current_brew.mash_out_temp_c = request.POST['mash_out_temp_c']
    current_brew.save()

    return redirect("edit_brew", pk=pk)


@login_required()
def save_mash(request, pk):
    current_brew = Brew.objects.get(pk=pk)

    if current_brew.owner != request.user:
        messages.error(request, "You can't edit someone else's brew")
        return redirect("edit_brew", pk=pk)

    current_brew.measured_mash_temp_c = request.POST['measured_mash_temp_c']
    current_brew.measured_mash_ph = request.POST['measured_mash_ph']
    current_brew.save()

    return redirect("edit_brew", pk=pk)


@login_required()
def save_boil(request, pk):
    current_brew = Brew.objects.get(pk=pk)

    if current_brew.owner != request.user:
        messages.error(request, "You can't edit someone else's brew")
        return redirect("edit_brew", pk=pk)

    current_brew.pre_boil_volume_l = request.POST['pre_boil_volume_l']
    current_brew.pre_boil_gravity = request.POST['pre_boil_gravity']
    current_brew.measured_og = request.POST['measured_og']
    current_brew.fermenter_volume_l = request.POST['fermenter_volume_l']
    current_brew.save()

    return redirect("edit_brew", pk=pk)


@login_required()
def save_fermenting(request, pk):
    current_brew = Brew.objects.get(pk=pk)

    if current_brew.owner != request.user:
        messages.error(request, "You can't edit someone else's brew")
        return redirect("edit_brew", pk=pk)

    if request.POST.get('monitor_project', None):
        current_brew.monitor_project = get_object_or_404(Project, pk=request.POST['monitor_project'])
        current_brew.save()

    return redirect("edit_brew", pk=pk)


@login_required()
def save_completed(request, pk):
    current_brew = Brew.objects.get(pk=pk)

    if current_brew.owner != request.user:
        messages.error(request, "You can't edit someone else's brew")
        return redirect("edit_brew", pk=pk)

    current_brew.bottling_date = request.POST['bottling_date']
    current_brew.measured_fg = request.POST['measured_fg']
    current_brew.bottling_volume_l = request.POST['bottling_volume_l']
    current_brew.save()

    return redirect("edit_brew", pk=pk)


@login_required()
def consume_ingredients(request, pk):
    current_brew = Brew.objects.get(pk=pk)

    if current_brew.owner != request.user:
        messages.error(request, "You can't edit someone else's brew")
        return redirect("edit_brew", pk=pk)

    grains = GrainRecipe.objects.filter(recipe=current_brew.recipe)
    hops = HopRecipe.objects.filter(recipe=current_brew.recipe)

    for ingredient in grains:
        stock_entry = Stock.objects.get(owner=request.user, ingredient=ingredient.grain)
        stock_entry.quantity_g -= ingredient.quantity_g
        stock_entry.save()

    for ingredient in hops:
        stock_entry = Stock.objects.get(owner=request.user, ingredient=ingredient.hop)
        stock_entry.quantity_g -= ingredient.quantity_g
        stock_entry.save()

    current_brew.ingredients_consumed = True
    current_brew.save()

    return redirect("edit_brew", pk=pk)

@login_required()
@require_POST
def create_monitor_project(request, pk):
    current_brew = Brew.objects.get(pk=pk)
    project_name = current_brew
    project_owner = request.user
    new_project = Project.objects.create(name=project_name, owner=project_owner)
    current_brew.monitor_project = new_project
    current_brew.save()

    return redirect("edit_brew", pk=pk)

