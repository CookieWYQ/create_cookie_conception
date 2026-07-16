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

andesite_code = '''package cretae.cookiewyq.create_cookie_conception.blocks.tiered;

import cretae.cookiewyq.create_cookie_conception.blockentity.TieredContainerBlockEntity;
import cretae.cookiewyq.create_cookie_conception.init.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
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

public class AndesiteContainerBlock extends Block implements EntityBlock, TieredContainerBlock {
    public AndesiteContainerBlock(BlockBehaviour.Properties properties) { super(properties); }

    @Override public int getInventorySlots() { return 54; }
    @Override public int getFluidTankCount() { return 1; }
    @Override public int getFluidTankCapacity() { return 32000; }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new TieredContainerBlockEntity(ModBlockEntities.TIERED_CONTAINER.get(), pos, state);
    }

    // Allow empty-hand breaking to actually drop the block
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

    // Wrench quick-pickup is handled by create:wrench_pickup tag, no code needed here

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
'''

brass_code = andesite_code.replace("AndesiteContainerBlock", "BrassContainerBlock")
brass_code = brass_code.replace("public int getInventorySlots() { return 54; }", "public int getInventorySlots() { return 108; }")
brass_code = brass_code.replace("public int getFluidTankCount() { return 1; }", "public int getFluidTankCount() { return 2; }")
brass_code = brass_code.replace("public int getFluidTankCapacity() { return 32000; }", "public int getFluidTankCapacity() { return 64000; }")

sturdy_code = andesite_code.replace("AndesiteContainerBlock", "SturdyContainerBlock")
sturdy_code = sturdy_code.replace("public int getInventorySlots() { return 54; }", "public int getInventorySlots() { return 162; }")
sturdy_code = sturdy_code.replace("public int getFluidTankCount() { return 1; }", "public int getFluidTankCount() { return 3; }")
sturdy_code = sturdy_code.replace("public int getFluidTankCapacity() { return 32000; }", "public int getFluidTankCapacity() { return 128000; }")

if __name__ == "__main__":
    tiered_dir = os.path.join(PACKAGE_PATH, "blocks", "tiered")

    write_file(os.path.join(tiered_dir, "AndesiteContainerBlock.java"), andesite_code)
    write_file(os.path.join(tiered_dir, "BrassContainerBlock.java"), brass_code)
    write_file(os.path.join(tiered_dir, "SturdyContainerBlock.java"), sturdy_code)

    print("\n空手破坏不掉落问题已修复：添加 canHarvestBlock 返回 true，允许空手破坏并正常掉落。")
    print("其他代码未作任何改动。")