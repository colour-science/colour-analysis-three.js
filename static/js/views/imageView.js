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

        this._cache = {};

        this.renderer.gammaOutput = settings.renderer.gammaOutput;

        this.scene.background = settings.scene.background;

        this.camera.position.copy(settings.camera.position);
        this.controls.target = settings.controls.target;

        this._workingColourspace = 'sRGB';
        this._compareColourspace = 'DCI-P3';
        this._colourspaceModel = 'CIE xyY';

        this._imageVisual = undefined;
    }

    addImageVisual(image, settings) {
        this._imageVisual = new ImageVisual(this.scene, {
            ...{
                colourspace: this._workingColourspace,
                colourspaceModel: this._colourspaceModel
            },
            ...settings
        });
        this._imageVisual.add();
    }
}

export { ImageView };
