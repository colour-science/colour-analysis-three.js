import merge from 'deepmerge';
import { PerspectiveView } from './perspective-view.js';
import { ViewAxesVisual } from '../visuals/view-axes-visual.js';
import { ColourspaceVisual } from '../visuals/colourspace-visual.js';
import { ImageScatterVisual } from '../visuals/image-scatter-visual.js';
import { PointerGamutVisual } from '../visuals/pointer-gamut-visual.js';
import { SpectralLocusVisual } from '../visuals/spectral-locus-visual.js';
import { VisibleSpectrumVisual } from '../visuals/visible-spectrum-visual.js';

/**
 * @author Colour Developers / https://www.colour-science.org/
 */

class GamutView extends PerspectiveView {
    constructor(container, settings) {
        super(container, settings);

        settings = merge(
            {
                scene: {
                    background: '#333333'
                },
                fog: {
                    enable: true,
                    color: '#333333',
                    density: 0.05
                },
                camera: { position: { x: -3, y: 3, z: 3 } },
                controls: { target: { x: 1 / 3, y: 0.5, z: 1 / 3 } },
                grid: {
                    enable: true,
                    size: 2,
                    divisions: 20,
                    colorCenterLine: '#111111',
                    colorGrid: '#222222'
                },
                axes: { enable: true },
                image: 'Rose.ProPhoto.jpg',
                primaryColourspace: 'sRGB',
                secondaryColourspace: 'DCI-P3',
                imageColourspace: 'Primary',
                imageDecodingCctf: 'sRGB',
                colourspaceModel: 'CIE xyY'
            },
            settings || {}
        );

        this.renderer.sortObjects = false;

        this.scene.background = new THREE.Color(settings.scene.background);
        if (settings.fog.enable) {
            this.scene.fog = new THREE.FogExp2(
                settings.fog.color,
                settings.fog.density
            );
        }

        this.camera.position.copy(
            new THREE.Vector3(
                settings.camera.position.x,
                settings.camera.position.y,
                settings.camera.position.z
            )
        );
        this.controls.target = new THREE.Vector3(
            settings.controls.target.x,
            settings.controls.target.y,
            settings.controls.target.z
        );

        if (settings.grid.enable) {
            this.grid = new THREE.GridHelper(
                settings.grid.size,
                settings.grid.divisions,
                settings.grid.colorCenterLine,
                settings.grid.colorGrid
            );
            this.grid.name = 'grid';
            this.scene.add(this.grid);
        }

        if (settings.axes.enable) {
            this.axes = new THREE.AxesHelper();
            // prettier-ignore
            this.axes.geometry.attributes.color.array.set([
                0, 0, 1, 0, 0, 1,
                0, 1, 0, 0, 1, 0,
                1, 0, 0, 1, 0, 0,
            ]);
            this.axes.name = 'axes';
            this.scene.add(this.axes);
        }

        this._image = settings.image;
        this._primaryColourspace = settings.primaryColourspace;
        this._secondaryColourspace = settings.secondaryColourspace;
        this._imageColourspace = settings.imageColourspace;
        this._imageDecodingCctf = settings.imageDecodingCctf;
        this._colourspaceModel = settings.colourspaceModel;

        this._viewAxesVisual = undefined;

        // The following groups are defining the rendering order.
        this._visibleSpectrumVisualGroup = new THREE.Group();
        this._visibleSpectrumVisualGroup.name = 'visible-spectrum-visual-group';
        this._scene.add(this._visibleSpectrumVisualGroup);
        this._visibleSpectrumVisual = undefined;

        this._spectralLocusVisualGroup = new THREE.Group();
        this._spectralLocusVisualGroup.name = 'spectral-locus-visual-group';
        this._scene.add(this._spectralLocusVisualGroup);
        this._spectralLocusVisual = undefined;

        this._pointerGamutVisualGroup = new THREE.Group();
        this._pointerGamutVisualGroup.name = 'pointer-gamut-visual-group';
        this._scene.add(this._pointerGamutVisualGroup);
        this._pointerGamutVisual = undefined;

        this._secondaryColourspaceVisualGroup = new THREE.Group();
        this._secondaryColourspaceVisualGroup.name =
            'secondary-colourspace-visual-group';
        this._scene.add(this._secondaryColourspaceVisualGroup);
        this._secondaryColourspaceVisual = undefined;

        this._primaryColourspaceVisualGroup = new THREE.Group();
        this._primaryColourspaceVisualGroup.name =
            'primary-colourspace-visual-group';
        this._scene.add(this._primaryColourspaceVisualGroup);
        this._primaryColourspaceVisual = undefined;

        this._imageScatterVisualGroup = new THREE.Group();
        this._imageScatterVisualGroup.name = 'image-scatter-visual-group';
        this._scene.add(this._imageScatterVisualGroup);
        this._imageScatterVisual = undefined;

        this._imageScatterOverlayVisualGroup = new THREE.Group();
        this._imageScatterOverlayVisualGroup.name =
            'image-scatter-overlay-visual-group';
        this._scene.add(this._imageScatterOverlayVisualGroup);
        this._imageScatterOverlayVisual = undefined;
    }

