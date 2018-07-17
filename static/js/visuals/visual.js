import { removeObjectByName } from '../common.js';

class Visual {
    constructor(scene, settings) {
        this._scene = scene;

        this._name = settings.name || 'visual';
        this._visible = settings.visible || true;

        this._cache = {};

        this._visual = undefined;
    }

    get scene() {
        return this._scene;
    }

    set scene(value) {
        if (this._scene != undefined) {
            removeObjectByName(this._scene, this._name);
        }
        this._scene = value;
        if (this._visual != undefined) {
            this._scene.add(this._visual);
        }
    }

    get name() {
        return this._name;
    }

    set name(value) {
        throw new Error('"name" property is read only!');
    }

    get visible() {
        return this._visible;
    }

    set visible(value) {
        this._visible = value;
        if (this._visual != undefined) {
            this._visual.visible = value;
        }
    }

    get cache() {
        return this._cache;
    }

    set cache(value) {
        throw new Error('"cache" property is read only!');
    }

    get visual() {
        return this._visual;
    }

    set visual(value) {
        if (this._scene != undefined) {
            removeObjectByName(this._scene, this._name);
        }
        this._visual = value;
        if (this._visual != undefined) {
            this._scene.add(this._visual);
        }
    }

    route() {
        throw Error('Method must be reimplemented in subclass!');
    }

    add() {
        if (this._scene != undefined) {
            removeObjectByName(this._scene, this._name);
        }

        var route = this.route();

        if (route in this._cache) {
            this._visual = this._cache[route];

            this._scene.add(this._visual);
        } else {
            this.fetch(route);
        }
    }

    create(geometry) {
        throw Error('Method must be reimplemented in subclass!');
    }

    fetch(route) {
        var loader = new THREE.BufferGeometryLoader();
        loader.load(
            route,
            function(geometry, materials) {
                this._visual = this.create(geometry);

                this._cache[route] = this._visual;

                this._scene.add(this._visual);
            }.bind(this)
        );
    }
}

export { Visual };
