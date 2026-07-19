package cretae.cookiewyq.create_cookie_conception.init;

import com.mojang.serialization.Codec;
import cretae.cookiewyq.create_cookie_conception.CookieConceptionMod;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.network.codec.ByteBufCodecs;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.function.Supplier;

public class ModDataComponents {
    public static final DeferredRegister<DataComponentType<?>> COMPONENTS =
            DeferredRegister.create(net.minecraft.core.registries.Registries.DATA_COMPONENT_TYPE, CookieConceptionMod.MODID);

    public static final Supplier<DataComponentType<Boolean>> HAS_STRAP =
            COMPONENTS.register("has_strap", () -> DataComponentType.<Boolean>builder()
                    .persistent(Codec.BOOL)
                    .networkSynchronized(ByteBufCodecs.BOOL)
                    .build());

    public static void register() {}
}
