from django.contrib import admin
from .models import Grain, Hop, Yeast, Stock, Recipe, GrainRecipe, HopRecipe, Brew

admin.site.register(Grain)
admin.site.register(Hop)
admin.site.register(Yeast)
admin.site.register(Stock)
admin.site.register(Recipe)
admin.site.register(GrainRecipe)
admin.site.register(HopRecipe)
admin.site.register(Brew)
