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

# ==================== TieredContainerBlockEntity.java ====================
blockentity_code = '''package cretae.cookiewyq.create_cookie_conception.blockentity;

import cretae.cookiewyq.create_cookie_conception.blocks.tiered.TieredContainerBlock;
import cretae.cookiewyq.create_cookie_conception.init.ModBlockEntities;
import cretae.cookiewyq.create_cookie_conception.menu.TieredContainerMenu;
import cretae.cookiewyq.create_cookie_conception.util.TankRenderInfo;
import cretae.cookiewyq.create_cookie_conception.util.TankModelData;
import net.minecraft.client.Minecraft;
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
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.*;
import net.minecraft.world.item.alchemy.PotionContents;
import net.minecraft.world.item.alchemy.Potions;
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

import com.simibubi.create.AllDataComponents;
import com.simibubi.create.content.fluids.potion.PotionFluid;
import com.simibubi.create.content.fluids.potion.PotionFluidHandler;
import net.createmod.catnip.data.Pair;

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

    private static boolean arePotionsEquivalent(PotionContents a, PotionContents b) {
        if (a == null || b == null) return false;
        List<MobEffectInstance> effectsA = new ArrayList<>();
        for (MobEffectInstance e : a.getAllEffects()) effectsA.add(e);
        List<MobEffectInstance> effectsB = new ArrayList<>();
        for (MobEffectInstance e : b.getAllEffects()) effectsB.add(e);
        if (effectsA.size() != effectsB.size()) return false;
        for (int i = 0; i < effectsA.size(); i++) {
            MobEffectInstance ea = effectsA.get(i);
            MobEffectInstance eb = effectsB.get(i);
            if (ea.getEffect().value() != eb.getEffect().value()) return false;
            if (ea.getAmplifier() != eb.getAmplifier()) return false;
            if (ea.getDuration() != eb.getDuration()) return false;
        }
        return true;
    }

    private static boolean canInternalInputMerge(FluidTank tank, FluidStack toFill) {
        if (tank.getFluid().isEmpty()) return true;
        Fluid existingFluid = tank.getFluid().getFluid();
        Fluid incomingFluid = toFill.getFluid();
        if (!(existingFluid == Fluids.WATER || existingFluid instanceof PotionFluid) ||
            !(incomingFluid == Fluids.WATER || incomingFluid instanceof PotionFluid)) {
            return existingFluid == incomingFluid;
        }
        if (existingFluid == Fluids.WATER && incomingFluid instanceof PotionFluid) return false;
        if (existingFluid instanceof PotionFluid && incomingFluid == Fluids.WATER) return false;
        if (existingFluid instanceof PotionFluid && incomingFluid instanceof PotionFluid) {
            PotionContents existingPotion = tank.getFluid().get(DataComponents.POTION_CONTENTS);
            PotionContents incomingPotion = toFill.get(DataComponents.POTION_CONTENTS);
            return arePotionsEquivalent(existingPotion, incomingPotion);
        }
        return existingFluid == incomingFluid;
    }

    // Custom tank that allows merging via forceMix parameter, with public trigger
    private static class TieredFluidTank extends FluidTank {
        public TieredFluidTank(int capacity, Predicate<FluidStack> validator) {
            super(capacity, validator);
        }

        public int mergeFluid(FluidStack resource, FluidAction action, boolean forceMix) {
            if (resource.isEmpty() || !isFluidValid(resource)) return 0;
            if (this.fluid.isEmpty()) {
                return fill(resource, action);
            }
            if (forceMix) {
                int space = capacity - this.fluid.getAmount();
                int amount = Math.min(space, resource.getAmount());
                if (amount <= 0) return 0;
                if (action.execute()) {
                    this.fluid.setAmount(this.fluid.getAmount() + amount);
                    if (resource.has(DataComponents.POTION_CONTENTS)) {
                        this.fluid.set(DataComponents.POTION_CONTENTS, resource.get(DataComponents.POTION_CONTENTS));
                    }
                    if (resource.has(AllDataComponents.POTION_FLUID_BOTTLE_TYPE)) {
                        this.fluid.set(AllDataComponents.POTION_FLUID_BOTTLE_TYPE, resource.get(AllDataComponents.POTION_FLUID_BOTTLE_TYPE));
                    }
                    onContentsChanged();
                }
                return amount;
            }
            if (this.fluid.getFluid() == resource.getFluid()) {
                return fill(resource, action);
            }
            return 0;
        }

        // Public method to force trigger onContentsChanged externally
        public void fireOnChanged() {
            onContentsChanged();
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
                fluidTanks.add(new TieredFluidTank(targetCap, stack -> true) {
                    @Override
                    protected void onContentsChanged() {
                        TieredContainerBlockEntity.this.onContentsChanged();
                    }
                });
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

        if (PotionFluidHandler.isPotionItem(stack)) {
            Pair<FluidStack, ItemStack> simEmpty = PotionFluidHandler.emptyPotion(stack.copy(), true);
            FluidStack potionFluid = simEmpty.getFirst();
            ItemStack emptyBottle = simEmpty.getSecond();
            if (!tank.isFluidValid(potionFluid)) return;
            if (!canInternalInputMerge(tank, potionFluid)) return;
            int space = tank.getCapacity() - tank.getFluidAmount();
            if (space < potionFluid.getAmount()) return;
            Pair<FluidStack, ItemStack> execEmpty = PotionFluidHandler.emptyPotion(stack.copy(), false);
            FluidStack execFluid = execEmpty.getFirst();
            ItemStack execBottle = execEmpty.getSecond();
            int filled;
            if (tank instanceof TieredFluidTank tf) {
                filled = tf.mergeFluid(execFluid, IFluidHandler.FluidAction.EXECUTE, true);
            } else {
                filled = tank.fill(execFluid, IFluidHandler.FluidAction.EXECUTE);
            }
            if (filled > 0) {
                input.setStackInSlot(0, ItemStack.EMPTY);
                input.setStackInSlot(0, execBottle);
            }
            return;
        }

        if (stack.is(Items.HONEY_BOTTLE)) {
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
            FluidStack fluidToFill = new FluidStack(honeyFluid, 250);
            ItemStack emptyBottle = new ItemStack(Items.GLASS_BOTTLE);
            if (!tank.isFluidValid(fluidToFill)) return;
            if (!canInternalInputMerge(tank, fluidToFill)) return;
            int space = tank.getCapacity() - tank.getFluidAmount();
            if (space < fluidToFill.getAmount()) return;
            int filled;
            if (tank instanceof TieredFluidTank tf) {
                filled = tf.mergeFluid(fluidToFill, IFluidHandler.FluidAction.EXECUTE, true);
            } else {
                filled = tank.fill(fluidToFill, IFluidHandler.FluidAction.EXECUTE);
            }
            if (filled > 0) {
                input.setStackInSlot(0, ItemStack.EMPTY);
                input.setStackInSlot(0, emptyBottle);
            }
            return;
        }

        Optional<FluidStack> containedOpt = FluidUtil.getFluidContained(stack);
        if (containedOpt.isPresent()) {
            FluidStack fluidToFill = containedOpt.get().copy();
            FluidActionResult simResult = FluidUtil.tryEmptyContainer(stack.copy(), tank, Integer.MAX_VALUE, null, false);
            ItemStack emptyResult;
            if (simResult.isSuccess()) {
                emptyResult = simResult.getResult().copy();
            } else {
                if (stack.getItem() == Items.WATER_BUCKET || stack.getItem() == Items.LAVA_BUCKET || stack.getItem() == Items.MILK_BUCKET) {
                    emptyResult = new ItemStack(Items.BUCKET);
                } else {
                    return;
                }
            }
            if (!tank.isFluidValid(fluidToFill)) return;
            if (!canInternalInputMerge(tank, fluidToFill)) return;
            int space = tank.getCapacity() - tank.getFluidAmount();
            if (space < fluidToFill.getAmount()) return;
            int filled;
            if (tank instanceof TieredFluidTank tf) {
                filled = tf.mergeFluid(fluidToFill, IFluidHandler.FluidAction.EXECUTE, true);
            } else {
                filled = tank.fill(fluidToFill, IFluidHandler.FluidAction.EXECUTE);
            }
            if (filled > 0) {
                input.setStackInSlot(0, ItemStack.EMPTY);
                input.setStackInSlot(0, emptyResult);
            }
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

            if (tankFluid.getFluid() instanceof PotionFluid || tankFluid.has(DataComponents.POTION_CONTENTS)) {
                FluidStack drained = tank.drain(250, IFluidHandler.FluidAction.SIMULATE);
                if (drained.getAmount() == 250) {
                    tank.drain(250, IFluidHandler.FluidAction.EXECUTE);
                    ItemStack filled = PotionFluidHandler.fillBottle(stack, drained);
                    output.setStackInSlot(0, filled);
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
                    output.setStackInSlot(0, PotionContents.createItemStack(Items.POTION, Potions.WATER));
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
            FluidTank tank = new TieredFluidTank(1000, stack -> true);
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
                fluidTanks.add(new TieredFluidTank(targetCap, stack -> true) {
                    @Override
                    protected void onContentsChanged() { TieredContainerBlockEntity.this.onContentsChanged(); }
                });
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

        public int fillTank(int index, FluidStack resource, FluidAction action, boolean forceMix) {
            if (index < 0 || index >= tanks.size()) return 0;
            FluidTank tank = tanks.get(index);
            if (tank instanceof TieredFluidTank tf) {
                return tf.mergeFluid(resource, action, forceMix);
            } else {
                FluidStack existing = tank.getFluid();
                if (existing.isEmpty()) return tank.fill(resource, action);
                boolean compatible = forceMix ? canInternalInputMerge(tank, resource) : existing.getFluid() == resource.getFluid();
                if (compatible) {
                    int space = tank.getCapacity() - existing.getAmount();
                    int amount = Math.min(space, resource.getAmount());
                    if (amount <= 0) return 0;
                    if (action.execute()) {
                        existing.setAmount(existing.getAmount() + amount);
                        if (resource.has(DataComponents.POTION_CONTENTS)) {
                            existing.set(DataComponents.POTION_CONTENTS, resource.get(DataComponents.POTION_CONTENTS));
                        }
                        if (resource.has(AllDataComponents.POTION_FLUID_BOTTLE_TYPE)) {
                            existing.set(AllDataComponents.POTION_FLUID_BOTTLE_TYPE, resource.get(AllDataComponents.POTION_FLUID_BOTTLE_TYPE));
                        }
                        if (tank instanceof TieredFluidTank tf) {
                            tf.fireOnChanged();
                        } else {
                            tank.fill(FluidStack.EMPTY, FluidAction.EXECUTE);
                        }
                    }
                    return amount;
                }
                return 0;
            }
        }

        @Override
        public int fill(FluidStack resource, FluidAction action) {
            if (resource.isEmpty()) return 0;
            for (int i = 0; i < tanks.size(); i++) {
                FluidTank tank = tanks.get(i);
                if (!tank.getFluid().isEmpty() && tank.getFluid().getFluid() == resource.getFluid()) {
                    int filled = fillTank(i, resource, action, false);
                    if (filled > 0) return filled;
                }
            }
            for (int i = 0; i < tanks.size(); i++) {
                FluidTank tank = tanks.get(i);
                if (tank.getFluid().isEmpty()) {
                    return fillTank(i, resource, action, false);
                }
            }
            return 0;
        }

        @Override
        public @NotNull FluidStack drain(FluidStack resource, FluidAction action) {
            if (resource.isEmpty()) return FluidStack.EMPTY;
            for (FluidTank tank : tanks) {
                FluidStack existing = tank.getFluid();
                if (!existing.isEmpty() && existing.getFluid() == resource.getFluid()) {
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

# ==================== TieredContainerScreen.java ====================
screen_code = '''package cretae.cookiewyq.create_cookie_conception.screen;

