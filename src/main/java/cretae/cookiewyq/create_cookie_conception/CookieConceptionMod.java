package cretae.cookiewyq.create_cookie_conception;

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
