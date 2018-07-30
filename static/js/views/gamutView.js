import { PerspectiveView } from './perspectiveView.js';
import { ViewAxesVisual } from '../visuals/viewAxesVisual.js';
import { ColourspaceVisual } from '../visuals/colourspaceVisual.js';
import { SpectralLocusVisual } from '../visuals/spectralLocusVisual.js';
import { ImageScatterVisual } from '../visuals/imageScatterVisual.js';

class GamutView extends PerspectiveView {
    constructor(container, settings) {
        super(container, settings);

        settings = {
            ...{
                scene: {
                    background: new THREE.Color('#333333')
                },
                fog: {
                    enable: true,
                    color: '#333333',
                    density: 0.05
                },
                camera: { position: new THREE.Vector3(-3, 3, 3) },
                controls: { target: new THREE.Vector3(1 / 3, 0.5, 1 / 3) },
                grid: {
                    enable: true,
                    size: 2,
                    divisions: 20,
                    colorCenterLine: '#111111',
                    colorGrid: '#222222'
                },
                axes: { enable: true }
            },
            ...settings
        };

        this.renderer.sortObjects = false;

        this.scene.background = settings.scene.background;
        if (settings.fog.enable) {
            this.scene.fog = new THREE.FogExp2(
                settings.fog.color,
                settings.fog.density
            );
        }

        this.camera.position.copy(settings.camera.position);
        this.controls.target = settings.controls.target;

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

        this._colourspaceModel = 'CIE xyY';

        this._primaryColourspace = 'sRGB';
        this._secondaryColourspace = 'DCI-P3';

        this._imageColourspace = 'Primary';

        this._viewAxesVisual = undefined;

        // The following groups are defining the rendering order.
        this._spectralLocusVisualGroup = new THREE.Group();
        this._spectralLocusVisualGroup.name = 'spectral-locus-visual-group';
        this._scene.add(this._spectralLocusVisualGroup);
        this._spectralLocusVisual = undefined;

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

    get colourspaceModel() {
        return this._colourspaceModel;
    }

    set colourspaceModel(value) {
        this._colourspaceModel = value;

        if (this._viewAxesVisual != undefined) {
            this._viewAxesVisual.colourspaceModel = value;
        }

        if (this._spectralLocusVisual != undefined) {
            this._spectralLocusVisual.colourspaceModel = value;
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

    get viewAxesVisual() {
        return this._viewAxesVisual;
    }

    set viewAxesVisual(value) {
        throw new Error('"viewAxesVisual" property is read only!');
    }

    get spectralLocusVisual() {
        return this._spectralLocusVisual;
    }

    set spectralLocusVisual(value) {
        throw new Error('"spectralLocusVisual" property is read only!');
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
        this._viewAxesVisual = new ViewAxesVisual(this, {
            ...{
                colourspaceModel: this._colourspaceModel
            },
            ...settings
        });
        this._viewAxesVisual.add();
    }

    addSpectralLocusVisual(settings) {
        this._spectralLocusVisual = new SpectralLocusVisual(
            this._spectralLocusVisualGroup,
            {
                ...{
                    colourspace: this._secondaryColourspace,
                    colourspaceModel: this._colourspaceModel
                },
                ...settings
            }
        );
        this._spectralLocusVisual.add();
    }

    addSecondaryColourspaceVisual(settings) {
        this._secondaryColourspaceVisual = new ColourspaceVisual(
            this._secondaryColourspaceVisualGroup,
            {
                ...{
                    name: 'secondary-colourspace-visual',
                    colourspace: this._secondaryColourspace,
                    colourspaceModel: this._colourspaceModel,
                    wireframe: true
                },
                ...settings
            }
        );
        this._secondaryColourspaceVisual.add();
    }

    addPrimaryColourspaceVisual(settings) {
        this._primaryColourspaceVisual = new ColourspaceVisual(
            this._primaryColourspaceVisualGroup,
            {
                ...{
                    name: 'primary-colourspace-visual',
                    colourspace: this._primaryColourspace,
                    colourspaceModel: this._colourspaceModel
                },
                ...settings
            }
        );
        this._primaryColourspaceVisual.add();
    }

    addImageScatterVisual(settings) {
        this._imageScatterVisual = new ImageScatterVisual(
            this._imageScatterVisualGroup,
            {
                ...{
                    image: settings.image,
                    primaryColourspace: this._primaryColourspace,
                    secondaryColourspace: this._secondaryColourspace,
                    imageColourspace: this._imageColourspace,
                    colourspaceModel: this._colourspaceModel
                },
                ...settings
            }
        );
        this._imageScatterVisual.add();
    }

    addImageScatterOverlayVisual(settings) {
        this._imageScatterOverlayVisual = new ImageScatterVisual(
            this._imageScatterOverlayVisualGroup,
            {
                ...{
                    name: 'image-scatter-overlay-visual',
                    image: settings.image,
                    primaryColourspace: this._primaryColourspace,
                    secondaryColourspace: this._secondaryColourspace,
                    imageColourspace: this._imageColourspace,
                    colourspaceModel: this._colourspaceModel,
                    uniformOpacity: 0.5
                },
                ...settings
            }
        );
        this._imageScatterOverlayVisual.add();
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
