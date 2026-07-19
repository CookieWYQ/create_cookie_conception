package cretae.cookiewyq.create_cookie_conception.event;

import cretae.cookiewyq.create_cookie_conception.init.ModDataComponents;
import cretae.cookiewyq.create_cookie_conception.items.TieredContainerBlockItem;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.player.ItemTooltipEvent;

@EventBusSubscriber(value = Dist.CLIENT)
public class TooltipEvents {
    @SubscribeEvent
    public static void onItemTooltip(ItemTooltipEvent event) {
        if (event.getItemStack().getItem() instanceof TieredContainerBlockItem) {
            Boolean hasStrap = event.getItemStack().get(ModDataComponents.HAS_STRAP.get());
            if (Boolean.TRUE.equals(hasStrap)) {
                event.getToolTip().add(Component.translatable("tooltip.create_cookie_conception.can_wear_on_back")
                        .withStyle(ChatFormatting.YELLOW));
            } else {
                event.getToolTip().add(Component.translatable("tooltip.create_cookie_conception.cannot_wear_on_back")
                        .withStyle(ChatFormatting.RED));
            }
        }
    }
}
