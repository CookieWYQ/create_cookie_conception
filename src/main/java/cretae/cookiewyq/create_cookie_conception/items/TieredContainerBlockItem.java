package cretae.cookiewyq.create_cookie_conception.items;

import cretae.cookiewyq.create_cookie_conception.blockentity.TieredContainerBlockEntity;
import cretae.cookiewyq.create_cookie_conception.blocks.tiered.TieredContainerBlock;
import cretae.cookiewyq.create_cookie_conception.init.ModDataComponents;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.type.capability.ICurioItem;

public class TieredContainerBlockItem extends BlockItem implements ICurioItem {

    @Override
    public boolean placeBlock(BlockPlaceContext ctx, BlockState state) {
        boolean placed = super.placeBlock(ctx, state);
        if (placed && ctx.getLevel().getBlockEntity(ctx.getClickedPos()) instanceof TieredContainerBlockEntity be) {
            be.setHasStrap(Boolean.TRUE.equals(ctx.getItemInHand().get(ModDataComponents.HAS_STRAP.get())));
        }
        return placed;
    }
    public TieredContainerBlockItem(Block block, Properties properties) {
        super(block, properties);
    }

    public int getInventorySlots() {
        if (getBlock() instanceof TieredContainerBlock tiered) {
            return tiered.getInventorySlots();
        }
        return 54;
    }

    public int getFluidTankCount() {
        if (getBlock() instanceof TieredContainerBlock tiered) {
            return tiered.getFluidTankCount();
        }
        return 3;
    }

    public int getFluidTankCapacity() {
        if (getBlock() instanceof TieredContainerBlock tiered) {
            return tiered.getFluidTankCapacity();
        }
        return 32000;
    }

    @Override
    public boolean canEquip(SlotContext slotContext, ItemStack stack) {
        return Boolean.TRUE.equals(stack.get(ModDataComponents.HAS_STRAP.get()));
    }
}
