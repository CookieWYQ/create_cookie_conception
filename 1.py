#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JAVA_SRC = os.path.join(BASE_DIR, "src", "main", "java")
PACKAGE_PATH = os.path.join("cretae", "cookiewyq", "create_cookie_conception")

def write_file(full_path, content):
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[生成] {full_path}")

screen_code = '''package cretae.cookiewyq.create_cookie_conception.screen;

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

import java.util.List;

public class TieredContainerScreen extends AbstractContainerScreen<TieredContainerMenu> {
    private static final ResourceLocation TEXTURE = ResourceLocation.fromNamespaceAndPath("minecraft", "textures/gui/container/generic_54.png");
    private static final int VISIBLE_ROWS = 6;
    private static final int FLUID_BAR_WIDTH = 18;
    private static final int FLUID_BAR_HEIGHT = VISIBLE_ROWS * 18;
    private static final int FLUID_GAP = 2;
    private static final int TILE_SIZE = 16;
    private boolean isDraggingScroll = false;

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
            int y = startY;
            FluidTank tank = tanks.get(i);
            FluidStack fluid = tank.getFluid();

            // Pure white background
            graphics.fill(x, y, x + FLUID_BAR_WIDTH, y + FLUID_BAR_HEIGHT, 0xFFFFFFFF);

            if (fluid.isEmpty()) continue;

            int capacity = tank.getCapacity();
            int amount = fluid.getAmount();
            int fluidHeight = (int) (FLUID_BAR_HEIGHT * ((float) amount / capacity));
            if (fluidHeight <= 0) continue;

            int drawY = y + FLUID_BAR_HEIGHT - fluidHeight;

            IClientFluidTypeExtensions extensions = IClientFluidTypeExtensions.of(fluid.getFluid());
            ResourceLocation still = extensions.getStillTexture(fluid);
            if (still == null) continue;

            TextureAtlasSprite sprite = Minecraft.getInstance().getTextureAtlas(InventoryMenu.BLOCK_ATLAS).apply(still);
            if (sprite == null) {
                // Fallback: draw a magenta square to indicate missing texture
                graphics.fill(x, drawY, x + FLUID_BAR_WIDTH, y + FLUID_BAR_HEIGHT, 0xFFFF00FF);
                continue;
            }

            RenderSystem.setShaderTexture(0, InventoryMenu.BLOCK_ATLAS);
            RenderSystem.enableBlend();
            RenderSystem.defaultBlendFunc();
            // Pure white to show original texture colors
            RenderSystem.setShaderColor(1.0f, 1.0f, 1.0f, 1.0f);

            float u0 = sprite.getU0();
            float u1 = sprite.getU1();
            float v0 = sprite.getV0();
            float v1 = sprite.getV1();

            int fullTiles = fluidHeight / TILE_SIZE;
            int remainingPixels = fluidHeight % TILE_SIZE;

            // Draw full tiles from bottom to top
            for (int tile = 0; tile < fullTiles; tile++) {
                int tileY = drawY + fluidHeight - (tile + 1) * TILE_SIZE;
                graphics.blit(x, tileY, 0, FLUID_BAR_WIDTH, TILE_SIZE,
                              sprite, u0, v0, u1, v1);
            }

            // Draw partial top tile
            if (remainingPixels > 0) {
                float partialV0 = v1 - (remainingPixels / (float) TILE_SIZE) * (v1 - v0);
                graphics.blit(x, drawY, 0, FLUID_BAR_WIDTH, remainingPixels,
                              sprite, u0, partialV0, u1, v1);
            }

            RenderSystem.setShaderColor(1.0f, 1.0f, 1.0f, 1.0f);
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
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        super.render(graphics, mouseX, mouseY, partialTick);
        this.renderTooltip(graphics, mouseX, mouseY);
    }

    @Override
    public void renderTooltip(GuiGraphics graphics, int mouseX, int mouseY) {
        if (menu.getBlockEntity() != null) {
            List<FluidTank> tanks = menu.getBlockEntity().getFluidTanks();
            int tankCount = tanks.size();
            int totalWidth = tankCount * FLUID_BAR_WIDTH + (tankCount - 1) * FLUID_GAP;
            int startX = leftPos - totalWidth;
            int startY = topPos + 18;
            for (int i = 0; i < tankCount; i++) {
                int x = startX + i * (FLUID_BAR_WIDTH + FLUID_GAP);
                int y = startY;
                if (mouseX >= x && mouseX < x + FLUID_BAR_WIDTH && mouseY >= y && mouseY < y + FLUID_BAR_HEIGHT) {
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
'''

if __name__ == "__main__":
    rel_path = os.path.join(PACKAGE_PATH, "screen", "TieredContainerScreen.java")
    full_path = os.path.join(JAVA_SRC, rel_path)
    write_file(full_path, screen_code)
    print("✅ TieredContainerScreen.java 已更新。使用 TextureAtlasSprite 绘制，背景白色，流体原色，并添加了缺纹时的粉红色fallback。")