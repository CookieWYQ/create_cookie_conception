package cretae.cookiewyq.create_cookie_conception.network;

import cretae.cookiewyq.create_cookie_conception.CookieConceptionMod;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.registration.PayloadRegistrar;

public class ModNetworking {
    public static void register(IEventBus modEventBus) {
        modEventBus.addListener((RegisterPayloadHandlersEvent event) -> {
            PayloadRegistrar registrar = event.registrar("1");
            registrar.playToServer(OpenBackTankPacket.TYPE, OpenBackTankPacket.CODEC, OpenBackTankPacket::handle);
            registrar.playToClient(BackTankSyncPacket.TYPE, BackTankSyncPacket.CODEC, BackTankSyncPacket::handle);
        });
    }
}
