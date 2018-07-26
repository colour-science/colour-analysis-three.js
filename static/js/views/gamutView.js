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

        this._workingColourspace = 'sRGB';
        this._compareColourspace = 'DCI-P3';
        this._imageColourspace = 'sRGB';

        this._viewAxesVisual = undefined;

        // The following groups are defining the rendering order.
        this._spectralLocusVisualGroup = new THREE.Group();
        this._spectralLocusVisualGroup.name = 'spectral-locus-visual-group';
        this._scene.add(this._spectralLocusVisualGroup);
        this._spectralLocusVisual = undefined;

        this._compareColourspaceVisualGroup = new THREE.Group();
        this._compareColourspaceVisualGroup.name =
            'compare-colourspace-visual-group';
        this._scene.add(this._compareColourspaceVisualGroup);
        this._compareColourspaceVisual = undefined;

        this._workingColourspaceVisualGroup = new THREE.Group();
        this._workingColourspaceVisualGroup.name =
            'working-colourspace-visual-group';
        this._scene.add(this._workingColourspaceVisualGroup);
        this._workingColourspaceVisual = undefined;

        this._imageScatterVisualGroup = new THREE.Group();
        this._imageScatterVisualGroup.name = 'image-scatter-visual-group';
        this._scene.add(this._imageScatterVisualGroup);
        this._imageScatterVisual = undefined;
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

        if (this._compareColourspaceVisual != undefined) {
            this._compareColourspaceVisual.colourspaceModel = value;
        }

        if (this._workingColourspaceVisual != undefined) {
            this._workingColourspaceVisual.colourspaceModel = value;
        }

        if (this._imageScatterVisual != undefined) {
            this._imageScatterVisual.colourspaceModel = value;
        }
    }

    get workingColourspace() {
        return this._workingColourspace;
    }

    set workingColourspace(value) {
        this._workingColourspace = value;

        if (this._workingColourspaceVisual != undefined) {
            this._workingColourspaceVisual.colourspace = value;
        }
    }

    get compareColourspace() {
        return this._compareColourspace;
    }

    set compareColourspace(value) {
        this._compareColourspace = value;

        if (this._compareColourspaceVisual != undefined) {
            this._compareColourspaceVisual.colourspace = value;
        }
    }

    get imageColourspace() {
        return this._imageColourspace;
    }

    set imageColourspace(value) {
        this._imageColourspace = value;

        if (this._imageScatterVisual != undefined) {
            this._imageScatterVisual.colourspace = value;
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

    get compareColourspaceVisual() {
        return this._compareColourspaceVisual;
    }

    set compareColourspaceVisual(value) {
        throw new Error('"compareColourspaceVisual" property is read only!');
    }

    get workingColourspaceVisual() {
        return this._workingColourspaceVisual;
    }

    set workingColourspaceVisual(value) {
        throw new Error('"workingColourspaceVisual" property is read only!');
    }

    get imageScatterVisual() {
        return this._imageScatterVisual;
    }

    set imageScatterVisual(value) {
        throw new Error('"imageScatterVisual" property is read only!');
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
                    colourspace: this._compareColourspace,
                    colourspaceModel: this._colourspaceModel
                },
                ...settings
            }
        );
        this._spectralLocusVisual.add();
    }

    addCompareColourspaceVisual(settings) {
        this._compareColourspaceVisual = new ColourspaceVisual(
            this._compareColourspaceVisualGroup,
            {
                ...{
                    name: 'compare-colourspace-visual',
                    colourspace: this._compareColourspace,
                    colourspaceModel: this._colourspaceModel,
                    segments: 8,
                    wireframe: true
                },
                ...settings
            }
        );
        this._compareColourspaceVisual.add();
    }

    addWorkingColourspaceVisual(settings) {
        this._workingColourspaceVisual = new ColourspaceVisual(
            this._workingColourspaceVisualGroup,
            {
                ...{
                    name: 'working-colourspace-visual',
                    colourspace: this._workingColourspace,
                    colourspaceModel: this._colourspaceModel
                },
                ...settings
            }
        );
        this._workingColourspaceVisual.add();
    }

    addImageScatterVisual(settings) {
        this._imageScatterVisual = new ImageScatterVisual(
            this._imageScatterVisualGroup,
            {
                ...{
                    image: settings.image,
                    colourspace: this._workingColourspace,
                    colourspaceModel: this._colourspaceModel
                },
                ...settings
            }
        );
        this._imageScatterVisual.add();
    }
}

export { GamutView };
