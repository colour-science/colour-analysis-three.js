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
        this._imageColourspace = 'sRGB';

        this._imageVisual = undefined;
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
    }

    get secondaryColourspace() {
        return this._secondaryColourspace;
    }

    set secondaryColourspace(value) {
        this._secondaryColourspace = value;
    }

    get imageColourspace() {
        return this._imageColourspace;
    }

    set imageColourspace(value) {
        this._imageColourspace = value;
    }

    addImageVisual(settings) {
        this._imageVisual = new ImageVisual(this.scene, {
            ...{
                image: settings.image,
                colourspace: this._imageColourspace
            },
            ...settings
        });
        this._imageVisual.add();
    }
}

export { ImageView };
