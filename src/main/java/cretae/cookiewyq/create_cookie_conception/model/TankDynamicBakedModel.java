package cretae.cookiewyq.create_cookie_conception.model;

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
