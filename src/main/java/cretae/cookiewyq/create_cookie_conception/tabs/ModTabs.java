package cretae.cookiewyq.create_cookie_conception.tabs;

import cretae.cookiewyq.create_cookie_conception.CookieConceptionMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.CreativeModeTab;

public class ModTabs {
    public static final ResourceKey<CreativeModeTab> CREATIVE_TAB_KEY = 
            ResourceKey.create(Registries.CREATIVE_MODE_TAB, ResourceLocation.fromNamespaceAndPath(CookieConceptionMod.MODID, "tab"));
}