    get image() {
        return this._image;
    }

    set image(value) {
        this._image = value;

        if (this._imageScatterVisual != undefined) {
            this._imageScatterVisual.image = value;
        }

        if (this._imageScatterOverlayVisual != undefined) {
            this._imageScatterOverlayVisual.image = value;
        }
    }

    get primaryColourspace() {
        return this._primaryColourspace;
    }

    set primaryColourspace(value) {
        this._primaryColourspace = value;

        if (this._primaryColourspaceVisual != undefined) {
            this._primaryColourspaceVisual.colourspace = value;
        }

        if (this._imageScatterVisual != undefined) {
            this._imageScatterVisual.primaryColourspace = value;
        }

        if (this._imageScatterOverlayVisual != undefined) {
            this._imageScatterOverlayVisual.primaryColourspace = value;
        }
    }

    get secondaryColourspace() {
        return this._secondaryColourspace;
    }

    set secondaryColourspace(value) {
        this._secondaryColourspace = value;

        if (this._secondaryColourspaceVisual != undefined) {
            this._secondaryColourspaceVisual.colourspace = value;
        }

        if (this._imageScatterVisual != undefined) {
            this._imageScatterVisual.secondaryColourspace = value;
        }

        if (this._imageScatterOverlayVisual != undefined) {
            this._imageScatterOverlayVisual.secondaryColourspace = value;
        }
    }

    get imageColourspace() {
        return this._imageColourspace;
    }

    set imageColourspace(value) {
        if (!['Primary', 'Secondary'].includes(value)) {
            throw new Error(
                '"imageColourspace" value must be ' +
                    'one of ["Primary", "Secondary"]!'
            );
        }

        this._imageColourspace = value;

        if (this._imageScatterVisual != undefined) {
            this._imageScatterVisual.imageColourspace = value;
        }

        if (this._imageScatterOverlayVisual != undefined) {
            this._imageScatterOverlayVisual.imageColourspace = value;
        }
    }

    get imageDecodingCctf() {
        return this._imageDecodingCctf;
    }

    set imageDecodingCctf(value) {
        this._imageDecodingCctf = value;

        if (this._imageScatterVisual != undefined) {
            this._imageScatterVisual.imageDecodingCctf = value;
        }

        if (this._imageScatterOverlayVisual != undefined) {
            this._imageScatterOverlayVisual.imageDecodingCctf = value;
        }
    }

    get colourspaceModel() {
        return this._colourspaceModel;
    }

    set colourspaceModel(value) {
        this._colourspaceModel = value;

        if (this._viewAxesVisual != undefined) {
            this._viewAxesVisual.colourspaceModel = value;
        }

        if (this._visibleSpectrumVisual != undefined) {
            this._visibleSpectrumVisual.colourspaceModel = value;
        }

        if (this._spectralLocusVisual != undefined) {
            this._spectralLocusVisual.colourspaceModel = value;
        }

        if (this._pointerGamutVisual != undefined) {
            this._pointerGamutVisual.colourspaceModel = value;
        }

        if (this._secondaryColourspaceVisual != undefined) {
            this._secondaryColourspaceVisual.colourspaceModel = value;
        }

        if (this._primaryColourspaceVisual != undefined) {
            this._primaryColourspaceVisual.colourspaceModel = value;
        }

        if (this._imageScatterVisual != undefined) {
            this._imageScatterVisual.colourspaceModel = value;
        }

        if (this._imageScatterOverlayVisual != undefined) {
            this._imageScatterOverlayVisual.colourspaceModel = value;
        }
    }

    get viewAxesVisual() {
        return this._viewAxesVisual;
    }

    set viewAxesVisual(value) {
        throw new Error('"viewAxesVisual" property is read only!');
    }

    get visibleSpectrumVisual() {
        return this._visibleSpectrumVisual;
    }

    set visibleSpectrumVisual(value) {
        throw new Error('"visibleSpectrumVisual" property is read only!');
    }

    get spectralLocusVisual() {
        return this._spectralLocusVisual;
    }

    set spectralLocusVisual(value) {
        throw new Error('"spectralLocusVisual" property is read only!');
    }

    get pointerGamutVisual() {
        return this._pointerGamutVisual;
    }

    set pointerGamutVisual(value) {
        throw new Error('"pointerGamutVisual" property is read only!');
    }

    get secondaryColourspaceVisual() {
        return this._secondaryColourspaceVisual;
    }

    set secondaryColourspaceVisual(value) {
        throw new Error('"secondaryColourspaceVisual" property is read only!');
    }

