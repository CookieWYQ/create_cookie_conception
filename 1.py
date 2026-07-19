import os
import glob

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(base, "src", "main")
    java = os.path.join(src, "java", "cretae", "cookiewyq", "create_cookie_conception")
    res = os.path.join(src, "resources")
    data = os.path.join(res, "data", "create_cookie_conception")
    assets = os.path.join(res, "assets", "create_cookie_conception")

    # 1. TieredContainerBlockItem.java - implements ICurioItem correctly
    write_file(os.path.join(java, "items", "TieredContainerBlockItem.java"), '''package cretae.cookiewyq.create_cookie_conception.items;

import cretae.cookiewyq.create_cookie_conception.blocks.tiered.TieredContainerBlock;
import cretae.cookiewyq.create_cookie_conception.init.ModDataComponents;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.type.capability.ICurioItem;

public class TieredContainerBlockItem extends BlockItem implements ICurioItem {
    public TieredContainerBlockItem(Block block, Properties properties) {
        super(block, properties);
    }

    public int getInventorySlots() {
        if (getBlock() instanceof TieredContainerBlock tiered) {
            return tiered.getInventorySlots();
        }
        return 54;
    }

    public int getFluidTankCount() {
        if (getBlock() instanceof TieredContainerBlock tiered) {
            return tiered.getFluidTankCount();
        }
        return 3;
    }

    public int getFluidTankCapacity() {
        if (getBlock() instanceof TieredContainerBlock tiered) {
            return tiered.getFluidTankCapacity();
        }
        return 32000;
    }

    @Override
    public boolean canEquip(SlotContext slotContext, ItemStack stack) {
        return Boolean.TRUE.equals(stack.get(ModDataComponents.HAS_STRAP.get()));
    }
}
''')

    # 2. StrapRecipe.java - sets has_strap on result
    write_file(os.path.join(java, "recipe", "StrapRecipe.java"), '''package cretae.cookiewyq.create_cookie_conception.recipe;

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
''')

    # 3. ModBlocks.java - no Chinese comments, all tank items use TieredContainerBlockItem
    write_file(os.path.join(java, "blocks", "ModBlocks.java"), '''package cretae.cookiewyq.create_cookie_conception.blocks;

import com.simibubi.create.AllBlocks;
import com.simibubi.create.AllItems;
import com.simibubi.create.foundation.data.TagGen;
import com.tterrag.registrate.providers.RegistrateRecipeProvider;
import com.tterrag.registrate.util.entry.BlockEntry;
import cretae.cookiewyq.create_cookie_conception.CookieConceptionMod;
import cretae.cookiewyq.create_cookie_conception.blocks.tiered.AndesiteContainerBlock;
import cretae.cookiewyq.create_cookie_conception.blocks.tiered.BrassContainerBlock;
import cretae.cookiewyq.create_cookie_conception.blocks.tiered.SturdyContainerBlock;
import cretae.cookiewyq.create_cookie_conception.items.TieredContainerBlockItem;
import cretae.cookiewyq.create_cookie_conception.tabs.ModTabs;
import net.minecraft.data.recipes.RecipeCategory;
import net.minecraft.data.recipes.ShapedRecipeBuilder;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.material.MapColor;

import static cretae.cookiewyq.create_cookie_conception.CookieConceptionMod.REGISTRATE;

public class ModBlocks {
    public static final BlockEntry<Block> INVENTORY_PROXY = REGISTRATE
            .block("inventory_proxy", Block::new)
            .initialProperties(() -> Blocks.IRON_BLOCK)
            .properties(p -> p.mapColor(MapColor.COLOR_YELLOW).sound(SoundType.METAL).strength(3.0f, 6.0f).noOcclusion())
            .blockstate((c, p) -> {
                p.simpleBlock(c.get(), p.models().cubeBottomTop(c.getName(),
                        p.modLoc("block/inventory_proxy/inventory_proxy_side"),
                        p.modLoc("block/inventory_proxy/inventory_proxy_top"),
                        p.modLoc("block/inventory_proxy/inventory_proxy_side")));
            })
            .transform(TagGen.pickaxeOnly())
            .tag(BlockTags.MINEABLE_WITH_PICKAXE)
            .item()
            .tab(ModTabs.CREATIVE_TAB_KEY)
            .build()
            .lang("Inventory Proxy")
            .recipe((ctx, provider) -> ShapedRecipeBuilder.shaped(RecipeCategory.COMBAT, ctx.get())
                    .pattern("B B").pattern("AFA").pattern("B B")
                    .define('B', AllBlocks.BRASS_CASING.asItem())
                    .define('A', AllItems.ANDESITE_ALLOY.asItem())
                    .define('F', AllBlocks.BRASS_FUNNEL.asItem())
                    .unlockedBy("has_brass_casing", RegistrateRecipeProvider.has(AllBlocks.BRASS_CASING.asItem()))
                    .save(provider, CookieConceptionMod.modLoc("inventory_proxy")))
            .register();

    public static final BlockEntry<AndesiteContainerBlock> ANDESITE_TANK = REGISTRATE
            .block("andesite_tank", AndesiteContainerBlock::new)
            .initialProperties(() -> Blocks.IRON_BLOCK)
            .properties(p -> p.mapColor(MapColor.COLOR_GRAY).sound(SoundType.METAL).strength(0.2f, 1.0f))
            .blockstate((c, p) -> p.simpleBlock(c.get()))
            .transform(TagGen.pickaxeOnly())
            .tag(BlockTags.MINEABLE_WITH_PICKAXE)
            .item((block, props) -> new TieredContainerBlockItem(block, new Item.Properties()))
            .tab(ModTabs.CREATIVE_TAB_KEY)
            .build()
            .lang("Andesite Tank")
            .recipe((ctx, provider) -> ShapedRecipeBuilder.shaped(RecipeCategory.COMBAT, ctx.get())
                    .pattern("AAA")
                    .pattern("ASA")
                    .pattern("AAA")
                    .define('A', AllItems.ANDESITE_ALLOY.asItem())
                    .define('S', AllBlocks.ITEM_VAULT.asItem())
                    .unlockedBy("has_andesite_alloy", RegistrateRecipeProvider.has(AllItems.ANDESITE_ALLOY.asItem()))
                    .save(provider, CookieConceptionMod.modLoc("andesite_tank")))
            .register();

    public static final BlockEntry<BrassContainerBlock> BRASS_TANK = REGISTRATE
            .block("brass_tank", BrassContainerBlock::new)
            .initialProperties(() -> Blocks.IRON_BLOCK)
            .properties(p -> p.mapColor(MapColor.COLOR_YELLOW).sound(SoundType.METAL).strength(0.3f, 1.5f))
            .blockstate((c, p) -> p.simpleBlock(c.get()))
            .transform(TagGen.pickaxeOnly())
            .tag(BlockTags.MINEABLE_WITH_PICKAXE)
            .item((block, props) -> new TieredContainerBlockItem(block, new Item.Properties()))
            .tab(ModTabs.CREATIVE_TAB_KEY)
            .build()
            .lang("Brass Tank")
            .recipe((ctx, provider) -> ShapedRecipeBuilder.shaped(RecipeCategory.COMBAT, ctx.get())
                    .pattern("BBB")
                    .pattern("BSB")
                    .pattern("BBB")
                    .define('B', AllItems.BRASS_INGOT.asItem())
                    .define('S', AllBlocks.ITEM_VAULT.asItem())
                    .unlockedBy("has_brass_ingot", RegistrateRecipeProvider.has(AllItems.BRASS_INGOT.asItem()))
                    .save(provider, CookieConceptionMod.modLoc("brass_tank")))
            .register();

    public static final BlockEntry<SturdyContainerBlock> STURDY_TANK = REGISTRATE
            .block("sturdy_tank", SturdyContainerBlock::new)
            .initialProperties(() -> Blocks.IRON_BLOCK)
            .properties(p -> p.mapColor(MapColor.COLOR_BLACK).sound(SoundType.METAL).strength(0.4f, 2.0f))
            .blockstate((c, p) -> p.simpleBlock(c.get()))
            .transform(TagGen.pickaxeOnly())
            .tag(BlockTags.MINEABLE_WITH_PICKAXE)
            .item((block, props) -> new TieredContainerBlockItem(block, new Item.Properties()))
            .tab(ModTabs.CREATIVE_TAB_KEY)
            .build()
            .lang("Sturdy Tank")
            .recipe((ctx, provider) -> ShapedRecipeBuilder.shaped(RecipeCategory.COMBAT, ctx.get())
                    .pattern("III")
                    .pattern("ISI")
                    .pattern("III")
                    .define('I', AllItems.STURDY_SHEET.asItem())
                    .define('S', AllBlocks.ITEM_VAULT.asItem())
                    .unlockedBy("has_sturdy_sheet", RegistrateRecipeProvider.has(AllItems.STURDY_SHEET.asItem()))
                    .save(provider, CookieConceptionMod.modLoc("sturdy_tank")))
            .register();

    public static void register() {}
}
''')

    # 4. CookieConceptionMod.java - registers data components, no manual item addition
    write_file(os.path.join(java, "CookieConceptionMod.java"), '''package cretae.cookiewyq.create_cookie_conception;

import com.mojang.logging.LogUtils;
import com.simibubi.create.foundation.data.CreateRegistrate;
import com.simibubi.create.foundation.item.ItemDescription;
import com.simibubi.create.foundation.item.KineticStats;
import com.simibubi.create.foundation.item.TooltipModifier;
import cretae.cookiewyq.create_cookie_conception.blocks.ModBlocks;
import cretae.cookiewyq.create_cookie_conception.init.ModBlockEntities;
import cretae.cookiewyq.create_cookie_conception.init.ModDataComponents;
import cretae.cookiewyq.create_cookie_conception.init.ModMenus;
import cretae.cookiewyq.create_cookie_conception.items.ModItems;
import cretae.cookiewyq.create_cookie_conception.tabs.ModTabs;
import net.createmod.catnip.lang.FontHelper;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.event.server.ServerStartingEvent;
import net.neoforged.neoforge.registries.DeferredRegister;
import org.slf4j.Logger;

import java.util.function.Supplier;

@Mod(CookieConceptionMod.MODID)
public class CookieConceptionMod {
    public static final String MODID = "create_cookie_conception";
    public static final Logger LOGGER = LogUtils.getLogger();
    public static final CreateRegistrate REGISTRATE = CreateRegistrate.create(MODID);

    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, MODID);
    public static final Supplier<CreativeModeTab> CREATIVE_TAB = TABS.register("tab", () -> CreativeModeTab.builder()
            .icon(() -> new ItemStack(ModBlocks.ANDESITE_TANK.get()))
            .title(Component.translatable("itemGroup.create_cookie_conception"))
            .build());

    static {
        REGISTRATE.defaultCreativeTab(ModTabs.CREATIVE_TAB_KEY);
        REGISTRATE.setTooltipModifierFactory(item -> new ItemDescription.Modifier(item, FontHelper.Palette.STANDARD_CREATE)
                .andThen(TooltipModifier.mapNull(KineticStats.create(item))));
    }

    public CookieConceptionMod(IEventBus modEventBus, ModContainer modContainer) {
        modEventBus.addListener(this::commonSetup);
        ModBlocks.register();
        ModBlockEntities.register();
        ModItems.register();
        ModMenus.register(modEventBus);
        REGISTRATE.registerEventListeners(modEventBus);
        TABS.register(modEventBus);
        ModDataComponents.COMPONENTS.register(modEventBus);
        NeoForge.EVENT_BUS.register(this);
        modEventBus.addListener(this::addCreative);
        modContainer.registerConfig(ModConfig.Type.COMMON, Config.SPEC);
    }

    private void commonSetup(final FMLCommonSetupEvent event) {}

    private void addCreative(BuildCreativeModeTabContentsEvent event) {
        // Registrate automatically adds all items/blocks to the default tab.
    }

    @SubscribeEvent
    public void onServerStarting(ServerStartingEvent event) {}

    @EventBusSubscriber(modid = MODID, value = Dist.CLIENT)
    public static class ClientModEvents {
        @SubscribeEvent
        public static void onClientSetup(FMLClientSetupEvent event) {}
    }

    public static ResourceLocation modLoc(String path) {
        return ResourceLocation.fromNamespaceAndPath(MODID, path);
    }
}
''')

    # 5. Strap recipes JSONs (shapeless)
    andesite_strap = '''{
  "type": "create_cookie_conception:strap_crafting",
  "category": "misc",
  "ingredients": [
    { "item": "create_cookie_conception:andesite_tank" },
    { "item": "create_cookie_conception:backpack_strap" }
  ],
  "result": {
    "id": "create_cookie_conception:andesite_tank",
    "count": 1
  }
}'''
    brass_strap = '''{
  "type": "create_cookie_conception:strap_crafting",
  "category": "misc",
  "ingredients": [
    { "item": "create_cookie_conception:brass_tank" },
    { "item": "create_cookie_conception:backpack_strap" }
  ],
  "result": {
    "id": "create_cookie_conception:brass_tank",
    "count": 1
  }
}'''
    sturdy_strap = '''{
  "type": "create_cookie_conception:strap_crafting",
  "category": "misc",
  "ingredients": [
    { "item": "create_cookie_conception:sturdy_tank" },
    { "item": "create_cookie_conception:backpack_strap" }
  ],
  "result": {
    "id": "create_cookie_conception:sturdy_tank",
    "count": 1
  }
}'''

    recipe_dir = os.path.join(data, "recipe")
    write_file(os.path.join(recipe_dir, "andesite_tank_strap.json"), andesite_strap)
    write_file(os.path.join(recipe_dir, "brass_tank_strap.json"), brass_strap)
    write_file(os.path.join(recipe_dir, "sturdy_tank_strap.json"), sturdy_strap)

    # 6. Remove any .bak files that might interfere (optional but safe)
    for root, dirs, files in os.walk(src):
        for f in files:
            if f.endswith(".bak"):
                bak_path = os.path.join(root, f)
                os.remove(bak_path)
                print(f"Removed backup file: {bak_path}")

if __name__ == "__main__":
    main()