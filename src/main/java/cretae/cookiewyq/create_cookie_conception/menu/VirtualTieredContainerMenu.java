package cretae.cookiewyq.create_cookie_conception.menu;

import cretae.cookiewyq.create_cookie_conception.init.ModBlockEntities;
import cretae.cookiewyq.create_cookie_conception.init.ModDataComponents;
import cretae.cookiewyq.create_cookie_conception.init.ModMenus;
import cretae.cookiewyq.create_cookie_conception.items.TieredContainerBlockItem;
import cretae.cookiewyq.create_cookie_conception.network.BackTankSyncPacket;
import com.simibubi.create.content.fluids.potion.PotionFluid;
import com.simibubi.create.content.fluids.potion.PotionFluidHandler;
import net.createmod.catnip.data.Pair;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.PotionContents;
import net.minecraft.world.item.alchemy.Potions;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.fluids.FluidActionResult;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.FluidUtil;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;
import net.neoforged.neoforge.items.IItemHandler;
import net.neoforged.neoforge.items.ItemStackHandler;
import net.neoforged.neoforge.items.SlotItemHandler;
import net.neoforged.neoforge.network.PacketDistributor;
import top.theillusivec4.curios.api.CuriosApi;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class VirtualTieredContainerMenu extends AbstractContainerMenu {
    private final ItemStack backStack;
    private final Player player;
    private ItemStackHandler itemHandler;
    private final List<FluidTank> fluidTanks = new ArrayList<>();
    private final List<ItemStackHandler> inputHandlers = new ArrayList<>();
    private final List<ItemStackHandler> outputHandlers = new ArrayList<>();
    private final int containerSlots;
    private final int tankCount;
    private final int tankCapacity;
    private int scrollOffset = 0;
    private static final int VISIBLE_ROWS = 6;

    private final List<SlotItemHandler> inputSlots = new ArrayList<>();
    private final List<SlotItemHandler> outputSlots = new ArrayList<>();

    // Client constructor
    public VirtualTieredContainerMenu(int id, Inventory inv, FriendlyByteBuf extraData) {
        super(ModMenus.VIRTUAL_TIERED_CONTAINER.get(), id);
        this.player = inv.player;
        this.backStack = ItemStack.EMPTY;

        this.containerSlots = extraData.readVarInt();
        this.tankCount = extraData.readVarInt();
        this.tankCapacity = extraData.readVarInt();
        CompoundTag tag = extraData.readNbt();

        buildHandlers();
        if (tag != null) loadFromNBT(tag, inv.player.level().registryAccess());
        addDedicatedSlots();
        addMainSlots();
    }

    // Server constructor
    public VirtualTieredContainerMenu(int id, Inventory inv, ItemStack backStack, ServerPlayer player) {
        super(ModMenus.VIRTUAL_TIERED_CONTAINER.get(), id);
        this.player = player;
        this.backStack = backStack;

        int slots = 54, tanks = 3, capacity = 32000;
        if (backStack.getItem() instanceof TieredContainerBlockItem blockItem) {
            slots = blockItem.getInventorySlots();
            tanks = blockItem.getFluidTankCount();
            capacity = blockItem.getFluidTankCapacity();
        }
        this.containerSlots = slots;
        this.tankCount = tanks;
        this.tankCapacity = capacity;

        buildHandlers();
        CustomData customData = backStack.getOrDefault(DataComponents.BLOCK_ENTITY_DATA, CustomData.EMPTY);
        CompoundTag tag = customData.copyTag();
        if (!tag.isEmpty()) loadFromNBT(tag, player.level().registryAccess());
        addDedicatedSlots();
        addMainSlots();
    }

    private void buildHandlers() {
        this.itemHandler = new ItemStackHandler(containerSlots) {
            @Override
            protected void onContentsChanged(int slot) {
                broadcastChanges();
            }
        };

        for (int i = 0; i < tankCount; i++) {
            fluidTanks.add(new FluidTank(tankCapacity, stack -> true));
        }

        for (int i = 0; i < tankCount; i++) {
            ItemStackHandler input = new ItemStackHandler(1) {
                @Override
                protected void onContentsChanged(int slot) {
                    broadcastChanges();
                }
                @Override
                public int getSlotLimit(int slot) {
                    return 1;
                }
            };
            inputHandlers.add(input);

            ItemStackHandler output = new ItemStackHandler(1) {
                @Override
                protected void onContentsChanged(int slot) {
                    broadcastChanges();
                }
                @Override
                public int getSlotLimit(int slot) {
                    return 1;
                }
            };
            outputHandlers.add(output);
        }
    }

    private void loadFromNBT(CompoundTag tag, HolderLookup.Provider reg) {
        ItemStackHandler savedItems = new ItemStackHandler(0);
        savedItems.deserializeNBT(reg, tag.getCompound("Inventory"));
        for (int i = 0; i < Math.min(savedItems.getSlots(), containerSlots); i++) {
            itemHandler.setStackInSlot(i, savedItems.getStackInSlot(i));
        }

        CompoundTag tanksTag = tag.getCompound("FluidTanks");
        int count = 0;
        while (tanksTag.contains("Tank" + count)) {
            if (count < fluidTanks.size()) {
                fluidTanks.get(count).readFromNBT(reg, tanksTag.getCompound("Tank" + count));
            }
            count++;
        }

        CompoundTag inputTag = tag.getCompound("InputHandlers");
        CompoundTag outputTag = tag.getCompound("OutputHandlers");
        for (int i = 0; i < tankCount; i++) {
            if (inputTag.contains("Input" + i)) {
                inputHandlers.get(i).deserializeNBT(reg, inputTag.getCompound("Input" + i));
            }
            if (outputTag.contains("Output" + i)) {
                outputHandlers.get(i).deserializeNBT(reg, outputTag.getCompound("Output" + i));
            }
        }
    }

    private void saveToStack() {
        if (backStack == null || backStack.isEmpty()) return;
        HolderLookup.Provider reg = player.level().registryAccess();
        CompoundTag tag = new CompoundTag();

        tag.put("Inventory", itemHandler.serializeNBT(reg));
        CompoundTag tanksTag = new CompoundTag();
        for (int i = 0; i < fluidTanks.size(); i++) {
            tanksTag.put("Tank" + i, fluidTanks.get(i).writeToNBT(reg, new CompoundTag()));
        }
        tag.put("FluidTanks", tanksTag);

        CompoundTag inputTag = new CompoundTag();
        for (int i = 0; i < inputHandlers.size(); i++) {
            inputTag.put("Input" + i, inputHandlers.get(i).serializeNBT(reg));
        }
        tag.put("InputHandlers", inputTag);

        CompoundTag outputTag = new CompoundTag();
        for (int i = 0; i < outputHandlers.size(); i++) {
            outputTag.put("Output" + i, outputHandlers.get(i).serializeNBT(reg));
        }
        tag.put("OutputHandlers", outputTag);

        BlockItem.setBlockEntityData(backStack, ModBlockEntities.TIERED_CONTAINER.get(), tag);

        CuriosApi.getCuriosInventory((ServerPlayer) player).ifPresent(handler -> {
            handler.getStacksHandler("back").ifPresent(stacks -> {
                stacks.getStacks().setStackInSlot(0, backStack);
            });
        });
    }

    private void addDedicatedSlots() {
        for (int i = 0; i < tankCount; i++) {
            SlotItemHandler inputSlot = new SlotItemHandler(inputHandlers.get(i), 0, 0, 0) {
                @Override
                public boolean mayPlace(ItemStack stack) {
                    if (FluidUtil.getFluidContained(stack).isPresent()) return true;
                    return stack.is(Items.HONEY_BOTTLE) || stack.getItem() instanceof net.minecraft.world.item.PotionItem;
                }
            };
            this.addSlot(inputSlot);
            this.inputSlots.add(inputSlot);

            SlotItemHandler outputSlot = new SlotItemHandler(outputHandlers.get(i), 0, 0, 0) {
                @Override
                public boolean mayPlace(ItemStack stack) {
                    if (FluidUtil.getFluidContained(stack).isPresent()) return false;
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
                addSlot(new Slot(player.getInventory(), col + row * 9 + 9, 8 + col * 18, 140 + row * 18));
            }
        }
        for (int col = 0; col < 9; ++col) {
            addSlot(new Slot(player.getInventory(), col, 8 + col * 18, 198));
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

    public int getTankCount() {
        return tankCount;
    }

    public int getScrollOffset() {
        return scrollOffset;
    }

    public int getMaxScrollOffset() {
        int totalRows = (containerSlots + 8) / 9;
        return Math.max(0, totalRows - VISIBLE_ROWS);
    }

    public List<FluidTank> getFluidTanks() {
        return fluidTanks;
    }

    public IItemHandler getItemHandler() {
        return itemHandler;
    }

    public List<ItemStackHandler> getInputHandlers() {
        return inputHandlers;
    }

    public List<ItemStackHandler> getOutputHandlers() {
        return outputHandlers;
    }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        ItemStack itemstack = ItemStack.EMPTY;
        Slot slot = this.slots.get(index);
        if (slot != null && slot.hasItem()) {
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
        return true;
    }

    @Override
    public void removed(Player player) {
        super.removed(player);
        if (!player.level().isClientSide && backStack != null && !backStack.isEmpty()) {
            processFluidSlots();
            saveToStack();
        }
    }

    @Override
    public void broadcastChanges() {
        super.broadcastChanges();
        if (!player.level().isClientSide) {
            processFluidSlots();
            syncFluidData();
        }
    }

    private void processFluidSlots() {
        processInputSlots();
        processOutputSlots();
    }

    private void processInputSlots() {
        for (int i = 0; i < tankCount; i++) {
            ItemStack input = inputHandlers.get(i).getStackInSlot(0);
            if (input.isEmpty()) continue;
            FluidTank tank = fluidTanks.get(i);
            if (isEmptyContainer(input)) continue;

            if (PotionFluidHandler.isPotionItem(input)) {
                Pair<FluidStack, ItemStack> result = PotionFluidHandler.emptyPotion(input.copy(), false);
                FluidStack fluid = result.getFirst();
                ItemStack bottle = result.getSecond();
                if (!fluid.isEmpty() && canMerge(tank, fluid)) {
                    int filled = tank.fill(fluid, IFluidHandler.FluidAction.EXECUTE);
                    if (filled > 0) {
                        inputHandlers.get(i).setStackInSlot(0, bottle);
                        broadcastChanges();
                    }
                }
                continue;
            }

            if (input.is(Items.HONEY_BOTTLE)) {
                Fluid honey = findHoneyFluid();
                if (honey != null && honey != Fluids.EMPTY) {
                    FluidStack honeyStack = new FluidStack(honey, 250);
                    if (canMerge(tank, honeyStack)) {
                        int filled = tank.fill(honeyStack, IFluidHandler.FluidAction.EXECUTE);
                        if (filled > 0) {
                            inputHandlers.get(i).setStackInSlot(0, new ItemStack(Items.GLASS_BOTTLE));
                            broadcastChanges();
                        }
                    }
                }
                continue;
            }

            Optional<FluidStack> contained = FluidUtil.getFluidContained(input);
            if (contained.isPresent()) {
                FluidStack fluid = contained.get();
                if (canMerge(tank, fluid)) {
                    FluidActionResult result = FluidUtil.tryEmptyContainer(input, tank, Integer.MAX_VALUE, null, true);
                    if (result.isSuccess()) {
                        inputHandlers.get(i).setStackInSlot(0, result.getResult());
                        broadcastChanges();
                    }
                }
            }
        }
    }

    private void processOutputSlots() {
        for (int i = 0; i < tankCount; i++) {
            ItemStack output = outputHandlers.get(i).getStackInSlot(0);
            if (output.isEmpty()) continue;
            FluidTank tank = fluidTanks.get(i);
            FluidStack tankFluid = tank.getFluid();
            if (tankFluid.isEmpty() || tank.getFluidAmount() < 250) continue;

            if (output.is(Items.GLASS_BOTTLE)) {
                if (tankFluid.getFluid() instanceof PotionFluid || tankFluid.has(DataComponents.POTION_CONTENTS)) {
                    FluidStack drained = tank.drain(250, IFluidHandler.FluidAction.SIMULATE);
                    if (drained.getAmount() == 250) {
                        tank.drain(250, IFluidHandler.FluidAction.EXECUTE);
                        ItemStack filled = PotionFluidHandler.fillBottle(output, drained);
                        outputHandlers.get(i).setStackInSlot(0, filled);
                        broadcastChanges();
                    }
                    continue;
                }

                ResourceLocation id = BuiltInRegistries.FLUID.getKey(tankFluid.getFluid());
                if (id != null && id.getPath().contains("honey")) {
                    FluidStack drained = tank.drain(250, IFluidHandler.FluidAction.SIMULATE);
                    if (drained.getAmount() == 250) {
                        tank.drain(250, IFluidHandler.FluidAction.EXECUTE);
                        outputHandlers.get(i).setStackInSlot(0, new ItemStack(Items.HONEY_BOTTLE));
                        broadcastChanges();
                    }
                    continue;
                }

                if (tankFluid.is(Fluids.WATER)) {
                    FluidStack drained = tank.drain(250, IFluidHandler.FluidAction.SIMULATE);
                    if (drained.getAmount() == 250) {
                        tank.drain(250, IFluidHandler.FluidAction.EXECUTE);
                        outputHandlers.get(i).setStackInSlot(0, PotionContents.createItemStack(Items.POTION, Potions.WATER));
                        broadcastChanges();
                    }
                    continue;
                }
            }

            if (FluidUtil.getFluidHandler(output).isPresent()) {
                FluidActionResult result = FluidUtil.tryFillContainer(output, tank, Integer.MAX_VALUE, null, true);
                if (result.isSuccess()) {
                    outputHandlers.get(i).setStackInSlot(0, result.getResult());
                    broadcastChanges();
                }
            }
        }
    }

    private boolean canMerge(FluidTank tank, FluidStack toFill) {
        if (tank.getFluid().isEmpty()) return true;
        return tank.getFluid().getFluid() == toFill.getFluid();
    }

    private boolean isEmptyContainer(ItemStack stack) {
        if (stack.isEmpty()) return true;
        if (stack.is(Items.GLASS_BOTTLE) || stack.is(Items.BUCKET)) return true;
        if (FluidUtil.getFluidHandler(stack).isPresent()) {
            return FluidUtil.getFluidContained(stack).isEmpty();
        }
        return false;
    }

    private Fluid findHoneyFluid() {
        Fluid honey = BuiltInRegistries.FLUID.get(ResourceLocation.withDefaultNamespace("honey"));
        if (honey != null && honey != Fluids.EMPTY) return honey;
        for (Fluid f : BuiltInRegistries.FLUID) {
            if (BuiltInRegistries.FLUID.getKey(f).getPath().contains("honey")) {
                return f;
            }
        }
        return Fluids.EMPTY;
    }

    private void syncFluidData() {
        if (player instanceof ServerPlayer serverPlayer) {
            List<FluidStack> fluids = new ArrayList<>();
            for (FluidTank tank : fluidTanks) {
                fluids.add(tank.getFluid());
            }
            PacketDistributor.sendToPlayer(serverPlayer, new BackTankSyncPacket(fluids));
        }
    }

    public void updateFluidTanks(List<FluidStack> fluids) {
        if (player.level().isClientSide) {
            for (int i = 0; i < Math.min(fluids.size(), fluidTanks.size()); i++) {
                fluidTanks.get(i).setFluid(fluids.get(i));
            }
        }
    }
}
