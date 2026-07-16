package cretae.cookiewyq.create_cookie_conception.blockentity;

import cretae.cookiewyq.create_cookie_conception.blocks.tiered.TieredContainerBlock;
import cretae.cookiewyq.create_cookie_conception.init.ModBlockEntities;
import cretae.cookiewyq.create_cookie_conception.menu.TieredContainerMenu;
import cretae.cookiewyq.create_cookie_conception.util.TankRenderInfo;
import cretae.cookiewyq.create_cookie_conception.util.TankModelData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.client.model.data.ModelData;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;
import net.neoforged.neoforge.items.ItemStackHandler;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;

public class TieredContainerBlockEntity extends BlockEntity implements MenuProvider {
    private ItemStackHandler itemHandler = new ItemStackHandler(0) {
        @Override
        protected void onContentsChanged(int slot) {
            TieredContainerBlockEntity.this.onContentsChanged();
        }
    };
    private final List<FluidTank> fluidTanks = new ArrayList<>();
    private final IFluidHandler fluidHandler = new MultiTankFluidHandler(fluidTanks);
    private List<TankRenderInfo> tankRenderInfos = new ArrayList<>();

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
                fluidTanks.add(new FluidTank(targetCap) {
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
            updateRenderInfo();
        }
    }

    private void updateRenderInfo() {
        tankRenderInfos.clear();
        for (FluidTank tank : fluidTanks) {
            FluidStack fluid = tank.getFluid();
            float ratio = tank.getCapacity() > 0 ? (float) fluid.getAmount() / tank.getCapacity() : 0f;
            tankRenderInfos.add(new TankRenderInfo(fluid, ratio));
        }
        onContentsChanged();
    }

    @Override
    public void onLoad() {
        super.onLoad();
        applyCapacityFromBlock();
    }

    @Override
    public void setBlockState(BlockState state) {
        super.setBlockState(state);
        applyCapacityFromBlock();
    }

    public ItemStackHandler getItemHandler() { return itemHandler; }
    public List<FluidTank> getFluidTanks() { return fluidTanks; }
    public IFluidHandler getFluidHandler() { return fluidHandler; }
    public List<TankRenderInfo> getTankRenderInfos() { return tankRenderInfos; }

    public int getTotalItemCount() {
        int count = 0;
        for (int i = 0; i < itemHandler.getSlots(); i++) if (!itemHandler.getStackInSlot(i).isEmpty()) count++;
        return count;
    }

    @Override
    public @NotNull ModelData getModelData() {
        if (tankRenderInfos.isEmpty()) {
            return ModelData.EMPTY;
        }
        return ModelData.builder()
                .with(TankModelData.TANK_RENDER_INFO, tankRenderInfos.get(0))
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
            FluidTank tank = new FluidTank(1000);
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
                protected void onContentsChanged(int slot) {
                    TieredContainerBlockEntity.this.onContentsChanged();
                }
            };
            for (int i = 0; i < Math.min(savedItems.getSlots(), targetSlots); i++)
                itemHandler.setStackInSlot(i, savedItems.getStackInSlot(i));

            fluidTanks.clear();
            for (int i = 0; i < targetTanks; i++) {
                fluidTanks.add(new FluidTank(targetCap) {
                    @Override
                    protected void onContentsChanged() {
                        TieredContainerBlockEntity.this.onContentsChanged();
                    }
                });
            }
            for (int i = 0; i < savedTanks.size(); i++) {
                if (i < fluidTanks.size()) fluidTanks.get(i).fill(savedTanks.get(i).getFluid(), IFluidHandler.FluidAction.EXECUTE);
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
        return Component.translatable("block.create_cookie_conception." + getBlockState().getBlock().getDescriptionId().replace("block.create_cookie_conception.", ""));
    }

    @Nullable
    @Override
    public AbstractContainerMenu createMenu(int id, Inventory inv, Player player) {
        return new TieredContainerMenu(id, inv, this);
    }

    @Nullable @Override public ClientboundBlockEntityDataPacket getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
    @Override public CompoundTag getUpdateTag(HolderLookup.Provider reg) { return saveWithoutMetadata(reg); }
    @Override public void onDataPacket(Connection net, ClientboundBlockEntityDataPacket pkt, HolderLookup.Provider reg) { loadAdditional(pkt.getTag(), reg); }

    public void onContentsChanged() {
        setChanged();
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
            for (FluidTank tank : tanks) if (FluidStack.isSameFluidSameComponents(tank.getFluid(), resource)) return tank.fill(resource, action);
            for (FluidTank tank : tanks) if (tank.getFluid().isEmpty()) return tank.fill(resource, action);
            return 0;
        }

        @Override
        public @NotNull FluidStack drain(FluidStack resource, FluidAction action) {
            if (resource.isEmpty()) return FluidStack.EMPTY;
            for (FluidTank tank : tanks) if (FluidStack.isSameFluidSameComponents(tank.getFluid(), resource)) return tank.drain(resource.getAmount(), action);
            return FluidStack.EMPTY;
        }

        @Override
        public @NotNull FluidStack drain(int maxDrain, FluidAction action) {
            for (FluidTank tank : tanks) if (!tank.getFluid().isEmpty()) return tank.drain(maxDrain, action);
            return FluidStack.EMPTY;
        }
    }
}
