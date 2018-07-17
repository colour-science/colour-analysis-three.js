import { View } from './view.js';

class PerspectiveView extends View {
    constructor(container, settings) {
        super(container, settings);

        settings = {
            ...{
                camera: {
                    fov: 45,
                    up: new THREE.Vector3(0, 1, 0),
                    near: 0.001,
                    far: 1000
                }
            },
            ...settings
        };

        this._camera = new THREE.PerspectiveCamera(
            settings.camera.fov,
            this.container.clientWidth / this.container.clientHeight,
            settings.camera.near,
            settings.camera.far
        );
        this._camera.up = settings.camera.up;

        this._scene.add(this._camera);

        this._controls = new THREE.OrbitControls(this._camera, this.container);
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
            this._camera.aspect = width / height;
            this._camera.updateProjectionMatrix();
        }
    }
}

export { PerspectiveView };
