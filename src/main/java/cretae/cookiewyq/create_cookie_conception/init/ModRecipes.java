package cretae.cookiewyq.create_cookie_conception.init;

import cretae.cookiewyq.create_cookie_conception.CookieConceptionMod;
import cretae.cookiewyq.create_cookie_conception.recipe.StrapRecipe;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.function.Supplier;

public class ModRecipes {
    public static final DeferredRegister<RecipeSerializer<?>> RECIPES =
            DeferredRegister.create(Registries.RECIPE_SERIALIZER, CookieConceptionMod.MODID);

    public static final Supplier<RecipeSerializer<StrapRecipe>> STRAP_CRAFTING =
            RECIPES.register("strap_crafting", () -> StrapRecipe.SERIALIZER);

    public static void register() {}
}
