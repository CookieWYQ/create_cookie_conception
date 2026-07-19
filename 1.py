#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JAVA_SRC = os.path.join(BASE_DIR, "src", "main", "java")
RESOURCES = os.path.join(BASE_DIR, "src", "main", "resources")
PACKAGE_PATH = os.path.join("cretae", "cookiewyq", "create_cookie_conception")

def write_file(rel_path, content):
    full_path = os.path.join(JAVA_SRC, rel_path) if rel_path.endswith(".java") else os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[生成] {full_path}")

# ==================== TankModelData.java ====================
tank_model_data = '''package cretae.cookiewyq.create_cookie_conception.util;

import net.neoforged.neoforge.client.model.data.ModelProperty;

import java.util.List;

public class TankModelData {
    public static final ModelProperty<List<TankRenderInfo>> TANK_RENDER_INFO_LIST = new ModelProperty<>();
}
'''

# ==================== TieredContainerBlockEntity.java ====================
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
import net.minecraft.server.level.ServerPlayer;
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

    // Helper to compare potion effects
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

    // Internal input check: potion cannot go into water, water cannot go into potion
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

    // Custom tank that supports forced mixing
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
        return ModelData.builder()
                .with(TankModelData.TANK_RENDER_INFO_LIST, tankRenderInfos)
                .build();
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
            updateRenderInfo();
            requestModelDataUpdate();
        }
    }

    public void onContentsChanged() {
        setChanged();
        updateRenderInfo();
        if (level != null) {
            if (!level.isClientSide) {
                level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
                for (ServerPlayer player : level.getServer().getPlayerList().getPlayers()) {
                    if (player.distanceToSqr(worldPosition.getX() + 0.5, worldPosition.getY() + 0.5, worldPosition.getZ() + 0.5) <= 64 * 64) {
                        player.connection.send(getUpdatePacket());
                    }
                }
            } else {
                updateRenderInfo();
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
            // External fill: strict fluid type match, potion and water are different
            for (int i = 0; i < tanks.size(); i++) {
                FluidTank tank = tanks.get(i);
                if (!tank.getFluid().isEmpty() && tank.getFluid().getFluid() == resource.getFluid()) {
                    return fillTank(i, resource, action, false);
                }
            }
            for (FluidTank tank : tanks) {
                if (tank.getFluid().isEmpty()) return tank.fill(resource, action);
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

# ==================== TankDynamicBakedModel.java ====================
dynamic_model_code = '''package cretae.cookiewyq.create_cookie_conception.model;

import com.mojang.blaze3d.vertex.PoseStack;
import cretae.cookiewyq.create_cookie_conception.util.TankRenderInfo;
import cretae.cookiewyq.create_cookie_conception.util.TankModelData;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.renderer.block.model.ItemOverrides;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.client.ChunkRenderTypeSet;
import net.neoforged.neoforge.client.extensions.common.IClientFluidTypeExtensions;
import net.neoforged.neoforge.client.model.IDynamicBakedModel;
import net.neoforged.neoforge.client.model.data.ModelData;
import net.neoforged.neoforge.client.model.pipeline.QuadBakingVertexConsumer;
import net.neoforged.neoforge.fluids.FluidStack;
import org.jetbrains.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;

public class TankDynamicBakedModel implements IDynamicBakedModel {
    private final BakedModel baseModel;
    private final int tankCount;

    public TankDynamicBakedModel(BakedModel baseModel, int tankCount) {
        this.baseModel = baseModel;
        this.tankCount = tankCount;
    }

    @Override
    public List<BakedQuad> getQuads(@Nullable BlockState state, @Nullable Direction side, RandomSource rand, ModelData data, @Nullable RenderType renderType) {
        List<BakedQuad> quads = new ArrayList<>(baseModel.getQuads(state, side, rand, data, renderType));
        if (renderType == RenderType.translucent()) {
            List<TankRenderInfo> infos = data.get(TankModelData.TANK_RENDER_INFO_LIST);
            if (infos != null) {
                int count = Math.min(infos.size(), tankCount);
                for (int i = 0; i < count; i++) {
                    TankRenderInfo info = infos.get(i);
                    if (info == null || info.getFluid().isEmpty() || info.getFillRatio() <= 0.001f) continue;
                    FluidStack fluid = info.getFluid();
                    float ratio = info.getFillRatio();
                    IClientFluidTypeExtensions extensions = IClientFluidTypeExtensions.of(fluid.getFluid());
                    TextureAtlasSprite sprite = Minecraft.getInstance().getTextureAtlas(InventoryMenu.BLOCK_ATLAS)
                            .apply(extensions.getStillTexture(fluid));
                    if (sprite == null) continue;
                    int tint = extensions.getTintColor(fluid);
                    float r = ((tint >> 16) & 0xFF) / 255.0f;
                    float g = ((tint >> 8) & 0xFF) / 255.0f;
                    float b = (tint & 0xFF) / 255.0f;
                    float a = ((tint >> 24) & 0xFF) / 255.0f;
                    float segmentWidth = 1.0f / tankCount;
                    float minX = i * segmentWidth;
                    float maxX = (i + 1) * segmentWidth;
                    List<Direction> faces = (side == null) ? List.of(Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST, Direction.UP) : List.of(side);
                    for (Direction dir : faces) {
                        BakedQuad quad = buildFluidQuad(sprite, r, g, b, a, dir, ratio, minX, maxX);
                        if (quad != null) quads.add(quad);
                    }
                }
            }
        }
        return quads;
    }

    private BakedQuad buildFluidQuad(TextureAtlasSprite sprite, float r, float g, float b, float a,
                                      Direction dir, float ratio, float minX, float maxX) {
        QuadBakingVertexConsumer builder = new QuadBakingVertexConsumer();
        builder.setSprite(sprite);
        builder.setDirection(dir);
        builder.setTintIndex(-1);
        float minY = 0, maxY = ratio, minZ = 0, maxZ = 1;
        float u0 = sprite.getU0(), u1 = sprite.getU1();
        float v0 = sprite.getV0(), v1 = sprite.getV1();
        if (dir == Direction.EAST || dir == Direction.WEST) {
            minX = 0; maxX = 1; // full width for side faces
        }
        switch (dir) {
            case NORTH:
                builder.addVertex(maxX, minY, minZ).setColor(r, g, b, a).setUv(u1, v1).setNormal(0, 0, -1);
                builder.addVertex(minX, minY, minZ).setColor(r, g, b, a).setUv(u0, v1).setNormal(0, 0, -1);
                builder.addVertex(minX, maxY, minZ).setColor(r, g, b, a).setUv(u0, v0).setNormal(0, 0, -1);
                builder.addVertex(maxX, maxY, minZ).setColor(r, g, b, a).setUv(u1, v0).setNormal(0, 0, -1);
                break;
            case SOUTH:
                builder.addVertex(minX, minY, maxZ).setColor(r, g, b, a).setUv(u1, v1).setNormal(0, 0, 1);
                builder.addVertex(maxX, minY, maxZ).setColor(r, g, b, a).setUv(u0, v1).setNormal(0, 0, 1);
                builder.addVertex(maxX, maxY, maxZ).setColor(r, g, b, a).setUv(u0, v0).setNormal(0, 0, 1);
                builder.addVertex(minX, maxY, maxZ).setColor(r, g, b, a).setUv(u1, v0).setNormal(0, 0, 1);
                break;
            case EAST:
                builder.addVertex(maxX, minY, maxZ).setColor(r, g, b, a).setUv(u1, v1).setNormal(1, 0, 0);
                builder.addVertex(maxX, minY, minZ).setColor(r, g, b, a).setUv(u0, v1).setNormal(1, 0, 0);
                builder.addVertex(maxX, maxY, minZ).setColor(r, g, b, a).setUv(u0, v0).setNormal(1, 0, 0);
                builder.addVertex(maxX, maxY, maxZ).setColor(r, g, b, a).setUv(u1, v0).setNormal(1, 0, 0);
                break;
            case WEST:
                builder.addVertex(minX, minY, minZ).setColor(r, g, b, a).setUv(u1, v1).setNormal(-1, 0, 0);
                builder.addVertex(minX, minY, maxZ).setColor(r, g, b, a).setUv(u0, v1).setNormal(-1, 0, 0);
                builder.addVertex(minX, maxY, maxZ).setColor(r, g, b, a).setUv(u0, v0).setNormal(-1, 0, 0);
                builder.addVertex(minX, maxY, minZ).setColor(r, g, b, a).setUv(u1, v0).setNormal(-1, 0, 0);
                break;
            case UP:
                if (ratio >= 0.999f) return null;
                builder.addVertex(minX, ratio, 0).setColor(r, g, b, a).setUv(u0, v0).setNormal(0, 1, 0);
                builder.addVertex(maxX, ratio, 0).setColor(r, g, b, a).setUv(u1, v0).setNormal(0, 1, 0);
                builder.addVertex(maxX, ratio, 1).setColor(r, g, b, a).setUv(u1, v1).setNormal(0, 1, 0);
                builder.addVertex(minX, ratio, 1).setColor(r, g, b, a).setUv(u0, v1).setNormal(0, 1, 0);
                break;
            default: return null;
        }
        return builder.bakeQuad();
    }

    @Override
    public ChunkRenderTypeSet getRenderTypes(BlockState state, RandomSource rand, ModelData data) {
        return ChunkRenderTypeSet.all();
    }
    @Override
    public List<RenderType> getRenderTypes(ItemStack stack, boolean fabulous) {
        return List.of(RenderType.translucent());
    }
    @Override public boolean useAmbientOcclusion() { return true; }
    @Override public boolean isGui3d() { return true; }
    @Override public boolean usesBlockLight() { return true; }
    @Override public boolean isCustomRenderer() { return false; }
    @Override public TextureAtlasSprite getParticleIcon() { return baseModel.getParticleIcon(); }
    @Override public ItemOverrides getOverrides() { return ItemOverrides.EMPTY; }
    @Override
    public BakedModel applyTransform(ItemDisplayContext transformType, PoseStack poseStack, boolean applyLeftHandTransform) {
        baseModel.applyTransform(transformType, poseStack, applyLeftHandTransform);
        return this;
    }
}
'''

# ==================== ClientModEvents.java ====================
client_events_code = '''package cretae.cookiewyq.create_cookie_conception;

import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonObject;
import cretae.cookiewyq.create_cookie_conception.model.TankDynamicBakedModel;
import cretae.cookiewyq.create_cookie_conception.init.ModMenus;
import cretae.cookiewyq.create_cookie_conception.screen.TieredContainerScreen;
import net.minecraft.client.renderer.block.model.ItemOverrides;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.client.resources.model.Material;
import net.minecraft.client.resources.model.ModelBaker;
import net.minecraft.client.resources.model.ModelState;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ModelEvent;
import net.neoforged.neoforge.client.event.RegisterMenuScreensEvent;
import net.neoforged.neoforge.client.model.geometry.IGeometryBakingContext;
import net.neoforged.neoforge.client.model.geometry.IGeometryLoader;
import net.neoforged.neoforge.client.model.geometry.IUnbakedGeometry;
import org.jetbrains.annotations.NotNull;

import java.util.Objects;
import java.util.function.Function;

@EventBusSubscriber(modid = CookieConceptionMod.MODID, value = Dist.CLIENT)
public class ClientModEvents {

    @SubscribeEvent
    public static void registerScreens(RegisterMenuScreensEvent event) {
        event.register(ModMenus.TIERED_CONTAINER.get(), TieredContainerScreen::new);
    }

    @SubscribeEvent
    public static void registerGeometryLoaders(ModelEvent.RegisterGeometryLoaders event) {
        event.register(
            ResourceLocation.fromNamespaceAndPath(CookieConceptionMod.MODID, "tank_dynamic"),
            new TankGeometryLoader()
        );
    }

    private static class TankGeometryLoader implements IGeometryLoader<TankGeometry> {
        @Override
        public TankGeometry read(JsonObject jsonObject, JsonDeserializationContext deserializationContext) {
            int tankCount = jsonObject.has("tank_count") ? jsonObject.get("tank_count").getAsInt() : 1;
            return new TankGeometry(tankCount);
        }
    }

    private static class TankGeometry implements IUnbakedGeometry<TankGeometry> {
        private final int tankCount;

        public TankGeometry(int tankCount) {
            this.tankCount = tankCount;
        }

        @Override
        public @NotNull BakedModel bake(IGeometryBakingContext context, ModelBaker baker, Function<Material, TextureAtlasSprite> spriteGetter, ModelState modelState, ItemOverrides overrides) {
            BakedModel baseModel = baker.bake(Objects.requireNonNull(context.getRenderTypeHint()), modelState, spriteGetter);
            return new TankDynamicBakedModel(baseModel, tankCount);
        }
    }
}
'''

# ==================== 方块模型 JSON ====================
andesite_model = '''{
  "loader": "create_cookie_conception:tank_dynamic",
  "tank_count": 3,
  "model": {
    "parent": "minecraft:block/cube_all",
    "textures": {
      "all": "create_cookie_conception:block/andesite_tank"
    }
  }
}
'''

brass_model = '''{
  "loader": "create_cookie_conception:tank_dynamic",
  "tank_count": 4,
  "model": {
    "parent": "minecraft:block/cube_all",
    "textures": {
      "all": "create_cookie_conception:block/brass_tank"
    }
  }
}
'''

sturdy_model = '''{
  "loader": "create_cookie_conception:tank_dynamic",
  "tank_count": 5,
  "model": {
    "parent": "minecraft:block/cube_all",
    "textures": {
      "all": "create_cookie_conception:block/sturdy_tank"
    }
  }
}
'''

if __name__ == "__main__":
    write_file(os.path.join(PACKAGE_PATH, "util", "TankModelData.java"), tank_model_data)
    write_file(os.path.join(PACKAGE_PATH, "blockentity", "TieredContainerBlockEntity.java"), blockentity_code)
    write_file(os.path.join(PACKAGE_PATH, "model", "TankDynamicBakedModel.java"), dynamic_model_code)
    write_file(os.path.join(PACKAGE_PATH, "ClientModEvents.java"), client_events_code)

    models_dir = os.path.join(RESOURCES, "assets", "create_cookie_conception", "models", "block")
    write_file(os.path.join(models_dir, "andesite_tank.json"), andesite_model)
    write_file(os.path.join(models_dir, "brass_tank.json"), brass_model)
    write_file(os.path.join(models_dir, "sturdy_tank.json"), sturdy_model)

    print("\n全部文件更新完成。药水与水严格分离，纹理实时刷新。")