    get primaryColourspaceVisual() {
        return this._primaryColourspaceVisual;
    }

    set primaryColourspaceVisual(value) {
        throw new Error('"primaryColourspaceVisual" property is read only!');
    }

    get imageScatterVisual() {
        return this._imageScatterVisual;
    }

    set imageScatterVisual(value) {
        throw new Error('"imageScatterVisual" property is read only!');
    }

    get imageScatterOverlayVisual() {
        return this._imageScatterOverlayVisual;
    }

    set imageScatterOverlayVisual(value) {
        throw new Error('"imageScatterOverlayVisual" property is read only!');
    }

    addViewAxesVisual(settings) {
        this._viewAxesVisual = new ViewAxesVisual(
            this,
            merge(
                {
                    colourspaceModel: this._colourspaceModel
                },
                settings || {}
            )
        );
        this._viewAxesVisual.add();
    }

    addVisibleSpectrumVisual(settings) {
        this._visibleSpectrumVisual = new VisibleSpectrumVisual(
            this._visibleSpectrumVisualGroup,
            merge(
                {
                    colourspaceModel: this._colourspaceModel
                },
                settings || {}
            )
        );
        this._visibleSpectrumVisual.add();
    }

    addSpectralLocusVisual(settings) {
        this._spectralLocusVisual = new SpectralLocusVisual(
            this._spectralLocusVisualGroup,
            merge(
                {
                    colourspace: this._secondaryColourspace,
                    colourspaceModel: this._colourspaceModel
                },
                settings || {}
            )
        );
        this._spectralLocusVisual.add();
    }

    addPointerGamutVisual(settings) {
        this._pointerGamutVisual = new PointerGamutVisual(
            this._pointerGamutVisualGroup,
            merge(
                {
                    colourspaceModel: this._colourspaceModel
                },
                settings || {}
            )
        );
        this._pointerGamutVisual.add();
    }

    addSecondaryColourspaceVisual(settings) {
        this._secondaryColourspaceVisual = new ColourspaceVisual(
            this._secondaryColourspaceVisualGroup,
            merge(
                {
                    name: 'secondary-colourspace-visual',
                    colourspace: this._secondaryColourspace,
                    colourspaceModel: this._colourspaceModel,
                    wireframe: true,
                    uniformOpacity: 0.25
                },
                settings || {}
            )
        );
        this._secondaryColourspaceVisual.add();
    }

    addPrimaryColourspaceVisual(settings) {
        this._primaryColourspaceVisual = new ColourspaceVisual(
            this._primaryColourspaceVisualGroup,
            merge(
                {
                    name: 'primary-colourspace-visual',
                    colourspace: this._primaryColourspace,
                    colourspaceModel: this._colourspaceModel
                },
                settings || {}
            )
        );
        this._primaryColourspaceVisual.add();
    }

    addImageScatterVisual(settings) {
        this._imageScatterVisual = new ImageScatterVisual(
            this._imageScatterVisualGroup,
            merge(
                {
                    image: this._image,
                    primaryColourspace: this._primaryColourspace,
                    secondaryColourspace: this._secondaryColourspace,
                    imageColourspace: this._imageColourspace,
                    imageDecodingCctf: this._imageDecodingCctf,
                    colourspaceModel: this._colourspaceModel
                },
                settings || {}
            )
        );
        this._imageScatterVisual.add();
    }

    addImageScatterOverlayVisual(settings) {
        this._imageScatterOverlayVisual = new ImageScatterVisual(
            this._imageScatterOverlayVisualGroup,
            merge(
                {
                    name: 'image-scatter-overlay-visual',
                    image: this._image,
                    primaryColourspace: this._primaryColourspace,
                    secondaryColourspace: this._secondaryColourspace,
                    imageColourspace: this._imageColourspace,
                    imageDecodingCctf: this._imageDecodingCctf,
                    colourspaceModel: this._colourspaceModel,
                    uniformOpacity: 0.5
                },
                settings || {}
            )
        );
        this._imageScatterOverlayVisual.add();
    }

    isLoading() {
        return (
            this._viewAxesVisual.loading ||
            this._visibleSpectrumVisual.loading ||
            this._spectralLocusVisual.loading ||
            this._pointerGamutVisual.loading ||
            this._secondaryColourspaceVisual.loading ||
            this._primaryColourspaceVisual.loading ||
            this._imageScatterVisual.loading ||
            this._imageScatterOverlayVisual.loading
        );
    }

    animate() {
        if (this._imageScatterOverlayVisual != undefined) {
            if (this._imageScatterOverlayVisual.visual != undefined) {
                this._imageScatterOverlayVisual.visual.material.opacity =
                    (this._imageScatterOverlayVisual.uniformOpacity *
                        (1 + Math.sin(new Date().getTime() * 0.0015))) /
                    2;
            }
        }

        super.animate();
    }
}

export { GamutView };
