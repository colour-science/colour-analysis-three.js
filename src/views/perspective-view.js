import { View } from './view.js';
import merge from 'deepmerge';

/**
 * @author Colour Developers / https://www.colour-science.org/
 */

class PerspectiveView extends View {
    constructor(container, settings) {
        super(container, settings);

        settings = merge(
            {
                camera: {
                    fov: 45,
                    up: { x: 0, y: 1, z: 0 },
                    near: 0.001,
                    far: 1000
                }
            },
            settings || {}
        );

        this._camera = new THREE.PerspectiveCamera(
            settings.camera.fov,
            this.container.clientWidth / this.container.clientHeight,
            settings.camera.near,
            settings.camera.far
        );
        this._camera.name = 'perspective-camera';
        this._camera.up = new THREE.Vector3(
            settings.camera.up.x,
            settings.camera.up.y,
            settings.camera.up.z
        );

        this._scene.add(this._camera);

        this._controls = new THREE.TrackballControls(
            this._camera,
            this.container
        );
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
