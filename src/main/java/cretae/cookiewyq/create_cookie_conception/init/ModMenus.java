package cretae.cookiewyq.create_cookie_conception.init;

import cretae.cookiewyq.create_cookie_conception.CookieConceptionMod;
import cretae.cookiewyq.create_cookie_conception.menu.TieredContainerMenu;
import cretae.cookiewyq.create_cookie_conception.menu.VirtualTieredContainerMenu;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.inventory.MenuType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.common.extensions.IMenuTypeExtension;
import net.neoforged.neoforge.registries.DeferredRegister;
import java.util.function.Supplier;

public class ModMenus {
    private static final DeferredRegister<MenuType<?>> MENUS = DeferredRegister.create(Registries.MENU, CookieConceptionMod.MODID);
    public static final Supplier<MenuType<TieredContainerMenu>> TIERED_CONTAINER =
            MENUS.register("tiered_container", () -> IMenuTypeExtension.create(TieredContainerMenu::new));
    
    public static final Supplier<MenuType<VirtualTieredContainerMenu>> VIRTUAL_TIERED_CONTAINER =
            MENUS.register("virtual_tiered_container", () -> IMenuTypeExtension.create(VirtualTieredContainerMenu::new));

    public static void register(IEventBus modBus) { MENUS.register(modBus); }
}
