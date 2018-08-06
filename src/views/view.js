import { removeObjectByName } from '../common.js';

class View {
    constructor(container, settings) {
        this._container = container;

        settings = {
            ...{
                renderer: { antialias: true }
            },
            ...settings
        };

        this._renderer = new THREE.WebGLRenderer({
            antialias: settings.renderer.antialias
        });
        this._renderer.setPixelRatio(window.devicePixelRatio);
        this._renderer.setSize(
            this._container.clientWidth,
            this._container.clientHeight
        );
        this._container.appendChild(this._renderer.domElement);

        this._scene = new THREE.Scene();

        this._observer = new MutationObserver(
            this.resizeToContainer.bind(this)
        );
        this._observer.observe(this._container, {
            attributes: true
        });
        window.addEventListener(
            'resize',
            this.resizeToContainer.bind(this),
            false
        );
    }

    get container() {
        return this._container;
    }

    set container(value) {
        throw new Error('"container" property is read only!');
    }

    get renderer() {
        return this._renderer;
    }

    set renderer(value) {
        throw new Error('"renderer" property is read only!');
    }

    get scene() {
        return this._scene;
    }

    set scene(value) {
        throw new Error('"scene" property is read only!');
    }

    removeObjectByName(name) {
        removeObjectByName(this._scene, name);
    }

    resizeToContainer() {
        var width = this._container.clientWidth;
        var height = this._container.clientHeight;

        if (
            this._container.width !== width ||
            this._container.height !== height
        ) {
            this._renderer.setSize(width, height);
        }
    }

    animate() {
        requestAnimationFrame(this.animate.bind(this));
        this._controls.update();
        this.render();
    }

    render() {
        this._renderer.render(this._scene, this._camera);
    }
}

export { View };
