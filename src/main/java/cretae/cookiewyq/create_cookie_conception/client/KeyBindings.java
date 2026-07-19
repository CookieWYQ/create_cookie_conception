package cretae.cookiewyq.create_cookie_conception.client;

import cretae.cookiewyq.create_cookie_conception.CookieConceptionMod;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import org.lwjgl.glfw.GLFW;

public class KeyBindings {
    public static final KeyMapping OPEN_BACK_TANK = new KeyMapping(
            "key.create_cookie_conception.open_back_tank",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_O,
            "key.categories.create_cookie_conception"
    );

    public static void register(IEventBus modEventBus) {
        modEventBus.addListener((RegisterKeyMappingsEvent event) -> {
            event.register(OPEN_BACK_TANK);
        });
    }
}
