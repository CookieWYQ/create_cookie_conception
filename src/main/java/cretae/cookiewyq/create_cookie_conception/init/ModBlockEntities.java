package cretae.cookiewyq.create_cookie_conception.init;

import com.tterrag.registrate.util.entry.BlockEntityEntry;
import cretae.cookiewyq.create_cookie_conception.blockentity.TieredContainerBlockEntity;
import cretae.cookiewyq.create_cookie_conception.blocks.ModBlocks;
import static cretae.cookiewyq.create_cookie_conception.CookieConceptionMod.REGISTRATE;

public class ModBlockEntities {
    public static final BlockEntityEntry<TieredContainerBlockEntity> TIERED_CONTAINER = REGISTRATE
            .blockEntity("tiered_container", TieredContainerBlockEntity::new)
            .validBlocks(ModBlocks.ANDESITE_TANK, ModBlocks.BRASS_TANK, ModBlocks.STURDY_TANK)
            .register();
    public static void register() {}
}
