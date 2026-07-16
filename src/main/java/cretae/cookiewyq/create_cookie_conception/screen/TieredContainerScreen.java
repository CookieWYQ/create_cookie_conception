package cretae.cookiewyq.create_cookie_conception.screen;

import cretae.cookiewyq.create_cookie_conception.menu.TieredContainerMenu;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.InventoryMenu;
import net.neoforged.neoforge.client.extensions.common.IClientFluidTypeExtensions;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;
import org.jetbrains.annotations.NotNull;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TieredContainerScreen extends AbstractContainerScreen<TieredContainerMenu> {
    private static final ResourceLocation TEXTURE = ResourceLocation.fromNamespaceAndPath("minecraft", "textures/gui/container/generic_54.png");
    private static final int VISIBLE_ROWS = 6;
    private static final int FLUID_BAR_WIDTH = 18;
    private static final int FLUID_BAR_HEIGHT = VISIBLE_ROWS * 18;
    private static final int FLUID_GAP = 2;
    private boolean isDraggingScroll = false;
    private static final int TILE_SIZE = 16;

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
            FluidTank tank = tanks.get(i);
            FluidStack fluid = tank.getFluid();

            graphics.fill(x, startY, x + FLUID_BAR_WIDTH, startY + FLUID_BAR_HEIGHT, 0xFFFFFFFF);

            if (fluid.isEmpty()) continue;

            int capacity = tank.getCapacity();
            int amount = fluid.getAmount();
            if (amount <= 0) continue;

            int fluidHeight = (int) (FLUID_BAR_HEIGHT * ((float) amount / capacity));
            if (fluidHeight <= 0) continue;

            boolean lighterThanAir = fluid.getFluidType().isLighterThanAir();
            int drawY = lighterThanAir ? startY : startY + FLUID_BAR_HEIGHT - fluidHeight;

            IClientFluidTypeExtensions extensions = IClientFluidTypeExtensions.of(fluid.getFluid());
            ResourceLocation stillTexture = extensions.getStillTexture(fluid);

            TextureAtlasSprite sprite = spriteCache.computeIfAbsent(stillTexture, loc ->
                    Minecraft.getInstance().getTextureAtlas(InventoryMenu.BLOCK_ATLAS).apply(loc)
            );

            if (sprite == null) {
                continue;
            }

            int tintColor = extensions.getTintColor(fluid);
            float a = ((tintColor >> 24) & 0xFF) / 255.0F;
            float r = ((tintColor >> 16) & 0xFF) / 255.0F;
            float g = ((tintColor >> 8) & 0xFF) / 255.0F;
            float b = (tintColor & 0xFF) / 255.0F;

            RenderSystem.setShaderTexture(0, InventoryMenu.BLOCK_ATLAS);
            RenderSystem.enableBlend();
            RenderSystem.defaultBlendFunc();
            RenderSystem.setShaderColor(r, g, b, a);

            //////
            int fullTiles = fluidHeight / TILE_SIZE;
            int remainingPixels = fluidHeight % TILE_SIZE;

            // Draw full tiles from bottom to top
            for (int tile = 0; tile < fullTiles; tile++) {
                int tileY = drawY + fluidHeight - (tile + 1) * TILE_SIZE;
                graphics.blit(x, tileY, 0, FLUID_BAR_WIDTH, TILE_SIZE, sprite);
            }

            // Draw partial top tile using scissor
            if (remainingPixels > 0) {
                graphics.enableScissor(x, drawY, x + FLUID_BAR_WIDTH, drawY + remainingPixels);
                graphics.blit(x, drawY, 0, FLUID_BAR_WIDTH, TILE_SIZE, sprite);
                graphics.disableScissor();
            }
            /////



            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
            RenderSystem.disableBlend();
        }

        drawScrollBar(graphics);
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
    public void render(@NotNull GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        super.render(graphics, mouseX, mouseY, partialTick);
        this.renderTooltip(graphics, mouseX, mouseY);
    }

    @Override
    public void renderTooltip(@NotNull GuiGraphics graphics, int mouseX, int mouseY) {
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
                        String name = fluid.getHoverName().getString();
                        Component text = Component.literal(name + ": " + fluid.getAmount() + " / " + tank.getCapacity() + " mB");
                        graphics.renderTooltip(font, text, mouseX, mouseY);
                    }
                    break;
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