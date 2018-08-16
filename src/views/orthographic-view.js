import { View } from './view.js';

/**
 * @author Colour Developers / http://colour-science.org/
 */

class OrthographicView extends View {
    constructor(container, settings) {
        super(container, settings);

        settings = {
            ...{
                camera: {
                    up: new THREE.Vector3(0, 1, 0),
                    near: 0.001,
                    far: 1000
                }
            },
            ...settings
        };

        var aspectRatio =
            this.container.clientWidth / this.container.clientHeight;
        this._camera = new THREE.OrthographicCamera(
            -0.5,
            0.5,
            0.5 / aspectRatio,
            -0.5 / aspectRatio,
            settings.camera.near,
            settings.camera.far
        );
        this._camera.name = 'orthographic-camera';
        this._camera.up = settings.camera.up;

        this._scene.add(this._camera);

        this._controls = new THREE.OrbitControls(this._camera, this.container);
        this._controls.enableRotate = false;
    }

    get camera() {
        return this._camera;
    }

    set camera(value) {
        throw new Error('"camera" property is read only!');
    }

    get controls() {
        return this._controls;
    }

    set controls(value) {
        throw new Error('"controls" property is read only!');
    }

    resizeToContainer() {
        super.resizeToContainer();

        var width = this.container.clientWidth;
        var height = this.container.clientHeight;

        if (
            this.container.width !== width ||
            this.container.height !== height
        ) {
            this.renderer.setSize(width, height);
            var aspectRatio =
                this.container.clientWidth / this.container.clientHeight;
            this._camera.top = 0.5 / aspectRatio;
            this._camera.bottom = -0.5 / aspectRatio;
            this._camera.updateProjectionMatrix();
        }
    }
}

export { OrthographicView };
