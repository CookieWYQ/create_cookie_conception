package cretae.cookiewyq.create_cookie_conception.menu;

import cretae.cookiewyq.create_cookie_conception.blockentity.TieredContainerBlockEntity;
import cretae.cookiewyq.create_cookie_conception.blocks.ModBlocks;
import cretae.cookiewyq.create_cookie_conception.init.ModMenus;
import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.items.IItemHandler;
import net.neoforged.neoforge.items.ItemStackHandler;
import net.neoforged.neoforge.items.SlotItemHandler;

import java.lang.reflect.Field;
import java.util.List;

public class TieredContainerMenu extends AbstractContainerMenu {
    private final BlockPos pos;
    private final TieredContainerBlockEntity blockEntity;
    private final IItemHandler itemHandler;
    private final Inventory playerInventory;
    private final int containerSlots;
    private int scrollOffset = 0;
    private static final int VISIBLE_ROWS = 6;

    public TieredContainerMenu(int id, Inventory inv, FriendlyByteBuf extraData) {
        super(ModMenus.TIERED_CONTAINER.get(), id);
        this.pos = extraData.readBlockPos();
        int slots = extraData.readVarInt();
        int tanks = extraData.readVarInt();
        this.blockEntity = (TieredContainerBlockEntity) inv.player.level().getBlockEntity(pos);
        this.itemHandler = blockEntity != null ? blockEntity.getItemHandler() : new ItemStackHandler(slots);
        this.playerInventory = inv;
        this.containerSlots = itemHandler.getSlots();
        updateSlotPositions(0);
    }

    public TieredContainerMenu(int id, Inventory inv, TieredContainerBlockEntity be) {
        super(ModMenus.TIERED_CONTAINER.get(), id);
        this.pos = be.getBlockPos();
        this.blockEntity = be;
        this.itemHandler = be.getItemHandler();
        this.playerInventory = inv;
        this.containerSlots = itemHandler.getSlots();
        updateSlotPositions(0);
    }

    public void updateSlotPositions(int offset) {
        this.scrollOffset = Math.max(0, Math.min(offset, getMaxScrollOffset()));
        this.slots.clear();

        try {
            Field lastSlotsField = AbstractContainerMenu.class.getDeclaredField("lastSlots");
            lastSlotsField.setAccessible(true);
            List<ItemStack> lastSlots = (List<ItemStack>) lastSlotsField.get(this);
            lastSlots.clear();
        } catch (Exception ignored) {}

        int start = scrollOffset * 9;
        int end = Math.min(start + VISIBLE_ROWS * 9, containerSlots);
        for (int i = start; i < end; i++) {
            int row = (i - start) / 9;
            int col = i % 9;
            addSlot(new SlotItemHandler(itemHandler, i, 8 + col * 18, 18 + row * 18));
        }

        for (int row = 0; row < 3; ++row) {
            for (int col = 0; col < 9; ++col) {
                addSlot(new Slot(playerInventory, col + row * 9 + 9, 8 + col * 18, 140 + row * 18));
            }
        }
        for (int col = 0; col < 9; ++col) {
            addSlot(new Slot(playerInventory, col, 8 + col * 18, 198));
        }
    }

    public int getScrollOffset() { return scrollOffset; }
    public int getMaxScrollOffset() {
        int totalRows = (containerSlots + 8) / 9;
        return Math.max(0, totalRows - VISIBLE_ROWS);
    }

    public BlockPos getPos() { return pos; }
    public TieredContainerBlockEntity getBlockEntity() { return blockEntity; }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        ItemStack itemstack = ItemStack.EMPTY;
        Slot slot = this.slots.get(index);
        if (slot.hasItem()) {
            ItemStack slotStack = slot.getItem();
            itemstack = slotStack.copy();
            int containerSlots = this.slots.size() - 36;
            if (index < containerSlots) {
                if (!this.moveItemStackTo(slotStack, containerSlots, this.slots.size(), true))
                    return ItemStack.EMPTY;
            } else if (!this.moveItemStackTo(slotStack, 0, containerSlots, false)) {
                return ItemStack.EMPTY;
            }
            if (slotStack.isEmpty()) slot.set(ItemStack.EMPTY);
            else slot.setChanged();
        }
        return itemstack;
    }

    @Override
    public boolean stillValid(Player player) {
        return stillValid(ContainerLevelAccess.create(player.level(), pos), player, ModBlocks.ANDESITE_TANK.get())
            || stillValid(ContainerLevelAccess.create(player.level(), pos), player, ModBlocks.BRASS_TANK.get())
            || stillValid(ContainerLevelAccess.create(player.level(), pos), player, ModBlocks.STURDY_TANK.get());
    }
}
