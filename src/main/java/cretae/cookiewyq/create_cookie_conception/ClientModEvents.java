package cretae.cookiewyq.create_cookie_conception;

import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonObject;
import cretae.cookiewyq.create_cookie_conception.model.TankDynamicBakedModel;
import cretae.cookiewyq.create_cookie_conception.init.ModMenus;
import cretae.cookiewyq.create_cookie_conception.screen.TieredContainerScreen;
import net.minecraft.client.renderer.block.model.ItemOverrides;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.client.resources.model.Material;
import net.minecraft.client.resources.model.ModelBaker;
import net.minecraft.client.resources.model.ModelState;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ModelEvent;
import net.neoforged.neoforge.client.event.RegisterMenuScreensEvent;
import net.neoforged.neoforge.client.model.geometry.IGeometryBakingContext;
import net.neoforged.neoforge.client.model.geometry.IGeometryLoader;
import net.neoforged.neoforge.client.model.geometry.IUnbakedGeometry;
import org.jetbrains.annotations.NotNull;

import java.util.Objects;
import java.util.function.Function;

@EventBusSubscriber(modid = CookieConceptionMod.MODID, value = Dist.CLIENT)
public class ClientModEvents {

    @SubscribeEvent
    public static void registerScreens(RegisterMenuScreensEvent event) {
        event.register(ModMenus.TIERED_CONTAINER.get(), TieredContainerScreen::new);
    }

    @SubscribeEvent
    public static void registerGeometryLoaders(ModelEvent.RegisterGeometryLoaders event) {
        event.register(
            ResourceLocation.fromNamespaceAndPath(CookieConceptionMod.MODID, "tank_dynamic"),
            new TankGeometryLoader()
        );
    }

    private static class TankGeometryLoader implements IGeometryLoader<TankGeometry> {
        @Override
        public TankGeometry read(JsonObject jsonObject, JsonDeserializationContext deserializationContext) {
            int tankCount = jsonObject.has("tank_count") ? jsonObject.get("tank_count").getAsInt() : 1;
            return new TankGeometry(tankCount);
        }
    }

    private static class TankGeometry implements IUnbakedGeometry<TankGeometry> {
        private final int tankCount;

        public TankGeometry(int tankCount) {
            this.tankCount = tankCount;
        }

        @Override
        public @NotNull BakedModel bake(IGeometryBakingContext context, ModelBaker baker, Function<Material, TextureAtlasSprite> spriteGetter, ModelState modelState, ItemOverrides overrides) {
            BakedModel baseModel = baker.bake(Objects.requireNonNull(context.getRenderTypeHint()), modelState, spriteGetter);
            return new TankDynamicBakedModel(baseModel, tankCount);
        }
    }
}
