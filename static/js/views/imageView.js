import { OrthographicView } from './orthographicView.js';
import { ImageVisual } from '../visuals/imageVisual.js';

class ImageView extends OrthographicView {
    constructor(container, settings) {
        super(container, settings);

        settings = {
            ...{
                renderer: {
                    gammaOutput: true
                },
                scene: {
                    background: new THREE.Color('#333333')
                },
                camera: { position: new THREE.Vector3(0, 1, 0) },
                controls: { target: new THREE.Vector3(0, 0, 0) }
            },
            ...settings
        };

        this.renderer.gammaOutput = settings.renderer.gammaOutput;

        this.scene.background = settings.scene.background;

        this.camera.position.copy(settings.camera.position);
        this.controls.target = settings.controls.target;

        this._colourspaceModel = 'CIE xyY';

        this._primaryColourspace = 'sRGB';
        this._secondaryColourspace = 'DCI-P3';

        this._imageColourspace = 'Primary';

        // The following groups are defining the rendering order.
        this._imageVisualGroup = new THREE.Group();
        this._imageVisualGroup.name = 'image-visual-group';
        this._scene.add(this._imageVisualGroup);
        this._imageVisual = undefined;

        this._imageOverlayVisualGroup = new THREE.Group();
        this._imageOverlayVisualGroup.name = 'image-overlay-visual-group';
        this._scene.add(this._imageOverlayVisualGroup);
        this._imageOverlayVisual = undefined;
    }

    get colourspaceModel() {
        return this._colourspaceModel;
    }

    set colourspaceModel(value) {
        this._colourspaceModel = value;
    }

    get primaryColourspace() {
        return this._primaryColourspace;
    }

    set primaryColourspace(value) {
        this._primaryColourspace = value;

        if (this._imageOverlayVisual != undefined) {
            this._imageOverlayVisual.primaryColourspace = value;
        }
    }

    get secondaryColourspace() {
        return this._secondaryColourspace;
    }

    set secondaryColourspace(value) {
        this._secondaryColourspace = value;

        if (this._imageOverlayVisual != undefined) {
            this._imageOverlayVisual.secondaryColourspace = value;
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

        if (this._imageOverlayVisual != undefined) {
            this._imageOverlayVisual.imageColourspace = value;
        }
    }

    get imageVisual() {
        return this._imageVisual;
    }

    set imageVisual(value) {
        throw new Error('"imageVisual" property is read only!');
    }

    get imageOverlayVisual() {
        return this._imageOverlayVisual;
    }

    set imageOverlayVisual(value) {
        throw new Error('"imageOverlayVisual" property is read only!');
    }

    addImageVisual(settings) {
        this._imageVisual = new ImageVisual(this._imageVisualGroup, {
            ...{
                name: 'image-visual',
                image: settings.image,
                primaryColourspace: this._primaryColourspace,
                secondaryColourspace: this._secondaryColourspace,
                imageColourspace: this._imageColourspace
            },
            ...settings
        });
        this._imageVisual.add();
    }

    addImageOverlayVisual(settings) {
        this._imageOverlayVisual = new ImageVisual(
            this._imageOverlayVisualGroup,
            {
                ...{
                    name: 'image-overlay-visual',
                    image: settings.image,
                    primaryColourspace: this._primaryColourspace,
                    secondaryColourspace: this._secondaryColourspace,
                    imageColourspace: this._imageColourspace,
                    uniformOpacity: 0.5,
                    depth: 0.5
                },
                ...settings
            }
        );
        this._imageOverlayVisual.add();
    }

    isLoading() {
        return this._imageVisual.loading || this._imageOverlayVisual.loading;
    }

    animate() {
        if (this._imageOverlayVisual != undefined) {
            if (this._imageOverlayVisual.visual != undefined) {
                this._imageOverlayVisual.visual.material.opacity =
                    (this._imageOverlayVisual.uniformOpacity *
                        (1 + Math.sin(new Date().getTime() * 0.0015))) /
                    2;
            }
        }

        super.animate();
    }
}

export { ImageView };