import cretae.cookiewyq.create_cookie_conception.menu.TieredContainerMenu;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.PotionContents;
import net.neoforged.neoforge.client.extensions.common.IClientFluidTypeExtensions;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;

import java.lang.reflect.Field;
import java.util.*;

public class TieredContainerScreen extends AbstractContainerScreen<TieredContainerMenu> {
    private static final ResourceLocation TEXTURE = ResourceLocation.fromNamespaceAndPath("minecraft", "textures/gui/container/generic_54.png");
    private static final int VISIBLE_ROWS = 6;
    private static final int FLUID_BAR_WIDTH = 18;
    private static final int FLUID_BAR_HEIGHT = VISIBLE_ROWS * 18;
    private static final int FLUID_GAP = 2;
    private static final int TILE_SIZE = 16;
    private boolean isDraggingScroll = false;

    private final Map<ResourceLocation, TextureAtlasSprite> spriteCache = new HashMap<>();

    public TieredContainerScreen(TieredContainerMenu menu, Inventory inv, Component title) {
        super(menu, inv, title);
        this.imageWidth = 176;
        this.imageHeight = 222;
        this.inventoryLabelY = this.imageHeight - 94;
    }

    @Override
    protected void renderBg(GuiGraphics graphics, float partialTick, int mouseX, int mouseY) {
        RenderSystem.setShaderTexture(0, TEXTURE);
        graphics.blit(TEXTURE, leftPos, topPos, 0, 0, imageWidth, imageHeight);

        if (menu.getBlockEntity() == null) return;
        List<FluidTank> tanks = menu.getBlockEntity().getFluidTanks();
        int tankCount = tanks.size();
        if (tankCount == 0) return;

        int totalWidth = tankCount * FLUID_BAR_WIDTH + (tankCount - 1) * FLUID_GAP;
        int startX = leftPos - totalWidth;
        int startY = topPos + 18;

        for (int i = 0; i < tankCount; i++) {
            int x = startX + i * (FLUID_BAR_WIDTH + FLUID_GAP);
            int slotY = startY + FLUID_BAR_HEIGHT + 4;
            Slot inputSlot = menu.slots.get(i * 2);
            setSlotPosition(inputSlot, x - leftPos + 1, slotY - topPos + 1);
            Slot outputSlot = menu.slots.get(i * 2 + 1);
            setSlotPosition(outputSlot, x - leftPos + 1, slotY + 20 - topPos + 1);
        }

        // ---------- Fluid rendering, DO NOT MODIFY ----------
        for (int i = 0; i < tankCount; i++) {
            int x = startX + i * (FLUID_BAR_WIDTH + FLUID_GAP);
            int y = startY;
            FluidTank tank = tanks.get(i);
            FluidStack fluid = tank.getFluid();

            graphics.fill(x, y, x + FLUID_BAR_WIDTH, y + FLUID_BAR_HEIGHT, 0xFFFFFFFF);

            if (fluid.isEmpty()) continue;

            int capacity = tank.getCapacity();
            int amount = fluid.getAmount();
            if (amount <= 0) continue;

            int fluidHeight = (int) (FLUID_BAR_HEIGHT * ((float) amount / capacity));
            if (fluidHeight <= 0) continue;

            boolean lighterThanAir = fluid.getFluidType().isLighterThanAir();
            int drawY = lighterThanAir ? y : y + FLUID_BAR_HEIGHT - fluidHeight;

            IClientFluidTypeExtensions extensions = IClientFluidTypeExtensions.of(fluid.getFluid());
            ResourceLocation stillTexture = extensions.getStillTexture(fluid);

            TextureAtlasSprite sprite = spriteCache.computeIfAbsent(stillTexture, loc ->
                    Minecraft.getInstance().getTextureAtlas(InventoryMenu.BLOCK_ATLAS).apply(loc)
            );

            if (sprite == null) continue;

            int tintColor = extensions.getTintColor(fluid);
            float a = ((tintColor >> 24) & 0xFF) / 255.0F;
            float r = ((tintColor >> 16) & 0xFF) / 255.0F;
            float g = ((tintColor >> 8) & 0xFF) / 255.0F;
            float b = (tintColor & 0xFF) / 255.0F;

            RenderSystem.setShaderTexture(0, InventoryMenu.BLOCK_ATLAS);
            RenderSystem.enableBlend();
            RenderSystem.defaultBlendFunc();
            RenderSystem.setShaderColor(r, g, b, a);

            int fullTiles = fluidHeight / TILE_SIZE;
            int remainingPixels = fluidHeight % TILE_SIZE;

            for (int tile = 0; tile < fullTiles; tile++) {
                int tileY = drawY + fluidHeight - (tile + 1) * TILE_SIZE;
                graphics.blit(x, tileY, 0, FLUID_BAR_WIDTH, TILE_SIZE, sprite);
            }

            if (remainingPixels > 0) {
                graphics.enableScissor(x, drawY, x + FLUID_BAR_WIDTH, drawY + remainingPixels);
                graphics.blit(x, drawY, 0, FLUID_BAR_WIDTH, TILE_SIZE, sprite);
                graphics.disableScissor();
            }

            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
            RenderSystem.disableBlend();
        }
        // ---------- End of fluid rendering block ----------

        for (int i = 0; i < tankCount; i++) {
            int x = startX + i * (FLUID_BAR_WIDTH + FLUID_GAP);
            int inputY = startY + FLUID_BAR_HEIGHT + 4;
            int outputY = inputY + 20;

            graphics.fill(x, inputY, x + 18, inputY + 18, 0xFF404040);
            graphics.renderOutline(x, inputY, 18, 18, 0xFFFFFFFF);
            graphics.drawCenteredString(font, "I", x + 9, inputY + 5, 0xFFFFFF);

            graphics.fill(x, outputY, x + 18, outputY + 18, 0xFF404040);
            graphics.renderOutline(x, outputY, 18, 18, 0xFFFFFFFF);
            graphics.drawCenteredString(font, "O", x + 9, outputY + 5, 0xFFFFFF);
        }

        drawScrollBar(graphics);
    }

