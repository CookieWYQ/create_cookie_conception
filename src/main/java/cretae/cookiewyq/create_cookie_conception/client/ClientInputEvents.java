package cretae.cookiewyq.create_cookie_conception.client;

import cretae.cookiewyq.create_cookie_conception.CookieConceptionMod;
import cretae.cookiewyq.create_cookie_conception.network.OpenBackTankPacket;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.InputEvent;
import net.neoforged.neoforge.network.PacketDistributor;

@EventBusSubscriber(modid = CookieConceptionMod.MODID, value = Dist.CLIENT)
public class ClientInputEvents {
    @SubscribeEvent
    public static void onKeyInput(InputEvent.Key event) {
        if (KeyBindings.OPEN_BACK_TANK.consumeClick()) {
            PacketDistributor.sendToServer(new OpenBackTankPacket());
        }
    }
}
