#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JAVA_SRC = os.path.join(BASE_DIR, "src", "main", "java")
PACKAGE_PATH = os.path.join("cretae", "cookiewyq", "create_cookie_conception")

def write_file(rel_path, content):
    full_path = os.path.join(JAVA_SRC, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[生成] {full_path}")

blockentity_code = '''package cretae.cookiewyq.create_cookie_conception.blockentity;

import cretae.cookiewyq.create_cookie_conception.blocks.tiered.TieredContainerBlock;
import cretae.cookiewyq.create_cookie_conception.init.ModBlockEntities;
import cretae.cookiewyq.create_cookie_conception.menu.TieredContainerMenu;
import cretae.cookiewyq.create_cookie_conception.util.TankRenderInfo;
import cretae.cookiewyq.create_cookie_conception.util.TankModelData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.*;
import net.minecraft.world.item.alchemy.PotionContents;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.client.model.data.ModelData;
import net.neoforged.neoforge.fluids.FluidActionResult;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.FluidUtil;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;
import net.neoforged.neoforge.items.ItemStackHandler;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.function.Predicate;

public class TieredContainerBlockEntity extends BlockEntity implements MenuProvider {
    private ItemStackHandler itemHandler = new ItemStackHandler(0) {
        @Override
        protected void onContentsChanged(int slot) {
            TieredContainerBlockEntity.this.onContentsChanged();
        }
    };
    private final List<FluidTank> fluidTanks = new ArrayList<>();
    private final IFluidHandler fluidHandler = new MultiTankFluidHandler(fluidTanks);
    private final List<ItemStackHandler> inputHandlers = new ArrayList<>();
    private final List<ItemStackHandler> outputHandlers = new ArrayList<>();
    private List<TankRenderInfo> tankRenderInfos = new ArrayList<>();

    // Custom tank that allows merging same-fluid stacks with different components (potion vs plain water)
    private static class CompatibleFluidTank extends FluidTank {
        public CompatibleFluidTank(int capacity, Predicate<FluidStack> validator) {
            super(capacity, validator);
        }

        @Override
        public int fill(FluidStack resource, FluidAction action) {
            if (resource.isEmpty() || !isFluidValid(resource)) return 0;
            if (this.fluid.isEmpty()) {
                int amount = Math.min(capacity, resource.getAmount());
                if (action.execute()) {
                    this.fluid = resource.copy();
                    this.fluid.setAmount(amount);
                    onContentsChanged();
                }
                return amount;
            }
            // Allow mixing if the fluid type matches (ignore components)
            if (this.fluid.getFluid() == resource.getFluid()) {
                int space = capacity - this.fluid.getAmount();
                int amount = Math.min(space, resource.getAmount());
                if (amount <= 0) return 0;
                if (action.execute()) {
                    this.fluid.setAmount(this.fluid.getAmount() + amount);
                    // If the incoming fluid has richer components (e.g., PotionContents), overwrite existing ones
                    if (resource.has(DataComponents.POTION_CONTENTS)) {
                        this.fluid.set(DataComponents.POTION_CONTENTS, resource.get(DataComponents.POTION_CONTENTS));
                    }
                    onContentsChanged();
                }
                return amount;
            }
            return 0;
        }
    }

    public TieredContainerBlockEntity(BlockEntityType<TieredContainerBlockEntity> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    private void applyCapacityFromBlock() {
        if (level != null && getBlockState().getBlock() instanceof TieredContainerBlock tiered) {
            int targetSlots = tiered.getInventorySlots();
            int targetTanks = tiered.getFluidTankCount();
            int targetCap = tiered.getFluidTankCapacity();

            ItemStackHandler oldItems = itemHandler;
            itemHandler = new ItemStackHandler(targetSlots) {
                @Override
                protected void onContentsChanged(int slot) {
                    TieredContainerBlockEntity.this.onContentsChanged();
                }
            };
            for (int i = 0; i < Math.min(oldItems.getSlots(), targetSlots); i++) {
                itemHandler.setStackInSlot(i, oldItems.getStackInSlot(i));
            }

            List<FluidStack> oldFluids = new ArrayList<>();
            for (FluidTank tank : fluidTanks) oldFluids.add(tank.getFluid().copy());

            fluidTanks.clear();
            for (int i = 0; i < targetTanks; i++) {
                fluidTanks.add(new CompatibleFluidTank(targetCap, stack -> true));
            }
            for (int i = 0; i < oldFluids.size(); i++) {
                FluidStack fs = oldFluids.get(i);
                if (!fs.isEmpty() && i < fluidTanks.size()) {
                    fluidTanks.get(i).fill(fs, IFluidHandler.FluidAction.EXECUTE);
                }
            }

            List<ItemStackHandler> oldInputs = new ArrayList<>(inputHandlers);
            List<ItemStackHandler> oldOutputs = new ArrayList<>(outputHandlers);
            inputHandlers.clear();
            outputHandlers.clear();
            for (int i = 0; i < targetTanks; i++) {
                ItemStackHandler input = new ItemStackHandler(1) {
                    @Override
                    protected void onContentsChanged(int slot) {
                        TieredContainerBlockEntity.this.onContentsChanged();
                        TieredContainerBlockEntity.this.onInputSlotChanged(getSlotIndex(this));
                    }
                    @Override
                    public int getSlotLimit(int slot) { return 1; }
                };
                if (i < oldInputs.size()) input.setStackInSlot(0, oldInputs.get(i).getStackInSlot(0));
                inputHandlers.add(input);

                ItemStackHandler output = new ItemStackHandler(1) {
                    @Override
                    protected void onContentsChanged(int slot) {
                        TieredContainerBlockEntity.this.onContentsChanged();
                        TieredContainerBlockEntity.this.onOutputSlotChanged(getSlotIndex(this));
                    }
                    @Override
                    public int getSlotLimit(int slot) { return 1; }
                };
                if (i < oldOutputs.size()) output.setStackInSlot(0, oldOutputs.get(i).getStackInSlot(0));
                outputHandlers.add(output);
            }

            updateRenderInfo();
        }
    }

    private int getSlotIndex(ItemStackHandler handler) {
        for (int i = 0; i < inputHandlers.size(); i++)
            if (inputHandlers.get(i) == handler) return i;
        for (int i = 0; i < outputHandlers.size(); i++)
            if (outputHandlers.get(i) == handler) return i;
        return -1;
    }

    private void onInputSlotChanged(int index) {
        if (index < 0 || index >= inputHandlers.size()) return;
        if (level == null || level.isClientSide) return;
        ItemStackHandler input = inputHandlers.get(index);
        FluidTank tank = fluidTanks.get(index);
        ItemStack stack = input.getStackInSlot(0);
        if (stack.isEmpty()) return;
        if (isEmptyContainer(stack)) return;

        FluidStack fluidToFill = null;
        ItemStack emptyResult = null;

        Optional<FluidStack> containedOpt = FluidUtil.getFluidContained(stack);
        if (containedOpt.isPresent()) {
            fluidToFill = containedOpt.get().copy();
            FluidActionResult simResult = FluidUtil.tryEmptyContainer(stack.copy(), tank, Integer.MAX_VALUE, null, false);
            if (simResult.isSuccess()) {
                emptyResult = simResult.getResult().copy();
            } else {
                if (stack.getItem() == Items.WATER_BUCKET || stack.getItem() == Items.LAVA_BUCKET || stack.getItem() == Items.MILK_BUCKET) {
                    emptyResult = new ItemStack(Items.BUCKET);
                } else {
                    return;
                }
            }
        } else if (stack.getItem() instanceof PotionItem) {
            PotionContents contents = stack.get(DataComponents.POTION_CONTENTS);
            if (contents == null || contents.equals(PotionContents.EMPTY)) return;
            fluidToFill = new FluidStack(Fluids.WATER, 250);
            fluidToFill.set(DataComponents.POTION_CONTENTS, contents);
            emptyResult = new ItemStack(Items.GLASS_BOTTLE);
        } else if (stack.is(Items.HONEY_BOTTLE)) {
            Fluid honeyFluid = BuiltInRegistries.FLUID.get(ResourceLocation.withDefaultNamespace("honey"));
            if (honeyFluid == null || honeyFluid == Fluids.EMPTY) {
                for (Fluid f : BuiltInRegistries.FLUID) {
                    if (BuiltInRegistries.FLUID.getKey(f).getPath().contains("honey")) {
                        honeyFluid = f;
                        break;
                    }
                }
                if (honeyFluid == Fluids.EMPTY) return;
            }
            fluidToFill = new FluidStack(honeyFluid, 250);
            emptyResult = new ItemStack(Items.GLASS_BOTTLE);
        }

        if (fluidToFill == null || emptyResult == null) return;

        if (!tank.isFluidValid(fluidToFill)) return;
        if (!tank.getFluid().isEmpty() && tank.getFluid().getFluid() != fluidToFill.getFluid()) return;
        int space = tank.getCapacity() - tank.getFluidAmount();
        if (space < fluidToFill.getAmount()) return;

        int filled = tank.fill(fluidToFill, IFluidHandler.FluidAction.EXECUTE);
        if (filled > 0) {
            input.setStackInSlot(0, ItemStack.EMPTY);
            input.setStackInSlot(0, emptyResult);
        }
    }

    private boolean isEmptyContainer(ItemStack stack) {
        if (stack.isEmpty()) return true;
        if (stack.is(Items.GLASS_BOTTLE) || stack.is(Items.BUCKET)) return true;
        if (FluidUtil.getFluidHandler(stack).isPresent()) {
            return FluidUtil.getFluidContained(stack).isEmpty();
        }
        return false;
    }

    private void onOutputSlotChanged(int index) {
        if (index < 0 || index >= outputHandlers.size()) return;
        if (level == null || level.isClientSide) return;
        ItemStackHandler output = outputHandlers.get(index);
        FluidTank tank = fluidTanks.get(index);
        ItemStack stack = output.getStackInSlot(0);
        if (stack.isEmpty()) return;

        if (FluidUtil.getFluidContained(stack).isPresent()) return;

        if (stack.is(Items.GLASS_BOTTLE)) {
            FluidStack tankFluid = tank.getFluid();
            if (tankFluid.isEmpty() || tank.getFluidAmount() < 250) return;

            PotionContents potionContents = tankFluid.get(DataComponents.POTION_CONTENTS);
            if (potionContents != null && !potionContents.equals(PotionContents.EMPTY)) {
                FluidStack drained = tank.drain(250, IFluidHandler.FluidAction.SIMULATE);
                if (drained.getAmount() == 250) {
                    tank.drain(250, IFluidHandler.FluidAction.EXECUTE);
                    ItemStack potionStack = new ItemStack(Items.POTION);
                    potionStack.set(DataComponents.POTION_CONTENTS, potionContents);
                    output.setStackInSlot(0, potionStack);
                }
                return;
            }

            ResourceLocation fluidName = BuiltInRegistries.FLUID.getKey(tankFluid.getFluid());
            if (fluidName != null && fluidName.getPath().contains("honey")) {
                FluidStack drained = tank.drain(250, IFluidHandler.FluidAction.SIMULATE);
                if (drained.getAmount() == 250) {
                    tank.drain(250, IFluidHandler.FluidAction.EXECUTE);
                    output.setStackInSlot(0, new ItemStack(Items.HONEY_BOTTLE));
                }
                return;
            }

            if (tankFluid.is(Fluids.WATER)) {
                FluidStack drained = tank.drain(250, IFluidHandler.FluidAction.SIMULATE);
                if (drained.getAmount() == 250) {
                    tank.drain(250, IFluidHandler.FluidAction.EXECUTE);
                    output.setStackInSlot(0, PotionContents.createItemStack(Items.POTION, net.minecraft.world.item.alchemy.Potions.WATER));
                }
                return;
            }
            return;
        }

        if (FluidUtil.getFluidHandler(stack).isPresent()) {
            FluidActionResult result = FluidUtil.tryFillContainer(stack, tank, Integer.MAX_VALUE, null, true);
            if (result.isSuccess()) {
                output.setStackInSlot(0, result.getResult());
            }
        }
    }

    private void updateRenderInfo() {
        tankRenderInfos.clear();
        for (FluidTank tank : fluidTanks) {
            FluidStack fluid = tank.getFluid();
            float ratio = tank.getCapacity() > 0 ? (float) fluid.getAmount() / tank.getCapacity() : 0f;
            tankRenderInfos.add(new TankRenderInfo(fluid, ratio));
        }
    }

    @Override
    public void onLoad() { super.onLoad(); applyCapacityFromBlock(); }

    @Override
    public void setBlockState(BlockState state) {
        super.setBlockState(state);
        applyCapacityFromBlock();
    }

    public ItemStackHandler getItemHandler() { return itemHandler; }
    public List<FluidTank> getFluidTanks() { return fluidTanks; }
    public IFluidHandler getFluidHandler() { return fluidHandler; }
    public List<TankRenderInfo> getTankRenderInfos() { return tankRenderInfos; }
    public List<ItemStackHandler> getInputHandlers() { return inputHandlers; }
    public List<ItemStackHandler> getOutputHandlers() { return outputHandlers; }

    public int getTotalItemCount() {
        int count = 0;
        for (int i = 0; i < itemHandler.getSlots(); i++) if (!itemHandler.getStackInSlot(i).isEmpty()) count++;
        return count;
    }

    @Override
    public @NotNull ModelData getModelData() {
        if (tankRenderInfos.isEmpty()) return ModelData.EMPTY;
        return ModelData.builder().with(TankModelData.TANK_RENDER_INFO, tankRenderInfos.get(0)).build();
    }

    @Override
    public void saveAdditional(CompoundTag tag, HolderLookup.Provider reg) {
        super.saveAdditional(tag, reg);
        tag.put("Inventory", itemHandler.serializeNBT(reg));
        CompoundTag tanksTag = new CompoundTag();
        for (int i = 0; i < fluidTanks.size(); i++)
            tanksTag.put("Tank" + i, fluidTanks.get(i).writeToNBT(reg, new CompoundTag()));
        tag.put("FluidTanks", tanksTag);
        CompoundTag inputTag = new CompoundTag();
        for (int i = 0; i < inputHandlers.size(); i++)
            inputTag.put("Input" + i, inputHandlers.get(i).serializeNBT(reg));
        tag.put("InputHandlers", inputTag);
        CompoundTag outputTag = new CompoundTag();
        for (int i = 0; i < outputHandlers.size(); i++)
            outputTag.put("Output" + i, outputHandlers.get(i).serializeNBT(reg));
        tag.put("OutputHandlers", outputTag);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider reg) {
        super.loadAdditional(tag, reg);
        ItemStackHandler savedItems = new ItemStackHandler(0);
        savedItems.deserializeNBT(reg, tag.getCompound("Inventory"));
        List<FluidTank> savedTanks = new ArrayList<>();
        CompoundTag tanksTag = tag.getCompound("FluidTanks");
        int count = 0;
        while (tanksTag.contains("Tank" + count)) {
            FluidTank tank = new CompatibleFluidTank(1000, stack -> true);
            tank.readFromNBT(reg, tanksTag.getCompound("Tank" + count));
            savedTanks.add(tank);
            count++;
        }
        if (getBlockState().getBlock() instanceof TieredContainerBlock tiered) {
            int targetSlots = tiered.getInventorySlots();
            int targetTanks = tiered.getFluidTankCount();
            int targetCap = tiered.getFluidTankCapacity();
            itemHandler = new ItemStackHandler(targetSlots) {
                @Override
                protected void onContentsChanged(int slot) { TieredContainerBlockEntity.this.onContentsChanged(); }
            };
            for (int i = 0; i < Math.min(savedItems.getSlots(), targetSlots); i++)
                itemHandler.setStackInSlot(i, savedItems.getStackInSlot(i));
            fluidTanks.clear();
            for (int i = 0; i < targetTanks; i++) {
                fluidTanks.add(new CompatibleFluidTank(targetCap, stack -> true));
            }
            for (int i = 0; i < savedTanks.size(); i++) {
                if (i < fluidTanks.size()) fluidTanks.get(i).fill(savedTanks.get(i).getFluid(), IFluidHandler.FluidAction.EXECUTE);
            }
            inputHandlers.clear();
            outputHandlers.clear();
            CompoundTag inputTag = tag.getCompound("InputHandlers");
            CompoundTag outputTag = tag.getCompound("OutputHandlers");
            for (int i = 0; i < targetTanks; i++) {
                ItemStackHandler input = new ItemStackHandler(1) {
                    @Override
                    protected void onContentsChanged(int slot) {
                        TieredContainerBlockEntity.this.onContentsChanged();
                        TieredContainerBlockEntity.this.onInputSlotChanged(getSlotIndex(this));
                    }
                    @Override public int getSlotLimit(int slot) { return 1; }
                };
                if (inputTag.contains("Input" + i)) input.deserializeNBT(reg, inputTag.getCompound("Input" + i));
                inputHandlers.add(input);
                ItemStackHandler output = new ItemStackHandler(1) {
                    @Override
                    protected void onContentsChanged(int slot) {
                        TieredContainerBlockEntity.this.onContentsChanged();
                        TieredContainerBlockEntity.this.onOutputSlotChanged(getSlotIndex(this));
                    }
                    @Override public int getSlotLimit(int slot) { return 1; }
                };
                if (outputTag.contains("Output" + i)) output.deserializeNBT(reg, outputTag.getCompound("Output" + i));
                outputHandlers.add(output);
            }
            updateRenderInfo();
        } else {
            itemHandler = savedItems;
            fluidTanks.clear();
            fluidTanks.addAll(savedTanks);
        }
    }

    @Override
    public Component getDisplayName() {
        return Component.translatable("block.create_cookie_conception." +
                getBlockState().getBlock().getDescriptionId().replace("block.create_cookie_conception.", ""));
    }

    @Nullable @Override
    public AbstractContainerMenu createMenu(int id, Inventory inv, Player player) {
        return new TieredContainerMenu(id, inv, this);
    }

    @Nullable @Override public ClientboundBlockEntityDataPacket getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
    @Override public CompoundTag getUpdateTag(HolderLookup.Provider reg) { return saveWithoutMetadata(reg); }
    @Override public void onDataPacket(Connection net, ClientboundBlockEntityDataPacket pkt, HolderLookup.Provider reg) {
        loadAdditional(pkt.getTag(), reg);
        if (level != null && level.isClientSide) {
            requestModelDataUpdate();
            level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
        }
    }

    public void onContentsChanged() {
        setChanged();
        updateRenderInfo();
        if (level != null) {
            if (!level.isClientSide) {
                level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
            } else {
                requestModelDataUpdate();
                level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
            }
        }
    }

    public CompoundTag getPersistentData(HolderLookup.Provider reg) {
        CompoundTag tag = new CompoundTag();
        this.saveAdditional(tag, reg);
        return tag;
    }

    private static class MultiTankFluidHandler implements IFluidHandler {
        private final List<FluidTank> tanks;
        MultiTankFluidHandler(List<FluidTank> tanks) { this.tanks = tanks; }

        @Override public int getTanks() { return tanks.size(); }
        @Override public @NotNull FluidStack getFluidInTank(int tank) { return tanks.get(tank).getFluid(); }
        @Override public int getTankCapacity(int tank) { return tanks.get(tank).getCapacity(); }
        @Override public boolean isFluidValid(int tank, @NotNull FluidStack stack) { return tanks.get(tank).isFluidValid(stack); }

        @Override
        public int fill(FluidStack resource, FluidAction action) {
            if (resource.isEmpty()) return 0;
            // Prefer tanks with matching fluid type (ignore components)
            for (FluidTank tank : tanks) {
                if (!tank.getFluid().isEmpty() && tank.getFluid().getFluid() == resource.getFluid()) {
                    int filled = tank.fill(resource, action);
                    if (filled > 0) return filled;
                }
            }
            // Then empty tanks
            for (FluidTank tank : tanks) {
                if (tank.getFluid().isEmpty()) {
                    return tank.fill(resource, action);
                }
            }
            return 0;
        }

        @Override
        public @NotNull FluidStack drain(FluidStack resource, FluidAction action) {
            if (resource.isEmpty()) return FluidStack.EMPTY;
            for (FluidTank tank : tanks) {
                if (!tank.getFluid().isEmpty() && tank.getFluid().getFluid() == resource.getFluid()) {
                    int amount = Math.min(resource.getAmount(), tank.getFluidAmount());
                    FluidStack drained = tank.drain(amount, action);
                    if (!drained.isEmpty()) return drained;
                }
            }
            return FluidStack.EMPTY;
        }

        @Override
        public @NotNull FluidStack drain(int maxDrain, FluidAction action) {
            for (FluidTank tank : tanks) if (!tank.getFluid().isEmpty()) return tank.drain(maxDrain, action);
            return FluidStack.EMPTY;
        }
    }
}
'''

if __name__ == "__main__":
    write_file(os.path.join(PACKAGE_PATH, "blockentity", "TieredContainerBlockEntity.java"), blockentity_code)
    print("\n兼容性修复：自定义 CompatibleFluidTank 允许同流体类型不同组件混合，药水瓶与动力泵药水现在可互相填充。")