    private void setSlotPosition(Slot slot, int x, int y) {
        try {
            Field fX = Slot.class.getDeclaredField("x");
            Field fY = Slot.class.getDeclaredField("y");
            Field modifiers = Field.class.getDeclaredField("modifiers");
            modifiers.setAccessible(true);
            modifiers.setInt(fX, fX.getModifiers() & ~java.lang.reflect.Modifier.FINAL);
            modifiers.setInt(fY, fY.getModifiers() & ~java.lang.reflect.Modifier.FINAL);
            fX.setAccessible(true);
            fY.setAccessible(true);
            fX.setInt(slot, x);
            fY.setInt(slot, y);
        } catch (Exception e) {
            try {
                Field fX = Slot.class.getDeclaredField("x");
                Field fY = Slot.class.getDeclaredField("y");
                fX.setAccessible(true);
                fY.setAccessible(true);
                fX.setInt(slot, x);
                fY.setInt(slot, y);
            } catch (Exception ignored) {}
        }
    }

    private void drawScrollBar(GuiGraphics graphics) {
        int maxOffset = menu.getMaxScrollOffset();
        if (maxOffset <= 0) return;

        int barX = leftPos + imageWidth + 4;
        int barY = topPos + 18;
        int barHeight = VISIBLE_ROWS * 18;
        int totalRows = (menu.getBlockEntity().getItemHandler().getSlots() + 8) / 9;

        graphics.fill(barX, barY, barX + 8, barY + barHeight, 0x40000000);
        float ratio = menu.getScrollOffset() / (float) maxOffset;
        int sliderHeight = Math.max(8, barHeight / Math.max(1, totalRows));
        int sliderY = barY + (int) (ratio * (barHeight - sliderHeight));
        graphics.fill(barX, sliderY, barX + 8, sliderY + sliderHeight, 0xFFAAAAAA);
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        super.render(graphics, mouseX, mouseY, partialTick);
        renderTooltip(graphics, mouseX, mouseY);
    }

