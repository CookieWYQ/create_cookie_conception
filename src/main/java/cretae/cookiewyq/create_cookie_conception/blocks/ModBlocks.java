package cretae.cookiewyq.create_cookie_conception.blocks;

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
