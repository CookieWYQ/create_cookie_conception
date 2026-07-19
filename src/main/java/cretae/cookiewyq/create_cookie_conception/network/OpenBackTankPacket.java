package cretae.cookiewyq.create_cookie_conception.network;

import cretae.cookiewyq.create_cookie_conception.CookieConceptionMod;
import cretae.cookiewyq.create_cookie_conception.init.ModDataComponents;
import cretae.cookiewyq.create_cookie_conception.items.TieredContainerBlockItem;
import cretae.cookiewyq.create_cookie_conception.menu.VirtualTieredContainerMenu;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.network.chat.Component;
import net.neoforged.neoforge.network.handling.IPayloadContext;
import top.theillusivec4.curios.api.CuriosApi;

public record OpenBackTankPacket() implements CustomPacketPayload {
    public static final Type<OpenBackTankPacket> TYPE = new Type<>(
            ResourceLocation.fromNamespaceAndPath(CookieConceptionMod.MODID, "open_back_tank"));
    public static final StreamCodec<RegistryFriendlyByteBuf, OpenBackTankPacket> CODEC =
            StreamCodec.unit(new OpenBackTankPacket());

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }

    public static void handle(OpenBackTankPacket packet, IPayloadContext context) {
        context.enqueueWork(() -> {
            if (context.player() instanceof ServerPlayer player) {
                ItemStack backStack = CuriosApi.getCuriosInventory(player)
                        .flatMap(handler -> handler.getStacksHandler("back"))
                        .map(stacks -> stacks.getStacks().getStackInSlot(0))
                        .orElse(ItemStack.EMPTY);

                if (backStack.isEmpty()) return;
                if (!Boolean.TRUE.equals(backStack.get(ModDataComponents.HAS_STRAP.get()))) return;

                player.openMenu(new BackTankMenuProvider(backStack), buf -> {
                    int slots = 54, tanks = 3, capacity = 32000;
                    if (backStack.getItem() instanceof TieredContainerBlockItem blockItem) {
                        slots = blockItem.getInventorySlots();
                        tanks = blockItem.getFluidTankCount();
                        capacity = blockItem.getFluidTankCapacity();
                    }

                    CustomData customData = backStack.getOrDefault(DataComponents.BLOCK_ENTITY_DATA, CustomData.EMPTY);
                    CompoundTag tag = customData.copyTag();

                    buf.writeVarInt(slots);
                    buf.writeVarInt(tanks);
                    buf.writeVarInt(capacity);
                    buf.writeNbt(tag);
                });
            }
        });
    }

    private record BackTankMenuProvider(ItemStack backStack) implements MenuProvider {
        @Override
        public Component getDisplayName() {
            return backStack.getHoverName();
        }

        @Override
        public AbstractContainerMenu createMenu(int id, Inventory inv, Player player) {
            return new VirtualTieredContainerMenu(id, inv, backStack, (ServerPlayer) player);
        }
    }
}
