package cretae.cookiewyq.create_cookie_conception.items;

import com.tterrag.registrate.util.entry.ItemEntry;
import net.minecraft.world.item.Item;
import static cretae.cookiewyq.create_cookie_conception.CookieConceptionMod.REGISTRATE;

public class ModItems {
    public static final ItemEntry<Item> BACKPACK_STRAP = REGISTRATE.item("backpack_strap", Item::new)
            // .tab(ModTabs.CREATIVE_TAB_KEY)  // 移除，由 addCreative 手动添加
            .register();

    public static void register() {}
}
