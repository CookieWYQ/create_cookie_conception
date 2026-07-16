package cretae.cookiewyq.create_cookie_conception.blocks.tiered;

import com.simibubi.create.AllItems;
import cretae.cookiewyq.create_cookie_conception.blockentity.TieredContainerBlockEntity;
import cretae.cookiewyq.create_cookie_conception.init.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemInteractionResult;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class BrassContainerBlock extends Block implements EntityBlock, TieredContainerBlock {
    public BrassContainerBlock(BlockBehaviour.Properties properties) { super(properties); }

    @Override public int getInventorySlots() { return 108; }
    @Override public int getFluidTankCount() { return 2; }
    @Override public int getFluidTankCapacity() { return 64000; }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new TieredContainerBlockEntity(ModBlockEntities.TIERED_CONTAINER.get(), pos, state);
    }

    // Allow empty-hand breaking to drop the block
    @Override
    public boolean canHarvestBlock(BlockState state, BlockGetter level, BlockPos pos, Player player) {
        return true;
    }

    // Right-click with empty hand opens GUI
    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide && level.getBlockEntity(pos) instanceof TieredContainerBlockEntity be) {
            ((ServerPlayer) player).openMenu(be, buf -> {
                buf.writeBlockPos(pos);
                buf.writeVarInt(be.getItemHandler().getSlots());
                buf.writeVarInt(be.getFluidTanks().size());
            });
        }
        return InteractionResult.SUCCESS;
    }

    // Wrench sneak+right-click quick-pickup (works in all modes, including creative)
    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (stack.is(AllItems.WRENCH.asItem()) && player.isShiftKeyDown()) {
            if (!level.isClientSide) {
                BlockEntity be = level.getBlockEntity(pos);
                if (be instanceof TieredContainerBlockEntity tankBe) {
                    CompoundTag tag = tankBe.getPersistentData(level.registryAccess());
                    ItemStack dropStack = new ItemStack(this.asItem());
                    BlockItem.setBlockEntityData(dropStack, ModBlockEntities.TIERED_CONTAINER.get(), tag);
                    if (!player.getInventory().add(dropStack)) {
                        Containers.dropItemStack(level, pos.getX(), pos.getY(), pos.getZ(), dropStack);
                    }
                }
                level.removeBlock(pos, false);
            }
            return ItemInteractionResult.SUCCESS;
        }
        return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
    }

    // Drops the container with all its contents when broken by any means (survival/adventure/etc.)
    @Override
    public List<ItemStack> getDrops(BlockState state, LootParams.Builder builder) {
        BlockEntity be = builder.getOptionalParameter(net.minecraft.world.level.storage.loot.parameters.LootContextParams.BLOCK_ENTITY);
        if (be instanceof TieredContainerBlockEntity tankBe) {
            CompoundTag tag = tankBe.getPersistentData(builder.getLevel().registryAccess());
            ItemStack dropStack = new ItemStack(this.asItem());
            BlockItem.setBlockEntityData(dropStack, ModBlockEntities.TIERED_CONTAINER.get(), tag);
            return List.of(dropStack);
        }
        return List.of(new ItemStack(this.asItem()));
    }

    // Creative mode drops the NBT item while still removing the block correctly
    @Override
    public boolean onDestroyedByPlayer(BlockState state, Level level, BlockPos pos, Player player, boolean willHarvest, FluidState fluid) {
        if (!level.isClientSide && player.isCreative()) {
            BlockEntity be = level.getBlockEntity(pos);
            if (be instanceof TieredContainerBlockEntity tankBe) {
                CompoundTag tag = tankBe.getPersistentData(level.registryAccess());
                ItemStack dropStack = new ItemStack(this.asItem());
                BlockItem.setBlockEntityData(dropStack, ModBlockEntities.TIERED_CONTAINER.get(), tag);
                Containers.dropItemStack(level, pos.getX(), pos.getY(), pos.getZ(), dropStack);
            }
        }
        return super.onDestroyedByPlayer(state, level, pos, player, willHarvest, fluid);
    }

    @Override public boolean hasAnalogOutputSignal(BlockState state) { return true; }

    @Override
    public int getAnalogOutputSignal(BlockState state, Level level, BlockPos pos) {
        if (level.getBlockEntity(pos) instanceof TieredContainerBlockEntity be)
            return Math.min(15, be.getTotalItemCount() * 15 / be.getItemHandler().getSlots());
        return 0;
    }
}
