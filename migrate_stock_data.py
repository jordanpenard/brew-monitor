import sqlite3
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django
django.setup()

from django.contrib.auth.models import User
from stock.models import Ingredient, Grain, Hop, Yeast, Stock, Recipe, GrainRecipe, HopRecipe, Brew
from monitor.models import Project as MonitorProject, Sensor as MonitorSensor # Avoid name collision

def migrate_stock_data():
    old_db_path = "old-brew-planner.sqlite3"
    new_db_path = "db.sqlite3"

    conn_old = sqlite3.connect(old_db_path)
    cursor_old = conn_old.cursor()

    conn_new = sqlite3.connect(new_db_path)
    cursor_new = conn_new.cursor()

    # Enable foreign keys for integrity in the new DB
    cursor_new.execute("PRAGMA foreign_keys = ON;")

    # Mapping old owners (CharField) to new Django User IDs
    # This assumes that the usernames in the old db either exist or can be created.
    user_cache = {}
    for user in User.objects.all():
        user_cache[user.username] = user.id

    def get_or_create_user_id(username):
        if username not in user_cache:
            # Create a placeholder user, or handle existing users
            user, created = User.objects.get_or_create(username=username, defaults={
                "password": "!", # No usable password
                "is_active": False,
            })
            user_cache[username] = user.id
        return user_cache[username]

    # Migrate Ingredient types (PolymorphicModel needs special care if IDs clash, for now insert new)
    # For simplicity, we\'ll re-create ingredients and map them. This avoids polymorphic issues.
    old_ingredient_map = {}

    # Migrate Grains
    cursor_old.execute("SELECT ingredient_ptr_id, name, color_lovibond, ppg, diastatic_power FROM stock_grain INNER JOIN stock_ingredient ON stock_grain.ingredient_ptr_id = stock_ingredient.id")
    for old_id, name, color_lovibond, ppg, diastatic_power in cursor_old.fetchall():
        grain, created = Grain.objects.get_or_create(name=name, defaults={
            "color_lovibond": color_lovibond,
            "ppg": ppg,
            "diastatic_power": diastatic_power
        })
        old_ingredient_map[old_id] = grain.id

    # Migrate Hops
    cursor_old.execute("SELECT ingredient_ptr_id, name, alpha_acid, whole_not_pellet FROM stock_hop INNER JOIN stock_ingredient ON stock_hop.ingredient_ptr_id = stock_ingredient.id")
    for old_id, name, alpha_acid, whole_not_pellet in cursor_old.fetchall():
        hop, created = Hop.objects.get_or_create(name=name, defaults={
            "alpha_acid": alpha_acid,
            "whole_not_pellet": bool(whole_not_pellet)
        })
        old_ingredient_map[old_id] = hop.id

    # Migrate Yeasts
    cursor_old.execute("SELECT ingredient_ptr_id, name, liquid_not_dry FROM stock_yeast INNER JOIN stock_ingredient ON stock_yeast.ingredient_ptr_id = stock_ingredient.id")
    for old_id, name, liquid_not_dry in cursor_old.fetchall():
        yeast, created = Yeast.objects.get_or_create(name=name, defaults={
            "liquid_not_dry": bool(liquid_not_dry)
        })
        old_ingredient_map[old_id] = yeast.id

    # Migrate Stock
    cursor_old.execute("SELECT owner, ingredient_id, quantity_g FROM stock_stock")
    for owner_name, old_ingredient_id, quantity_g in cursor_old.fetchall():
        new_owner_id = get_or_create_user_id(owner_name)
        new_ingredient_id = old_ingredient_map.get(old_ingredient_id)
        if new_ingredient_id:
            Stock.objects.create(owner=User.objects.get(pk=new_owner_id), ingredient=Ingredient.objects.get(pk=new_ingredient_id), quantity_g=quantity_g)

    # Migrate Recipes
    old_recipe_map = {}
    cursor_old.execute("SELECT id, owner, name, batch_size_l, comments, yeast_id, mash_temperature_c, fermentation_temperature_c, boil_time_min FROM stock_recipe")
    for old_id, owner_name, name, batch_size_l, comments, old_yeast_id, mash_temperature_c, fermentation_temperature_c, boil_time_min in cursor_old.fetchall():
        new_owner_id = get_or_create_user_id(owner_name)
        new_yeast = Ingredient.objects.get(pk=old_ingredient_map[old_yeast_id]) if old_yeast_id else None

        recipe = Recipe.objects.create(
            owner=User.objects.get(pk=new_owner_id),
            name=name,
            batch_size_l=batch_size_l,
            comments=comments,
            yeast=new_yeast,
            mash_temperature_c=mash_temperature_c,
            fermentation_temperature_c=fermentation_temperature_c,
            boil_time_min=boil_time_min
        )
        old_recipe_map[old_id] = recipe.id

    # Migrate GrainRecipe
    cursor_old.execute("SELECT recipe_id, grain_id, quantity_g FROM stock_grainrecipe")
    for old_recipe_id, old_grain_id, quantity_g in cursor_old.fetchall():
        new_recipe_id = old_recipe_map.get(old_recipe_id)
        new_grain_id = old_ingredient_map.get(old_grain_id)
        if new_recipe_id and new_grain_id:
            GrainRecipe.objects.create(recipe=Recipe.objects.get(pk=new_recipe_id), grain=Grain.objects.get(pk=new_grain_id), quantity_g=quantity_g)

    # Migrate HopRecipe
    cursor_old.execute("SELECT recipe_id, hop_id, quantity_g, time_min, dry_hop FROM stock_hoprecipe")
    for old_recipe_id, old_hop_id, quantity_g, time_min, dry_hop in cursor_old.fetchall():
        new_recipe_id = old_recipe_map.get(old_recipe_id)
        new_hop_id = old_ingredient_map.get(old_hop_id)
        if new_recipe_id and new_hop_id:
            HopRecipe.objects.create(
                recipe=Recipe.objects.get(pk=new_recipe_id),
                hop=Hop.objects.get(pk=new_hop_id),
                quantity_g=quantity_g,
                time_min=time_min,
                dry_hop=bool(dry_hop)
            )

    # Migrate Brews
    cursor_old.execute("SELECT name, owner, recipe_id, state, ingredients_consumed, brew_date, bottling_date, mash_thickness_lpkg, evaporation_lph, mash_out_temp_c, pre_boil_volume_l, pre_boil_gravity, measured_og, measured_fg, measured_mash_ph, measured_mash_temp_c, fermenter_volume_l, bottling_volume_l, brew_monitor_link FROM stock_brew")
    for name, owner_name, old_recipe_id, state, ingredients_consumed, brew_date, bottling_date, mash_thickness_lpkg, evaporation_lph, mash_out_temp_c, pre_boil_volume_l, pre_boil_gravity, measured_og, measured_fg, measured_mash_ph, measured_mash_temp_c, fermenter_volume_l, bottling_volume_l, brew_monitor_link in cursor_old.fetchall():
        new_owner_id = get_or_create_user_id(owner_name)
        new_recipe_id = old_recipe_map.get(old_recipe_id)

        # Handle brew_monitor_link if it was a Project ID before
        monitor_project = None
        if brew_monitor_link and brew_monitor_link.isdigit():
            try:
                monitor_project = MonitorProject.objects.get(pk=int(brew_monitor_link))
            except MonitorProject.DoesNotExist:
                pass # Project might not exist in the new monitor app

        if new_recipe_id:
            Brew.objects.create(
                name=name,
                owner=User.objects.get(pk=new_owner_id),
                recipe=Recipe.objects.get(pk=new_recipe_id),
                state=state,
                ingredients_consumed=bool(ingredients_consumed),
                brew_date=brew_date,
                bottling_date=bottling_date,
                mash_thickness_lpkg=mash_thickness_lpkg,
                evaporation_lph=evaporation_lph,
                mash_out_temp_c=mash_out_temp_c,
                pre_boil_volume_l=pre_boil_volume_l,
                pre_boil_gravity=pre_boil_gravity,
                measured_og=measured_og,
                measured_fg=measured_fg,
                measured_mash_ph=measured_mash_ph,
                measured_mash_temp_c=measured_mash_temp_c,
                fermenter_volume_l=fermenter_volume_l,
                bottling_volume_l=bottling_volume_l,
                project_monitor=monitor_project,
            )

    conn_old.close()
    conn_new.close()
    print("Stock data migration completed!")

if __name__ == "__main__":
    migrate_stock_data()
