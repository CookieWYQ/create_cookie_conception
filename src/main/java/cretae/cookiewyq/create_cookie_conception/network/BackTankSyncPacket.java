package cretae.cookiewyq.create_cookie_conception.network;

import cretae.cookiewyq.create_cookie_conception.CookieConceptionMod;
import cretae.cookiewyq.create_cookie_conception.menu.VirtualTieredContainerMenu;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.network.handling.IPayloadContext;

import java.util.ArrayList;
import java.util.List;

public record BackTankSyncPacket(List<FluidStack> fluids) implements CustomPacketPayload {
    public static final Type<BackTankSyncPacket> TYPE = new Type<>(
            ResourceLocation.fromNamespaceAndPath(CookieConceptionMod.MODID, "back_tank_sync"));

    public static final StreamCodec<RegistryFriendlyByteBuf, BackTankSyncPacket> CODEC = StreamCodec.of(
            (buf, pkt) -> {
                buf.writeVarInt(pkt.fluids.size());
                for (FluidStack fluid : pkt.fluids) {
                    FluidStack.OPTIONAL_STREAM_CODEC.encode(buf, fluid);
                }
            },
            buf -> {
                int size = buf.readVarInt();
                List<FluidStack> list = new ArrayList<>();
                for (int i = 0; i < size; i++) {
                    list.add(FluidStack.OPTIONAL_STREAM_CODEC.decode(buf));
                }
                return new BackTankSyncPacket(list);
            }
    );

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }

    public static void handle(BackTankSyncPacket packet, IPayloadContext context) {
        context.enqueueWork(() -> {
            if (context.player().containerMenu instanceof VirtualTieredContainerMenu menu) {
                menu.updateFluidTanks(packet.fluids());
            }
        });
    }
}