    @Override
    protected void renderTooltip(GuiGraphics graphics, int mouseX, int mouseY) {
        if (menu.getBlockEntity() != null) {
            List<FluidTank> tanks = menu.getBlockEntity().getFluidTanks();
            int tankCount = tanks.size();
            int totalWidth = tankCount * FLUID_BAR_WIDTH + (tankCount - 1) * FLUID_GAP;
            int startX = leftPos - totalWidth;
            int startY = topPos + 18;
            for (int i = 0; i < tankCount; i++) {
                int x = startX + i * (FLUID_BAR_WIDTH + FLUID_GAP);
                if (mouseX >= x && mouseX < x + FLUID_BAR_WIDTH && mouseY >= startY && mouseY < startY + FLUID_BAR_HEIGHT) {
                    FluidTank tank = tanks.get(i);
                    FluidStack fluid = tank.getFluid();
                    if (!fluid.isEmpty()) {
                        List<Component> lines = new ArrayList<>();

                        String displayName = fluid.getHoverName().getString();
                        PotionContents potionContents = fluid.get(DataComponents.POTION_CONTENTS);
                        if (potionContents != null && !potionContents.equals(PotionContents.EMPTY)) {
                            ItemStack dummyStack = new ItemStack(Items.POTION);
                            dummyStack.set(DataComponents.POTION_CONTENTS, potionContents);
                            displayName = dummyStack.getHoverName().getString();
                        }
                        lines.add(Component.literal(displayName + ": " + fluid.getAmount() + " / " + tank.getCapacity() + " mB"));

                        if (potionContents != null && !potionContents.equals(PotionContents.EMPTY)) {
                            for (MobEffectInstance effect : potionContents.getAllEffects()) {
                                Component effectLine = Component.translatable(effect.getDescriptionId())
                                        .append(" " + (effect.getAmplifier() + 1))
                                        .append(" (" + effect.getDuration() / 20 + "s)");
                                lines.add(effectLine);
                            }
                        }

                        graphics.renderComponentTooltip(font, lines, mouseX, mouseY);
                        return;
                    }
                }
            }
        }
        super.renderTooltip(graphics, mouseX, mouseY);
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double scrollX, double scrollY) {
        if (mouseX >= leftPos && mouseX <= leftPos + imageWidth && mouseY >= topPos && mouseY <= topPos + imageHeight) {
            int maxOffset = menu.getMaxScrollOffset();
            if (maxOffset > 0) {
                menu.updateSlotPositions(menu.getScrollOffset() - (int) scrollY);
                return true;
            }
        }
        return super.mouseScrolled(mouseX, mouseY, scrollX, scrollY);
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        int barX = leftPos + imageWidth + 4;
        int barY = topPos + 18;
        int barHeight = VISIBLE_ROWS * 18;
        if (mouseX >= barX && mouseX <= barX + 8 && mouseY >= barY && mouseY <= barY + barHeight) {
            isDraggingScroll = true;
            updateScrollFromMouse(mouseY);
            return true;
        }
        return super.mouseClicked(mouseX, mouseY, button);
    }

