package cretae.cookiewyq.create_cookie_conception.recipe;

import com.mojang.serialization.MapCodec;
import cretae.cookiewyq.create_cookie_conception.init.ModDataComponents;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.*;
import org.jetbrains.annotations.NotNull;

public class StrapRecipe extends ShapelessRecipe {
    public static final RecipeSerializer<StrapRecipe> SERIALIZER = new Serializer();

    public StrapRecipe(String group, CraftingBookCategory category, ItemStack result, NonNullList<Ingredient> ingredients) {
        super(group, category, result, ingredients);
    }

    public StrapRecipe(ShapelessRecipe shapeless) {
        super(shapeless.getGroup(), shapeless.category(), shapeless.getResultItem(null), shapeless.getIngredients());
    }

    @Override
    public @NotNull ItemStack assemble(CraftingInput input, HolderLookup.Provider registries) {
        for (int i = 0; i < input.size(); i++) {
            ItemStack stack = input.getItem(i);
            if (stack.getItem() == getResultItem(registries).getItem()) {
                ItemStack result = stack.copy();
                result.setCount(1);
                result.set(ModDataComponents.HAS_STRAP.get(), true);
                return result;
            }
        }
        return super.assemble(input, registries);
    }

    @Override
    public @NotNull RecipeSerializer<?> getSerializer() {
        return SERIALIZER;
    }

    public static class Serializer implements RecipeSerializer<StrapRecipe> {
        @SuppressWarnings("unchecked")
        private static final RecipeSerializer<ShapelessRecipe> VANILLA_SERIALIZER =
                (RecipeSerializer<ShapelessRecipe>) BuiltInRegistries.RECIPE_SERIALIZER
                        .get(ResourceLocation.withDefaultNamespace("crafting_shapeless"));

        public static final MapCodec<StrapRecipe> CODEC = VANILLA_SERIALIZER.codec()
                .xmap(StrapRecipe::new, r -> r);
        public static final StreamCodec<RegistryFriendlyByteBuf, StrapRecipe> STREAM_CODEC =
                VANILLA_SERIALIZER.streamCodec().map(StrapRecipe::new, r -> r);

        @Override
        public @NotNull MapCodec<StrapRecipe> codec() {
            return CODEC;
        }

        @Override
        public @NotNull StreamCodec<RegistryFriendlyByteBuf, StrapRecipe> streamCodec() {
            return STREAM_CODEC;
        }
    }
}
