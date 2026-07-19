package cretae.cookiewyq.create_cookie_conception.util;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.nbt.NbtOps;
import net.neoforged.neoforge.fluids.FluidStack;
import java.util.Optional;

public class TankRenderInfo {
    private final FluidStack fluid;
    private final float fillRatio;

    public TankRenderInfo(FluidStack fluid, float fillRatio) {
        this.fluid = fluid.copy();
        this.fillRatio = fillRatio;
    }

    public FluidStack getFluid() { return fluid; }
    public float getFillRatio() { return fillRatio; }

    public CompoundTag serialize() {
        CompoundTag tag = new CompoundTag();
        // NeoForge 1.21.1 uses Codec to serialize FluidStack
        Tag fluidTag = FluidStack.OPTIONAL_CODEC.encodeStart(NbtOps.INSTANCE, fluid).getOrThrow();
        tag.put("Fluid", fluidTag);
        tag.putFloat("FillRatio", fillRatio);
        return tag;
    }

    public static TankRenderInfo deserialize(CompoundTag tag) {
        Optional<FluidStack> fluidOpt = FluidStack.OPTIONAL_CODEC.parse(NbtOps.INSTANCE, tag.get("Fluid")).result();
        FluidStack fluid = fluidOpt.orElse(FluidStack.EMPTY);
        float ratio = tag.getFloat("FillRatio");
        return new TankRenderInfo(fluid, ratio);
    }
}
