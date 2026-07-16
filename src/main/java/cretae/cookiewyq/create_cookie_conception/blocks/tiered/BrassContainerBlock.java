package cretae.cookiewyq.create_cookie_conception.blocks.tiered;

import cretae.cookiewyq.create_cookie_conception.blockentity.TieredContainerBlockEntity;
import cretae.cookiewyq.create_cookie_conception.init.ModBlockEntities;
import cretae.cookiewyq.create_cookie_conception.items.TieredContainerBlockItem;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
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

    @Override
    public List<ItemStack> getDrops(BlockState state, LootParams.Builder builder) {
        return List.of();
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moved) {
        if (!state.is(newState.getBlock())) {
            BlockEntity be = level.getBlockEntity(pos);
            if (be instanceof TieredContainerBlockEntity tankBe) {
                CompoundTag tag = new CompoundTag();
                tankBe.saveAdditional(tag, level.registryAccess());
                ItemStack dropStack = new ItemStack(this.asItem());
                BlockItem.setBlockEntityData(dropStack, ModBlockEntities.TIERED_CONTAINER.get(), tag);
                Containers.dropItemStack(level, pos.getX(), pos.getY(), pos.getZ(), dropStack);
                level.removeBlockEntity(pos);
                level.setBlock(pos, newState, 3);
                return;
            }
        }
        super.onRemove(state, level, pos, newState, moved);
    }

    @Override public boolean hasAnalogOutputSignal(BlockState state) { return true; }

    @Override
    public int getAnalogOutputSignal(BlockState state, Level level, BlockPos pos) {
        if (level.getBlockEntity(pos) instanceof TieredContainerBlockEntity be)
            return Math.min(15, be.getTotalItemCount() * 15 / be.getItemHandler().getSlots());
        return 0;
    }
}