    @Override
    public boolean mouseDragged(double mouseX, double mouseY, int button, double dragX, double dragY) {
        if (isDraggingScroll) {
            updateScrollFromMouse(mouseY);
            return true;
        }
        return super.mouseDragged(mouseX, mouseY, button, dragX, dragY);
    }

    @Override
    public boolean mouseReleased(double mouseX, double mouseY, int button) {
        isDraggingScroll = false;
        return super.mouseReleased(mouseX, mouseY, button);
    }

    private void updateScrollFromMouse(double mouseY) {
        int barY = topPos + 18;
        int barHeight = VISIBLE_ROWS * 18;
        int maxOffset = menu.getMaxScrollOffset();
        if (maxOffset > 0) {
            float ratio = (float) (mouseY - barY) / barHeight;
            ratio = Math.max(0, Math.min(1, ratio));
            menu.updateSlotPositions((int) (ratio * maxOffset));
        }
    }
}
'''

if __name__ == "__main__":
    write_file(os.path.join(PACKAGE_PATH, "blockentity", "TieredContainerBlockEntity.java"), blockentity_code)
    write_file(os.path.join(PACKAGE_PATH, "screen", "TieredContainerScreen.java"), screen_code)
    print("\n编译错误修复，流体更新采用动力泵同款机制，纹理实时刷新。")