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
import net.minecraft.world.item.Items;
import net.minecraft.world.item.PotionItem;
import net.neoforged.neoforge.fluids.FluidUtil;
import net.neoforged.neoforge.items.IItemHandler;
import net.neoforged.neoforge.items.ItemStackHandler;
import net.neoforged.neoforge.items.SlotItemHandler;

import java.util.ArrayList;
import java.util.List;

public class TieredContainerMenu extends AbstractContainerMenu {
    private final BlockPos pos;
    private final TieredContainerBlockEntity blockEntity;
    private final IItemHandler itemHandler;
    private final Inventory playerInventory;
    private final int containerSlots;
    private final int tankCount;
    private int scrollOffset = 0;
    private static final int VISIBLE_ROWS = 6;

    private final List<SlotItemHandler> inputSlots = new ArrayList<>();
    private final List<SlotItemHandler> outputSlots = new ArrayList<>();

    // Client constructor
    public TieredContainerMenu(int id, Inventory inv, FriendlyByteBuf extraData) {
        super(ModMenus.TIERED_CONTAINER.get(), id);
        extraData.readBoolean(); // consume virtual flag (always false)
        this.pos = extraData.readBlockPos();
        int slots = extraData.readVarInt();
        int tanks = extraData.readVarInt();
        this.blockEntity = (TieredContainerBlockEntity) inv.player.level().getBlockEntity(pos);
        this.itemHandler = blockEntity != null ? blockEntity.getItemHandler() : new ItemStackHandler(slots);
        this.playerInventory = inv;
        this.containerSlots = itemHandler.getSlots();
        this.tankCount = blockEntity != null ? blockEntity.getFluidTanks().size() : tanks;

        addDedicatedSlots();
        addMainSlots();
    }

    // Server constructor
    public TieredContainerMenu(int id, Inventory inv, TieredContainerBlockEntity be) {
        super(ModMenus.TIERED_CONTAINER.get(), id);
        this.pos = be.getBlockPos();
        this.blockEntity = be;
        this.itemHandler = be.getItemHandler();
        this.playerInventory = inv;
        this.containerSlots = itemHandler.getSlots();
        this.tankCount = be.getFluidTanks().size();

        addDedicatedSlots();
        addMainSlots();
    }

    private void addDedicatedSlots() {
        if (blockEntity == null) return;
        List<ItemStackHandler> inputs = blockEntity.getInputHandlers();
        List<ItemStackHandler> outputs = blockEntity.getOutputHandlers();
        for (int i = 0; i < tankCount; i++) {
            // Input slot: accept any item that contains a fluid (potion, bottle, bucket, honey bottle)
            SlotItemHandler inputSlot = new SlotItemHandler(inputs.get(i), 0, 0, 0) {
                @Override
                public boolean mayPlace(ItemStack stack) {
                    // Allow any fluid handler with fluid inside
                    if (FluidUtil.getFluidContained(stack).isPresent()) return true;
                    // Allow honey bottle and potion items explicitly (might not be caught by FluidUtil)
                    return stack.is(Items.HONEY_BOTTLE) || stack.getItem() instanceof PotionItem;
                }
            };
            this.addSlot(inputSlot);
            this.inputSlots.add(inputSlot);

            // Output slot: accept empty fluid containers (bucket, glass bottle, etc.)
            SlotItemHandler outputSlot = new SlotItemHandler(outputs.get(i), 0, 0, 0) {
                @Override
                public boolean mayPlace(ItemStack stack) {
                    // Must be empty of fluid
                    if (FluidUtil.getFluidContained(stack).isPresent()) return false;
                    // Must be a fluid handler or a glass bottle
                    return FluidUtil.getFluidHandler(stack).isPresent() || stack.is(Items.GLASS_BOTTLE);
                }
            };
            this.addSlot(outputSlot);
            this.outputSlots.add(outputSlot);
        }
    }

    private void addMainSlots() {
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

    public void updateSlotPositions(int offset) {
        this.scrollOffset = Math.max(0, Math.min(offset, getMaxScrollOffset()));
        int dedicatedCount = tankCount * 2;
        while (this.slots.size() > dedicatedCount) {
            this.slots.remove(this.slots.size() - 1);
        }
        addMainSlots();
    }

    public int getTankCount() { return tankCount; }
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

            int dedicatedSlots = tankCount * 2;
            int firstMainSlot = dedicatedSlots;
            int mainSlotCount = this.slots.size() - dedicatedSlots - 36;
            int firstPlayerSlot = firstMainSlot + mainSlotCount;
            int totalSlots = this.slots.size();

            if (index < firstMainSlot) {
                if (!this.moveItemStackTo(slotStack, firstPlayerSlot, totalSlots, true))
                    return ItemStack.EMPTY;
            } else if (index < firstPlayerSlot) {
                if (!this.moveItemStackTo(slotStack, firstPlayerSlot, totalSlots, true))
                    return ItemStack.EMPTY;
            } else {
                if (!this.moveItemStackTo(slotStack, firstMainSlot, firstPlayerSlot, false))
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
